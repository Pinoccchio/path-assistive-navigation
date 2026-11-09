"""Render person proposals so reviewers can find misses and false boxes."""

import json

from PIL import Image, ImageDraw

from build_v16_person_quarantine import ROOT, SOURCE

OUT = ROOT / "runs/public_phase1_v15_oi_quarantine/person_draft_960"


def main():
    rows = json.loads((OUT / "draft.json").read_text(encoding="utf-8"))["rows"]
    index = []
    for start in range(0, len(rows), 4):
        sheet = Image.new("RGB", (1800, 1200), "white")
        draw = ImageDraw.Draw(sheet)
        name = f"sheet_{start // 4 + 1:02}.jpg"
        for slot, row in enumerate(rows[start:start + 4]):
            image_id = row["image_id"]
            with Image.open(SOURCE / "images/train" / f"oi_v10_train_{image_id}.jpg") as source:
                image = source.convert("RGB")
            scale = min(870 / image.width, 530 / image.height)
            x0, y0 = (slot % 2) * 900 + 15, (slot // 2) * 600 + 45
            sheet.paste(image.resize((round(image.width * scale), round(image.height * scale))), (x0, y0))
            draw.text((x0, y0 - 22), f"{image_id} draft persons: {len(row['proposals'])}", fill="black")
            for proposal in row["proposals"]:
                x1, y1, x2, y2 = proposal["xyxy_pixels"]
                draw.rectangle((x0 + x1 * scale, y0 + y1 * scale, x0 + x2 * scale, y0 + y2 * scale),
                               outline="#ff1744", width=2)
                draw.text((x0 + x1 * scale, y0 + y1 * scale), str(proposal["confidence"]), fill="#ff1744")
            index.append({"image_id": image_id, "sheet": name, "slot": slot + 1,
                          "proposal_count": len(row["proposals"])})
        sheet.save(OUT / name, quality=92)
    (OUT / "index.json").write_text(json.dumps(index, indent=2) + "\n", encoding="utf-8")
    print(f"Rendered {len(rows)} images on {(len(rows) + 3) // 4} sheets")


if __name__ == "__main__":
    main()
