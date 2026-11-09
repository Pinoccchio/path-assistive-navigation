"""Read-only inventory of every processed image, label, and split."""

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path

from PIL import Image

from phase1 import NAMES, OUTPUT, ROOT, dhash, sha256


def main() -> None:
    global OUTPUT
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", type=Path, default=OUTPUT)
    args = parser.parse_args()
    OUTPUT = args.dataset.resolve()
    manifest = [json.loads(line) for line in (OUTPUT / "dataset_manifest.jsonl").read_text(encoding="utf-8").splitlines()]
    issues = []
    groups = defaultdict(set)
    hashes = defaultdict(set)
    source_by_class = defaultdict(Counter)
    boxes_by_class = Counter()
    small_boxes = Counter()
    fingerprints = []
    for row in manifest:
        split, stem = row["split"], row["id"]
        image_path = OUTPUT / "images" / split / f"{stem}.jpg"
        label_path = OUTPUT / "labels" / split / f"{stem}.txt"
        if not image_path.is_file() or not label_path.is_file():
            issues.append({"id": stem, "issue": "missing image or label"})
            continue
        data = image_path.read_bytes()
        digest = sha256(data)
        if digest != row["sha256"]:
            issues.append({"id": stem, "issue": "image SHA-256 differs from manifest"})
        try:
            with Image.open(image_path) as image:
                width, height = image.size
                image.verify()
        except Exception as error:
            issues.append({"id": stem, "issue": f"unreadable image: {error}"})
            continue
        labels = [line.split() for line in label_path.read_text(encoding="utf-8").splitlines()]
        actual_classes = set()
        for fields in labels:
            if len(fields) != 5:
                issues.append({"id": stem, "issue": "invalid label field count"})
                continue
            cls = int(fields[0])
            actual_classes.add(cls)
            boxes_by_class[NAMES[cls]] += 1
            _, _, box_width, box_height = map(float, fields[1:])
            if box_width * width < 16 or box_height * height < 16:
                small_boxes[NAMES[cls]] += 1
        if actual_classes != set(row["class_ids"]):
            issues.append({"id": stem, "issue": "manifest classes differ from label"})
        groups[row["group"]].add(split)
        hashes[digest].add(split)
        fingerprints.append((dhash(image_path), row))
        for cls in actual_classes:
            source_by_class[NAMES[cls]][row["source"]] += 1
    report = {
        "images_checked": len(manifest),
        "split_counts": dict(Counter(row["split"] for row in manifest)),
        "issues": issues,
        "capture_groups_in_multiple_splits": {group: sorted(splits) for group, splits in groups.items() if len(splits) > 1},
        "exact_image_hashes_in_multiple_splits": sum(len(splits) > 1 for splits in hashes.values()),
        "source_image_counts_by_class": {name: dict(source_by_class[name]) for name in NAMES},
        "box_counts_by_class": dict(boxes_by_class),
        "boxes_under_16px_on_either_side": dict(small_boxes),
    }
    train = [(fingerprint, row) for fingerprint, row in fingerprints if row["split"] == "train"]
    test = [(fingerprint, row) for fingerprint, row in fingerprints if row["split"] == "test"]
    near_pairs = []
    for test_hash, test_row in test:
        for train_hash, train_row in train:
            distance = (test_hash ^ train_hash).bit_count()
            if distance <= 13 and set(test_row["class_ids"]) & set(train_row["class_ids"]):
                near_pairs.append({"test": test_row["id"], "train": train_row["id"],
                                   "distance": distance})
    report["cross_split_dhash_pairs_at_most_13"] = sorted(near_pairs, key=lambda row: row["distance"])
    run_name = "public_phase1_v1" if OUTPUT.name == "public_phase1_v1" else OUTPUT.name
    out = ROOT / "runs" / run_name / "qa_inventory.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({key: value for key, value in report.items() if key not in ("issues", "cross_split_dhash_pairs_at_most_13")}, indent=2))
    print(f"Cross-split dHash candidates at distance <= 13: {len(near_pairs)}")
    print(f"Issue count: {len(issues)}")


if __name__ == "__main__":
    main()
