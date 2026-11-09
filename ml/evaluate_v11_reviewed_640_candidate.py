"""Compare v9/v10/v11 on the same OI vehicle and small-bicycle diagnostics."""

import argparse
import hashlib
import json
from collections import Counter

from ultralytics import YOLO

from evaluate_v10_oi_vehicle_candidate import OI, assess
from phase1 import ROOT


RUN = ROOT / "runs" / "public_phase1_v11_reviewed_640_candidate"
WEIGHTS = {
    "v9": ROOT / "runs" / "public_phase1_v9_coco_train_candidate" / "yolov8n" / "weights" / "best.pt",
    "v10": ROOT / "runs" / "public_phase1_v10_oi_vehicle_candidate" / "yolov8n" / "weights" / "best.pt",
    "v11": RUN / "yolov8n" / "weights" / "best.pt",
}


def selection(kind):
    if kind == "vehicle":
        selected = json.loads((OI / "test_selection.json").read_text(encoding="utf-8"))
        review_path = OI / "review_exclusions.json"
        excluded = json.loads(review_path.read_text(encoding="utf-8"))["test"]
        rows = [row for row in selected["rows"] if row["image_id"] not in excluded]
        hashes = json.loads((OI / "test_download_report.json").read_text(encoding="utf-8"))["sha256_by_image_id"]
        assert len(rows) == 64
    else:
        selected = json.loads((OI / "test_small_selection.json").read_text(encoding="utf-8"))
        review_path = OI / "test_small_review_exclusions.json"
        excluded = json.loads(review_path.read_text(encoding="utf-8"))["excluded"]
        rows = []
        for original in selected["rows"]:
            if original["image_id"] in excluded:
                continue
            row = dict(original)
            row["boxes"] = [box for box in original["boxes"] if box[0] == 4
                            and 12 <= (box[3] * box[4]) ** 0.5 * 512 < 64]
            if row["boxes"]:
                rows.append(row)
        hashes = json.loads((OI / "test_small_download_report.json").read_text(encoding="utf-8"))["sha256_by_image_id"]
        assert len(rows) == 31
    return rows, hashes, review_path, selected


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--imgsz", type=int, choices=(512, 640), default=640)
    args = parser.parse_args()
    RUN.mkdir(parents=True, exist_ok=True)
    for kind in ("vehicle", "small_bicycle"):
        rows, hashes, review_path, selected = selection(kind)
        report = {"kind": kind, "source": "Open Images V7 test", "imgsz": args.imgsz,
                  "conf": 0.25, "matching_iou": 0.5, "images": len(rows),
                  "groups": dict(Counter(row["group"] for row in rows)),
                  "selection_seed": selected["seed"],
                  "selection_sha256": hashlib.sha256((OI / ("test_selection.json" if kind == "vehicle" else "test_small_selection.json")).read_bytes()).hexdigest(),
                  "review_sha256": hashlib.sha256(review_path.read_bytes()).hexdigest(),
                  "limitations": "Development comparison on public images already used to choose this experiment; not independent or phone-domain validation.",
                  "models": {}}
        for name, weights in WEIGHTS.items():
            report["models"][name] = {"weights_sha256": hashlib.sha256(weights.read_bytes()).hexdigest(),
                                      **assess(YOLO(str(weights)), rows, hashes, args.imgsz)}
        path = RUN / f"oi_{kind}_comparison_{args.imgsz}.json"
        path.write_text(json.dumps(report, indent=2), encoding="utf-8")
        print(kind, args.imgsz, json.dumps({name: report["models"][name]["counts"] for name in WEIGHTS}, indent=2))


if __name__ == "__main__":
    main()
