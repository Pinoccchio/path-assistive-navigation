# Person annotation pilot, 2026-10-04

Five low-complexity images from the 179-image v18 queue were opened at full resolution and checked against [rendered proposal overlays](../runs/public_phase1_v15_oi_quarantine/person_draft_960/pilot_review_overlays). The AI-assisted drafts were saved under `runs/public_phase1_v15_oi_quarantine/person_draft_960/human_reviews/` with `status=in_progress`, `reviewer=Codex AI visual triage`, and both `all_visible_people_checked` and `vehicle_completeness_checked` set to false. They are **not completed human annotations** and cannot enter training.

| Image ID | Visual finding / saved draft |
| --- | --- |
| `1271622877a21c47` | One cyclist; person proposal retained. A distant red car appears visible but the source label has no car box. |
| `17d51251e2ce55f0` | One rider; proposed person box ended above a visible leg, so the in-progress box extends to the lower image edge. Tightness requires review. |
| `5da1151716ece103` | One person beside a motorcycle; widened the in-progress box slightly to include the visible right hand. |
| `654c3cb2305ea843` | One person; extended the in-progress box toward visible hand/leg. Two motorcycles appear visible while the source label contains one motorcycle box. |
| `69880732bf53c286` | One rider; person proposal retained for human review. |

`ml/save_person_review_pilot_drafts.py` validates each source-image hash and the review payload before writing; it refuses to overwrite existing reviews. The [review integrity report](../runs/public_phase1_v15_oi_quarantine/person_draft_960/human_review_progress.json) now shows **5 in progress, 174 not started, 0 ready**, with no invalid or unexpected review files. No source labels, test labels, model weights, or app files were changed.

Next: a human reviewer must inspect each entire image and correct the saved boxes, then a different reviewer must check person and vehicle completeness. The remaining queue can be processed in prioritized batches. Do not equate an AI triage draft with human-reviewed ground truth.
