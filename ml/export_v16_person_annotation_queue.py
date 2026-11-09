"""Export the reviewed zero-person-label images in vehicle-value priority order."""

import csv
import json

from build_v16_person_quarantine import CLASSES, LEDGER, SOURCE, ROOT

SHEETS = ROOT / "runs/public_phase1_v15_oi_quarantine/person_zero_gt_sheets"
OUTPUT = ROOT / "runs/public_phase1_v15_oi_quarantine/person_annotation_priority.csv"


def main():
    excluded = json.loads(LEDGER.read_text(encoding="utf-8"))["excluded"]
    index = json.loads((SHEETS / "index.json").read_text(encoding="utf-8"))
    locations = {row["image_id"]: row for row in index}
    assert set(locations) == set(excluded)
    rows = []
    for image_id in excluded:
        stem = f"oi_v10_train_{image_id}"
        counts = {name: 0 for name in CLASSES}
        for line in (SOURCE / "labels/train" / f"{stem}.txt").read_text().splitlines():
            counts[CLASSES[int(line.split()[0])]] += 1
        rows.append({"image_id": image_id, "review_sheet": str(SHEETS / locations[image_id]["sheet"]),
                     "sheet_slot": locations[image_id]["slot"],
                     "image_path": str(SOURCE / "images/train" / f"{stem}.jpg"),
                     "label_path": str(SOURCE / "labels/train" / f"{stem}.txt"),
                     "bicycle_boxes": counts["bicycle"], "motorcycle_boxes": counts["motorcycle"],
                     "car_boxes": counts["car"], "status": "person annotation needed; vehicle completeness unverified"})
    rows.sort(key=lambda r: (-(r["bicycle_boxes"] + r["motorcycle_boxes"]), -r["bicycle_boxes"], r["image_id"]))
    with OUTPUT.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    assert len(rows) == 109
    print(f"Wrote {len(rows)} annotation priorities to {OUTPUT}")


if __name__ == "__main__":
    main()
