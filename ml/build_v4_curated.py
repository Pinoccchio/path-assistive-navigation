"""Build a traceable public-data correction candidate from frozen v3."""

import argparse
import csv
import json
import shutil
from collections import Counter

from phase1 import NAMES, ROOT


SOURCE = ROOT / "data" / "processed" / "public_phase1_v3_screened"
TARGET = ROOT / "data" / "processed" / "public_phase1_v4_curated_candidate"

# Image-level corrections inspected on the v3 contact sheets.
REMOVE_CLASS = {
    "openimagesv7_test_412e3fddac13e4cf": (2, "ladder_not_staircase"),
    "openimagesv7_train_2eb41aeba506f4f3": (2, "escalator_not_fixed_staircase"),
    "openimagesv7_train_acd4e0d765b6c7a5": (2, "escalators_not_fixed_staircase"),
    "openimagesv7_validation_3b24969867312817": (2, "escalators_not_fixed_staircase"),
    "openimagesv7_validation_bebc0d02872d34ef": (2, "escalator_not_fixed_staircase"),
    "openimagesv7_validation_ec737163fc7941cb": (2, "ladder_not_staircase"),
    "rod_test_IMG_19194": (6, "empty_pot"),
    "rod_train_IMG_00093": (6, "empty_pots"),
    "rod_train_IMG_00116": (6, "empty_pots"),
    "rod_train_IMG_00141": (6, "empty_pot"),
    "pilot_train_IMG_00151": (6, "empty_pot"),
    "pilot_train_IMG_00163": (6, "empty_pot"),
    "pilot_train_IMG_00133": (6, "flower_vase_not_potted_plant"),
    "rod_validation_IMG_22572": (6, "flower_vase_not_potted_plant"),
}

# Only the visually identified bare pot; the other planted containers stay.
REMOVE_LINE = {
    "pilot_train_IMG_09326": ({0}, "bare_pot_among_planted_containers"),
    "pilot_train_IMG_09416": ({0}, "bare_pot_among_planted_containers"),
    "rod_validation_IMG_22601": ({2}, "bare_pot_among_planted_containers"),
}
QUARANTINE_IDS = {
    "openimagesv7_validation_11e182562844e361": "mixed_unlabeled_stairs_and_mislabeled_escalators",
}
STREETLIGHT_IDS = {
    "rod_test_IMG_20587", "rod_test_IMG_20595", "rod_test_IMG_20597", "rod_test_IMG_20598",
    "rod_validation_IMG_23777", "rod_validation_IMG_23780", "rod_validation_IMG_23787",
    "rod_validation_IMG_23792", "rod_validation_IMG_23798", "rod_validation_IMG_23804",
    "rod_train_IMG_16638", "rod_train_IMG_16684", "rod_train_IMG_16711",
    "rod_train_IMG_16728", "rod_train_IMG_16735", "rod_train_IMG_16751",
    "rod_train_IMG_16786", "rod_train_IMG_16809", "rod_train_IMG_16824",
    "rod_train_IMG_16833", "rod_train_IMG_16877", "rod_train_IMG_16884",
    "rod_train_IMG_16888", "rod_train_IMG_16891", "rod_train_IMG_16897",
    "rod_train_IMG_16901", "rod_train_IMG_16909", "rod_train_IMG_16938",
    "rod_train_IMG_16942", "pilot_train_IMG_16573", "pilot_train_IMG_16863",
    "pilot_train_IMG_16869", "pilot_train_IMG_16880", "pilot_train_IMG_16893",
    "pilot_train_IMG_16911", "pilot_val_IMG_23782", "pilot_val_IMG_23791",
    "pilot_val_IMG_23797",
}


def main():
    global TARGET
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--name", default="public_phase1_v6_curated_candidate")
    args = parser.parse_args()
    TARGET = ROOT / "data" / "processed" / args.name
    if TARGET.exists():
        raise SystemExit(f"Output already exists: {TARGET}")
    rows = [json.loads(line) for line in (SOURCE / "dataset_manifest.jsonl").read_text(encoding="utf-8").splitlines()]
    pole_ledger = list(csv.DictReader((SOURCE / "pole_review_ledger.csv").open(newline="", encoding="utf-8")))
    pole_ids = {row["id"] for row in pole_ledger if row["proposed_action"] ==
                "remove_electrical_pole_boxes_in_next_version"}
    expected = pole_ids | STREETLIGHT_IDS | set(REMOVE_CLASS) | set(REMOVE_LINE) | set(QUARANTINE_IDS)
    actual = {row["id"] for row in rows}
    if missing := expected - actual:
        raise ValueError(f"Corrections missing from v3: {sorted(missing)}")
    if len(pole_ids) != 24:
        raise ValueError(f"Unexpected pole correction count: {len(pole_ids)}")
    if len(STREETLIGHT_IDS) != 38 or pole_ids & STREETLIGHT_IDS:
        raise ValueError("Unexpected streetlight correction set")

    for split in ("train", "val", "test"):
        (TARGET / "images" / split).mkdir(parents=True)
        (TARGET / "labels" / split).mkdir(parents=True)
    correction_log = []
    quarantine = []
    kept = []
    for row in rows:
        stem, split = row["id"], row["split"]
        source_label = SOURCE / "labels" / split / f"{stem}.txt"
        lines = source_label.read_text(encoding="utf-8").splitlines()
        stair_count = sum(line.startswith("2 ") for line in lines)
        # Three or more boxes are frequently per-step annotations, contrary
        # to the one-staircase-region policy. Quarantine whole images until
        # a person can distinguish that pattern from multiple staircases.
        if stem in QUARANTINE_IDS or stair_count >= 3:
            quarantine.append({"id": stem, "split": split,
                               "reason": QUARANTINE_IDS.get(stem, "stair_box_granularity_review_required"),
                               "stair_boxes": stair_count})
            continue
        drop_classes = {}
        if stem in pole_ids:
            drop_classes[5] = "crossing_button_post_not_utility_pole"
        if stem in STREETLIGHT_IDS:
            drop_classes[5] = "streetlight_post_not_utility_pole"
        if stem in REMOVE_CLASS:
            class_id, reason = REMOVE_CLASS[stem]
            drop_classes[class_id] = reason
        drop_lines, line_reason = REMOVE_LINE.get(stem, (set(), ""))
        if not drop_lines.issubset(set(range(len(lines)))):
            raise ValueError(f"Invalid line index for {stem}")
        new_lines = []
        for index, line in enumerate(lines):
            class_id = int(line.split()[0])
            reason = line_reason if index in drop_lines else drop_classes.get(class_id)
            if reason:
                correction_log.append({"id": stem, "split": split, "line_index": index,
                                       "class_id": class_id, "reason": reason, "old_label": line})
            else:
                new_lines.append(line)
        if stem in REMOVE_LINE and not any(item["id"] == stem and item["reason"] == line_reason
                                           for item in correction_log):
            raise ValueError(f"No line correction applied for {stem}")
        shutil.copy2(SOURCE / "images" / split / f"{stem}.jpg",
                     TARGET / "images" / split / f"{stem}.jpg")
        (TARGET / "labels" / split / f"{stem}.txt").write_text(
            "\n".join(new_lines) + ("\n" if new_lines else ""), encoding="utf-8")
        kept.append({**row, "class_ids": sorted({int(line.split()[0]) for line in new_lines})})

    (TARGET / "dataset.yaml").write_text(
        f"path: {TARGET.as_posix()}\ntrain: images/train\nval: images/val\ntest: images/test\nnames:\n" +
        "".join(f"  {index}: {name}\n" for index, name in enumerate(NAMES)), encoding="utf-8")
    (TARGET / "dataset_manifest.jsonl").write_text(
        "".join(json.dumps(row) + "\n" for row in kept), encoding="utf-8")
    report = {
        "source": str(SOURCE), "target": str(TARGET),
        "status": "candidate_partial_semantic_review_not_independent_test",
        "class_policy": "ml/PUBLIC_LABEL_POLICY.md",
        "kept_by_split": dict(Counter(row["split"] for row in kept)),
        "quarantined_by_split": dict(Counter(row["split"] for row in quarantine)),
        "corrected_boxes_by_reason": dict(Counter(item["reason"] for item in correction_log)),
        "images_with_corrected_boxes": len({item["id"] for item in correction_log}),
        "quarantined_images": quarantine,
        "corrections": correction_log,
    }
    (TARGET / "build_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({key: value for key, value in report.items()
                      if key not in ("quarantined_images", "corrections")}, indent=2))


if __name__ == "__main__":
    main()
