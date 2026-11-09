"""Record visually confirmed pole-label mismatches without changing v3."""

import csv

from phase1 import ROOT


DATASET = ROOT / "data" / "processed" / "public_phase1_v3_screened"
CONFIRMED_CROSSING_POSTS = {
    "rod_test_IMG_20089", "rod_test_IMG_20091", "rod_test_IMG_20626",
    "rod_validation_IMG_23956",
    "rod_train_IMG_10618", "rod_train_IMG_10620", "rod_train_IMG_10633",
    "rod_train_IMG_10642", "rod_train_IMG_10645", "rod_train_IMG_17819",
    "rod_train_IMG_17842", "rod_train_IMG_17849", "rod_train_IMG_17851",
    "pilot_train_IMG_10613", "pilot_train_IMG_10623", "pilot_train_IMG_10625",
    "pilot_train_IMG_10643", "pilot_train_IMG_10648", "pilot_train_IMG_17817",
    "pilot_train_IMG_17821", "pilot_train_IMG_17823", "pilot_train_IMG_17840",
    "pilot_train_IMG_17846", "pilot_val_IMG_22677",
}


def main():
    with (DATASET / "semantic_review_queue.csv").open(newline="", encoding="utf-8") as file:
        rows = [row for row in csv.DictReader(file) if "electrical_pole" in row["classes"]]
    ids = {row["id"] for row in rows}
    if missing := CONFIRMED_CROSSING_POSTS - ids:
        raise ValueError(f"Review IDs missing from v3: {sorted(missing)}")
    target = DATASET / "pole_review_ledger.csv"
    with target.open("w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(("id", "split", "image_path", "review_status", "visual_finding",
                         "proposed_action", "notes"))
        for row in rows:
            mismatch = row["id"] in CONFIRMED_CROSSING_POSTS
            writer.writerow((row["id"], row["split"], row["image_path"],
                             "reviewed" if mismatch else "needs_closer_review",
                             "pedestrian_crossing_button_post" if mismatch else "",
                             "remove_electrical_pole_boxes_in_next_version" if mismatch else "",
                             "Crossing-button post is outside the utility/electrical-pole class; retain other object labels."
                             if mismatch else "Inspect image and box before accepting its class and geometry."))
    print(f"{target}: {len(rows)} images, {len(CONFIRMED_CROSSING_POSTS)} proposed corrections")


if __name__ == "__main__":
    main()
