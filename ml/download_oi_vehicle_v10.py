"""Download selected Open Images photos with resumable integrity checks."""

import argparse
import hashlib
import io
import json
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests
from PIL import Image

from phase1 import ROOT


OUT = ROOT / "data" / "source" / "oi_vehicle_v10"


def fetch(split, row):
    image_id = row["image_id"]
    dest = OUT / "images" / split / f"{image_id}.jpg"
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists():
        data = dest.read_bytes()
        with Image.open(io.BytesIO(data)) as image:
            image.verify()
        return image_id, hashlib.sha256(data).hexdigest()
    url = f"https://open-images-dataset.s3.amazonaws.com/{split}/{image_id}.jpg"
    for attempt in range(4):
        try:
            response = requests.get(url, timeout=90)
            response.raise_for_status()
            data = response.content
            with Image.open(io.BytesIO(data)) as image:
                image.verify()
            temp = dest.with_suffix(".part")
            temp.write_bytes(data)
            temp.replace(dest)
            return image_id, hashlib.sha256(data).hexdigest()
        except (requests.RequestException, OSError):
            if attempt == 3:
                raise
            time.sleep(attempt + 1)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--split", choices=("train", "test"), required=True)
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--selection-name", help="Selection filename; defaults to split selection")
    parser.add_argument("--report-name", help="Report filename; defaults to split download report")
    args = parser.parse_args()
    selection = json.loads((OUT / (args.selection_name or f"{args.split}_selection.json")).read_text(encoding="utf-8"))
    rows = selection["rows"]
    hashes, failures = {}, {}
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = {pool.submit(fetch, args.split, row): row["image_id"] for row in rows}
        for future in as_completed(futures):
            image_id = futures[future]
            try:
                key, digest = future.result()
                hashes[key] = digest
            except Exception as exc:
                failures[image_id] = str(exc)
    report = {"split": args.split, "selected": len(rows), "downloaded_verified": len(hashes),
              "sha256_by_image_id": hashes, "failures": failures}
    path = OUT / (args.report_name or f"{args.split}_download_report.json")
    path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({key: value for key, value in report.items()
                      if key != "sha256_by_image_id"}, indent=2))
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
