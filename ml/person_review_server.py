"""Local-only review UI for v16 person drafts. Never modifies training labels."""

import csv
import hashlib
import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from phase1 import ROOT

RUN = ROOT / "runs/public_phase1_v15_oi_quarantine/person_draft_960"
SOURCE = ROOT / "data/processed/public_phase1_v15_oi_quarantine/images/train"
REVIEW = RUN / "human_reviews"
UI = ROOT / "ml/person_review_ui.html"
PRIORITY = ROOT / "runs/public_phase1_v15_oi_quarantine/person_annotation_priority_v18.csv"
MAX_BODY = 1024 * 1024


def draft_rows():
    return {row["image_id"]: row for row in json.loads((RUN / "draft_v18_179.json").read_text(encoding="utf-8"))["rows"]}


def validate_review(payload, draft):
    if not isinstance(payload, dict) or payload.get("image_id") != draft["image_id"]:
        raise ValueError("Image ID mismatch")
    if payload.get("image_sha256") != draft["image_sha256"]:
        raise ValueError("Source image hash mismatch")
    if payload.get("status") not in ("in_progress", "first_review_complete", "second_review_complete"):
        raise ValueError("Invalid review status")
    if not isinstance(payload.get("boxes"), list):
        raise ValueError("boxes must be an array")
    if not isinstance(payload.get("reviewer"), str) or len(payload["reviewer"].strip()) < 2:
        raise ValueError("Reviewer name is required")
    if not isinstance(payload.get("notes", ""), str) or len(payload["reviewer"]) > 100 or len(payload.get("notes", "")) > 2000:
        raise ValueError("Reviewer or notes too long")
    if payload["status"] != "in_progress" and not payload.get("all_visible_people_checked"):
        raise ValueError("Confirm all visible people were checked before completion")
    if payload["status"] != "in_progress" and not payload["boxes"]:
        raise ValueError("At least one visible person must have a box")
    if payload["status"] == "second_review_complete":
        if not isinstance(payload.get("second_reviewer"), str) or len(payload["second_reviewer"].strip()) < 2:
            raise ValueError("Second reviewer name is required")
        if payload["second_reviewer"].strip().casefold() == payload["reviewer"].strip().casefold():
            raise ValueError("Second reviewer must differ from first reviewer")
    for box in payload["boxes"]:
        if not isinstance(box, list) or len(box) != 4 or not all(isinstance(v, (int, float)) for v in box):
            raise ValueError("Each box must be four numeric pixel coordinates")
        x1, y1, x2, y2 = box
        if not (0 <= x1 < x2 <= draft["width"] and 0 <= y1 < y2 <= draft["height"]):
            raise ValueError("Box outside source image")
    return {"image_id": draft["image_id"], "image_sha256": draft["image_sha256"],
            "width": draft["width"], "height": draft["height"],
            "status": payload["status"], "reviewer": payload["reviewer"].strip(),
            "second_reviewer": payload.get("second_reviewer", "").strip(),
            "all_visible_people_checked": bool(payload.get("all_visible_people_checked")),
            "vehicle_completeness_checked": bool(payload.get("vehicle_completeness_checked")),
            "notes": payload.get("notes", ""), "boxes": payload["boxes"]}


class Handler(BaseHTTPRequestHandler):
    def send(self, code, body, content_type="application/json"):
        data = body if isinstance(body, bytes) else body.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        path = urlparse(self.path).path
        rows = draft_rows()
        if path == "/":
            return self.send(200, UI.read_bytes(), "text/html; charset=utf-8")
        if path == "/api/images":
            items = []
            with PRIORITY.open(newline="", encoding="utf-8") as handle:
                priority_ids = [row["image_id"] for row in csv.DictReader(handle)]
            if set(priority_ids) != set(rows):
                return self.send(409, json.dumps({"error": "Priority queue differs from draft"}))
            for image_id in priority_ids:
                row = rows[image_id]
                review_path = REVIEW / f"{row['image_id']}.json"
                status = json.loads(review_path.read_text(encoding="utf-8"))["status"] if review_path.exists() else "not_started"
                items.append({"image_id": row["image_id"], "status": status,
                              "draft_boxes": len(row["proposals"]),
                              "source_person_boxes": row.get("source_person_boxes", 0)})
            return self.send(200, json.dumps(items))
        parts = path.strip("/").split("/")
        if len(parts) == 3 and parts[:2] == ["api", "image"] and parts[2] in rows:
            image_id = parts[2]
            image = SOURCE / f"oi_v10_train_{image_id}.jpg"
            if hashlib.sha256(image.read_bytes()).hexdigest() != rows[image_id]["image_sha256"]:
                return self.send(409, json.dumps({"error": "Source image hash changed"}))
            return self.send(200, image.read_bytes(), "image/jpeg")
        if len(parts) == 3 and parts[:2] == ["api", "review"] and parts[2] in rows:
            row = rows[parts[2]]
            review_path = REVIEW / f"{row['image_id']}.json"
            if review_path.exists():
                payload = json.loads(review_path.read_text(encoding="utf-8"))
            else:
                payload = {"image_id": row["image_id"], "image_sha256": row["image_sha256"],
                           "width": row["width"], "height": row["height"], "status": "in_progress",
                           "reviewer": "", "second_reviewer": "", "all_visible_people_checked": False,
                           "vehicle_completeness_checked": False, "notes": "",
                           "boxes": [p["xyxy_pixels"] for p in row["proposals"]]}
            return self.send(200, json.dumps(payload))
        return self.send(404, json.dumps({"error": "Not found"}))

    def do_POST(self):
        path = urlparse(self.path).path
        parts = path.strip("/").split("/")
        rows = draft_rows()
        if len(parts) != 3 or parts[:2] != ["api", "review"] or parts[2] not in rows:
            return self.send(404, json.dumps({"error": "Not found"}))
        try:
            size = int(self.headers.get("Content-Length", "0"))
            if not 0 < size <= MAX_BODY:
                raise ValueError("Invalid request size")
            payload = json.loads(self.rfile.read(size))
            review = validate_review(payload, rows[parts[2]])
            image = SOURCE / f"oi_v10_train_{parts[2]}.jpg"
            if hashlib.sha256(image.read_bytes()).hexdigest() != review["image_sha256"]:
                raise ValueError("Source image hash changed")
            REVIEW.mkdir(parents=True, exist_ok=True)
            dest = REVIEW / f"{parts[2]}.json"
            if dest.exists():
                previous = json.loads(dest.read_text(encoding="utf-8"))
                if previous["status"] == "second_review_complete":
                    raise ValueError("Finalized review is locked")
            else:
                previous = None
            if review["status"] == "second_review_complete":
                if previous is None or previous["status"] != "first_review_complete":
                    raise ValueError("Save the first review before second review")
                if previous["reviewer"] != review["reviewer"]:
                    raise ValueError("First reviewer identity cannot change during second review")
            temp = dest.with_suffix(".tmp")
            temp.write_text(json.dumps(review, indent=2) + "\n", encoding="utf-8")
            os.replace(temp, dest)
            return self.send(200, json.dumps({"saved": True, "status": review["status"]}))
        except (ValueError, KeyError, TypeError, json.JSONDecodeError) as error:
            return self.send(400, json.dumps({"error": str(error)}))


def main():
    if not RUN.joinpath("draft_v18_179.json").exists():
        raise SystemExit("Generate person draft first")
    server = ThreadingHTTPServer(("127.0.0.1", 8765), Handler)
    print("Open http://127.0.0.1:8765/ for local-only review")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
