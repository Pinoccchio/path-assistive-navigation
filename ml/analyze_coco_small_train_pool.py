"""Count disjoint small-vehicle candidates in the local COCO train label archive."""

import json
import zipfile
from collections import Counter

from build_v9_coco_train_candidate import SELECTION, ZIP


def size_bin(side):
    if side < 12:
        return "under_12"
    if side < 24:
        return "12_24"
    if side < 40:
        return "24_40"
    if side < 64:
        return "40_64"
    return "64_plus"


def main():
    excluded = {row["image_id"] for row in json.loads(SELECTION.read_text())["rows"]}
    bins = Counter()
    image_bins = Counter()
    examples = []
    with zipfile.ZipFile(ZIP) as archive:
        for path in archive.namelist():
            if not path.startswith("coco/labels/train2017/") or not path.endswith(".txt"):
                continue
            image_id = path.rsplit("/", 1)[-1][:-4]
            if image_id in excluded:
                continue
            lines = [line.split() for line in archive.read(path).decode().splitlines() if line.strip()]
            classes = {int(row[0]) for row in lines}
            if 58 in classes:
                continue
            bicycle = [row for row in lines if int(row[0]) == 1]
            motorcycle = [row for row in lines if int(row[0]) == 3]
            if not bicycle and not motorcycle:
                continue
            image_categories = set()
            for category, rows in (("bicycle", bicycle), ("motorcycle", motorcycle)):
                for row in rows:
                    side = max(float(row[3]), float(row[4])) * 512
                    bucket = size_bin(side)
                    bins[f"{category}:{bucket}"] += 1
                    image_categories.add(f"{category}:{bucket}")
            image_bins.update(image_categories)
            if bicycle and any(12 <= max(float(row[3]), float(row[4])) * 512 < 40 for row in bicycle):
                examples.append(image_id)
    print(json.dumps({"excluded_prior_coco_train_images": len(excluded),
                      "box_counts": dict(sorted(bins.items())),
                      "image_counts": dict(sorted(image_bins.items())),
                      "small_bicycle_candidate_images": len(examples),
                      "first_20_candidate_ids": examples[:20]}, indent=2))


if __name__ == "__main__":
    main()
