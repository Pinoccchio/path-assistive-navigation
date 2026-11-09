"""Generate deterministic, per-class prediction and annotation review sheets."""

import argparse
import json
from pathlib import Path

from PIL import Image, ImageDraw
from ultralytics import YOLO

from phase1 import NAMES, OUTPUT, ROOT


def tile(row, result):
    path = OUTPUT / "images" / row["split"] / f"{row['id']}.jpg"
    with Image.open(path) as source:
        original = source.convert("RGB")
    width, height = original.size
    canvas = original.copy()
    draw = ImageDraw.Draw(canvas)
    label = OUTPUT / "labels" / row["split"] / f"{row['id']}.txt"
    for line in label.read_text(encoding="utf-8").splitlines():
        cls, cx, cy, bw, bh = map(float, line.split())
        box = ((cx - bw / 2) * width, (cy - bh / 2) * height,
               (cx + bw / 2) * width, (cy + bh / 2) * height)
        draw.rectangle(box, outline="#00b050", width=5)
        draw.text((box[0], max(0, box[1] - 14)), f"GT {NAMES[int(cls)]}", fill="#00b050")
    for box in result.boxes:
        coords = tuple(float(value) for value in box.xyxy[0])
        draw.rectangle(coords, outline="#ff3333", width=4)
        draw.text((coords[0], coords[1]), f"P {NAMES[int(box.cls)]} {float(box.conf):.2f}", fill="#ff3333")
    canvas.thumbnail((492, 345))
    tile_image = Image.new("RGB", (500, 375), "white")
    tile_image.paste(canvas, ((500 - canvas.width) // 2, 25))
    ImageDraw.Draw(tile_image).text((5, 5), f"{row['source']} {row['id'][-24:]}", fill="black")
    return tile_image


def main():
    global OUTPUT
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset-name", default="public_phase1_v1")
    parser.add_argument("--weights", default=None)
    parser.add_argument("--model-tag", default="")
    args = parser.parse_args()
    OUTPUT = ROOT / "data" / "processed" / args.dataset_name
    rows = [json.loads(line) for line in (OUTPUT / "dataset_manifest.jsonl").read_text(encoding="utf-8").splitlines()]
    weights = args.weights or ROOT / "runs" / "public_phase1_v1" / "yolov8n" / "weights" / "best.pt"
    model = YOLO(str(weights))
    target_dir = ROOT / "runs" / args.dataset_name / "qa_sheets"
    target_dir.mkdir(exist_ok=True)
    for split, class_ids in (("test", range(7)), ("train", (2, 5, 6))):
        for class_id in class_ids:
            matches = [row for row in rows if row["split"] == split and class_id in row["class_ids"]]
            chosen = [matches[round(index * (len(matches) - 1) / 8)] for index in range(9)]
            paths = [str(OUTPUT / "images" / split / f"{row['id']}.jpg") for row in chosen]
            results = model.predict(source=paths, imgsz=512, conf=0.25, device="cpu", verbose=False)
            sheet = Image.new("RGB", (1500, 1125), "white")
            for index, (row, result) in enumerate(zip(chosen, results)):
                sheet.paste(tile(row, result), ((index % 3) * 500, (index // 3) * 375))
            suffix = f"_{args.model_tag}" if args.model_tag else ""
            path = target_dir / f"{split}_{NAMES[class_id]}{suffix}.jpg"
            sheet.save(path, quality=90)
            print(path)


if __name__ == "__main__":
    main()
