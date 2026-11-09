"""Render every retained newly selected OI train image with current v14 labels."""

import json
from collections import Counter

from PIL import Image, ImageDraw

from phase1 import ROOT


DATASET = ROOT / "data/processed/public_phase1_v14_six_box_pilot"
SELECTION = ROOT / "data/source/oi_vehicle_v10/train_selection.json"
QUEUE = ROOT / "runs/public_phase1_v11_reviewed_640_candidate/train_vehicle_label_audit_queue.json"
OUTPUT = ROOT / "runs/public_phase1_v14_six_box_pilot/oi_completeness_sheets"
COLORS = {0: "#05c5ff", 4: "#16ed30", 7: "#ff9a00"}


def main():
    selected = json.loads(SELECTION.read_text(encoding="utf-8"))["rows"]
    manifest = [json.loads(line) for line in (DATASET / "dataset_manifest.jsonl").read_text(encoding="utf-8").splitlines()]
    retained = {row["source_id"] for row in manifest if row["split"] == "train" and row["source"] == "OpenImagesV7"}
    rows = [row for row in selected if row["image_id"] in retained]
    assert len(rows) == 290
    flagged = {row["image_id"] for row in json.loads(QUEUE.read_text(encoding="utf-8"))["rows"]}
    OUTPUT.mkdir(parents=True, exist_ok=True)
    index = []
    for start in range(0, len(rows), 4):
        sheet = Image.new("RGB", (1800, 1200), "white")
        draw = ImageDraw.Draw(sheet)
        for slot, row in enumerate(rows[start:start + 4]):
            image_id = row["image_id"]
            stem = f"oi_v10_train_{image_id}"
            with Image.open(DATASET / "images/train" / f"{stem}.jpg") as original:
                image = original.convert("RGB")
            scale = min(870 / image.width, 530 / image.height)
            x0, y0 = (slot % 2) * 900 + 15, (slot // 2) * 600 + 45
            sheet.paste(image.resize((round(image.width * scale), round(image.height * scale))), (x0, y0))
            label_lines = (DATASET / "labels/train" / f"{stem}.txt").read_text(encoding="utf-8").splitlines()
            counts = Counter()
            for line in label_lines:
                cls, xc, yc, bw, bh = map(float, line.split())
                cls = int(cls)
                if cls not in COLORS:
                    continue
                counts[cls] += 1
                box = (x0 + (xc - bw / 2) * image.width * scale,
                       y0 + (yc - bh / 2) * image.height * scale,
                       x0 + (xc + bw / 2) * image.width * scale,
                       y0 + (yc + bh / 2) * image.height * scale)
                draw.rectangle(box, outline=COLORS[cls], width=2)
            number = start // 4 + 1
            draw.text((x0, y0 - 22),
                      f"{image_id} {row['group']} {'FLAGGED' if image_id in flagged else 'unflagged'} "
                      f"P:{counts[0]} B:{counts[4]} M:{counts[7]}", fill="black")
            index.append({"image_id": image_id, "group": row["group"], "flagged_by_v11": image_id in flagged,
                          "person_boxes": counts[0], "bicycle_boxes": counts[4], "motorcycle_boxes": counts[7],
                          "sheet": f"sheet_{number:03}.jpg", "slot": slot + 1,
                          "status": "human_review_pending"})
        sheet.save(OUTPUT / f"sheet_{start // 4 + 1:03}.jpg", quality=85)
    report = {"dataset": str(DATASET), "images": len(index), "sheets": (len(index) + 3) // 4,
              "flagged": sum(row["flagged_by_v11"] for row in index),
              "unflagged": sum(not row["flagged_by_v11"] for row in index),
              "status": "Review aid only; no auto-approved label corrections."}
    (OUTPUT / "index.json").write_text(json.dumps(index, indent=2), encoding="utf-8")
    (OUTPUT / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
