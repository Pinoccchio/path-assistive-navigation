"""Generate higher-recall person proposals for review, never training labels."""

import csv
import hashlib
import json

from PIL import Image
from ultralytics import YOLO

from build_v16_person_quarantine import LEDGER, ROOT, SOURCE

OUT = ROOT / "runs/public_phase1_v15_oi_quarantine/person_draft_960"
WEIGHTS = ROOT / "notebooks/yolov8n.pt"


def main():
    ids = sorted(json.loads(LEDGER.read_text(encoding="utf-8"))["excluded"])
    OUT.mkdir(parents=True, exist_ok=True)
    model = YOLO(str(WEIGHTS))
    rows = []
    for image_id in ids:
        image = SOURCE / "images/train" / f"oi_v10_train_{image_id}.jpg"
        with Image.open(image) as source:
            width, height = source.size
        result = model.predict(str(image), imgsz=960, conf=0.15, iou=0.5,
                               classes=[0], verbose=False)[0]
        proposals = []
        for box in result.boxes:
            coords = [round(float(v), 1) for v in box.xyxy[0]]
            proposals.append({"xyxy_pixels": coords, "confidence": round(float(box.conf[0]), 4),
                              "yolo_normalized": [round((coords[0] + coords[2]) / (2 * width), 8),
                                                  round((coords[1] + coords[3]) / (2 * height), 8),
                                                  round((coords[2] - coords[0]) / width, 8),
                                                  round((coords[3] - coords[1]) / height, 8)]})
        rows.append({"image_id": image_id, "image_sha256": hashlib.sha256(image.read_bytes()).hexdigest(),
                     "width": width, "height": height, "proposals": proposals,
                     "review_status": "unverified_draft"})
    report = {"model": str(WEIGHTS), "model_sha256": hashlib.sha256(WEIGHTS.read_bytes()).hexdigest(),
              "imgsz": 960, "confidence": 0.15, "nms_iou": 0.5,
              "images": len(rows), "proposals": sum(len(row["proposals"]) for row in rows),
              "policy": "Review aid only. Do not copy proposals to training labels without exhaustive human correction and QA.",
              "rows": rows}
    (OUT / "draft.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    with (OUT / "draft.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(("image_id", "proposal_number", "confidence", "x1", "y1", "x2", "y2", "review_status"))
        for row in rows:
            for number, proposal in enumerate(row["proposals"], 1):
                writer.writerow((row["image_id"], number, proposal["confidence"],
                                 *proposal["xyxy_pixels"], "pending_human_review"))
    print(json.dumps({key: value for key, value in report.items() if key != "rows"}, indent=2))


if __name__ == "__main__":
    main()
