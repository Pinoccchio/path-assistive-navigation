"""Render original-size vehicle overlays for the 18 lower-restriction license candidates."""

import json
import zipfile
from pathlib import Path

from PIL import Image, ImageDraw

from build_v9_coco_train_candidate import ZIP


ROOT = Path(__file__).resolve().parents[1]
REVIEW = ROOT / "data/source/coco_external/small_bicycle_review_v1"
ALLOWED_METADATA = {"Attribution License", "Attribution-ShareAlike License"}


def main():
    rows = [json.loads(line) for line in (REVIEW / "review_ledger.jsonl").read_text(encoding="utf-8").splitlines()]
    official = {row["image_id"]: row for row in
                (json.loads(line) for line in (REVIEW / "official_annotation_comparison.jsonl").read_text(encoding="utf-8").splitlines())}
    out = REVIEW / "license_priority_overlays"
    out.mkdir(exist_ok=True)
    count = 0
    with zipfile.ZipFile(ZIP) as archive:
        for row in rows:
            if row["license_name"] not in ALLOWED_METADATA:
                continue
            image_id = row["image_id"]
            with Image.open(REVIEW / "images" / f"{image_id}.jpg") as raw:
                image = raw.convert("RGB")
            draw = ImageDraw.Draw(image)
            path = f"coco/labels/train2017/{image_id}.txt"
            for index, line in enumerate(archive.read(path).decode().splitlines(), 1):
                fields = line.split()
                if not fields or int(fields[0]) not in (1, 3):
                    continue
                cls = int(fields[0])
                cx, cy, w, h = map(float, fields[1:5])
                box = ((cx - w / 2) * image.width, (cy - h / 2) * image.height,
                       (cx + w / 2) * image.width, (cy + h / 2) * image.height)
                color = "#00ff00" if cls == 1 else "#ff0000"
                draw.rectangle(box, outline=color, width=2)
                draw.text((box[0], max(0, box[1] - 12)), f"{index}:{'B' if cls == 1 else 'M'}", fill=color)
            for crowd in official[image_id]["unmatched_official"]:
                draw.rectangle(crowd["bbox_xyxy"], outline="yellow", width=2)
            image.save(out / f"{image_id}.jpg", quality=94)
            count += 1
    print(json.dumps({"overlays": count, "legend": {"green": "bicycle", "red": "motorcycle", "yellow": "official crowd region"}}))


if __name__ == "__main__":
    main()
