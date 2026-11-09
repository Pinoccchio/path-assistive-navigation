"""Render queued public vehicle test images with GT and v11 predictions."""

import csv
import json

from PIL import Image, ImageDraw
from ultralytics import YOLO

from phase1 import ROOT


RUN = ROOT / "runs" / "public_phase1_v11_reviewed_640_candidate"
SOURCE = ROOT / "data" / "source" / "oi_vehicle_v10"


def main():
    queue = list(csv.DictReader((RUN / "review_queue_512.csv").open(encoding="utf-8", newline="")))
    small = json.loads((SOURCE / "test_small_selection.json").read_text(encoding="utf-8"))["rows"]
    vehicle = json.loads((SOURCE / "test_selection.json").read_text(encoding="utf-8"))["rows"]
    labels = {row["image_id"]: row for row in small + vehicle}
    model = YOLO(str(RUN / "yolov8n" / "weights" / "best.pt"))
    out = RUN / "review_sheets_512"
    out.mkdir(exist_ok=True)
    for start in range(0, len(queue), 4):
        sheet = Image.new("RGB", (1800, 1200), "#ffffff")
        draw = ImageDraw.Draw(sheet)
        for i, item in enumerate(queue[start:start + 4]):
            image_id = item["image_id"]
            image_path = SOURCE / "images" / "test" / f"{image_id}.jpg"
            with Image.open(image_path) as original:
                image = original.convert("RGB")
            result = model.predict(str(image_path), imgsz=512, conf=0.25, verbose=False)[0]
            scale = min(870 / image.width, 535 / image.height)
            rendered = image.resize((round(image.width * scale), round(image.height * scale)))
            x0, y0 = (i % 2) * 900 + 15, (i // 2) * 600 + 45
            sheet.paste(rendered, (x0, y0))
            draw.text((x0, y0 - 22), f"{image_id}  {item['slice']}  GT green=cycle orange=motorcycle  P red", fill="black")
            for cls, xc, yc, w, h in labels[image_id]["boxes"]:
                if cls not in (4, 7):
                    continue
                box = ((xc - w / 2) * image.width * scale, (yc - h / 2) * image.height * scale,
                       (xc + w / 2) * image.width * scale, (yc + h / 2) * image.height * scale)
                draw.rectangle(tuple(value + (x0 if j % 2 == 0 else y0) for j, value in enumerate(box)),
                               outline="#00ff00" if cls == 4 else "#ffac00", width=3)
            for box in result.boxes:
                cls = int(box.cls[0])
                if cls not in (4, 7):
                    continue
                coords = [float(value) * scale for value in box.xyxy[0]]
                draw.rectangle(tuple(value + (x0 if j % 2 == 0 else y0) for j, value in enumerate(coords)),
                               outline="#ff1744" if cls == 4 else "#a600ff", width=2)
        sheet.save(out / f"queue_{start // 4 + 1:02}.jpg", quality=90)
    print(json.dumps({"images": len(queue), "sheets": (len(queue) + 3) // 4, "directory": str(out)}))


if __name__ == "__main__":
    main()
