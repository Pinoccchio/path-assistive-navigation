"""Paired staircase diagnostic for the person-retention checkpoint."""

import hashlib
import json

from evaluate_stair_pretrained_candidates import DATA, RUN, evaluate
from phase1 import ROOT
from ultralytics import YOLO


WEIGHTS = ROOT / "runs/public_phase1_person_retention_candidate/yolov8n_local/weights/best.pt"
OUT = ROOT / "runs/public_phase1_person_retention_candidate/stair_public_diagnostic_512.json"


def main():
    rows = [json.loads(line) for line in (DATA / "dataset_manifest.jsonl")
            .read_text(encoding="utf-8").splitlines()]
    rows = [row for row in rows if row["split"] == "test"]
    assert len(rows) == 620
    assert WEIGHTS.exists(), WEIGHTS
    model = YOLO(str(WEIGHTS))
    class_ids = {index for index, name in model.names.items() if name.casefold() == "stairs"}
    assert len(class_ids) == 1, model.names
    report = {"images": len(rows), "imgsz": 512, "conf": 0.25,
              "matching_iou": 0.5,
              "weights_sha256": hashlib.sha256(WEIGHTS.read_bytes()).hexdigest(),
              "baseline_report": str(RUN / "stair_pretrained_comparison_512.json"),
              "limitations": "Reused public development images with imperfect stair labels; not independent or phone validation.",
              "candidate": evaluate(model, "person_retention", rows, class_ids)}
    OUT.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report["candidate"]["counts"], indent=2))


if __name__ == "__main__":
    main()
