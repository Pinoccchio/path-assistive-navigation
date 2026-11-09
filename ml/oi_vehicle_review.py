"""Render frozen Open Images vehicle labels for semantic review before inference."""

import argparse
import json
from PIL import Image, ImageDraw

from phase1 import ROOT


DATA = ROOT / "data" / "source" / "oi_vehicle_v10"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--split", choices=("train", "test"), required=True)
    parser.add_argument("--selection-name", help="Selection filename; defaults to split selection")
    parser.add_argument("--prefix", help="Review sheet prefix; defaults to split")
    args = parser.parse_args()
    rows = json.loads((DATA / (args.selection_name or f"{args.split}_selection.json")).read_text(encoding="utf-8"))["rows"]
    output = DATA / "review"
    output.mkdir(exist_ok=True)
    for group in ("small_bicycle", "motorcycle"):
        members = [row for row in rows if row["group"] == group]
        for start in range(0, len(members), 20):
            sheet = Image.new("RGB", (1800, 1120), "white")
            draw = ImageDraw.Draw(sheet)
            for index, row in enumerate(members[start:start + 20]):
                path = DATA / "images" / args.split / f'{row["image_id"]}.jpg'
                if not path.exists():
                    continue
                with Image.open(path) as im:
                    im = im.convert("RGB")
                    scale = min(350 / im.width, 245 / im.height)
                    resized = im.resize((round(im.width * scale), round(im.height * scale)))
                    col, grid_row = index % 5, index // 5
                    x0, y0 = col * 360, grid_row * 280 + 20
                    sheet.paste(resized, (x0, y0))
                    draw.text((x0, y0 - 16), row["image_id"] + " " + group[:1], fill="black")
                    for class_id, xc, yc, w, h in row["boxes"]:
                        if class_id not in (4, 7):
                            continue
                        x1, y1 = (xc - w / 2) * im.width * scale, (yc - h / 2) * im.height * scale
                        x2, y2 = (xc + w / 2) * im.width * scale, (yc + h / 2) * im.height * scale
                        draw.rectangle((x0 + x1, y0 + y1, x0 + x2, y0 + y2),
                                       outline="lime" if class_id == 4 else "orange", width=2)
            sheet.save(output / f"{args.prefix or args.split}_{group}_{start // 20 + 1:02}.jpg", quality=90)
    print(str(output))


if __name__ == "__main__":
    main()
