"""Validation checks for the local human-annotation gate."""

import unittest
import json
import threading
from http.server import ThreadingHTTPServer
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from person_review_server import Handler, draft_rows, validate_review


class ReviewValidationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.draft = next(iter(draft_rows().values()))

    def review(self):
        d = self.draft
        return {"image_id": d["image_id"], "image_sha256": d["image_sha256"],
                "status": "first_review_complete", "reviewer": "Reviewer A",
                "second_reviewer": "", "all_visible_people_checked": True,
                "vehicle_completeness_checked": False, "notes": "Checked full image",
                "boxes": [[0, 0, 20, 20]]}

    def test_valid_first_review(self):
        result = validate_review(self.review(), self.draft)
        self.assertEqual(result["status"], "first_review_complete")
        self.assertEqual(result["boxes"], [[0, 0, 20, 20]])

    def test_hash_mismatch_rejected(self):
        row = self.review()
        row["image_sha256"] = "wrong"
        with self.assertRaisesRegex(ValueError, "hash mismatch"):
            validate_review(row, self.draft)

    def test_missing_people_check_rejected(self):
        row = self.review()
        row["all_visible_people_checked"] = False
        with self.assertRaisesRegex(ValueError, "all visible people"):
            validate_review(row, self.draft)

    def test_outside_box_rejected(self):
        row = self.review()
        row["boxes"] = [[0, 0, self.draft["width"] + 1, 20]]
        with self.assertRaisesRegex(ValueError, "outside"):
            validate_review(row, self.draft)

    def test_same_second_reviewer_rejected(self):
        row = self.review()
        row["status"] = "second_review_complete"
        row["second_reviewer"] = "reviewer a"
        with self.assertRaisesRegex(ValueError, "must differ"):
            validate_review(row, self.draft)

    def test_http_read_and_hash_rejection(self):
        server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        worker = threading.Thread(target=server.serve_forever, daemon=True)
        worker.start()
        base = f"http://127.0.0.1:{server.server_port}"
        try:
            with urlopen(base + "/", timeout=5) as response:
                self.assertIn(b"Person annotation review", response.read())
            with urlopen(base + "/api/images", timeout=5) as response:
                items = json.load(response)
            self.assertEqual(len(items), 179)
            self.assertIn(items[0]["status"],
                          ("not_started", "in_progress", "first_review_complete", "second_review_complete"))
            with urlopen(base + "/api/review/" + self.draft["image_id"], timeout=5) as response:
                review = json.load(response)
            self.assertEqual(review["image_sha256"], self.draft["image_sha256"])
            review["image_sha256"] = "wrong"
            request = Request(base + "/api/review/" + self.draft["image_id"],
                              data=json.dumps(review).encode(), headers={"Content-Type": "application/json"})
            with self.assertRaises(HTTPError) as caught:
                urlopen(request, timeout=5)
            self.assertEqual(caught.exception.code, 400)
            self.assertIn("hash mismatch", caught.exception.read().decode())
        finally:
            server.shutdown()
            server.server_close()
            worker.join(timeout=5)


if __name__ == "__main__":
    unittest.main()
