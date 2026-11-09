"""Post-hoc size-stratified diagnostic; evaluate only small bicycle GT boxes."""

import argparse
import hashlib
import json

from ultralytics import YOLO

from evaluate_v10_oi_vehicle_candidate import OI, RUN, WEIGHTS, assess


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--imgsz", type=int, default=512)
    args = parser.parse_args()
    selection = json.loads((OI / "test_small_selection.json").read_text(encoding="utf-8"))
    review_path = OI / "test_small_review_exclusions.json"
    review = json.loads(review_path.read_text(encoding="utf-8"))["excluded"]
    download = json.loads((OI / "test_small_download_report.json").read_text(encoding="utf-8"))
    rows = []
    for original in selection["rows"]:
        if original["image_id"] in review:
            continue
        row = dict(original)
        row["boxes"] = [box for box in original["boxes"]
                        if box[0] == 4 and 12 <= (box[3] * box[4]) ** 0.5 * 512 < 64]
        if row["boxes"]:
            rows.append(row)
    assert len(rows) == 31
    report = {"scope": "Post-hoc small-bicycle diagnostic, not independent model-selection test",
              "source": "Open Images V7 test", "selection_seed": selection["seed"],
              "review_sha256": hashlib.sha256(review_path.read_bytes()).hexdigest(),
              "images": len(rows), "imgsz": args.imgsz,
              "target": "bicycle boxes with approximate sqrt(area)*512 in [12,64)",
              "selection_note": "This slice was selected after the first vehicle test exposed too few small boxes, before inference on these IDs. Models were not retrained.",
              "metrics_note": "Use matched/GT recall only; larger bicycles and incomplete source labels make prediction precision invalid here.",
              "models": {}}
    for name, weights in WEIGHTS.items():
        report["models"][name] = {"weights_sha256": hashlib.sha256(weights.read_bytes()).hexdigest(),
                                  **assess(YOLO(str(weights)), rows, download["sha256_by_image_id"], args.imgsz)}
    path = RUN / ("oi_small_bicycle_diagnostic.json" if args.imgsz == 512 else f"oi_small_bicycle_diagnostic_{args.imgsz}.json")
    path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({name: model["counts"] for name, model in report["models"].items()}, indent=2))


if __name__ == "__main__":
    main()
