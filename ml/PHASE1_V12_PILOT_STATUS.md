# V12 two-box annotation pilot

This is an **annotation workflow pilot, not a trained model or release candidate**. The [correction ledger](../data/source/oi_vehicle_v10/train_corrections_v12_pilot.json) records two full-resolution visual approvals on Open Images training images:

| Image ID | Approved addition | Why |
| --- | --- | --- |
| `fc39516ed15ec5ba` | One small pedal-bicycle box at the far-left edge | The visible bicycle was missing from the source boxes. |
| `b8de9ce8cb2f4d94` | One parked-motorcycle box beside a cycling race | The motorcycle was visible but the source image only boxed bicycles/persons. |

The ledger also rejects two model proposals: a stroller misclassified as a bicycle in `fcd2173e996fee72`, and a hot-rod car misclassified as a motorcycle in `22502af39e25fe90`. These examples show why the remaining model-suggested boxes cannot be imported automatically.

The [isolated v12 dataset copy](../data/processed/public_phase1_v12_two_box_pilot/dataset.yaml) has 3,302 train, 251 validation, and 620 test images. Its [build report](../data/processed/public_phase1_v12_two_box_pilot/build_report.json) records exactly two added **training** boxes. The [byte-level QA report](../data/processed/public_phase1_v12_two_box_pilot/qa_report.json) verified that all 4,173 image files match v11 and that exactly two training label files changed; validation and test labels are unchanged. The [visual QA overlay](../data/processed/public_phase1_v12_two_box_pilot/correction_review.jpg) was inspected after the build. V11 source data and checkpoint remain intact.

Do **not** retrain yet. Two corrections cannot resolve the [40-image training review queue](../runs/public_phase1_v11_reviewed_640_candidate/train_vehicle_label_audit_queue.csv), let alone unflagged instances the model never predicted. The [proposal-level review CSV](../runs/public_phase1_v11_reviewed_640_candidate/train_box_proposals_for_review.csv) contains 93 model suggestions: 89 still pending full-resolution review, two tied to this pilot's approved images, and two from visually rejected images. Complete full-resolution, instance-by-instance adjudication of the flagged images and sample the other 250 retained Open Images images. Add only confirmed boxes to a new versioned ledger and rebuild under a new dataset name. If the corrected training set still misses 12–40px bicycles, collect targeted rights-reviewed training data from a different source and lock a new independent-source test before tuning.

Reproduce the current pilot from v11 with `ml/build_v12_vehicle_label_pilot.py`; run `ml/qa_v12_vehicle_label_pilot.py` afterward. The builder preserves old data and refuses to overwrite an existing v12 build; the QA script refreshes its report and overlay inside that build.
