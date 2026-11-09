"""High-recall review triage across all newly selected v15 OI training images."""

import hashlib
import json
from collections import Counter

from PIL import Image
from ultralytics import YOLO

from audit_v15_person_labels import iou
from phase1 import ROOT

DATASET = ROOT / "data/processed/public_phase1_v15_oi_quarantine"
SELECTION = ROOT / "data/source/oi_vehicle_v10/train_selection.json"
OLD_LEDGER = ROOT / "data/source/oi_vehicle_v10/train_quarantine_v16_person.json"
WEIGHTS = ROOT / "notebooks/yolov8n.pt"
OUT = ROOT / "runs/public_phase1_v15_oi_quarantine/person_audit_960_all"


def main():
    selected = json.loads(SELECTION.read_text(encoding="utf-8"))["rows"]
    manifest = [json.loads(line) for line in (DATASET / "dataset_manifest.jsonl").read_text(encoding="utf-8").splitlines()]
    retained = {row["source_id"] for row in manifest if row["split"] == "train" and row["source"] == "OpenImagesV7"}
    rows = [item for item in selected if item["image_id"] in retained]
    assert len(rows) == 283
    known = set(json.loads(OLD_LEDGER.read_text(encoding="utf-8"))["excluded"])
    model = YOLO(str(WEIGHTS))
    findings = []
    categories = Counter()
    for item in rows:
        image_id = item["image_id"]
        stem = f"oi_v10_train_{image_id}"
        image = DATASET / "images/train" / f"{stem}.jpg"
        label = DATASET / "labels/train" / f"{stem}.txt"
        with Image.open(image) as source:
            width, height = source.size
        truth = []
        for line in label.read_text(encoding="utf-8").splitlines():
            cls, xc, yc, bw, bh = map(float, line.split())
            if int(cls) == 0:
                truth.append([(xc - bw / 2) * width, (yc - bh / 2) * height,
                              (xc + bw / 2) * width, (yc + bh / 2) * height])
        result = model.predict(str(image), imgsz=960, conf=0.15, iou=0.5, classes=[0], verbose=False)[0]
        proposals = []
        for box in result.boxes:
            coords = [round(float(v), 1) for v in box.xyxy[0]]
            best = max((iou(coords, existing) for existing in truth), default=0.0)
            if best < 0.1:
                proposals.append({"confidence": round(float(box.conf[0]), 4),
                                  "box_xyxy": coords, "best_person_iou": round(best, 4)})
        category = ("known_zero_person" if image_id in known else
                    "new_zero_person_candidate" if not truth and proposals else
                    "existing_person_candidate" if truth and proposals else "no_unmatched_proposal")
        categories[category] += 1
        if proposals:
            findings.append({"image_id": image_id, "group": item["group"],
                             "image_sha256": hashlib.sha256(image.read_bytes()).hexdigest(),
                             "width": width, "height": height,
                             "existing_person_boxes": len(truth), "category": category,
                             "proposals": proposals})
    OUT.mkdir(parents=True, exist_ok=True)
    report = {"dataset": str(DATASET), "model": str(WEIGHTS),
              "model_sha256": hashlib.sha256(WEIGHTS.read_bytes()).hexdigest(),
              "imgsz": 960, "confidence": 0.15, "nms_iou": 0.5,
              "retained_new_oi_images": len(rows), "categories": dict(categories),
              "flagged_images": len(findings),
              "flagged_proposals": sum(len(row["proposals"]) for row in findings),
              "policy": "Triage only. Every new zero-person candidate requires visual confirmation; no boxes auto-added to training.",
              "rows": findings}
    (OUT / "audit.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: value for key, value in report.items() if key != "rows"}, indent=2))


if __name__ == "__main__":
    main()
