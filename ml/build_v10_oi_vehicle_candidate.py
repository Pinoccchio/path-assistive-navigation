"""Add reviewed Open Images train photos to v9 and freeze a separate OI test."""

import hashlib
import json
import os
from collections import Counter

from phase1 import ROOT, NAMES, valid_yolo_line


SOURCE = ROOT / "data" / "processed" / "public_phase1_v9_coco_train_candidate"
TARGET = ROOT / "data" / "processed" / "public_phase1_v10_oi_vehicle_candidate"
OI = ROOT / "data" / "source" / "oi_vehicle_v10"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    if TARGET.exists():
        raise SystemExit(f"Output already exists: {TARGET}")
    review = json.loads((OI / "review_exclusions.json").read_text(encoding="utf-8"))
    old = [json.loads(line) for line in (SOURCE / "dataset_manifest.jsonl").read_text(encoding="utf-8").splitlines()]
    old_hashes = {row["sha256"] for row in old}
    rows = list(old)
    counts = Counter()
    new_hashes = set()
    for row in old:
        split, stem = row["split"], row["id"]
        src_image = SOURCE / "images" / split / f"{stem}.jpg"
        src_label = SOURCE / "labels" / split / f"{stem}.txt"
        assert src_image.exists() and src_label.exists()
        dest_image = TARGET / "images" / split / f"{stem}.jpg"
        dest_label = TARGET / "labels" / split / f"{stem}.txt"
        dest_image.parent.mkdir(parents=True, exist_ok=True)
        dest_label.parent.mkdir(parents=True, exist_ok=True)
        os.link(src_image, dest_image)
        dest_label.write_bytes(src_label.read_bytes())
        counts["v9_" + split] += 1
    train_ids = {r["image_id"] for r in json.loads((OI / "train_selection.json").read_text(encoding="utf-8"))["rows"]}
    test_ids = {r["image_id"] for r in json.loads((OI / "test_selection.json").read_text(encoding="utf-8"))["rows"]}
    assert train_ids.isdisjoint(test_ids)
    for split in ("train", "test"):
        selection = json.loads((OI / f"{split}_selection.json").read_text(encoding="utf-8"))
        download = json.loads((OI / f"{split}_download_report.json").read_text(encoding="utf-8"))
        assert not download["failures"] and download["downloaded_verified"] == len(selection["rows"])
        assert set(review[split]).issubset({r["image_id"] for r in selection["rows"]})
        for item in selection["rows"]:
            image_id = item["image_id"]
            if image_id in review[split]:
                counts[split + "_quarantined"] += 1
                continue
            src = OI / "images" / split / f"{image_id}.jpg"
            sha = digest(src)
            assert sha == download["sha256_by_image_id"][image_id]
            assert sha not in old_hashes and sha not in new_hashes, image_id
            new_hashes.add(sha)
            label_rows = [" ".join([str(int(box[0])), *(f"{x:.8f}" for x in box[1:])]) for box in item["boxes"]]
            assert label_rows and all(valid_yolo_line(line) or int(line.split()[0]) == 7 for line in label_rows)
            assert any(int(line.split()[0]) in (4, 7) for line in label_rows)
            stem = "oi_v10_" + split + "_" + image_id
            dest = TARGET / "images" / split / f"{stem}.jpg"
            dest.parent.mkdir(parents=True, exist_ok=True)
            (TARGET / "labels" / split).mkdir(parents=True, exist_ok=True)
            os.link(src, dest)
            (TARGET / "labels" / split / f"{stem}.txt").write_text("\n".join(label_rows) + "\n", encoding="utf-8")
            rows.append({"id": stem, "split": split, "group": "oi_v10:" + image_id,
                         "source": "OpenImagesV7", "source_id": image_id,
                         "license_status": item["License"], "sha256": sha,
                         "class_ids": sorted({int(line.split()[0]) for line in label_rows})})
            counts[split + "_" + item["group"]] += 1
    (TARGET / "dataset.yaml").write_text(
        f"path: {TARGET.as_posix()}\ntrain: images/train\nval: images/val\ntest: images/test\nnames:\n" +
        "".join(f"  {index}: {name}\n" for index, name in enumerate((*NAMES, "motorcycle"))), encoding="utf-8")
    (TARGET / "dataset_manifest.jsonl").write_text(
        "".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")
    report = {"source": str(SOURCE), "target": str(TARGET), "counts": dict(counts),
              "test_policy": "new Open Images test IDs, no model inference before review exclusions; source annotations still incomplete",
              "review_ledger_sha256": digest(OI / "review_exclusions.json")}
    (TARGET / "build_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
