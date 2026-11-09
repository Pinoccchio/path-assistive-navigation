"""Build an immutable, conservatively screened v2 from the v1 public set.

This is an interim public-data experiment, not a fully human-reviewed dataset.
The existing v1 files and evaluation artifacts are never modified.
"""

import argparse
import json
import shutil
from collections import Counter
from pathlib import Path

from PIL import Image

from phase1 import NAMES, OUTPUT, ROOT, dhash
from qa_phash import phash


TARGET = ROOT / "data" / "processed" / "public_phase1_v2_screened"
KNOWN_BAD = {
    "openimagesv7_test_14fe08f87965e8a0",  # Escalator labeled stairs.
    "rod_test_IMG_19835",  # Motorcycle labeled bicycle.
    "rod_test_IMG_19193",  # Bare pot labeled plant_pot.
    "rod_test_IMG_19614",  # Backless stool labeled chair.
    "rod_test_IMG_20088",  # Crossing-button post labeled electrical_pole.
    "rod_test_IMG_20090",
    "rod_test_IMG_20092",
    "rod_train_IMG_10612",
    "rod_train_IMG_10621",
    "rod_train_IMG_17832",
    "pilot_val_IMG_23955",
}


def image_path(row):
    return OUTPUT / "images" / row["split"] / f"{row['id']}.jpg"


def pole_box_is_wide(row):
    path = OUTPUT / "labels" / row["split"] / f"{row['id']}.txt"
    with Image.open(image_path(row)) as source:
        width, height = source.size
    for line in path.read_text(encoding="utf-8").splitlines():
        cls, _, _, box_width, box_height = map(float, line.split())
        if int(cls) == 5 and box_width * width >= 0.6 * box_height * height:
            return True
    return False


def main():
    global TARGET
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--name", default="public_phase1_v2_screened")
    parser.add_argument("--phash-distance", type=int, default=None)
    args = parser.parse_args()
    TARGET = ROOT / "data" / "processed" / args.name
    if TARGET.exists():
        raise SystemExit(f"Output already exists: {TARGET}")
    rows = [json.loads(line) for line in (OUTPUT / "dataset_manifest.jsonl").read_text(encoding="utf-8").splitlines()]
    fingerprints = {row["id"]: dhash(image_path(row)) for row in rows}
    perceptual = {row["id"]: phash(image_path(row)) for row in rows} if args.phash_distance is not None else {}
    reasons = {}
    bad_seeds = [row for row in rows if row["id"] in KNOWN_BAD]
    for row in rows:
        if row["id"] in KNOWN_BAD:
            reasons[row["id"]] = "confirmed_semantic_mismatch"
        elif pole_box_is_wide(row):
            reasons[row["id"]] = "pole_box_not_vertical_review_required"
        elif any(set(row["class_ids"]) & set(seed["class_ids"])
                 and (fingerprints[row["id"]] ^ fingerprints[seed["id"]]).bit_count() <= 7
                 for seed in bad_seeds):
            reasons[row["id"]] = "near_confirmed_semantic_mismatch_review_required"

    def overlaps(left, right):
        return bool(set(left["class_ids"]) & set(right["class_ids"])) and (
            left["group"] == right["group"] or
            (fingerprints[left["id"]] ^ fingerprints[right["id"]]).bit_count() <= 13 or
            (args.phash_distance is not None and
             (perceptual[left["id"]] ^ perceptual[right["id"]]).bit_count() <= args.phash_distance)
        )

    test = [row for row in rows if row["split"] == "test" and row["id"] not in reasons]
    val = []
    for row in rows:
        if row["split"] != "val" or row["id"] in reasons:
            continue
        if any(overlaps(row, other) for other in test):
            reasons[row["id"]] = "validation_scene_overlaps_test"
        else:
            val.append(row)
    train = []
    heldout = test + val
    for row in rows:
        if row["split"] != "train" or row["id"] in reasons:
            continue
        if any(overlaps(row, other) for other in heldout):
            reasons[row["id"]] = "training_scene_may_overlap_heldout"
        else:
            train.append(row)

    kept = [row for row in rows if row["id"] not in reasons]
    for split in ("train", "val", "test"):
        (TARGET / "images" / split).mkdir(parents=True)
        (TARGET / "labels" / split).mkdir(parents=True)
    for row in kept:
        split, stem = row["split"], row["id"]
        shutil.copy2(image_path(row), TARGET / "images" / split / f"{stem}.jpg")
        shutil.copy2(OUTPUT / "labels" / split / f"{stem}.txt", TARGET / "labels" / split / f"{stem}.txt")
    (TARGET / "dataset.yaml").write_text(
        f"path: {TARGET.as_posix()}\ntrain: images/train\nval: images/val\ntest: images/test\nnames:\n" +
        "".join(f"  {index}: {name}\n" for index, name in enumerate(NAMES)), encoding="utf-8")
    (TARGET / "dataset_manifest.jsonl").write_text(
        "".join(json.dumps(row) + "\n" for row in kept), encoding="utf-8")
    report = {
        "source_dataset": str(OUTPUT), "output_dataset": str(TARGET),
        "method": "known_bad_exclusions_plus_wide_pole_box_screen_plus_dhash_scene_screen" +
                  ("_plus_phash_scene_screen" if args.phash_distance is not None else ""),
        "dhash_scene_screen_distance": 13,
        "phash_scene_screen_distance": args.phash_distance,
        "manual_status": "provisional_not_all_images_semantically_reviewed",
        "kept_by_split": dict(Counter(row["split"] for row in kept)),
        "removed_by_reason": dict(Counter(reasons.values())),
        "removed": reasons,
        "class_images_by_split": {split: {name: sum(row["split"] == split and index in row["class_ids"] for row in kept)
                                          for index, name in enumerate(NAMES)} for split in ("train", "val", "test")},
    }
    (TARGET / "build_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({key: value for key, value in report.items() if key != "removed"}, indent=2))


if __name__ == "__main__":
    main()
