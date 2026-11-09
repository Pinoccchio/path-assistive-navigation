"""Prioritize public vehicle images for human annotation and error review."""

import csv
import json

from phase1 import ROOT


RUN = ROOT / "runs" / "public_phase1_v11_reviewed_640_candidate"
OUT = RUN / "review_queue_512.csv"


def main():
    queue = []
    for kind in ("small_bicycle", "vehicle"):
        report = json.loads((RUN / f"oi_{kind}_comparison_512.json").read_text(encoding="utf-8"))
        rows = report["models"]["v11"]["rows"]
        for row in rows:
            bike_miss = row["bicycle_gt"] - row["bicycle_matched"]
            moto_miss = row["motorcycle_gt"] - row["motorcycle_matched"]
            confusion = (row["group"] == "motorcycle" and row["bicycle_pred"] > 0) or (
                row["group"] in ("small_bicycle", "bicycle") and row["motorcycle_pred"] > 0
            )
            if not (bike_miss or moto_miss or confusion):
                continue
            queue.append({
                "priority": 0 if kind == "small_bicycle" and bike_miss else 1 if confusion else 2,
                "slice": kind,
                "image_id": row["image_id"],
                "group": row["group"],
                "bicycle_gt": row["bicycle_gt"],
                "bicycle_matched": row["bicycle_matched"],
                "bicycle_predictions": row["bicycle_pred"],
                "motorcycle_gt": row["motorcycle_gt"],
                "motorcycle_matched": row["motorcycle_matched"],
                "motorcycle_predictions": row["motorcycle_pred"],
                "review_task": "verify all bicycle/motorcycle instances and boxes; classify miss, confusion, or incomplete source labels",
                "image_path": str(ROOT / "data" / "source" / "oi_vehicle_v10" / "images" / "test" / f"{row['image_id']}.jpg"),
            })
    queue.sort(key=lambda row: (row["priority"], row["slice"], row["image_id"]))
    with OUT.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(queue[0]))
        writer.writeheader()
        writer.writerows(queue)
    print(json.dumps({"queue": str(OUT), "images": len(queue),
                      "small_bicycle_miss_images": sum(row["slice"] == "small_bicycle" and
                                                        row["bicycle_gt"] > row["bicycle_matched"] for row in queue),
                      "motorcycle_miss_images": sum(row["motorcycle_gt"] > row["motorcycle_matched"] for row in queue)},
                     indent=2))


if __name__ == "__main__":
    main()
