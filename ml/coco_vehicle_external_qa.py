"""Deterministic COCO-val bicycle/motorcycle QA for a frozen local detector.

Downloads only selected official COCO images. Never uses this slice for training.
"""

import argparse
import hashlib
import json
import random
import urllib.request
from collections import defaultdict
from pathlib import Path

from ultralytics import YOLO

from phase1 import ROOT


def iou(a, b):
    x1, y1 = max(a[0], b[0]), max(a[1], b[1])
    x2, y2 = min(a[2], b[2]), min(a[3], b[3])
    overlap = max(0, x2 - x1) * max(0, y2 - y1)
    area_a = (a[2] - a[0]) * (a[3] - a[1])
    area_b = (b[2] - b[0]) * (b[3] - b[1])
    return overlap / (area_a + area_b - overlap) if area_a + area_b > overlap else 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model")
    parser.add_argument("--prepare-only", action="store_true")
    parser.add_argument("--report-name", default="v7_external_vehicle_qa.json")
    parser.add_argument("--selection-name", default="selection.json")
    parser.add_argument("--exclude-selection", action="append")
    parser.add_argument("--seed", type=int, default=20260929)
    parser.add_argument("--per-group", type=int, default=40)
    parser.add_argument("--conf", type=float, default=0.25)
    args = parser.parse_args()
    root = ROOT / "data" / "source" / "coco_external"
    annotation_path = root / "instances_val2017.json"
    expected = "e8c7f7908f1d7278341fae127d0da654f102f11bd7b21d8aeefa635b8c810b6f"
    if hashlib.sha256(annotation_path.read_bytes()).hexdigest() != expected:
        raise ValueError("COCO annotation checksum mismatch")
    data = json.loads(annotation_path.read_text(encoding="utf-8"))
    categories = {x["name"]: x["id"] for x in data["categories"]}
    bicycle, motorcycle = categories["bicycle"], categories["motorcycle"]
    by_image = defaultdict(list)
    for ann in data["annotations"]:
        if ann["category_id"] in (bicycle, motorcycle) and not ann.get("iscrowd"):
            by_image[ann["image_id"]].append(ann)
    images = {x["id"]: x for x in data["images"]}
    candidates = {"bicycle_only": [], "motorcycle_only": []}
    for image_id, anns in by_image.items():
        kinds = {ann["category_id"] for ann in anns}
        if kinds == {bicycle}:
            candidates["bicycle_only"].append(image_id)
        elif kinds == {motorcycle}:
            candidates["motorcycle_only"].append(image_id)
    excluded = set()
    for excluded_name in args.exclude_selection or []:
        old = json.loads((root / excluded_name).read_text(encoding="utf-8"))
        excluded.update(row["image_id"] for row in old["selected_before_inference"])
    rng = random.Random(args.seed)
    selected = {}
    for group, ids in candidates.items():
        available = sorted(set(ids) - excluded)
        selected[group] = rng.sample(available, min(args.per_group, len(available)))
    manifest = root / args.selection_name
    if manifest.exists():
        frozen = json.loads(manifest.read_text(encoding="utf-8"))
        selected = {group: [row["image_id"] for row in frozen["selected_before_inference"]
                            if row["group"] == group] for group in candidates}
        if any(len(ids) != args.per_group for ids in selected.values()):
            raise ValueError("Frozen selection size differs from requested per-group size")
    image_dir = root / "images"
    image_dir.mkdir(exist_ok=True)
    rows = []
    for group, ids in selected.items():
        for image_id in ids:
            info = images[image_id]
            path = image_dir / info["file_name"]
            if not path.exists():
                url = f'http://images.cocodataset.org/val2017/{info["file_name"]}'
                urllib.request.urlretrieve(url, path)
            rows.append({"group": group, "image_id": image_id,
                         "file_name": info["file_name"], "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                         "annotations": [ann["bbox"] for ann in by_image[image_id] if ann["category_id"] == bicycle]})
    if manifest.exists():
        if rows != frozen["selected_before_inference"]:
            raise ValueError("Frozen selection contents or image hash changed")
    else:
        manifest.write_text(json.dumps({"seed": args.seed, "source_split": "COCO val2017",
                                        "selection": "random images containing only one of bicycle/motorcycle among those two categories",
                                        "excluded_selection": args.exclude_selection,
                                        "selected_before_inference": rows}, indent=2), encoding="utf-8")
    if args.prepare_only:
        print(json.dumps({"prepared_selection": str(manifest),
                          "images_by_group": {group: len(ids) for group, ids in selected.items()},
                          "excluded_prior_images": len(excluded)}))
        return
    if not args.model:
        raise ValueError("--model is required unless --prepare-only is set")
    model = YOLO(args.model)
    result_rows = []
    matched = total_gt = total_predictions = false_predictions = 0
    for row in rows:
        result = model.predict(str(image_dir / row["file_name"]), imgsz=512, conf=args.conf, verbose=False)[0]
        predictions = [list(map(float, box.xyxy[0].tolist())) for box in result.boxes
                       if int(box.cls[0]) == 4]
        ground_truth = [[x, y, x + w, y + h] for x, y, w, h in row["annotations"]]
        pairs = sorted(((iou(pred, gt), pi, gi) for pi, pred in enumerate(predictions)
                        for gi, gt in enumerate(ground_truth)), reverse=True)
        used_p, used_g = set(), set()
        for score, pi, gi in pairs:
            if score < 0.5:
                break
            if pi not in used_p and gi not in used_g:
                used_p.add(pi)
                used_g.add(gi)
        matched += len(used_g)
        total_gt += len(ground_truth)
        total_predictions += len(predictions)
        false_predictions += len(predictions) - len(used_p)
        result_rows.append({"file_name": row["file_name"], "group": row["group"],
                            "gt_bicycle": len(ground_truth), "predicted_bicycle": len(predictions),
                            "matched_bicycle_iou50": len(used_g)})
    summary = {"model": args.model, "conf": args.conf, "imgsz": 512,
               "images_by_group": {group: len(ids) for group, ids in selected.items()},
               "matched_bicycle_iou50": matched, "gt_bicycle": total_gt,
               "bicycle_recall_iou50": matched / total_gt if total_gt else None,
               "bicycle_precision_iou50": matched / total_predictions if total_predictions else None,
               "false_bicycle_predictions": false_predictions,
               "motorcycle_only_images_with_bicycle_prediction": sum(row["group"] == "motorcycle_only" and row["predicted_bicycle"] > 0 for row in result_rows),
               "rows": result_rows}
    report_path = root / args.report_name
    report_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps({key: value for key, value in summary.items() if key != "rows"}, indent=2))


if __name__ == "__main__":
    main()
