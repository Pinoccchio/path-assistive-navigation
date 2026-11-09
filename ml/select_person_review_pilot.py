"""Select low-complexity images for a careful first manual person-review batch."""

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DRAFT = ROOT / "runs/public_phase1_v15_oi_quarantine/person_draft_960/draft_v18_179.json"
QUEUE = ROOT / "runs/public_phase1_v15_oi_quarantine/person_annotation_priority_v18.csv"


def main():
    drafts = {row["image_id"]: row for row in json.loads(DRAFT.read_text(encoding="utf-8"))["rows"]}
    with QUEUE.open(newline="", encoding="utf-8") as handle:
        priority = list(csv.DictReader(handle))
    candidates = []
    for item in priority:
        row = drafts[item["image_id"]]
        if row.get("source_person_boxes", 0) == 0 and 0 < len(row["proposals"]) <= 2:
            candidates.append({"id": item["image_id"],
                               "proposals": len(row["proposals"]),
                               "bicycle": int(item["bicycle_boxes"]),
                               "motorcycle": int(item["motorcycle_boxes"]),
                               "car": int(item["car_boxes"])})
    candidates.sort(key=lambda row: (row["bicycle"] + row["motorcycle"] + row["car"],
                                     row["proposals"], row["id"]))
    print(json.dumps(candidates[:15], indent=2))


if __name__ == "__main__":
    main()
