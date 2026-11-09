"""Print image dimensions, source labels, and draft person boxes for pilot review."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DRAFT = ROOT / "runs/public_phase1_v15_oi_quarantine/person_draft_960/draft_v18_179.json"
LABELS = ROOT / "data/processed/public_phase1_v15_oi_quarantine/labels/train"
IDS = ["1271622877a21c47", "17d51251e2ce55f0", "5da1151716ece103",
       "654c3cb2305ea843", "69880732bf53c286"]


def main():
    rows = {row["image_id"]: row for row in json.loads(DRAFT.read_text(encoding="utf-8"))["rows"]}
    for image_id in IDS:
        row = rows[image_id]
        label = (LABELS / f"oi_v10_train_{image_id}.txt").read_text(encoding="utf-8")
        print(json.dumps({"id": image_id, "width": row["width"], "height": row["height"],
                          "proposals": [p["xyxy_pixels"] for p in row["proposals"]],
                          "source_labels": label.splitlines()}))


if __name__ == "__main__":
    main()
