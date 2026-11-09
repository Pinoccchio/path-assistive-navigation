"""Inventory and visually sample one HOT-OSM utility-pole candidate shard."""

import argparse
import io
import json
from collections import Counter
from pathlib import Path

import pyarrow.parquet as pq
from PIL import Image, ImageDraw

from phase1 import ROOT, sha256


SOURCE = ROOT / "data" / "source" / "hotosm_pole_candidate"
SHARD = SOURCE / "val-00000-of-00002.parquet"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--shard", default=SHARD.name)
    args = parser.parse_args()
    shard = SOURCE / args.shard
    rows = []
    parquet = pq.ParquetFile(shard)
    for batch in parquet.iter_batches(batch_size=16):
        for row in batch.to_pylist():
            boxes = [box for box, cls in zip(row["objects"]["bbox"], row["objects"]["category"]) if cls == 0]
            rows.append({"id": row["image_id"], "width": row["width"], "height": row["height"],
                         "source": row["source"], "panoramax_id": row["panoramax_id"],
                         "source_url": row["source_url"], "pole_boxes": boxes,
                         "image_bytes": row["image"]["bytes"]})
    positive = [row for row in rows if row["pole_boxes"]]
    sample_count = min(30, len(positive))
    chosen = [positive[round(index * (len(positive) - 1) / (sample_count - 1))]
              for index in range(sample_count)] if sample_count > 1 else positive
    previews = SOURCE / "preview" / shard.stem
    previews.mkdir(parents=True, exist_ok=True)
    sheet = Image.new("RGB", (1500, ((len(chosen) + 5) // 6) * 240), "white")
    for index, row in enumerate(chosen):
        with Image.open(io.BytesIO(row["image_bytes"])) as source:
            image = source.convert("RGB")
        draw = ImageDraw.Draw(image)
        for x, y, width, height in row["pole_boxes"]:
            draw.rectangle((x, y, x + width, y + height), outline="#ff3333", width=8)
        image.thumbnail((245, 180))
        x, y = (index % 6) * 250, (index // 6) * 240
        sheet.paste(image, (x, y + 20))
        ImageDraw.Draw(sheet).text((x + 3, y + 3), f"{index}: {row['source']} {row['id'][:12]}", fill="black")
    sheet_path = previews / "pole_review_sheet.jpg"
    sheet.save(sheet_path, quality=90)
    summary = {"source_url": "https://huggingface.co/datasets/hotosm/streetlevel-poles",
               "license_listed": "CC-BY-SA-4.0", "shard": shard.name,
               "shard_sha256": sha256(shard.read_bytes()), "rows": len(rows), "pole_positive_rows": len(positive),
               "positive_source_counts": dict(Counter(row["source"] for row in positive)),
               "sample_ids": [row["id"] for row in chosen],
               "status": "candidate_not_integrated_into_seven_class_training"}
    (SOURCE / f"{shard.stem}_inventory.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps({key: value for key, value in summary.items() if key != "sample_ids"}, indent=2))
    print(sheet_path)


if __name__ == "__main__":
    main()
