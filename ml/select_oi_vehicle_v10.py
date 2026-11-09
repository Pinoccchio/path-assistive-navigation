"""Freeze rights-tracked Open Images bicycle/motorcycle train or test selections."""

import argparse
import csv
import hashlib
import json
from collections import defaultdict

from phase1 import ROOT


OI = ROOT / "data" / "source" / "oi_public_phase1"
OUT = ROOT / "data" / "source" / "oi_vehicle_v10"
MIDS = {"/m/01g317": 0, "/m/01mzpv": 1, "/m/01lynh": 2,
        "/m/0k4j": 3, "/m/0199g": 4, "/m/04_sv": 7}
BIKE, MOTO = "/m/0199g", "/m/04_sv"


def rank(seed, group, image_id):
    return int.from_bytes(hashlib.blake2b(f"{seed}:{group}:{image_id}".encode(), digest_size=8).digest(), "big")


def valid(row):
    if row["LabelName"] not in MIDS or row["IsDepiction"] == "1" or row["IsGroupOf"] == "1":
        return None
    try:
        a, b, c, d = [float(row[k]) for k in ("XMin", "XMax", "YMin", "YMax")]
    except (ValueError, KeyError):
        return None
    if not (0 <= a < b <= 1 and 0 <= c < d <= 1):
        return None
    return [MIDS[row["LabelName"]], (a + b) / 2, (c + d) / 2, b - a, d - c]


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--split", choices=("train", "test"), required=True)
    p.add_argument("--bike-count", type=int, required=True)
    p.add_argument("--moto-count", type=int, required=True)
    p.add_argument("--seed", type=int, required=True)
    p.add_argument("--selection-name", help="Optional new frozen selection filename")
    p.add_argument("--test-small-bike", action="store_true")
    args = p.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    dest = OUT / (args.selection_name or f"{args.split}_selection.json")
    if dest.exists():
        raise SystemExit(f"Frozen selection already exists: {dest}")
    existing = {row["source_id"] for row in
                (json.loads(line) for line in (ROOT / "data" / "processed" /
                 "public_phase1_v9_coco_train_candidate" / "dataset_manifest.jsonl").read_text(encoding="utf-8").splitlines())
                if row["source"] == "OpenImagesV7"}
    if args.test_small_bike:
        assert args.split == "test" and args.moto_count == 0 and args.selection_name
        for name in ("train_selection.json", "test_selection.json"):
            existing.update(row["image_id"] for row in json.loads((OUT / name).read_text(encoding="utf-8"))["rows"])
    boxes = defaultdict(lambda: {"bike": [], "moto": []})
    with (OI / f"{args.split}_boxes.csv").open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            mid, image_id = row["LabelName"], row["ImageID"]
            if mid not in (BIKE, MOTO) or image_id in existing:
                continue
            box = valid(row)
            if box:
                boxes[image_id]["bike" if mid == BIKE else "moto"].append(box)
    eligible = {image_id for image_id, item in boxes.items() if bool(item["bike"]) != bool(item["moto"])}
    info = {}
    with (OI / f"{args.split}_image_info.csv").open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row["ImageID"] in eligible and row["License"].rstrip("/") in {
                "https://creativecommons.org/licenses/by/2.0",
                "https://creativecommons.org/licenses/by/4.0",
            }:
                info[row["ImageID"]] = {key: row[key] for key in
                                        ("OriginalURL", "OriginalLandingURL", "License", "Author")}
    groups = {"small_bicycle": [], "motorcycle": []}
    for image_id, item in boxes.items():
        if image_id not in info or image_id not in eligible:
            continue
        if item["bike"]:
            # Approximate screen size; exact 512-letterbox size is checked after download.
            smallest = min((box[3] * box[4]) ** 0.5 * 512 for box in item["bike"])
            if (args.split == "train" or args.test_small_bike) and not (12 <= smallest < 64):
                continue
            group = "small_bicycle"
        else:
            group = "motorcycle"
        groups[group].append(image_id)
    limits = {"small_bicycle": args.bike_count, "motorcycle": args.moto_count}
    selected = []
    for group, ids in groups.items():
        ranked = sorted(ids, key=lambda image_id: (rank(args.seed, group, image_id), image_id))
        if len(ranked) < limits[group]:
            raise ValueError(f"Only {len(ranked)} eligible {group} images")
        selected.extend({"group": group, "image_id": image_id, **info[image_id]}
                        for image_id in ranked[:limits[group]])
    selected_ids = {row["image_id"] for row in selected}
    labeled = defaultdict(list)
    with (OI / f"{args.split}_boxes.csv").open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row["ImageID"] in selected_ids:
                box = valid(row)
                if box:
                    labeled[row["ImageID"]].append(box)
    for row in selected:
        row["boxes"] = labeled[row["image_id"]]
        assert any(box[0] == (4 if row["group"] == "small_bicycle" else 7) for box in row["boxes"])
    dest.write_text(json.dumps({"source": "Open Images V7", "source_split": args.split,
                                "seed": args.seed, "bike_count": args.bike_count,
                                "moto_count": args.moto_count, "test_small_bike": args.test_small_bike,
                                "box_policy": "non-group, non-depiction target-class boxes",
                                "rows": selected}, indent=2), encoding="utf-8")
    print(json.dumps({"selection": str(dest), "eligible": {k: len(v) for k, v in groups.items()},
                      "selected": {k: sum(row["group"] == k for row in selected) for k in groups}}))


if __name__ == "__main__":
    main()
