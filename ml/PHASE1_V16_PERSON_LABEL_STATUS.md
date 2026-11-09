# V16 person-label audit and training decision

The latest trained checkpoint remains **v11**. It is a research candidate, not cleared for the Flutter app. V15 and v16 are dataset-only quality experiments. No campus data was collected or used.

The [person audit queue](../runs/public_phase1_v15_oi_quarantine/person_label_audit_queue.json) used the original COCO-pretrained YOLOv8n only to find review candidates among 283 newly selected Open Images training images retained in v15. At 512 px and confidence 0.5, it flagged 130 images and 466 candidate person boxes. Of these, 109 images have zero person boxes in the training labels. All 28 [zero-person-label contact sheets](../runs/public_phase1_v15_oi_quarantine/person_zero_gt_sheets) were visually reviewed at image level; each of the 109 images visibly contains at least one person. Candidate detections are **not** accepted ground truth, and person instances have not been exhaustively annotated.

The [v16 exclusion ledger](../data/source/oi_vehicle_v10/train_quarantine_v16_person.json) records these 109 image IDs, image and label hashes, and the review reason. The [v16 build](build_v16_person_quarantine.py) removes only those train rows, preserving the v15 source, all originals, and all validation/test samples. [QA](../data/processed/public_phase1_v16_person_quarantine/qa_report.json) verified that all 4,057 retained image/label pairs are byte-identical to v15. The splits are 3,186 train, 251 validation, and 620 test.

The [raw-source audit](../runs/public_phase1_v15_oi_quarantine/source_person_row_audit.json) checked the original Open Images train-box CSV: 107 of the 109 images have no person row at all; the other two have only a `IsGroupOf=1` person row excluded by the existing individual-box policy. There are no individual source boxes to restore. A [higher-resolution draft](../runs/public_phase1_v15_oi_quarantine/person_draft_960/draft.json) generated 1,057 candidate boxes at 960 px/confidence 0.15, with [28 overlay sheets](../runs/public_phase1_v15_oi_quarantine/person_draft_960) for correction. Visual spot checks of sheets 01 and 14 show duplicate/partial boxes and missed people. These proposals remain **unverified** and must not enter training labels directly.

| Class | V15 train boxes | V16 train boxes | Lost |
| --- | ---: | ---: | ---: |
| Bicycle | 1,339 | 1,057 | 282 (21.1%) |
| Motorcycle | 757 | 631 | 126 (16.6%) |
| Car | 1,728 | 1,716 | 12 (0.7%) |
| Person | 4,167 | 4,167 | 0 labeled boxes; missing boxes remain unresolved |

**Decision:** Do not train or promote v16 as the corrected dataset. Quarantining all 109 images prevents those known missing-person labels from teaching background, but discards too many target vehicle examples. V16 is a reversible control. The [prioritized annotation queue](../runs/public_phase1_v15_oi_quarantine/person_annotation_priority.csv) gives source paths, review sheet/slot, and existing vehicle counts for all 109 images. Prioritize exhaustive person annotation, starting with images carrying bicycle/motorcycle boxes; review bicycle and motorcycle completeness in the same pass. Record accepted boxes with image hashes, a second visual QA pass, and immutable val/test. Then build a new version retaining corrected images and train it from the same initial weights/settings as v11. Compare per-class recall, precision, false alerts, and small-object cases on the unchanged development set; use a separately locked, visually verified holdout before choosing a model for the app.

The remaining 21 model-flagged images with some existing person boxes also need instance-level review. The 153 unflagged new Open Images images have not been certified complete. These limits prevent an accuracy or deployment claim for v15/v16.

The [local annotation reviewer](PERSON_ANNOTATION_REVIEW.md) supports per-image box correction, saved progress, and separate first/second reviewer gates. Its [progress QA](../runs/public_phase1_v15_oi_quarantine/person_draft_960/human_review_progress.json) reports the current backlog. This is an annotation tool, not a new trained model.
The [subsequent v17 audit](PHASE1_V17_PERSON_AUDIT_STATUS.md) confirmed 11 additional missing-person-label images and expanded the review backlog to 120. The v16 quarantine itself remains frozen at the original 109 exclusions.
