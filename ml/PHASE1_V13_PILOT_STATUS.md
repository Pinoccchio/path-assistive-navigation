# V13 four-box annotation pilot

V13 extends the [v12 two-box pilot](PHASE1_V12_PILOT_STATUS.md) with two more full-resolution, visually verified **training** bicycle boxes. The [v13 correction ledger](../data/source/oi_vehicle_v10/train_corrections_v13_pilot.json) records:

| Image ID | Additional box | Visual finding |
| --- | --- | --- |
| `8dfef66be8e71bd6` | Clipped bicycle at the left edge of a street scene | Existing boxes cover different bicycles. |
| `627931ae6e6b7e3c` | Background cyclist's bicycle | Neighboring bicycles had source boxes; this distinct bicycle did not. |

The same review rejected five high-confidence wrong-class proposals, including a pedal bicycle predicted as a motorcycle and several motorcycles predicted as bicycles. The [review CSV](../runs/public_phase1_v11_reviewed_640_candidate/train_box_proposals_for_review.csv) now tracks **80 pending proposals**, five proposals on corrected images, and eight on rejected images. A proposal's status is at the image level; the approved box geometry is in the versioned ledger.

The [v13 dataset](../data/processed/public_phase1_v13_four_box_pilot/dataset.yaml) remains an **annotation pilot, not a trained model**. Its [build report](../data/processed/public_phase1_v13_four_box_pilot/build_report.json) records two additions over v12, four cumulative additions over v11. [Byte-level QA](../data/processed/public_phase1_v13_four_box_pilot/qa_report.json) confirmed exactly two v12-to-v13 training label changes, 4,173 unchanged images, and unchanged validation/test labels. The [new-box overlay](../data/processed/public_phase1_v13_four_box_pilot/correction_review.jpg) was visually inspected after build.

Do not retrain on four corrections while most flagged and unflagged Open Images instances remain unreviewed. Continue full-resolution instance annotation, recording exact approved boxes and explicit rejected proposals. New rights-reviewed distant-vehicle data and an independent-source locked test come after this cleanup. Campus collection remains deferred.
