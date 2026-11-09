"""Save five AI visual-triage drafts as in-progress, never as human-complete."""

import hashlib
import json
from pathlib import Path

from person_review_server import REVIEW, SOURCE, draft_rows, validate_review


# Box coordinates were checked against the full-resolution images and proposal
# overlays. These remain provisional; the human reviewer must inspect the
# entire image, person instances, and vehicle completeness before completion.
PILOT = {
    "1271622877a21c47": {
        "boxes": [[487.8, 418.7, 539.4, 536.9]],
        "notes": "AI triage: one visible cyclist; person proposal plausible. Small red car appears unboxed under project car policy; review vehicle labels. Human full-image review required.",
    },
    "17d51251e2ce55f0": {
        "boxes": [[23.5, 32.0, 683.0, 1024.0]],
        "notes": "AI triage: one rider. Original draft ended above visible lower leg; extended to image bottom. Tightness/occlusion needs human adjustment; check motorcycle label.",
    },
    "5da1151716ece103": {
        "boxes": [[425.8, 186.7, 770.0, 452.3]],
        "notes": "AI triage: one person beside motorcycle; widened right edge to include visible hand. Human full-image and motorcycle-box review required.",
    },
    "654c3cb2305ea843": {
        "boxes": [[340.0, 136.4, 660.1, 455.0]],
        "notes": "AI triage: one person; extended box toward visible hand/leg. Two motorcycles appear visible but source has one motorcycle box; vehicle completeness unresolved.",
    },
    "69880732bf53c286": {
        "boxes": [[218.1, 21.4, 592.9, 671.2]],
        "notes": "AI triage: one rider; draft person box plausible. Human full-image and motorcycle-box review required.",
    },
}


def main():
    drafts = draft_rows()
    REVIEW.mkdir(parents=True, exist_ok=True)
    saved = []
    for image_id, item in PILOT.items():
        draft = drafts[image_id]
        assert draft.get("source_person_boxes", 0) == 0
        assert len(draft["proposals"]) == 1
        image = SOURCE / f"oi_v10_train_{image_id}.jpg"
        assert hashlib.sha256(image.read_bytes()).hexdigest() == draft["image_sha256"]
        dest = REVIEW / f"{image_id}.json"
        if dest.exists():
            raise FileExistsError(f"Existing review must be preserved: {dest}")
        payload = {"image_id": image_id, "image_sha256": draft["image_sha256"],
                   "status": "in_progress", "reviewer": "Codex AI visual triage",
                   "second_reviewer": "", "all_visible_people_checked": False,
                   "vehicle_completeness_checked": False,
                   "notes": item["notes"], "boxes": item["boxes"]}
        review = validate_review(payload, draft)
        dest.write_text(json.dumps(review, indent=2) + "\n", encoding="utf-8")
        saved.append(image_id)
    print(json.dumps({"saved_in_progress": saved, "human_complete": 0,
                      "ready_for_training": 0}, indent=2))


if __name__ == "__main__":
    main()
