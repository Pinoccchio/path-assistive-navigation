"""Render top train-label audit cases with original boxes and unmatched predictions."""

import json

from PIL import Image, ImageDraw

from phase1 import ROOT


SOURCE = ROOT / "data" / "source" / "oi_vehicle_v10"
RUN = ROOT / "runs" / "public_phase1_v11_reviewed_640_candidate"


def main():
    rows = json.loads((RUN / "train_vehicle_label_audit_queue.json").read_text(encoding="utf-8"))["rows"]
    selection = json.loads((SOURCE / "train_selection.json").read_text(encoding="utf-8"))["rows"]
    labels = {row["image_id"]: row["boxes"] for row in selection}
    out = RUN / "train_label_audit_sheets"
    out.mkdir(exist_ok=True)
    for start in range(0, len(rows), 4):
        sheet = Image.new("RGB", (1800, 1200), "white")
        draw = ImageDraw.Draw(sheet)
        for i, row in enumerate(rows[start:start + 4]):
            image_id = row["image_id"]
            with Image.open(SOURCE / "images" / "train" / f"{image_id}.jpg") as original:
                image = original.convert("RGB")
            scale = min(870 / image.width, 530 / image.height)
            x0, y0 = (i % 2) * 900 + 15, (i // 2) * 600 + 45
            sheet.paste(image.resize((round(image.width * scale), round(image.height * scale))), (x0, y0))
            draw.text((x0, y0 - 22), f"{image_id} GT: green bike/orange moto; unmatched P: red bike/purple moto", fill="black")
            for cls, xc, yc, w, h in labels[image_id]:
                if cls not in (4, 7):
                    continue
                coords = ((xc - w / 2) * image.width * scale, (yc - h / 2) * image.height * scale,
                          (xc + w / 2) * image.width * scale, (yc + h / 2) * image.height * scale)
                draw.rectangle(tuple(value + (x0 if j % 2 == 0 else y0) for j, value in enumerate(coords)),
                               outline="#00ff00" if cls == 4 else "#ffac00", width=3)
            for pred in row["unmatched_predictions"]:
                coords = [value * scale for value in pred["box_xyxy"]]
                draw.rectangle(tuple(value + (x0 if j % 2 == 0 else y0) for j, value in enumerate(coords)),
                               outline="#ff1744" if pred["class_id"] == 4 else "#a600ff", width=2)
        sheet.save(out / f"train_{start // 4 + 1:02}.jpg", quality=90)
    print(json.dumps({"images": len(rows), "sheets": (len(rows) + 3) // 4, "directory": str(out)}))


if __name__ == "__main__":
    main()
