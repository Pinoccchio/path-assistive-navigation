"""Export one row per model-suggested vehicle box for human annotation review."""

import csv
import json

from phase1 import ROOT


RUN = ROOT / "runs" / "public_phase1_v11_reviewed_640_candidate"
SOURCE = ROOT / "data" / "source" / "oi_vehicle_v10"
LEDGERS = (SOURCE / "train_corrections_v12_pilot.json",
           SOURCE / "train_corrections_v13_pilot.json")


def main():
    audit = json.loads((RUN / "train_vehicle_label_audit_queue.json").read_text(encoding="utf-8"))
    ledgers = [json.loads(path.read_text(encoding="utf-8")) for path in LEDGERS]
    rejected_images = {image_id: reason for ledger in ledgers
                       for image_id, reason in ledger["reviewed_without_label_addition"].items()}
    corrected_images = {image_id for ledger in ledgers for image_id in ledger["add_boxes"]}
    path = RUN / "train_box_proposals_for_review.csv"
    count = 0
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(("image_id", "proposal_index", "suggested_class", "confidence", "x1", "y1", "x2", "y2",
                         "review_status", "review_note", "source_image"))
        for row in audit["rows"]:
            image_id = row["image_id"]
            for index, proposal in enumerate(row["unmatched_predictions"]):
                status = "pending_full_resolution_review"
                note = "Model suggestion only; verify class, complete object extent, and duplicate source boxes."
                if image_id in rejected_images:
                    status = "reviewed_image_do_not_auto_add"
                    note = rejected_images[image_id]
                elif image_id in corrected_images:
                    status = "reviewed_image_see_versioned_ledger"
                    note = "An approved box is recorded in a versioned correction ledger; this model proposal may be a duplicate."
                x1, y1, x2, y2 = proposal["box_xyxy"]
                writer.writerow((image_id, index, "bicycle" if proposal["class_id"] == 4 else "motorcycle",
                                 round(proposal["confidence"], 4), round(x1, 1), round(y1, 1), round(x2, 1), round(y2, 1),
                                 status, note, SOURCE / "images" / "train" / f"{image_id}.jpg"))
                count += 1
    print(json.dumps({"images": len(audit["rows"]), "proposal_boxes": count, "csv": str(path)}, indent=2))


if __name__ == "__main__":
    main()
