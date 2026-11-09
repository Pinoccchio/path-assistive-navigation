"""Paired eight-class diagnostic for the completed person-retention candidate."""

import hashlib
import json

from ultralytics import YOLO

from compare_v11_with_coco_pretrained import DATA, RUN as BASE_RUN, evaluate, evaluate_small
from phase1 import ROOT


CANDIDATE_DATA = ROOT / "data/processed/public_phase1_person_retention_candidate"
CANDIDATE_RUN = ROOT / "runs/public_phase1_person_retention_candidate"
WEIGHTS = CANDIDATE_RUN / "yolov8n_local/weights/best.pt"
OUT = CANDIDATE_RUN / "paired_public_diagnostic_512.json"


def test_rows(path):
    return [json.loads(line) for line in (path / "dataset_manifest.jsonl")
            .read_text(encoding="utf-8").splitlines()
            if json.loads(line)["split"] == "test"]


def main():
    assert WEIGHTS.exists(), WEIGHTS
    baseline_rows = test_rows(DATA)
    candidate_rows = test_rows(CANDIDATE_DATA)
    assert len(baseline_rows) == len(candidate_rows) == 620
    assert [(row["id"], row["sha256"]) for row in baseline_rows] == [
        (row["id"], row["sha256"]) for row in candidate_rows]
    model = YOLO(str(WEIGHTS))
    report = {"weights_sha256": hashlib.sha256(WEIGHTS.read_bytes()).hexdigest(),
              "images": len(candidate_rows), "imgsz": 512, "conf": 0.25,
              "matching_iou": 0.5,
              "test_manifest_unchanged": True,
              "limitations": "Same reused public development images and incomplete source labels as the v11 comparison; not independent, phone, or navigation validation.",
              "public_test": evaluate(model, "v11", baseline_rows),
              "small_bicycle": evaluate_small(model, "v11"),
              "baseline_report": str(BASE_RUN / "coco_pretrained_comparison_512.json")}
    OUT.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({"public_test_counts": report["public_test"]["counts"],
                      "small_bicycle": report["small_bicycle"]}, indent=2))


if __name__ == "__main__":
    main()
