"""Per-box bicycle and motorcycle error audit on three frozen COCO-val slices."""

import json
from collections import Counter, defaultdict
from pathlib import Path

from PIL import Image, ImageDraw
from ultralytics import YOLO

from coco_vehicle_external_qa import iou
from phase1 import ROOT


DATA = ROOT / "data" / "source" / "coco_external"
OUT = ROOT / "runs" / "public_phase1_v9_coco_train_candidate" / "failure_analysis"
MODEL = ROOT / "runs" / "public_phase1_v9_coco_train_candidate" / "yolov8n" / "weights" / "best.pt"
SLICES = ("selection.json", "selection_holdout.json", "selection_holdout_v9.json")


def size_bin(area_at_512):
    side = area_at_512 ** 0.5
    if side < 16:
        return "lt16"
    if side < 32:
        return "16to32"
    if side < 64:
        return "32to64"
    return "ge64"


def sheet(items, filename, title):
    if not items:
        return
    width, height, cols, rows = 360, 280, 4, 8
    canvas = Image.new("RGB", (width * cols, height * rows), "white")
    draw = ImageDraw.Draw(canvas)
    for index, item in enumerate(items[:cols * rows]):
        src = DATA / "images" / item["file_name"]
        with Image.open(src) as im:
            im = im.convert("RGB")
            scale = min((width - 12) / im.width, (height - 38) / im.height)
            image = im.resize((round(im.width * scale), round(im.height * scale)))
            x0, y0 = (index % cols) * width, (index // cols) * height + 24
            canvas.paste(image, (x0, y0))
            for box in item["gt_bicycle_boxes"]:
                x1, y1, x2, y2 = [v * scale for v in box]
                draw.rectangle((x0 + x1, y0 + y1, x0 + x2, y0 + y2), outline="lime", width=2)
            for box in item["gt_motorcycle_boxes"]:
                x1, y1, x2, y2 = [v * scale for v in box]
                draw.rectangle((x0 + x1, y0 + y1, x0 + x2, y0 + y2), outline="orange", width=2)
            for pred in item["predictions"]:
                x1, y1, x2, y2 = [v * scale for v in pred["xyxy"]]
                draw.rectangle((x0 + x1, y0 + y1, x0 + x2, y0 + y2),
                               outline="red" if pred["class_id"] == 4 else "cyan", width=2)
            draw.text((x0 + 3, y0 - 18), item["file_name"] + " " + item["group"][:1], fill="black")
    canvas.save(OUT / filename, quality=90)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    annotation = json.loads((DATA / "instances_val2017.json").read_text(encoding="utf-8"))
    images = {row["id"]: row for row in annotation["images"]}
    by_image = defaultdict(list)
    for ann in annotation["annotations"]:
        if ann["category_id"] in (2, 4) and not ann.get("iscrowd"):
            by_image[ann["image_id"]].append(ann)
    selections = []
    for name in SLICES:
        selections.extend(json.loads((DATA / name).read_text(encoding="utf-8"))["selected_before_inference"])
    assert len(selections) == len({row["image_id"] for row in selections}) == 240
    model = YOLO(str(MODEL))
    counts = defaultdict(Counter)
    cases = []
    for row in selections:
        info = images[row["image_id"]]
        scale = 512 / max(info["width"], info["height"])
        result = model.predict(str(DATA / "images" / row["file_name"]), imgsz=512,
                               conf=0.25, verbose=False)[0]
        preds = [{"class_id": int(box.cls[0]), "confidence": float(box.conf[0]),
                  "xyxy": list(map(float, box.xyxy[0].tolist()))} for box in result.boxes
                 if int(box.cls[0]) in (4, 7)]
        bikes = [p for p in preds if p["class_id"] == 4]
        motos = [p for p in preds if p["class_id"] == 7]
        gt_bikes, gt_motos = [], []
        for ann in by_image[row["image_id"]]:
            x, y, w, h = ann["bbox"]
            (gt_bikes if ann["category_id"] == 2 else gt_motos).append([x, y, x + w, y + h])
        matches = sorted(((iou(pred["xyxy"], gt), pi, gi)
                          for pi, pred in enumerate(bikes) for gi, gt in enumerate(gt_bikes)), reverse=True)
        used_p, used_g = set(), set()
        for overlap, pi, gi in matches:
            if overlap < 0.5:
                break
            if pi not in used_p and gi not in used_g:
                used_p.add(pi)
                used_g.add(gi)
        for gi, gt in enumerate(gt_bikes):
            area = (gt[2] - gt[0]) * (gt[3] - gt[1]) * scale * scale
            bin_name = size_bin(area)
            counts[bin_name]["gt"] += 1
            if gi in used_g:
                counts[bin_name]["matched"] += 1
            elif any(iou(pred["xyxy"], gt) >= 0.3 for pred in motos):
                counts[bin_name]["miss_as_motorcycle"] += 1
            elif any(iou(pred["xyxy"], gt) >= 0.1 for pred in bikes):
                counts[bin_name]["poor_localization"] += 1
            else:
                counts[bin_name]["no_nearby_vehicle_prediction"] += 1
        if row["group"] == "motorcycle_only" and bikes:
            counts["motorcycle_false_alarms"]["images"] += 1
            counts["motorcycle_false_alarms"]["bicycle_predictions"] += len(bikes)
            counts["motorcycle_false_alarms"]["overlap_moto_gt_iou30"] += sum(
                any(iou(pred["xyxy"], gt) >= 0.3 for gt in gt_motos) for pred in bikes)
        cases.append({"image_id": row["image_id"], "file_name": row["file_name"],
                      "group": row["group"], "gt_bicycle_boxes": gt_bikes,
                      "gt_motorcycle_boxes": gt_motos, "predictions": preds,
                      "matched_bicycle": len(used_g), "missed_bicycle": len(gt_bikes) - len(used_g),
                      "false_bicycle_on_motorcycle_only": len(bikes) if row["group"] == "motorcycle_only" else 0})
    summary = {"model": str(MODEL), "slices": list(SLICES), "confidence": 0.25,
               "input_size": 512, "size_bins": "sqrt(box area) after 512-pixel letterbox scale",
               "counts": {key: dict(value) for key, value in counts.items()}, "cases": cases}
    (OUT / "v9_failure_analysis.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    bike_cases = sorted((x for x in cases if x["missed_bicycle"]),
                        key=lambda x: (-x["missed_bicycle"], x["file_name"]))
    moto_cases = sorted((x for x in cases if x["false_bicycle_on_motorcycle_only"]),
                        key=lambda x: (-x["false_bicycle_on_motorcycle_only"], x["file_name"]))
    sheet(bike_cases, "missed_bicycles.jpg", "Missed bicycles")
    sheet(moto_cases, "motorcycle_false_alarms.jpg", "Motorcycle false alarms")
    print(json.dumps({"counts": summary["counts"], "missed_bicycle_images": len(bike_cases),
                      "motorcycle_false_alarm_images": len(moto_cases)}, indent=2))


if __name__ == "__main__":
    main()
