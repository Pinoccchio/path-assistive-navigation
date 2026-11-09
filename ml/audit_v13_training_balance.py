"""Summarize v13 training boxes by source, class, and approximate input size."""

import json
from collections import Counter

from phase1 import ROOT


DATA = ROOT / "data/processed/public_phase1_v13_four_box_pilot"
NAMES = ("person", "chair", "stairs", "car", "bicycle", "electrical_pole", "plant_pot", "motorcycle")


def main():
    rows = [json.loads(line) for line in (DATA / "dataset_manifest.jsonl").read_text(encoding="utf-8").splitlines()]
    sources, boxes, images, sizes = Counter(), Counter(), Counter(), Counter()
    for row in rows:
        if row["split"] != "train":
            continue
        source = row["source"]
        sources[source] += 1
        seen = set()
        label = DATA / "labels/train" / f'{row["id"]}.txt'
        for line in label.read_text(encoding="utf-8").splitlines():
            fields = line.split()
            if not fields:
                continue
            name = NAMES[int(fields[0])]
            boxes[(source, name)] += 1
            seen.add(name)
            side = (float(fields[3]) * float(fields[4])) ** 0.5 * 512
            sizes[(name, "under_40" if side < 40 else "40_plus")] += 1
        images.update((source, name) for name in seen)
    print(json.dumps({"train_images_by_source": dict(sources),
                      "train_boxes_by_source_class": {f"{s}:{n}": v for (s, n), v in sorted(boxes.items())},
                      "train_images_by_source_class": {f"{s}:{n}": v for (s, n), v in sorted(images.items())},
                      "approx_box_size_at_512": {f"{n}:{bucket}": v for (n, bucket), v in sorted(sizes.items())}}, indent=2))


if __name__ == "__main__":
    main()
