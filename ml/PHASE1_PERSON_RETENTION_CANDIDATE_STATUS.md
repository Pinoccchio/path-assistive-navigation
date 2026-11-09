# Person-retention retrain diagnostic, 2026-10-04

The 12-epoch YOLOv8n training run completed and produced [best.pt](../runs/public_phase1_person_retention_candidate/yolov8n_local/weights/best.pt) (SHA-256 `4271b0279c9f4017c75d667b805db1a20020a2e6d49d969ef9b73cf13a1cfa2b`). This is a research checkpoint, **not an app-ready navigation model**.

The [versioned candidate dataset](../data/processed/public_phase1_person_retention_candidate/build_report.json) contains 3,008 training, 251 validation, and 620 test images. Compared with v11, it excludes all 290 newly added, incompletely reviewed Open Images training images and four ambiguous stair images; four other training stair labels use the reviewed overlay. Validation and test image/label bytes are unchanged. The run reused v11's initial COCO YOLOv8n weights and 12-epoch, 640-pixel, batch-4, seed-42 recipe on an RTX 3050 Laptop GPU. [Environment metadata](../runs/public_phase1_person_retention_candidate/environment.json) and the training `results.csv` are saved with the run. The first launch failed before training because optional WandB interpreted the Windows project path as an invalid project name; the completed `yolov8n_local` retry disabled optional remote loggers for that process.

On the **same reused 620-image public development test**, at 512 pixels, confidence 0.25, and one-to-one IoU 0.5 box matching:

| Label | Labeled boxes | v11 matched | Candidate matched | Change |
| --- | ---: | ---: | ---: | ---: |
| Person | 510 | 246 | 317 | +71 |
| Chair | 168 | 125 | 138 | +13 |
| Car | 253 | 189 | 192 | +3 |
| Bicycle | 95 | 75 | 70 | -5 |
| Motorcycle | 90 | 48 | 42 | -6 |
| Stairs | 122 | 98 | 101 | +3 |

The small-bicycle slice fell from 10/48 to 9/48 matched boxes. Full [five-class paired report](../runs/public_phase1_person_retention_candidate/paired_public_diagnostic_512.json) and [stair report](../runs/public_phase1_person_retention_candidate/stair_public_diagnostic_512.json) include image-level results. The original COCO-pretrained model had 372/510 person matches on this same set, so the candidate still trails it for person alone. Box matches are diagnostic counts, not field recall or navigation accuracy; source labels can omit visible objects. The three dataset changes happened together, so this run cannot isolate which change caused each difference.

**Decision:** retain v11 and the person-retention checkpoint as separate research candidates. Do not replace the app model or combine their predictions yet. Person improved, but bicycle and motorcycle worsened and small bicycles remain a clear weakness. Human completion of the 179-image person review queue, source-complete labels, a genuinely held-out source test, and physical-device latency/alert QA remain necessary before model selection. Campus collection remains deferred as requested; independent non-campus evaluation can be prepared without calling this set independent.
