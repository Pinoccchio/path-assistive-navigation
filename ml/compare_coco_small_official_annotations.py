"""Compare the frozen YOLO review labels with official COCO train2017 boxes."""

import hashlib
import json
import zipfile
from collections import Counter, defaultdict
from pathlib import Path

from build_v9_coco_train_candidate import ZIP as YOLO_ZIP


ROOT = Path(__file__).resolve().parents[1]
REVIEW = ROOT / "data/source/coco_external/small_bicycle_review_v1"
OFFICIAL_ZIP = ROOT / "data/source/coco_external/annotations_trainval2017.zip"
COCO_TO_YOLO = {2: 1, 4: 3}


def iou(a, b):
    left, top = max(a[0], b[0]), max(a[1], b[1])
    right, bottom = min(a[2], b[2]), min(a[3], b[3])
    intersection = max(0, right - left) * max(0, bottom - top)
    area_a = (a[2] - a[0]) * (a[3] - a[1])
    area_b = (b[2] - b[0]) * (b[3] - b[1])
    return intersection / (area_a + area_b - intersection) if area_a + area_b > intersection else 0


def main():
    selection = json.loads((REVIEW / "selection.json").read_text(encoding="utf-8"))["rows"]
    selected = {int(row["image_id"]) for row in selection}
    assert OFFICIAL_ZIP.exists(), OFFICIAL_ZIP
    with zipfile.ZipFile(OFFICIAL_ZIP) as archive:
        assert archive.testzip() is None, "Official annotation archive failed CRC verification"
        official = json.loads(archive.read("annotations/instances_train2017.json"))
    images = {row["id"]: row for row in official["images"] if row["id"] in selected}
    assert set(images) == selected
    licenses = {row["id"]: row for row in official["licenses"]}
    annotations = defaultdict(list)
    for row in official["annotations"]:
        if row["image_id"] in selected and row["category_id"] in COCO_TO_YOLO:
            annotations[row["image_id"]].append(row)
    results = []
    with zipfile.ZipFile(YOLO_ZIP) as archive:
        for selected_row in selection:
            image_id = int(selected_row["image_id"])
            info = images[image_id]
            label_path = f"coco/labels/train2017/{selected_row['image_id']}.txt"
            raw = archive.read(label_path)
            assert hashlib.sha256(raw).hexdigest() == selected_row["label_sha256"]
            yolo = []
            for line in raw.decode().splitlines():
                values = line.split()
                if not values or int(values[0]) not in (1, 3):
                    continue
                cls = int(values[0])
                cx, cy, w, h = map(float, values[1:5])
                yolo.append((cls, ((cx - w / 2) * info["width"], (cy - h / 2) * info["height"],
                                   (cx + w / 2) * info["width"], (cy + h / 2) * info["height"])))
            official_rows = []
            for ann in annotations[image_id]:
                x, y, w, h = ann["bbox"]
                official_rows.append((COCO_TO_YOLO[ann["category_id"]], (x, y, x + w, y + h), ann["id"], ann["iscrowd"]))
            unmatched = set(range(len(official_rows)))
            matched = []
            for cls, box in yolo:
                candidates = [(iou(box, official_rows[j][1]), j) for j in unmatched if official_rows[j][0] == cls]
                if candidates:
                    score, j = max(candidates)
                    if score >= 0.95:
                        matched.append((j, score))
                        unmatched.remove(j)
            image_license = licenses.get(info["license"], {})
            results.append({"image_id": selected_row["image_id"], "group": selected_row["group"],
                            "official_bicycle_boxes": sum(row[0] == 1 for row in official_rows),
                            "official_motorcycle_boxes": sum(row[0] == 3 for row in official_rows),
                            "converted_vehicle_boxes": len(yolo), "matched_iou_095": len(matched),
                            "unmatched_official": [{"annotation_id": official_rows[j][2],
                                                    "class": official_rows[j][0],
                                                    "iscrowd": official_rows[j][3],
                                                    "bbox_xyxy": official_rows[j][1]}
                                                   for j in sorted(unmatched)],
                            "unmatched_converted_boxes": len(yolo) - len(matched),
                            "license_id": info["license"], "license_name": image_license.get("name"),
                            "license_url": image_license.get("url"),
                            "flickr_url": info.get("flickr_url"), "coco_url": info.get("coco_url")})
    (REVIEW / "official_annotation_comparison.jsonl").write_text(
        "".join(json.dumps(row) + "\n" for row in results), encoding="utf-8")
    print(json.dumps({"images": len(results), "exact_vehicle_box_count_match": sum(
        row["converted_vehicle_boxes"] == row["matched_iou_095"] ==
        row["official_bicycle_boxes"] + row["official_motorcycle_boxes"] for row in results),
        "license_counts": dict(Counter(row["license_name"] for row in results)),
        "unmatched_converted_boxes": sum(row["unmatched_converted_boxes"] for row in results),
        "unmatched_official_boxes": sum(len(row["unmatched_official"]) for row in results)}, indent=2))


if __name__ == "__main__":
    main()
