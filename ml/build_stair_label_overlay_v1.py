"""Create a small, reversible stair-label correction overlay from reviewed sources.

This does not modify the v11 dataset. Future candidate builders may opt into
the overlay and quarantine list after review of the exact manifest.
"""

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data/processed/public_phase1_v11_reviewed_640_candidate"
LEDGER = ROOT / "runs/public_phase1_v11_reviewed_640_candidate/stair_review_proposals_v1.json"
OUT = ROOT / "data/processed/stair_label_overlay_v1"

# Zero-based line index to remove from each two-box training label. The retained
# line was visually checked against the full-resolution staircase image.
CORRECTIONS = {
    "pilot_train_IMG_09074": (1, "Remove near-full-image duplicate box; retain upper/visible flight box."),
    "pilot_train_IMG_09199": (1, "Remove landing-only box; retain the visible descending-flight box."),
    "pilot_train_IMG_09245": (1, "Remove landing-only box; retain the visible descending-flight box."),
    "pilot_train_IMG_09282": (1, "Remove landing-only box; retain the near descending-flight box."),
}

# These images still show stair-label ambiguity or missing stair boxes. Exclude
# them only in a future candidate; the original v11 dataset stays unchanged.
QUARANTINE = {
    "openimagesv7_train_5a08b0bfc03b87a9": "Fountain ledges boxed as stairs while true side stairs are not boxed.",
    "rod_train_IMG_18372": "Low exterior steps/curb identity remains ambiguous.",
    "pilot_train_IMG_09075": "Overlapping boxes span one descending flight and foreground; needs reboxing.",
    "pilot_train_IMG_09338": "Overlapping boxes cover stairs and landing; needs reboxing.",
}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    ledger = json.loads(LEDGER.read_text(encoding="utf-8"))
    indexed = {(row["split"], row["id"]): row for row in ledger["rows"]}
    output_rows = []
    for image_id, (remove_index, reason) in CORRECTIONS.items():
        row = indexed[("train", image_id)]
        image = SOURCE / "images/train" / f"{image_id}.jpg"
        label = SOURCE / "labels/train" / f"{image_id}.txt"
        assert digest(image) == row["image_sha256"]
        assert digest(label) == row["label_sha256"]
        lines = [line for line in label.read_text(encoding="utf-8").splitlines() if line.strip()]
        assert lines == row["current_stair_lines"] and len(lines) == 2
        assert 0 <= remove_index < len(lines)
        kept = [line for index, line in enumerate(lines) if index != remove_index]
        target = OUT / "labels/train" / f"{image_id}.txt"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("\n".join(kept) + "\n", encoding="utf-8")
        assert len(kept) == 1 and kept[0].startswith("2 ")
        output_rows.append({"id": image_id, "source_image_sha256": row["image_sha256"],
                            "source_label_sha256": row["label_sha256"],
                            "overlay_label_sha256": digest(target),
                            "removed_line": lines[remove_index],
                            "retained_line": kept[0], "reason": reason})
    quarantine_rows = []
    for image_id, reason in QUARANTINE.items():
        row = indexed[("train", image_id)]
        image = SOURCE / "images/train" / f"{image_id}.jpg"
        label = SOURCE / "labels/train" / f"{image_id}.txt"
        assert digest(image) == row["image_sha256"]
        assert digest(label) == row["label_sha256"]
        quarantine_rows.append({"id": image_id, "image_sha256": row["image_sha256"],
                                "label_sha256": row["label_sha256"], "reason": reason})
    manifest = {"source_dataset": str(SOURCE), "status": "candidate_overlay_not_trained",
                "corrected_train_labels": output_rows,
                "quarantine_train_images": quarantine_rows,
                "validation_or_test_edits": 0,
                "remaining_gates": ["second visual review of corrections",
                                    "complete person and vehicle instance review",
                                    "independent-source evaluation before model selection"]}
    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"Overlay: {len(output_rows)} corrected training labels, "
          f"{len(quarantine_rows)} proposed train quarantines, zero val/test edits")


if __name__ == "__main__":
    main()
