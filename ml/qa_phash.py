"""Screen the provisional v2 split for train/test perceptual-hash matches."""

import argparse
import json
from pathlib import Path

import cv2
import numpy as np

from phase1 import ROOT


DATA = ROOT / "data" / "processed" / "public_phase1_v2_screened"
RUN = ROOT / "runs" / "public_phase1_v2_screened"


def phash(path: Path) -> int:
    image = cv2.imread(str(path), cv2.IMREAD_GRAYSCALE)
    resized = cv2.resize(image, (32, 32), interpolation=cv2.INTER_AREA).astype(np.float32)
    frequency = cv2.dct(resized)[:8, :8].flatten()
    threshold = np.median(frequency[1:])
    bits = 0
    for value in frequency:
        bits = (bits << 1) | int(value > threshold)
    return bits


def main():
    global DATA, RUN
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset-name", default="public_phase1_v2_screened")
    args = parser.parse_args()
    DATA = ROOT / "data" / "processed" / args.dataset_name
    RUN = ROOT / "runs" / args.dataset_name
    RUN.mkdir(parents=True, exist_ok=True)
    rows = [json.loads(line) for line in (DATA / "dataset_manifest.jsonl").read_text(encoding="utf-8").splitlines()]
    hashed = [(phash(DATA / "images" / row["split"] / f"{row['id']}.jpg"), row) for row in rows]
    train = [(value, row) for value, row in hashed if row["split"] == "train"]
    test = [(value, row) for value, row in hashed if row["split"] == "test"]
    pairs = []
    for test_hash, test_row in test:
        for train_hash, train_row in train:
            if not set(test_row["class_ids"]) & set(train_row["class_ids"]):
                continue
            distance = (test_hash ^ train_hash).bit_count()
            if distance <= 10:
                pairs.append({"test": test_row["id"], "train": train_row["id"], "distance": distance})
    pairs.sort(key=lambda row: row["distance"])
    out = RUN / "qa_phash_pairs.json"
    out.write_text(json.dumps({"pairs": pairs, "note": "Candidate pairs require manual review"}, indent=2), encoding="utf-8")
    print(f"pHash candidate pairs <=10: {len(pairs)}; unique test images: {len({row['test'] for row in pairs})}")
    print(*pairs[:20], sep="\n")


if __name__ == "__main__":
    main()
