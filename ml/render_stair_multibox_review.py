"""Render multi-stair-box images for visual policy review; labels stay unchanged."""

import json
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/processed/public_phase1_v11_reviewed_640_candidate"
RUN = ROOT / "runs/public_phase1_v11_reviewed_640_candidate"
SHEETS = RUN / "stair_multibox_review_sheets"


def main():
    report = json.loads((RUN / "stair_label_inventory.json").read_text(encoding="utf-8"))
    rows = report["multi_stair_box_images"]
    SHEETS.mkdir(parents=True, exist_ok=True)
    cell_w, cell_h = 540, 390
    sheet_rows, sheet_cols = 3, 2
    for page in range(math.ceil(len(rows) / (sheet_rows * sheet_cols))):
        sheet = Image.new("RGB", (cell_w * sheet_cols, cell_h * sheet_rows), "#ffffff")
        draw = ImageDraw.Draw(sheet)
        batch = rows[page * sheet_rows * sheet_cols:(page + 1) * sheet_rows * sheet_cols]
        for position, row in enumerate(batch):
            split, image_id = row["split"], row["id"]
            image = Image.open(DATA / "images" / split / f"{image_id}.jpg").convert("RGB")
            original_w, original_h = image.size
            thumb = ImageOps.contain(image, (cell_w - 20, cell_h - 48))
            x = position % sheet_cols * cell_w + (cell_w - thumb.width) // 2
            y = position // sheet_cols * cell_h + 32 + (cell_h - 48 - thumb.height) // 2
            sheet.paste(thumb, (x, y))
            labels = (DATA / "labels" / split / f"{image_id}.txt").read_text(encoding="utf-8")
            for line in labels.splitlines():
                parts = line.split()
                if parts and int(parts[0]) == 2:
                    xc, yc, w, h = map(float, parts[1:5])
                    left = x + (xc - w / 2) * original_w * thumb.width / original_w
                    top = y + (yc - h / 2) * original_h * thumb.height / original_h
                    right = x + (xc + w / 2) * original_w * thumb.width / original_w
                    bottom = y + (yc + h / 2) * original_h * thumb.height / original_h
                    draw.rectangle((left, top, right, bottom), outline="#f43f5e", width=3)
            draw.text((position % sheet_cols * cell_w + 8,
                       position // sheet_cols * cell_h + 8),
                      f"{split}: {image_id}  ({row['stair_boxes']} boxes)",
                      fill="#111111", font=ImageFont.load_default())
        sheet.save(SHEETS / f"sheet_{page + 1:02d}.jpg", quality=90)
    print(f"Rendered {len(rows)} images across {math.ceil(len(rows) / 6)} sheets at {SHEETS}")


if __name__ == "__main__":
    main()
