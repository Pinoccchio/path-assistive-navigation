"""Compare frozen v9/v10 models on the same reviewed OI vehicle test IDs."""

import argparse
import hashlib
import json
from collections import Counter

from ultralytics import YOLO

from coco_vehicle_external_qa import iou
from phase1 import ROOT


OI = ROOT / "data" / "source" / "oi_vehicle_v10"
RUN = ROOT / "runs" / "public_phase1_v10_oi_vehicle_candidate"
WEIGHTS = {
    "v9": ROOT / "runs" / "public_phase1_v9_coco_train_candidate" / "yolov8n" / "weights" / "best.pt",
    "v10": RUN / "yolov8n" / "weights" / "best.pt",
}


def boxes(row, class_id, width, height):
    return [[(xc - w / 2) * width, (yc - h / 2) * height,
             (xc + w / 2) * width, (yc + h / 2) * height]
            for category, xc, yc, w, h in row["boxes"] if category == class_id]


def assess(model, rows, checksums, imgsz=512):
    summary = Counter()
    details = []
    for row in rows:
        image_id = row["image_id"]
        path = OI / "images" / "test" / f"{image_id}.jpg"
        assert hashlib.sha256(path.read_bytes()).hexdigest() == checksums[image_id]
        result = model.predict(str(path), imgsz=imgsz, conf=0.25, verbose=False)[0]
        width, height = result.orig_shape[1], result.orig_shape[0]
        pred = {category: [list(map(float, box.xyxy[0].tolist())) for box in result.boxes
                           if int(box.cls[0]) == category] for category in (4, 7)}
        truth = {category: boxes(row, category, width, height) for category in (4, 7)}
        outcome = {"image_id": image_id, "group": row["group"]}
        for category, name in ((4, "bicycle"), (7, "motorcycle")):
            pairs = sorted(((iou(p, g), pi, gi) for pi, p in enumerate(pred[category])
                            for gi, g in enumerate(truth[category])), reverse=True)
            used_p, used_g = set(), set()
            for score, pi, gi in pairs:
                if score < 0.5:
                    break
                if pi not in used_p and gi not in used_g:
                    used_p.add(pi)
                    used_g.add(gi)
            summary[name + "_gt"] += len(truth[category])
            summary[name + "_matched"] += len(used_g)
            summary[name + "_pred"] += len(pred[category])
            outcome[name + "_gt"] = len(truth[category])
            outcome[name + "_matched"] = len(used_g)
            outcome[name + "_pred"] = len(pred[category])
        if row["group"] == "motorcycle" and pred[4]:
            summary["moto_only_images_with_bicycle_prediction"] += 1
        if row["group"] == "small_bicycle" and pred[7]:
            summary["bike_only_images_with_motorcycle_prediction"] += 1
        details.append(outcome)
    return {"counts": dict(summary), "rows": details}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--imgsz", type=int, default=512)
    args = parser.parse_args()
    selection = json.loads((OI / "test_selection.json").read_text(encoding="utf-8"))
    review = json.loads((OI / "review_exclusions.json").read_text(encoding="utf-8"))
    download = json.loads((OI / "test_download_report.json").read_text(encoding="utf-8"))
    rows = [row for row in selection["rows"] if row["image_id"] not in review["test"]]
    assert len(rows) == 64
    report = {"source": "Open Images V7 test", "selection_seed": selection["seed"],
              "pre_inference_review_sha256": hashlib.sha256((OI / "review_exclusions.json").read_bytes()).hexdigest(),
              "images": len(rows), "groups": dict(Counter(row["group"] for row in rows)),
              "conf": 0.25, "imgsz": args.imgsz, "matching_iou": 0.5,
              "limitations": "Source boxes may omit objects; public images do not measure campus or phone performance.",
              "models": {}}
    for name, weights in WEIGHTS.items():
        report["models"][name] = {"weights_sha256": hashlib.sha256(weights.read_bytes()).hexdigest(),
                                  **assess(YOLO(str(weights)), rows, download["sha256_by_image_id"], args.imgsz)}
    RUN.mkdir(parents=True, exist_ok=True)
    filename = "oi_vehicle_test_comparison.json" if args.imgsz == 512 else f"oi_vehicle_test_comparison_{args.imgsz}.json"
    (RUN / filename).write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({name: model["counts"] for name, model in report["models"].items()}, indent=2))


if __name__ == "__main__":
    main()
