"""Build v11 without seven visually invalid OI train images; preserve v10 splits."""

import hashlib
import json
import os
from collections import Counter

from phase1 import ROOT


SOURCE = ROOT / "data" / "processed" / "public_phase1_v10_oi_vehicle_candidate"
TARGET = ROOT / "data" / "processed" / "public_phase1_v11_reviewed_640_candidate"
LEDGER = ROOT / "data" / "source" / "oi_vehicle_v10" / "train_review_v11.json"


def main():
    if TARGET.exists():
        raise SystemExit(f"Output already exists: {TARGET}")
    review = json.loads(LEDGER.read_text(encoding="utf-8"))
    excluded = set(review["excluded"])
    old_rows = [json.loads(line) for line in (SOURCE / "dataset_manifest.jsonl").read_text(encoding="utf-8").splitlines()]
    assert len(old_rows) == 4180
    old_train_oi = {row["source_id"] for row in old_rows if row["split"] == "train"
                    and row["source"] == "OpenImagesV7" and row["id"].startswith("oi_v10_train_")}
    assert excluded.issubset(old_train_oi)
    kept = []
    for row in old_rows:
        if row["source_id"] in excluded and row["split"] == "train" and row["id"].startswith("oi_v10_train_"):
            continue
        split, stem = row["split"], row["id"]
        image = SOURCE / "images" / split / f"{stem}.jpg"
        label = SOURCE / "labels" / split / f"{stem}.txt"
        assert image.exists() and label.exists()
        dest_image = TARGET / "images" / split / f"{stem}.jpg"
        dest_label = TARGET / "labels" / split / f"{stem}.txt"
        dest_image.parent.mkdir(parents=True, exist_ok=True)
        dest_label.parent.mkdir(parents=True, exist_ok=True)
        os.link(image, dest_image)
        dest_label.write_bytes(label.read_bytes())
        kept.append(row)
    assert len(kept) == len(old_rows) - len(excluded)
    assert Counter(row["split"] for row in kept) == Counter({"train": 3302, "val": 251, "test": 620})
    yaml = (SOURCE / "dataset.yaml").read_text(encoding="utf-8")
    assert SOURCE.as_posix() in yaml
    (TARGET / "dataset.yaml").write_text(yaml.replace(SOURCE.as_posix(), TARGET.as_posix()), encoding="utf-8")
    (TARGET / "dataset_manifest.jsonl").write_text("".join(json.dumps(row) + "\n" for row in kept), encoding="utf-8")
    report = {"source": str(SOURCE), "target": str(TARGET), "excluded_train_images": review["excluded"],
              "ledger_sha256": hashlib.sha256(LEDGER.read_bytes()).hexdigest(),
              "kept_by_split": dict(Counter(row["split"] for row in kept)),
              "unchanged_val_test": True,
              "limitations": "Only seven clearly invalid OI training images were quarantined; other source labels remain provisional."}
    (TARGET / "build_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({k: v for k, v in report.items() if k != "excluded_train_images"}, indent=2))


if __name__ == "__main__":
    main()
