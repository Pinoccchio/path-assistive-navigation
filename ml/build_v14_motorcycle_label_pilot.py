"""Build isolated v14 train-label pilot on top of v13."""

import hashlib
import json
import os
from collections import Counter

from PIL import Image

from phase1 import ROOT


SOURCE = ROOT / "data/processed/public_phase1_v13_four_box_pilot"
TARGET = ROOT / "data/processed/public_phase1_v14_six_box_pilot"
LEDGER = ROOT / "data/source/oi_vehicle_v10/train_corrections_v14_pilot.json"


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    if TARGET.exists():
        raise SystemExit(f"Output already exists: {TARGET}")
    ledger = json.loads(LEDGER.read_text(encoding="utf-8"))
    corrections = ledger["add_boxes"]
    assert len(corrections) == 2 and sum(len(item["boxes_xyxy"]) for item in corrections.values()) == 2
    rows = [json.loads(line) for line in (SOURCE / "dataset_manifest.jsonl").read_text(encoding="utf-8").splitlines()]
    assert len(rows) == 4173
    seen, output_rows = set(), []
    for original in rows:
        row = dict(original)
        split, stem = row["split"], row["id"]
        source_image = SOURCE / "images" / split / f"{stem}.jpg"
        source_label = SOURCE / "labels" / split / f"{stem}.txt"
        assert source_image.exists() and source_label.exists()
        target_image = TARGET / "images" / split / f"{stem}.jpg"
        target_label = TARGET / "labels" / split / f"{stem}.txt"
        target_image.parent.mkdir(parents=True, exist_ok=True)
        target_label.parent.mkdir(parents=True, exist_ok=True)
        correction = corrections.get(row["source_id"]) if split == "train" else None
        if correction:
            assert row["source"] == "OpenImagesV7" and stem == f"oi_v10_train_{row['source_id']}"
            assert sha256(source_image) == correction["image_sha256"] == row["sha256"]
            with Image.open(source_image) as image:
                width, height = image.size
            assert [width, height] == correction["image_size"]
            label_text = source_label.read_text(encoding="utf-8").rstrip("\n") + "\n"
            existing = []
            for line in label_text.splitlines():
                cls, xc, yc, bw, bh = map(float, line.split())
                if int(cls) == 7:
                    existing.append(((xc - bw / 2) * width, (yc - bh / 2) * height,
                                     (xc + bw / 2) * width, (yc + bh / 2) * height))
            for cls, x1, y1, x2, y2 in correction["boxes_xyxy"]:
                assert cls == 7 and 0 <= x1 < x2 <= width and 0 <= y1 < y2 <= height
                assert all((max(0, min(x2, b[2]) - max(x1, b[0])) *
                            max(0, min(y2, b[3]) - max(y1, b[1]))) /
                           ((x2 - x1) * (y2 - y1) + (b[2] - b[0]) * (b[3] - b[1]) -
                            max(0, min(x2, b[2]) - max(x1, b[0])) *
                            max(0, min(y2, b[3]) - max(y1, b[1]))) < 0.5 for b in existing)
                label_text += f"{cls} {(x1 + x2) / (2 * width):.8f} {(y1 + y2) / (2 * height):.8f} {(x2 - x1) / width:.8f} {(y2 - y1) / height:.8f}\n"
                row["class_ids"] = sorted(set(row["class_ids"]) | {cls})
            target_label.write_text(label_text, encoding="utf-8")
            seen.add(row["source_id"])
        else:
            target_label.write_bytes(source_label.read_bytes())
        os.link(source_image, target_image)
        output_rows.append(row)
    assert seen == set(corrections)
    assert Counter(row["split"] for row in output_rows) == Counter({"train": 3302, "val": 251, "test": 620})
    yaml = (SOURCE / "dataset.yaml").read_text(encoding="utf-8")
    assert SOURCE.as_posix() in yaml
    (TARGET / "dataset.yaml").write_text(yaml.replace(SOURCE.as_posix(), TARGET.as_posix()), encoding="utf-8")
    (TARGET / "dataset_manifest.jsonl").write_text("".join(json.dumps(row) + "\n" for row in output_rows), encoding="utf-8")
    report = {"source": str(SOURCE), "target": str(TARGET), "ledger_sha256": sha256(LEDGER),
              "corrected_train_ids": sorted(seen), "added_boxes_this_version": 2,
              "added_boxes_cumulative_from_v11": 6,
              "kept_by_split": dict(Counter(row["split"] for row in output_rows)),
              "val_test_unchanged": True,
              "status": "Annotation pilot only; not ready for retraining or app promotion."}
    (TARGET / "build_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
