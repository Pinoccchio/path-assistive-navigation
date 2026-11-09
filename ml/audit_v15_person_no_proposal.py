"""Inventory and render the unflagged OI images with zero person labels."""

import json
from collections import Counter

from PIL import Image, ImageDraw

from audit_v15_person_960_all import DATASET, OUT
from phase1 import ROOT

SELECTION = ROOT / "data/source/oi_vehicle_v10/train_selection.json"


def main():
    selected = json.loads(SELECTION.read_text(encoding="utf-8"))["rows"]
    manifest = [json.loads(line) for line in (DATASET / "dataset_manifest.jsonl").read_text(encoding="utf-8").splitlines()]
    retained = {row["source_id"] for row in manifest if row["split"] == "train" and row["source"] == "OpenImagesV7"}
    flagged = {row["image_id"] for row in json.loads((OUT / "audit.json").read_text(encoding="utf-8"))["rows"]}
    no_proposal = [row for row in selected if row["image_id"] in retained and row["image_id"] not in flagged]
    assert len(no_proposal) == 97
    counts = Counter()
    zero = []
    for row in no_proposal:
        image_id = row["image_id"]
        label = DATASET / "labels/train" / f"oi_v10_train_{image_id}.txt"
        persons = sum(line.startswith("0 ") for line in label.read_text().splitlines())
        counts["zero_person_labels" if persons == 0 else "some_person_labels"] += 1
        if persons == 0:
            zero.append(image_id)
    folder = OUT / "no_proposal_zero_person_sheets"
    folder.mkdir(parents=True, exist_ok=True)
    index = []
    for start in range(0, len(zero), 4):
        sheet = Image.new("RGB", (1800, 1200), "white")
        draw = ImageDraw.Draw(sheet)
        sheet_name = f"sheet_{start//4+1:02}.jpg"
        for slot, image_id in enumerate(zero[start:start+4]):
            with Image.open(DATASET / "images/train" / f"oi_v10_train_{image_id}.jpg") as source:
                image = source.convert("RGB")
            scale = min(870/image.width, 530/image.height)
            x0, y0 = (slot%2)*900+15, (slot//2)*600+45
            sheet.paste(image.resize((round(image.width*scale), round(image.height*scale))), (x0,y0))
            draw.text((x0,y0-22), f"{image_id} | zero person labels; zero 960px proposals", fill="black")
            index.append({"image_id": image_id, "sheet": sheet_name, "slot": slot+1})
        sheet.save(folder/sheet_name, quality=92)
    (folder/"index.json").write_text(json.dumps(index, indent=2)+"\n", encoding="utf-8")
    report = {"unflagged_images": len(no_proposal), "counts": dict(counts),
              "rendered_zero_person_images": len(zero), "sheets": (len(zero)+3)//4,
              "policy": "No model proposal does not prove no visible person; sheets require visual review."}
    (OUT/"no_proposal_inventory.json").write_text(json.dumps(report, indent=2)+"\n", encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
