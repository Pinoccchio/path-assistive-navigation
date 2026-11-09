"""Count bicycle detections on the reviewed motorcycle/scooter hard negatives."""

import argparse
import json

from ultralytics import YOLO

from phase1 import ROOT


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset-name", default="public_phase1_v7_vehicle_labels_candidate")
    parser.add_argument("--weights", required=True)
    parser.add_argument("--model-tag", required=True)
    args = parser.parse_args()
    dataset = ROOT / "data" / "processed" / args.dataset_name
    run = ROOT / "runs" / args.dataset_name
    report = json.loads((dataset / "build_report.json").read_text(encoding="utf-8"))
    reviewed = {(row["split"], row["id"]) for row in report["corrections"] if row["class_id"] == 4}
    model = YOLO(args.weights)
    summary = {}
    for split in ("train", "val", "test"):
        ids = sorted(stem for candidate_split, stem in reviewed if candidate_split == split)
        paths = [str(dataset / "images" / split / f"{stem}.jpg") for stem in ids]
        results = model.predict(paths, imgsz=512, conf=0.25, device="cpu", batch=8, verbose=False)
        rows = []
        for stem, result in zip(ids, results):
            bicycle_conf = [float(box.conf) for box in result.boxes if int(box.cls) == 4]
            rows.append({"id": stem, "bicycle_detections": len(bicycle_conf),
                         "max_bicycle_confidence": max(bicycle_conf, default=0.0)})
        summary[split] = {"reviewed_images": len(rows),
                          "images_with_bicycle_prediction": sum(row["bicycle_detections"] > 0 for row in rows),
                          "bicycle_predictions": sum(row["bicycle_detections"] for row in rows),
                          "images": rows}
    output = run / f"vehicle_negative_qa_{args.model_tag}.json"
    output.write_text(json.dumps({"weights": args.weights, "threshold": 0.25,
                                  "imgsz": 512, "results": summary}, indent=2), encoding="utf-8")
    print(json.dumps({split: {key: value for key, value in split_report.items() if key != "images"}
                      for split, split_report in summary.items()}, indent=2))
    print(output)


if __name__ == "__main__":
    main()
