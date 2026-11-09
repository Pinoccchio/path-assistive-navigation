"""Count staircase annotations and source distribution without changing labels."""

import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/processed/public_phase1_v11_reviewed_640_candidate"
OUT = ROOT / "runs/public_phase1_v11_reviewed_640_candidate/stair_label_inventory.json"


def source_for(image_id):
    if image_id.startswith("openimagesv7_"):
        return "Open Images V7"
    if image_id.startswith("rod_"):
        return "ROD"
    if image_id.startswith("coco_"):
        return "COCO"
    return image_id.split("_", 1)[0]


def main():
    rows = [json.loads(line) for line in (DATA / "dataset_manifest.jsonl")
            .read_text(encoding="utf-8").splitlines()]
    summary = {}
    flagged = []
    for split in ("train", "val", "test"):
        split_rows = [row for row in rows if row["split"] == split]
        counts = Counter()
        sources = {}
        for row in split_rows:
            label_path = DATA / "labels" / split / f'{row["id"]}.txt'
            labels = [line.split() for line in label_path.read_text(encoding="utf-8").splitlines()
                      if line.strip()]
            stair_count = sum(int(label[0]) == 2 for label in labels)
            source = source_for(row["id"])
            counts["images"] += 1
            counts["stair_boxes"] += stair_count
            counts["stair_positive_images"] += bool(stair_count)
            sources.setdefault(source, Counter())["images"] += 1
            sources[source]["stair_boxes"] += stair_count
            sources[source]["stair_positive_images"] += bool(stair_count)
            if stair_count > 1:
                counts["multi_stair_box_images"] += 1
                flagged.append({"split": split, "id": row["id"], "stair_boxes": stair_count})
        summary[split] = {"counts": dict(counts),
                          "sources": {source: dict(source_counts)
                                      for source, source_counts in sorted(sources.items())}}
    report = {"dataset": str(DATA), "splits": summary,
              "multi_stair_box_images": flagged,
              "limitations": "Structural inventory only; no visual verification of complete or policy-consistent staircase boxes."}
    OUT.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({split: item["counts"] for split, item in summary.items()}, indent=2))


if __name__ == "__main__":
    main()
