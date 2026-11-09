"""Create a small held-out test contact sheet for manual detector review."""

import json
from pathlib import Path

from PIL import Image, ImageDraw
from ultralytics import YOLO

from phase1 import NAMES, OUTPUT, ROOT


def main() -> None:
    rows = [json.loads(line) for line in (OUTPUT / "dataset_manifest.jsonl").read_text(encoding="utf-8").splitlines()]
    chosen = []
    for class_id in range(len(NAMES)):
        matches = [row for row in rows if row["split"] == "test" and class_id in row["class_ids"]]
        chosen.extend(matches[:2])
    model = YOLO(ROOT / "runs" / "public_phase1_v1" / "yolov8n" / "weights" / "best.pt")
    paths = [OUTPUT / "images" / "test" / f"{row['id']}.jpg" for row in chosen]
    results = model.predict(source=[str(path) for path in paths], imgsz=512, conf=0.25,
                            device="cpu", verbose=False)
    sheet = Image.new("RGB", (4 * 400, 4 * 340), "white")
    for index, (row, path, result) in enumerate(zip(chosen, paths, results)):
        with Image.open(path) as original:
            image = original.convert("RGB")
        width, height = image.size
        canvas = image.copy()
        draw = ImageDraw.Draw(canvas)
        label_path = OUTPUT / "labels" / "test" / f"{path.stem}.txt"
        for line in label_path.read_text(encoding="utf-8").splitlines():
            cls, cx, cy, bw, bh = map(float, line.split())
            box = ((cx - bw / 2) * width, (cy - bh / 2) * height,
                   (cx + bw / 2) * width, (cy + bh / 2) * height)
            draw.rectangle(box, outline="#19a76b", width=4)
            draw.text((box[0], max(0, box[1] - 13)), f"GT {NAMES[int(cls)]}", fill="#19a76b")
        for box in result.boxes:
            coords = tuple(float(value) for value in box.xyxy[0])
            draw.rectangle(coords, outline="#e63946", width=3)
            draw.text((coords[0], coords[1]), f"P {NAMES[int(box.cls)]} {float(box.conf):.2f}", fill="#e63946")
        canvas.thumbnail((390, 300))
        x, y = (index % 4) * 400, (index // 4) * 340
        sheet.paste(canvas, (x, y + 25))
        ImageDraw.Draw(sheet).text((x + 5, y + 5), f"{NAMES[index // 2]}: {path.stem[-12:]}", fill="black")
    target = ROOT / "runs" / "public_phase1_v1" / "visual_qa_sheet.jpg"
    sheet.save(target, quality=90)
    print(target)


if __name__ == "__main__":
    main()
