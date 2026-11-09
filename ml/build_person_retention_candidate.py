"""Build a controlled v11-derived dataset without the unreviewed new OI batch.

This is a research candidate: images are hard-linked to save disk space, labels
are copied, and the original v11 dataset is never edited.
"""

import hashlib
import json
import os
from collections import Counter

from phase1 import ROOT


SOURCE = ROOT / "data/processed/public_phase1_v11_reviewed_640_candidate"
OVERLAY = ROOT / "data/processed/stair_label_overlay_v1"
TARGET = ROOT / "data/processed/public_phase1_person_retention_candidate"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    if TARGET.exists():
        raise SystemExit(f"Candidate output already exists: {TARGET}")
    overlay = json.loads((OVERLAY / "manifest.json").read_text(encoding="utf-8"))
    corrected = {row["id"]: row for row in overlay["corrected_train_labels"]}
    quarantine = {row["id"] for row in overlay["quarantine_train_images"]}
    assert len(corrected) == 4 and len(quarantine) == 4
    assert overlay["validation_or_test_edits"] == 0
    rows = [json.loads(line) for line in (SOURCE / "dataset_manifest.jsonl")
            .read_text(encoding="utf-8").splitlines()]
    assert len(rows) == 4173
    new_oi = {row["id"] for row in rows if row["split"] == "train"
              and row["id"].startswith("oi_v10_train_")}
    assert len(new_oi) == 290
    kept = []
    for row in rows:
        split, stem = row["split"], row["id"]
        if split == "train" and (stem in new_oi or stem in quarantine):
            continue
        image = SOURCE / "images" / split / f"{stem}.jpg"
        label = SOURCE / "labels" / split / f"{stem}.txt"
        assert image.exists() and label.exists()
        dest_image = TARGET / "images" / split / f"{stem}.jpg"
        dest_label = TARGET / "labels" / split / f"{stem}.txt"
        dest_image.parent.mkdir(parents=True, exist_ok=True)
        dest_label.parent.mkdir(parents=True, exist_ok=True)
        os.link(image, dest_image)
        if split == "train" and stem in corrected:
            correction = corrected[stem]
            assert digest(image) == correction["source_image_sha256"]
            assert digest(label) == correction["source_label_sha256"]
            overlay_label = OVERLAY / "labels/train" / f"{stem}.txt"
            assert digest(overlay_label) == correction["overlay_label_sha256"]
            dest_label.write_bytes(overlay_label.read_bytes())
        else:
            dest_label.write_bytes(label.read_bytes())
        kept.append(row)
    counts = Counter(row["split"] for row in kept)
    assert counts == Counter({"train": 3008, "val": 251, "test": 620}), counts
    assert corrected.keys() <= {row["id"] for row in kept if row["split"] == "train"}
    yaml = (SOURCE / "dataset.yaml").read_text(encoding="utf-8")
    assert SOURCE.as_posix() in yaml
    (TARGET / "dataset.yaml").write_text(
        yaml.replace(SOURCE.as_posix(), TARGET.as_posix()), encoding="utf-8")
    (TARGET / "dataset_manifest.jsonl").write_text(
        "".join(json.dumps(row) + "\n" for row in kept), encoding="utf-8")
    report = {"source": str(SOURCE), "target": str(TARGET),
              "source_manifest_sha256": digest(SOURCE / "dataset_manifest.jsonl"),
              "overlay_manifest_sha256": digest(OVERLAY / "manifest.json"),
              "removed_unreviewed_new_oi_train_images": len(new_oi),
              "removed_ambiguous_stair_train_images": sorted(quarantine),
              "corrected_stair_train_labels": sorted(corrected),
              "kept_by_split": dict(counts), "validation_and_test_bytes_unchanged": True,
              "limitations": "Controlled public-data experiment, not a cleaned independent dataset. Other older source labels remain provisional."}
    (TARGET / "build_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
