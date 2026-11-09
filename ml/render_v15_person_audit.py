"""Render top pretrained-person proposal cases beside current v15 labels."""

import argparse
import json

from PIL import Image, ImageDraw

from phase1 import ROOT


DATASET = ROOT / "data/processed/public_phase1_v15_oi_quarantine"
RUN = ROOT / "runs/public_phase1_v15_oi_quarantine"
OUT = RUN / "person_audit_sheets"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--zero-gt", action="store_true", help="Render every flagged image with zero person labels")
    args = parser.parse_args()
    rows = json.loads((RUN / "person_label_audit_queue.json").read_text(encoding="utf-8"))["rows"]
    rows = [row for row in rows if row["person_boxes"] == 0] if args.zero_gt else rows[:40]
    out = RUN / "person_zero_gt_sheets" if args.zero_gt else OUT
    out.mkdir(parents=True, exist_ok=True)
    for start in range(0, len(rows), 4):
        sheet = Image.new("RGB", (1800, 1200), "white")
        draw = ImageDraw.Draw(sheet)
        for slot, row in enumerate(rows[start:start + 4]):
            stem = f"oi_v10_train_{row['image_id']}"
            with Image.open(DATASET / "images/train" / f"{stem}.jpg") as source:
                image = source.convert("RGB")
            scale = min(870 / image.width, 530 / image.height)
            x0, y0 = (slot % 2) * 900 + 15, (slot // 2) * 600 + 45
            sheet.paste(image.resize((round(image.width * scale), round(image.height * scale))), (x0, y0))
            draw.text((x0, y0 - 22), f"{row['image_id']} GT person: cyan; proposal: red; P:{len(row['proposals'])}", fill="black")
            for line in (DATASET / "labels/train" / f"{stem}.txt").read_text(encoding="utf-8").splitlines():
                cls, xc, yc, bw, bh = map(float, line.split())
                if int(cls) != 0:
                    continue
                box = (x0 + (xc - bw / 2) * image.width * scale, y0 + (yc - bh / 2) * image.height * scale,
                       x0 + (xc + bw / 2) * image.width * scale, y0 + (yc + bh / 2) * image.height * scale)
                draw.rectangle(box, outline="#00d9ff", width=2)
            for proposal in row["proposals"]:
                x1, y1, x2, y2 = proposal["box_xyxy"]
                draw.rectangle((x0 + x1 * scale, y0 + y1 * scale, x0 + x2 * scale, y0 + y2 * scale),
                               outline="#ff1744", width=2)
        sheet.save(out / f"sheet_{start // 4 + 1:02}.jpg", quality=90)
    (out / "index.json").write_text(json.dumps([{"image_id": row["image_id"], "sheet": f"sheet_{i // 4 + 1:02}.jpg",
                                                  "slot": i % 4 + 1} for i, row in enumerate(rows)], indent=2), encoding="utf-8")
    print(json.dumps({"rendered_images": len(rows), "sheets": (len(rows) + 3) // 4, "output": str(out)}))


if __name__ == "__main__":
    main()
