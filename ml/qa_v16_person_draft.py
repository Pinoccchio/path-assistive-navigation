"""Structural QA for draft proposals; does not certify semantic accuracy."""

import hashlib
import json

from build_v16_person_quarantine import LEDGER, ROOT, SOURCE

OUT = ROOT / "runs/public_phase1_v15_oi_quarantine/person_draft_960"


def main():
    expected = set(json.loads(LEDGER.read_text(encoding="utf-8"))["excluded"])
    report = json.loads((OUT / "draft.json").read_text(encoding="utf-8"))
    rows = report["rows"]
    assert len(rows) == len(expected) == 109
    assert {row["image_id"] for row in rows} == expected
    assert report["proposals"] == sum(len(row["proposals"]) for row in rows)
    assert report["model_sha256"] == hashlib.sha256((ROOT / "notebooks/yolov8n.pt").read_bytes()).hexdigest()
    for row in rows:
        image = SOURCE / "images/train" / f"oi_v10_train_{row['image_id']}.jpg"
        assert hashlib.sha256(image.read_bytes()).hexdigest() == row["image_sha256"]
        assert row["review_status"] == "unverified_draft"
        for proposal in row["proposals"]:
            x1, y1, x2, y2 = proposal["xyxy_pixels"]
            assert 0 <= x1 < x2 <= row["width"] and 0 <= y1 < y2 <= row["height"]
            assert 0 <= proposal["confidence"] <= 1
            xc, yc, w, h = proposal["yolo_normalized"]
            assert all(0 <= value <= 1 for value in (xc, yc, w, h))
    index = json.loads((OUT / "index.json").read_text(encoding="utf-8"))
    assert {row["image_id"] for row in index} == expected
    assert all((OUT / row["sheet"]).exists() for row in index)
    result = {"images_verified": len(rows), "draft_boxes_geometry_checked": report["proposals"],
              "review_sheets": len({row["sheet"] for row in index}),
              "semantic_qa": "not performed; proposals must be manually corrected"}
    (OUT / "qa_report.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
