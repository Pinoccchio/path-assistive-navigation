"""Add a frozen, source-disjoint COCO train2017 vehicle slice to v8 training."""

import hashlib
import json
import os
import random
import time
import urllib.request
import zipfile
from collections import Counter

from PIL import Image

from phase1 import NAMES, ROOT


SOURCE = ROOT / "data" / "processed" / "public_phase1_v8_motorcycle_candidate"
TARGET = ROOT / "data" / "processed" / "public_phase1_v9_coco_train_candidate"
DATA = ROOT / "data" / "source" / "coco_external"
ZIP = DATA / "coco2017labels-libreyolo.zip"
SELECTION = DATA / "train_selection.json"
MAP = {0: 0, 56: 1, 2: 3, 1: 4, 3: 7}


def select(z):
    if SELECTION.exists():
        frozen = json.loads(SELECTION.read_text(encoding="utf-8"))
        assert frozen["seed"] == 20261001 and frozen["per_group"] == 150
        return frozen["rows"]
    groups = {"bicycle_only": [], "motorcycle_only": []}
    for name in z.namelist():
        if not name.startswith("coco/labels/train2017/") or not name.endswith(".txt"):
            continue
        lines = z.read(name).decode("utf-8").splitlines()
        ids = {int(line.split()[0]) for line in lines if line.strip()}
        if 58 in ids:  # COCO potted plant label includes foliage, conflicting with pot-only policy
            continue
        if ids & {1, 3} == {1}:
            groups["bicycle_only"].append(name)
        elif ids & {1, 3} == {3}:
            groups["motorcycle_only"].append(name)
    rng = random.Random(20261001)
    rows = []
    for group, names in groups.items():
        for name in rng.sample(sorted(names), 150):
            image_id = name.rsplit("/", 1)[-1][:-4]
            rows.append({"group": group, "image_id": image_id,
                         "label_sha256": hashlib.sha256(z.read(name)).hexdigest()})
    SELECTION.write_text(json.dumps({"seed": 20261001, "per_group": 150,
                                     "source": "COCO train2017 labels and images",
                                     "labels_zip_sha256": hashlib.sha256(ZIP.read_bytes()).hexdigest(),
                                     "rows": rows}, indent=2), encoding="utf-8")
    return rows


def download(row):
    folder = DATA / "train_images"
    folder.mkdir(exist_ok=True)
    dest = folder / f'{row["image_id"]}.jpg'
    if dest.exists():
        with Image.open(dest) as im:
            im.verify()
        return dest
    url = f'http://images.cocodataset.org/train2017/{row["image_id"]}.jpg'
    temp = dest.with_suffix(".part")
    for attempt in range(5):
        try:
            urllib.request.urlretrieve(url, temp)
            with Image.open(temp) as im:
                im.verify()
            temp.replace(dest)
            return dest
        except Exception:
            if attempt == 4:
                raise
            time.sleep(2 * (attempt + 1))


def main():
    if TARGET.exists():
        raise SystemExit(f"Output already exists: {TARGET}")
    expected_zip = "bdda16fd74809745d9fc303335dad63e6d1fe85ca53b2c32a49c252587252cbb"
    assert hashlib.sha256(ZIP.read_bytes()).hexdigest() == expected_zip
    with zipfile.ZipFile(ZIP) as z:
        selection = select(z)
        downloaded = [(row, download(row)) for row in selection]
        old_rows = [json.loads(line) for line in (SOURCE / "dataset_manifest.jsonl").read_text(encoding="utf-8").splitlines()]
        kept = []
        for row in old_rows:
            split, stem = row["split"], row["id"]
            dest_image = TARGET / "images" / split / f"{stem}.jpg"
            dest_label = TARGET / "labels" / split / f"{stem}.txt"
            dest_image.parent.mkdir(parents=True, exist_ok=True)
            dest_label.parent.mkdir(parents=True, exist_ok=True)
            os.link(SOURCE / "images" / split / f"{stem}.jpg", dest_image)
            dest_label.write_bytes((SOURCE / "labels" / split / f"{stem}.txt").read_bytes())
            kept.append(row)
        existing_hashes = {hashlib.sha256((SOURCE / "images" / row["split"] / f'{row["id"]}.jpg').read_bytes()).hexdigest()
                           for row in old_rows}
        new_hashes = set()
        for row, image in downloaded:
            digest = hashlib.sha256(image.read_bytes()).hexdigest()
            assert digest not in existing_hashes and digest not in new_hashes, row["image_id"]
            new_hashes.add(digest)
            stem = "coco_train2017_" + row["image_id"]
            label_path = f"coco/labels/train2017/{row['image_id']}.txt"
            raw = z.read(label_path).decode("utf-8").splitlines()
            mapped = [str(MAP[int(line.split()[0])]) + line[line.find(" "):] for line in raw
                      if line.strip() and int(line.split()[0]) in MAP]
            assert any(line.startswith("4 ") or line.startswith("7 ") for line in mapped)
            os.link(image, TARGET / "images" / "train" / f"{stem}.jpg")
            (TARGET / "labels" / "train" / f"{stem}.txt").write_text("\n".join(mapped) + "\n", encoding="utf-8")
            kept.append({"id": stem, "split": "train", "group": "coco_train2017:" + row["image_id"],
                         "source": "COCO train2017", "source_id": row["image_id"],
                         "license_status": "per_image_coco_license_not_captured", "sha256": digest,
                         "class_ids": sorted({int(line.split()[0]) for line in mapped})})
    names = (*NAMES, "motorcycle")
    (TARGET / "dataset.yaml").write_text(
        f"path: {TARGET.as_posix()}\ntrain: images/train\nval: images/val\ntest: images/test\nnames:\n" +
        "".join(f"  {index}: {name}\n" for index, name in enumerate(names)), encoding="utf-8")
    (TARGET / "dataset_manifest.jsonl").write_text(
        "".join(json.dumps(row) + "\n" for row in kept), encoding="utf-8")
    report = {"source": str(SOURCE), "target": str(TARGET), "new_train_images": len(selection),
              "new_train_by_group": dict(Counter(row["group"] for row in selection)),
              "kept_by_split": dict(Counter(row["split"] for row in kept)),
              "status": "candidate_requires_audited_holdout_evaluation",
              "selection": str(SELECTION)}
    (TARGET / "build_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
