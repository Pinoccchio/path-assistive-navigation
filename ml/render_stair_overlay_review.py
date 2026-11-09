"""Visualize only the retained staircase boxes in the candidate overlay."""

import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data/processed/public_phase1_v11_reviewed_640_candidate"
OVERLAY = ROOT / "data/processed/stair_label_overlay_v1"
OUT = OVERLAY / "review_sheet.jpg"


def main():
    rows = json.loads((OVERLAY / "manifest.json").read_text(encoding="utf-8"))["corrected_train_labels"]
    sheet = Image.new("RGB", (1024, 1024), "white")
    draw = ImageDraw.Draw(sheet)
    for index, row in enumerate(rows):
        image_id = row["id"]
        source = Image.open(SOURCE / "images/train" / f"{image_id}.jpg").convert("RGB")
        thumb = ImageOps.contain(source, (496, 470))
        x = index % 2 * 512 + (512 - thumb.width) // 2
        y = index // 2 * 512 + 32 + (470 - thumb.height) // 2
        sheet.paste(thumb, (x, y))
        line = (OVERLAY / "labels/train" / f"{image_id}.txt").read_text(encoding="utf-8").strip()
        _, xc, yc, w, h = line.split()
        xc, yc, w, h = map(float, (xc, yc, w, h))
        draw.rectangle((x + (xc - w / 2) * thumb.width,
                        y + (yc - h / 2) * thumb.height,
                        x + (xc + w / 2) * thumb.width,
                        y + (yc + h / 2) * thumb.height), outline="#e11d48", width=4)
        draw.text((index % 2 * 512 + 8, index // 2 * 512 + 8), image_id,
                  fill="black", font=ImageFont.load_default())
    sheet.save(OUT, quality=92)
    print(OUT)


if __name__ == "__main__":
    main()
