"""Render source-resolution target crops for the frozen COCO review batch."""

import json
import zipfile
from pathlib import Path

from PIL import Image, ImageDraw

from build_v9_coco_train_candidate import ZIP


ROOT = Path(__file__).resolve().parents[1]
REVIEW = ROOT / "data/source/coco_external/small_bicycle_review_v1"


def bicycle_boxes(archive, image_id, width, height):
    path = f"coco/labels/train2017/{image_id}.txt"
    for line in archive.read(path).decode().splitlines():
        row = line.split()
        if not row or int(row[0]) != 1:
            continue
        cx, cy, w, h = map(float, row[1:5])
        yield ((cx - w / 2) * width, (cy - h / 2) * height,
               (cx + w / 2) * width, (cy + h / 2) * height)


def main():
    rows = json.loads((REVIEW / "selection.json").read_text(encoding="utf-8"))["rows"]
    out = REVIEW / "detail_sheets"
    out.mkdir(exist_ok=True)
    with zipfile.ZipFile(ZIP) as archive:
        for start in range(0, len(rows), 5):
            canvas = Image.new("RGB", (1600, 5 * 270), "white")
            draw = ImageDraw.Draw(canvas)
            for n, row in enumerate(rows[start:start + 5]):
                image_id = row["image_id"]
                with Image.open(REVIEW / "images" / f"{image_id}.jpg") as original:
                    source = original.convert("RGB")
                boxes = list(bicycle_boxes(archive, image_id, source.width, source.height))
                eligible = [box for box in boxes if 12 <= max((box[2] - box[0]) / source.width,
                                                        (box[3] - box[1]) / source.height) * 512 < 40]
                y = n * 270
                draw.text((5, y + 3), f"{image_id}  {row['group']}  image={source.width}x{source.height}  bicycles={len(boxes)}",
                          fill="black")
                context = source.copy()
                context.thumbnail((530, 235))
                for box in boxes:
                    draw_box = tuple(v * (context.width / source.width if i % 2 == 0 else context.height / source.height)
                                     for i, v in enumerate(box))
                    ImageDraw.Draw(context).rectangle(draw_box, outline="lime", width=2)
                canvas.paste(context, (5, y + 25))
                for j, box in enumerate(eligible[:3]):
                    cx, cy = (box[0] + box[2]) / 2, (box[1] + box[3]) / 2
                    radius = max(60, int(max(box[2] - box[0], box[3] - box[1]) * 3))
                    region = (max(0, int(cx - radius)), max(0, int(cy - radius)),
                              min(source.width, int(cx + radius)), min(source.height, int(cy + radius)))
                    crop = source.crop(region)
                    box_on_crop = (box[0] - region[0], box[1] - region[1], box[2] - region[0], box[3] - region[1])
                    ImageDraw.Draw(crop).rectangle(box_on_crop, outline="lime", width=2)
                    crop.thumbnail((340, 230))
                    canvas.paste(crop, (550 + j * 345, y + 25))
                    draw.text((550 + j * 345, y + 250),
                              f"target {j + 1}: {int(box[2]-box[0])}x{int(box[3]-box[1])} source px", fill="black")
            canvas.save(out / f"detail_{start // 5 + 1:02d}.jpg", quality=93)
    print(json.dumps({"images": len(rows), "detail_sheets": len(list(out.glob("detail_*.jpg")))}))


if __name__ == "__main__":
    main()
