# Local person-annotation review

The [v16 audit](PHASE1_V16_PERSON_LABEL_STATUS.md) found 109 Open Images train photos with visible people and zero person labels. A [second 960 px audit](PHASE1_V17_PERSON_AUDIT_STATUS.md) visually confirmed 11 more. A [partial-label audit](PHASE1_V18_PARTIAL_PERSON_AUDIT_STATUS.md) added 59 photos with some existing person labels but unmatched proposals. The review backlog now contains **179 photos**: 120 confirmed zero-person-label images and 59 partial-label review candidates. The [combined review draft](../runs/public_phase1_v15_oi_quarantine/person_draft_960/draft_v18_179.json) includes source person boxes as editable starting boxes and model proposals for inspection. Spot checks found duplicates, partial boxes, false positives, and missed people.

Run the local reviewer from the thesis workspace:

```powershell
.\.venv\Scripts\python.exe ml/person_review_server.py
```

Open `http://127.0.0.1:8765/`. It binds only to localhost. A desktop or laptop screen is recommended for precise box work; the narrow-screen layout is usable for inspection. The list follows the [vehicle-value priority queue](../runs/public_phase1_v15_oi_quarantine/person_annotation_priority_v18.csv). For each photo, compare the full image with all red boxes; the page shows how many started as source person labels. Click a box to select it; use **Move**, **Resize corner**, or **Delete selected** to correct drafts. Use **Draw box** to add every missed visible person, including partial and small people. Check bicycle/motorcycle completeness in the source photo too, and record unresolved cases in Notes. Save as **First review complete** only after checking the whole photo. A different reviewer should inspect every box and missed person before saving **Second review complete**. Finalized reviews lock against editing; if a correction is later needed, preserve the review file and create a documented revision rather than silently overwriting it.

Progress saves as one JSON file per image under `runs/public_phase1_v15_oi_quarantine/person_draft_960/human_reviews/`. The original images, v15/v16 datasets, and proposal JSON stay unchanged. To check review integrity and readiness:

```powershell
.\.venv\Scripts\python.exe ml/qa_v16_human_reviews.py
```

Its [progress report](../runs/public_phase1_v15_oi_quarantine/person_draft_960/human_review_progress.json) counts images ready for a corrected dataset only after second review and vehicle-completeness confirmation. A future builder must validate the accepted coordinates against each image hash, create a new immutable dataset version, and keep validation/test unchanged. Do not use draft proposals or first-pass reviews directly for training.
