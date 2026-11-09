"""Add a motorcycle training class using v7's reviewed removed bicycle boxes."""

import json
import os
from collections import Counter, defaultdict

from phase1 import NAMES, ROOT


SOURCE = ROOT / "data" / "processed" / "public_phase1_v7_vehicle_labels_candidate"
TARGET = ROOT / "data" / "processed" / "public_phase1_v8_motorcycle_candidate"
STAIR_QUARANTINE = "openimagesv7_train_b11a9ac6faa28d32"


def main():
    if TARGET.exists():
        raise SystemExit(f"Output already exists: {TARGET}")
    source_report = json.loads((SOURCE / "build_report.json").read_text(encoding="utf-8"))
    additions = defaultdict(list)
    for correction in source_report["corrections"]:
        assert correction["class_id"] == 4
        additions[(correction["split"], correction["id"])].append(
            "7" + correction["old_label"][1:])
    rows = [json.loads(line) for line in (SOURCE / "dataset_manifest.jsonl").read_text(encoding="utf-8").splitlines()]
    expected_keys = set(additions)
    seen_keys = set()
    kept = []
    for row in rows:
        split, stem = row["split"], row["id"]
        if stem == STAIR_QUARANTINE:
            assert split == "train"
            continue
        image_target = TARGET / "images" / split / f"{stem}.jpg"
        label_target = TARGET / "labels" / split / f"{stem}.txt"
        image_target.parent.mkdir(parents=True, exist_ok=True)
        label_target.parent.mkdir(parents=True, exist_ok=True)
        os.link(SOURCE / "images" / split / f"{stem}.jpg", image_target)
        lines = (SOURCE / "labels" / split / f"{stem}.txt").read_text(encoding="utf-8").splitlines()
        key = (split, stem)
        if key in additions:
            seen_keys.add(key)
            lines.extend(additions[key])
        label_target.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")
        kept.append({**row, "class_ids": sorted({int(line.split()[0]) for line in lines})})
    assert seen_keys == expected_keys, expected_keys - seen_keys
    names = (*NAMES, "motorcycle")
    (TARGET / "dataset.yaml").write_text(
        f"path: {TARGET.as_posix()}\ntrain: images/train\nval: images/val\ntest: images/test\nnames:\n" +
        "".join(f"  {index}: {name}\n" for index, name in enumerate(names)), encoding="utf-8")
    (TARGET / "dataset_manifest.jsonl").write_text(
        "".join(json.dumps(row) + "\n" for row in kept), encoding="utf-8")
    report = {"source": str(SOURCE), "target": str(TARGET),
              "status": "candidate_eight_class_requires_new_untouched_test",
              "added_motorcycle_boxes": sum(map(len, additions.values())),
              "added_motorcycle_boxes_by_split": dict(Counter(split for split, _ in
                                                          (key for key, lines in additions.items() for _ in lines))),
              "quarantined_stair_image": STAIR_QUARANTINE,
              "image_storage": "hardlinks_to_immutable_v7_images; labels_are_separate_files",
              "kept_by_split": dict(Counter(row["split"] for row in kept))}
    (TARGET / "build_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
