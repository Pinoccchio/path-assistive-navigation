"""Render OI images with existing person labels and unmatched proposals."""

import json

from PIL import Image, ImageDraw

from audit_v15_person_960_all import DATASET, OUT


def main():
    rows = [row for row in json.loads((OUT / "audit.json").read_text(encoding="utf-8"))["rows"]
            if row["category"] == "existing_person_candidate"]
    assert len(rows) == 59
    folder = OUT / "partial_person_sheets"
    folder.mkdir(parents=True, exist_ok=True)
    index = []
    for start in range(0, len(rows), 4):
        sheet = Image.new("RGB", (1800, 1200), "white")
        draw = ImageDraw.Draw(sheet)
        sheet_name = f"sheet_{start // 4 + 1:02}.jpg"
        for slot, row in enumerate(rows[start:start + 4]):
            image_id = row["image_id"]
            with Image.open(DATASET / "images/train" / f"oi_v10_train_{image_id}.jpg") as source:
                image = source.convert("RGB")
            scale = min(870 / image.width, 530 / image.height)
            x0, y0 = (slot % 2) * 900 + 15, (slot // 2) * 600 + 45
            sheet.paste(image.resize((round(image.width * scale), round(image.height * scale))), (x0, y0))
            draw.text((x0, y0 - 22),
                      f"{image_id} | existing: {row['existing_person_boxes']} (cyan) proposals: {len(row['proposals'])} (red)",
                      fill="black")
            for line in (DATASET / "labels/train" / f"oi_v10_train_{image_id}.txt").read_text().splitlines():
                cls, xc, yc, bw, bh = map(float, line.split())
                if int(cls) != 0:
                    continue
                draw.rectangle((x0 + (xc-bw/2)*image.width*scale, y0 + (yc-bh/2)*image.height*scale,
                                x0 + (xc+bw/2)*image.width*scale, y0 + (yc+bh/2)*image.height*scale),
                               outline="#00d9ff", width=2)
            for proposal in row["proposals"]:
                x1, y1, x2, y2 = proposal["box_xyxy"]
                draw.rectangle((x0 + x1*scale, y0 + y1*scale, x0 + x2*scale, y0 + y2*scale),
                               outline="#ff1744", width=2)
            index.append({"image_id": image_id, "sheet": sheet_name, "slot": slot + 1,
                          "existing_person_boxes": row["existing_person_boxes"],
                          "proposal_count": len(row["proposals"])})
        sheet.save(folder / sheet_name, quality=92)
    (folder / "index.json").write_text(json.dumps(index, indent=2) + "\n", encoding="utf-8")
    print(f"Rendered {len(rows)} images on {(len(rows)+3)//4} sheets")


if __name__ == "__main__":
    main()
