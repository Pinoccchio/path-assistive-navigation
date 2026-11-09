"""Remove visually confirmed motorcycle/scooter-as-bicycle labels from frozen v6."""

import argparse
import json
import shutil
from collections import Counter

from phase1 import NAMES, ROOT


SOURCE_NAME = "public_phase1_v6_curated_candidate"

# Reviewed on the v6 ROD bicycle annotation sheets under runs/<source>/semantic_review.
# Keep these images as hard negatives (and preserve any other valid class boxes).
INVALID_BICYCLE_IDS = {
    "rod_train_IMG_01473", "rod_train_IMG_01935", "rod_train_IMG_02745",
    "rod_train_IMG_02795", "rod_train_IMG_02800", "rod_train_IMG_03312",
    "rod_train_IMG_03343", "rod_train_IMG_03345", "rod_train_IMG_03585",
    "rod_train_IMG_03657", "rod_train_IMG_03945",
    "rod_train_IMG_05293", "rod_train_IMG_05297", "rod_train_IMG_06173",
    "rod_train_IMG_06193", "rod_train_IMG_06195", "rod_train_IMG_06203",
    "rod_train_IMG_06210", "rod_train_IMG_06217", "rod_train_IMG_06228",
    "rod_train_IMG_06232", "rod_train_IMG_06239", "rod_train_IMG_06240",
    "rod_train_IMG_06248", "rod_train_IMG_06250", "rod_train_IMG_07354",
    "rod_train_IMG_07356", "rod_train_IMG_10957", "rod_train_IMG_10961",
    "rod_train_IMG_11014", "rod_train_IMG_11016", "rod_train_IMG_11465",
    "rod_train_IMG_11605", "rod_train_IMG_12194",
    "rod_train_IMG_14227", "rod_train_IMG_16367", "rod_train_IMG_16498",
    "pilot_train_IMG_04058", "pilot_train_IMG_05298", "pilot_train_IMG_06196",
    "pilot_train_IMG_06197", "pilot_train_IMG_06198", "pilot_train_IMG_06201",
    "pilot_train_IMG_06202", "pilot_train_IMG_06205", "pilot_train_IMG_06206",
    "pilot_train_IMG_06207", "pilot_train_IMG_06209", "pilot_train_IMG_06211",
    "pilot_train_IMG_06213", "pilot_train_IMG_06216", "pilot_train_IMG_06219",
    "pilot_train_IMG_06220", "pilot_train_IMG_06222", "pilot_train_IMG_06223",
    "pilot_train_IMG_06226", "pilot_train_IMG_06227", "pilot_train_IMG_06231",
    "pilot_train_IMG_06235", "pilot_train_IMG_06236", "pilot_train_IMG_06237",
    "pilot_train_IMG_06247", "pilot_train_IMG_07353", "pilot_train_IMG_10956",
    "pilot_train_IMG_11468", "pilot_train_IMG_12517", "pilot_train_IMG_14223",
    "pilot_train_IMG_18966",
    "rod_validation_IMG_21222", "rod_validation_IMG_21232",
    "rod_validation_IMG_21401", "rod_validation_IMG_21461",
    "rod_validation_IMG_22012", "rod_validation_IMG_22019",
    "rod_validation_IMG_22020", "rod_validation_IMG_23348",
    "pilot_val_IMG_22005", "pilot_val_IMG_22007", "pilot_val_IMG_22015",
    "pilot_val_IMG_22016", "pilot_val_IMG_22021", "pilot_val_IMG_22023",
    "rod_test_IMG_19421", "rod_test_IMG_19442", "rod_test_IMG_19719",
    "rod_test_IMG_19720", "rod_test_IMG_19721", "rod_test_IMG_19722",
    "rod_test_IMG_19723", "rod_test_IMG_19724", "rod_test_IMG_19725",
    "rod_test_IMG_19726", "rod_test_IMG_19727", "rod_test_IMG_19728",
    "rod_test_IMG_19729", "rod_test_IMG_19839", "rod_test_IMG_20136",
    "rod_test_IMG_20289",
}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--name", default="public_phase1_v7_vehicle_labels_candidate")
    args = parser.parse_args()
    source = ROOT / "data" / "processed" / SOURCE_NAME
    target = ROOT / "data" / "processed" / args.name
    if target.exists():
        raise SystemExit(f"Output already exists: {target}")
    rows = [json.loads(line) for line in (source / "dataset_manifest.jsonl").read_text(encoding="utf-8").splitlines()]
    by_id = {row["id"]: row for row in rows}
    missing = INVALID_BICYCLE_IDS - set(by_id)
    if missing:
        raise ValueError(f"Reviewed IDs missing from source: {sorted(missing)}")
    for split in ("train", "val", "test"):
        (target / "images" / split).mkdir(parents=True)
        (target / "labels" / split).mkdir(parents=True)
    corrections = []
    kept = []
    for row in rows:
        stem, split = row["id"], row["split"]
        old_lines = (source / "labels" / split / f"{stem}.txt").read_text(encoding="utf-8").splitlines()
        new_lines = []
        for index, line in enumerate(old_lines):
            class_id = int(line.split()[0])
            if stem in INVALID_BICYCLE_IDS and class_id == 4:
                corrections.append({"id": stem, "split": split, "line_index": index,
                                    "class_id": class_id, "old_label": line,
                                    "reason": "motorcycle_or_scooter_not_pedal_bicycle"})
            else:
                new_lines.append(line)
        shutil.copy2(source / "images" / split / f"{stem}.jpg",
                     target / "images" / split / f"{stem}.jpg")
        (target / "labels" / split / f"{stem}.txt").write_text(
            "\n".join(new_lines) + ("\n" if new_lines else ""), encoding="utf-8")
        kept.append({**row, "class_ids": sorted({int(line.split()[0]) for line in new_lines})})
    if {item["id"] for item in corrections} != INVALID_BICYCLE_IDS:
        raise ValueError("Some reviewed IDs had no bicycle annotation")
    (target / "dataset.yaml").write_text(
        f"path: {target.as_posix()}\ntrain: images/train\nval: images/val\ntest: images/test\nnames:\n" +
        "".join(f"  {index}: {name}\n" for index, name in enumerate(NAMES)), encoding="utf-8")
    (target / "dataset_manifest.jsonl").write_text(
        "".join(json.dumps(row) + "\n" for row in kept), encoding="utf-8")
    report = {"source": str(source), "target": str(target),
              "status": "candidate_partial_semantic_review_not_independent_test",
              "class_policy": "ml/PUBLIC_LABEL_POLICY.md",
              "kept_by_split": dict(Counter(row["split"] for row in kept)),
              "quarantined_images": [], "corrections": corrections,
              "images_with_corrected_boxes": len(INVALID_BICYCLE_IDS),
              "corrected_boxes_by_reason": dict(Counter(item["reason"] for item in corrections))}
    (target / "build_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({key: value for key, value in report.items()
                      if key not in ("corrections", "quarantined_images")}, indent=2))


if __name__ == "__main__":
    main()
