"""Verify that v8 changes only the reviewed motorcycle boxes and one quarantine."""

import json
from collections import defaultdict

from build_v8_motorcycle_candidate import SOURCE, STAIR_QUARANTINE, TARGET


def main():
    corrections = json.loads((SOURCE / "build_report.json").read_text(encoding="utf-8"))["corrections"]
    expected = defaultdict(list)
    for correction in corrections:
        expected[(correction["split"], correction["id"])].append("7" + correction["old_label"][1:])
    rows = [json.loads(line) for line in (SOURCE / "dataset_manifest.jsonl").read_text(encoding="utf-8").splitlines()]
    changed = 0
    for row in rows:
        split, stem = row["split"], row["id"]
        image = TARGET / "images" / split / f"{stem}.jpg"
        label = TARGET / "labels" / split / f"{stem}.txt"
        if stem == STAIR_QUARANTINE:
            assert not image.exists() and not label.exists()
            continue
        assert image.exists() and image.samefile(SOURCE / "images" / split / f"{stem}.jpg")
        old = (SOURCE / "labels" / split / f"{stem}.txt").read_text(encoding="utf-8").splitlines()
        new = label.read_text(encoding="utf-8").splitlines()
        assert new == old + expected.get((split, stem), []), stem
        changed += bool(expected.get((split, stem)))
    assert changed == len(expected) == 98, changed
    target_rows = [json.loads(line) for line in (TARGET / "dataset_manifest.jsonl").read_text(encoding="utf-8").splitlines()]
    assert len(target_rows) == len(rows) - 1
    print(json.dumps({"images_checked": len(rows), "changed_images": changed,
                      "motorcycle_boxes_added": len(corrections), "quarantined_images": 1,
                      "unexpected_changes": 0}))


if __name__ == "__main__":
    main()
