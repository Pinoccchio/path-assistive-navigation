"""Freeze full-resolution stair review proposals with source hashes; edit no labels."""

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/processed/public_phase1_v11_reviewed_640_candidate"
OUT = ROOT / "runs/public_phase1_v11_reviewed_640_candidate/stair_review_proposals_v1.json"

# Visual triage from contact sheets, with a subset also opened at source
# resolution, 2026-10-04. A proposal is not an accepted annotation.
REVIEW = [
    ("train", "openimagesv7_train_5a08b0bfc03b87a9", "quarantine_for_rebox",
     "Both boxes cover fountain ledges while the walkable side stairs are unboxed."),
    ("train", "openimagesv7_train_9510399b9adc7dcd", "review_flight_boundary",
     "Two staircase flights may be separated by a landing; assess the current lower box geometry."),
    ("train", "rod_train_IMG_18372", "quarantine_for_identity_review",
     "Low exterior steps or curb around a utility cover; staircase identity is ambiguous."),
    ("train", "pilot_train_IMG_09074", "remove_duplicate_rebox_remaining",
     "One stair box spans nearly the full image and duplicates a tighter box."),
    ("train", "pilot_train_IMG_09075", "merge_or_rebox",
     "Two boxes overlap one descending flight and one extends onto foreground pavement."),
    ("train", "pilot_train_IMG_09199", "review_landing_box",
     "One box covers the visible flight; a second appears to cover the landing."),
    ("train", "pilot_train_IMG_09245", "review_landing_box",
     "One box covers the visible flight; a second appears to cover the landing."),
    ("train", "pilot_train_IMG_09282", "review_landing_box",
     "One box covers the near flight; a second appears to cover the far landing."),
    ("train", "pilot_train_IMG_09338", "merge_or_rebox",
     "Boxes overlap a continuous flight and landing; boundaries need a single consistent policy."),
    ("val", "openimagesv7_validation_8eb32c27fcb2dd3e", "review_non_stair_box",
     "One small box appears to cover a railing/post beside the real stair segment."),
    ("test", "rod_test_IMG_19846", "review_frozen_test_geometry",
     "Two boxes appear to split one continuous staircase; do not silently alter test labels."),
    ("test", "rod_test_IMG_19857", "review_frozen_test_geometry",
     "Two boxes appear to split one continuous staircase; do not silently alter test labels."),
]


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    rows = []
    for split, image_id, proposal, reason in REVIEW:
        image = DATA / "images" / split / f"{image_id}.jpg"
        label = DATA / "labels" / split / f"{image_id}.txt"
        assert image.exists() and label.exists(), (image, label)
        boxes = [line for line in label.read_text(encoding="utf-8").splitlines()
                 if line.strip() and line.split()[0] == "2"]
        assert len(boxes) >= 2, image_id
        rows.append({"split": split, "id": image_id,
                     "image_sha256": sha256(image), "label_sha256": sha256(label),
                     "current_stair_lines": boxes, "proposal": proposal,
                     "reason": reason, "status": "visual_triage_only"})
    OUT.write_text(json.dumps({"review_date": "2026-10-04", "rows": rows,
                               "limitations": "No labels changed or approved; review source-resolution boxes and independent-source evaluation before training."},
                              indent=2), encoding="utf-8")
    print(f"Saved {len(rows)} hash-locked proposals to {OUT}")


if __name__ == "__main__":
    main()
