"""Build isolated v15 by quarantining verified incomplete OI train images."""

import hashlib
import json
import os
from collections import Counter

from phase1 import ROOT


SOURCE = ROOT / "data/processed/public_phase1_v14_six_box_pilot"
TARGET = ROOT / "data/processed/public_phase1_v15_oi_quarantine"
LEDGER = ROOT / "data/source/oi_vehicle_v10/train_quarantine_v15.json"


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    if TARGET.exists():
        raise SystemExit(f"Output already exists: {TARGET}")
    ledger = json.loads(LEDGER.read_text(encoding="utf-8"))
    excluded = ledger["excluded"]
    assert len(excluded) == 7
    old_rows = [json.loads(line) for line in (SOURCE / "dataset_manifest.jsonl").read_text(encoding="utf-8").splitlines()]
    assert len(old_rows) == 4173
    retained, seen = [], set()
    for row in old_rows:
        split, stem = row["split"], row["id"]
        source_image = SOURCE / "images" / split / f"{stem}.jpg"
        source_label = SOURCE / "labels" / split / f"{stem}.txt"
        if row["source_id"] in excluded and split == "train" and row["source"] == "OpenImagesV7":
            assert stem == f"oi_v10_train_{row['source_id']}"
            assert sha256(source_image) == excluded[row["source_id"]]["image_sha256"] == row["sha256"]
            seen.add(row["source_id"])
            continue
        assert source_image.exists() and source_label.exists()
        target_image = TARGET / "images" / split / f"{stem}.jpg"
        target_label = TARGET / "labels" / split / f"{stem}.txt"
        target_image.parent.mkdir(parents=True, exist_ok=True)
        target_label.parent.mkdir(parents=True, exist_ok=True)
        os.link(source_image, target_image)
        target_label.write_bytes(source_label.read_bytes())
        retained.append(row)
    assert seen == set(excluded)
    assert Counter(row["split"] for row in retained) == Counter({"train": 3295, "val": 251, "test": 620})
    yaml = (SOURCE / "dataset.yaml").read_text(encoding="utf-8")
    assert SOURCE.as_posix() in yaml
    (TARGET / "dataset.yaml").write_text(yaml.replace(SOURCE.as_posix(), TARGET.as_posix()), encoding="utf-8")
    (TARGET / "dataset_manifest.jsonl").write_text("".join(json.dumps(row) + "\n" for row in retained), encoding="utf-8")
    report = {"source": str(SOURCE), "target": str(TARGET), "ledger_sha256": sha256(LEDGER),
              "quarantined_train_ids": sorted(seen), "kept_by_split": dict(Counter(row["split"] for row in retained)),
              "val_test_unchanged": True, "status": "Data-quality pilot; remaining train images are not yet exhaustively audited."}
    (TARGET / "build_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
