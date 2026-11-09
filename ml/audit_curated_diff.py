"""Verify a curated candidate differs from its source only as recorded."""

import argparse
import json
from collections import defaultdict

from phase1 import ROOT, sha256


def read_manifest(path):
    return {row["id"]: row for row in
            (json.loads(line) for line in (path / "dataset_manifest.jsonl").read_text(encoding="utf-8").splitlines())}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--name", default="public_phase1_v6_curated_candidate")
    parser.add_argument("--source-name", default="public_phase1_v3_screened")
    args = parser.parse_args()
    source = ROOT / "data" / "processed" / args.source_name
    target = ROOT / "data" / "processed" / args.name
    report = json.loads((target / "build_report.json").read_text(encoding="utf-8"))
    assert report["source"] == str(source)
    before, after = read_manifest(source), read_manifest(target)
    quarantined = {item["id"] for item in report["quarantined_images"]}
    assert set(before) - set(after) == quarantined
    assert not set(after) - set(before)
    corrections = defaultdict(list)
    for item in report["corrections"]:
        corrections[item["id"]].append(item)
    removed_boxes = 0
    for stem, row in after.items():
        assert row["split"] == before[stem]["split"]
        split = row["split"]
        old_image = source / "images" / split / f"{stem}.jpg"
        new_image = target / "images" / split / f"{stem}.jpg"
        assert sha256(old_image.read_bytes()) == sha256(new_image.read_bytes()) == row["sha256"]
        old_lines = (source / "labels" / split / f"{stem}.txt").read_text(encoding="utf-8").splitlines()
        new_lines = (target / "labels" / split / f"{stem}.txt").read_text(encoding="utf-8").splitlines()
        changed = corrections.get(stem, [])
        removed_indices = {item["line_index"] for item in changed}
        assert len(removed_indices) == len(changed)
        assert all(old_lines[item["line_index"]] == item["old_label"] for item in changed)
        assert new_lines == [line for index, line in enumerate(old_lines) if index not in removed_indices]
        assert row["class_ids"] == sorted({int(line.split()[0]) for line in new_lines})
        removed_boxes += len(removed_indices)
    assert set(corrections) <= set(after)
    print(json.dumps({"retained_images": len(after), "quarantined_images": len(quarantined),
                      "corrected_images": len(corrections), "removed_boxes": removed_boxes,
                      "unreported_changes": 0}, indent=2))


if __name__ == "__main__":
    main()
