"""Build a reversible data-quality candidate from visually reviewed zero-person-label images."""

import hashlib
import json
import os
from collections import Counter

from phase1 import ROOT

SOURCE = ROOT / "data/processed/public_phase1_v15_oi_quarantine"
TARGET = ROOT / "data/processed/public_phase1_v16_person_quarantine"
QUEUE = ROOT / "runs/public_phase1_v15_oi_quarantine/person_label_audit_queue.json"
LEDGER = ROOT / "data/source/oi_vehicle_v10/train_quarantine_v16_person.json"
CLASSES = ("person", "chair", "stairs", "car", "bicycle", "electrical_pole", "plant_pot", "motorcycle")


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    if TARGET.exists() or LEDGER.exists():
        raise SystemExit("v16 output already exists; refusing to overwrite")
    queue = json.loads(QUEUE.read_text(encoding="utf-8"))
    ids = {row["image_id"] for row in queue["rows"] if row["person_boxes"] == 0}
    assert len(ids) == 109, "Review set changed; recheck all 28 sheets"
    rows = [json.loads(line) for line in (SOURCE / "dataset_manifest.jsonl").read_text(encoding="utf-8").splitlines()]
    excluded = {}
    lost_boxes = Counter()
    for row in rows:
        if row["source_id"] not in ids:
            continue
        assert row["split"] == "train" and row["source"] == "OpenImagesV7"
        assert row["id"] == f"oi_v10_train_{row['source_id']}"
        image = SOURCE / "images/train" / f"{row['id']}.jpg"
        label = SOURCE / "labels/train" / f"{row['id']}.txt"
        assert sha256(image) == row["sha256"]
        assert not any(line.startswith("0 ") for line in label.read_text().splitlines())
        excluded[row["source_id"]] = {"image_sha256": row["sha256"],
                                      "label_sha256": sha256(label),
                                      "reason": "Visible person(s) in reviewed whole-image sheet; source has zero person boxes."}
        for line in label.read_text().splitlines():
            lost_boxes[CLASSES[int(line.split()[0])]] += 1
    assert set(excluded) == ids
    ledger = {"scope": "Exclude 109 visually reviewed Open Images training images with visible people and zero person labels; retain source and all val/test files.",
              "review_evidence": "All 28 person_zero_gt_sheets reviewed visually at image level; individual detector proposals were not accepted as labels.",
              "review_sheets": str(ROOT / "runs/public_phase1_v15_oi_quarantine/person_zero_gt_sheets"),
              "excluded": dict(sorted(excluded.items())), "lost_labeled_boxes": dict(lost_boxes),
              "caveat": "This is not an exhaustive instance-level audit of all retained images."}
    LEDGER.write_text(json.dumps(ledger, indent=2) + "\n", encoding="utf-8")
    kept = []
    for row in rows:
        if row["source_id"] in ids:
            continue
        split, stem = row["split"], row["id"]
        for kind, ext in (("images", ".jpg"), ("labels", ".txt")):
            src = SOURCE / kind / split / f"{stem}{ext}"
            dst = TARGET / kind / split / f"{stem}{ext}"
            dst.parent.mkdir(parents=True, exist_ok=True)
            if kind == "images":
                os.link(src, dst)
            else:
                dst.write_bytes(src.read_bytes())
        kept.append(row)
    counts = Counter(row["split"] for row in kept)
    assert counts == Counter({"train": 3186, "val": 251, "test": 620})
    yaml = (SOURCE / "dataset.yaml").read_text(encoding="utf-8")
    assert SOURCE.as_posix() in yaml
    (TARGET / "dataset.yaml").write_text(yaml.replace(SOURCE.as_posix(), TARGET.as_posix()), encoding="utf-8")
    (TARGET / "dataset_manifest.jsonl").write_text("".join(json.dumps(row) + "\n" for row in kept), encoding="utf-8")
    report = {"source": str(SOURCE), "target": str(TARGET), "excluded_train_images": len(ids),
              "kept_by_split": dict(counts), "lost_labeled_boxes": dict(lost_boxes),
              "ledger_sha256": sha256(LEDGER), "val_test_unchanged": True}
    (TARGET / "build_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
