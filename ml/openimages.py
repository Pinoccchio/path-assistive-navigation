"""Acquire a rights-tracked Open Images V7 five-class supplement.

Open Images has no directly equivalent electrical-pole or plant-pot box class.
The output is a source manifest consumed by phase1.py build.
"""

from __future__ import annotations

import argparse
import csv
import io
import json
import hashlib
import heapq
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import requests
from PIL import Image

from phase1 import ROOT, sha256


DEST = ROOT / "data" / "source" / "oi_public_phase1"
MIDS = {"/m/01g317": 0, "/m/01mzpv": 1, "/m/01lynh": 2,
        "/m/0k4j": 3, "/m/0199g": 4}
BOX_URLS = {
    "train": "https://storage.googleapis.com/openimages/v6/oidv6-train-annotations-bbox.csv",
    "validation": "https://storage.googleapis.com/openimages/v5/validation-annotations-bbox.csv",
    "test": "https://storage.googleapis.com/openimages/v5/test-annotations-bbox.csv",
}
INFO_URLS = {
    "train": "https://storage.googleapis.com/openimages/2018_04/train/train-images-boxable-with-rotation.csv",
    "validation": "https://storage.googleapis.com/openimages/2018_04/validation/validation-images-with-rotation.csv",
    "test": "https://storage.googleapis.com/openimages/2018_04/test/test-images-with-rotation.csv",
}


def download_csv(url: str, path: Path) -> None:
    if path.exists():
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    response = requests.get(url, timeout=180, stream=True)
    response.raise_for_status()
    temp = path.with_suffix(".partial")
    with temp.open("wb") as file:
        for chunk in response.iter_content(1024 * 1024):
            file.write(chunk)
    temp.replace(path)


def valid_box(row: dict) -> list[float] | None:
    if row["LabelName"] not in MIDS or row["IsDepiction"] == "1" or row["IsGroupOf"] == "1":
        return None
    try:
        xmin, xmax, ymin, ymax = [float(row[key]) for key in ("XMin", "XMax", "YMin", "YMax")]
    except (ValueError, KeyError):
        return None
    if not (0 <= xmin < xmax <= 1 and 0 <= ymin < ymax <= 1):
        return None
    return [MIDS[row["LabelName"]], (xmin + xmax) / 2, (ymin + ymax) / 2, xmax - xmin, ymax - ymin]


def selected_boxes(split: str, per_class: int, seed: int) -> dict[str, list[list[float]]]:
    path = DEST / f"{split}_boxes.csv"
    download_csv(BOX_URLS[split], path)
    heaps: dict[int, list[tuple[int, str]]] = defaultdict(list)
    selected_by_class: dict[int, set[str]] = defaultdict(set)
    with path.open(newline="", encoding="utf-8") as file:
        for row in csv.DictReader(file):
            box = valid_box(row)
            if box is None:
                continue
            target, image_id = int(box[0]), row["ImageID"]
            if image_id in selected_by_class[target]:
                continue
            rank = int.from_bytes(hashlib.blake2b(f"{seed}:{target}:{image_id}".encode(), digest_size=8).digest(), "big")
            heap = heaps[target]
            if len(heap) >= per_class and rank >= -heap[0][0]:
                continue
            if len(heap) >= per_class:
                _, removed = heapq.heappop(heap)
                selected_by_class[target].remove(removed)
            heapq.heappush(heap, (-rank, image_id))
            selected_by_class[target].add(image_id)
    selected = set().union(*selected_by_class.values())
    boxes: dict[str, list[list[float]]] = defaultdict(list)
    with path.open(newline="", encoding="utf-8") as file:
        for row in csv.DictReader(file):
            if row["ImageID"] in selected:
                box = valid_box(row)
                if box is not None:
                    boxes[row["ImageID"]].append(box)
    return dict(boxes)


def licensed_info(split: str, image_ids: set[str]) -> dict[str, dict]:
    path = DEST / f"{split}_image_info.csv"
    download_csv(INFO_URLS[split], path)
    details = {}
    with path.open(newline="", encoding="utf-8") as file:
        for row in csv.DictReader(file):
            if row["ImageID"] in image_ids and row["License"].rstrip("/") in {
                "https://creativecommons.org/licenses/by/2.0",
                "https://creativecommons.org/licenses/by/4.0",
            }:
                details[row["ImageID"]] = row
    return details


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--train-per-class", type=int, default=100)
    parser.add_argument("--val-per-class", type=int, default=25)
    parser.add_argument("--test-per-class", type=int, default=25)
    parser.add_argument("--workers", type=int, default=8)
    args = parser.parse_args()
    manifest = DEST / "manifest.jsonl"
    known = set()
    if manifest.exists():
        known = {(row["source_split"], row["source_id"])
                 for row in (json.loads(line) for line in manifest.read_text(encoding="utf-8").splitlines())}
    DEST.mkdir(parents=True, exist_ok=True)
    limits = {"train": args.train_per_class, "validation": args.val_per_class, "test": args.test_per_class}
    with manifest.open("a", encoding="utf-8") as ledger:
        for split, per_class in limits.items():
            if per_class == 0:
                continue
            boxes = selected_boxes(split, per_class, 42 + len(split))
            info = licensed_info(split, set(boxes))
            ids = [image_id for image_id in boxes if image_id in info and (split, image_id) not in known]
            print(f"{split}: {len(ids)} eligible images", flush=True)

            def fetch(image_id: str) -> tuple[str, bytes]:
                url = f"https://open-images-dataset.s3.amazonaws.com/{split}/{image_id}.jpg"
                response = requests.get(url, timeout=90)
                response.raise_for_status()
                image = Image.open(io.BytesIO(response.content))
                image.verify()
                return image_id, response.content

            with ThreadPoolExecutor(max_workers=args.workers) as pool:
                futures = {pool.submit(fetch, image_id): image_id for image_id in ids}
                for index, future in enumerate(as_completed(futures), 1):
                    image_id = futures[future]
                    try:
                        _, content = future.result()
                    except (requests.RequestException, OSError) as exc:
                        print(f"skip {image_id}: {exc}", flush=True)
                        continue
                    path = DEST / "images" / split / f"{image_id}.jpg"
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.write_bytes(content)
                    row = info[image_id]
                    entry = {
                        "source": "OpenImagesV7", "source_split": split, "source_id": image_id,
                        "source_url": f"https://open-images-dataset.s3.amazonaws.com/{split}/{image_id}.jpg",
                        "original_url": row["OriginalURL"], "landing_url": row["OriginalLandingURL"],
                        "license_url": row["License"], "author": row["Author"],
                        "sha256": sha256(content), "class_ids": sorted({box[0] for box in boxes[image_id]}),
                        "boxes": boxes[image_id], "license_status": "listed_CC_BY_verify_original",
                        "group": f"openimages:{image_id}",
                    }
                    ledger.write(json.dumps(entry) + "\n")
                    ledger.flush()
                    known.add((split, image_id))
                    if index % 100 == 0:
                        print(f"{split}: {index}/{len(ids)}", flush=True)
    print(f"manifest: {manifest}")


if __name__ == "__main__":
    main()
