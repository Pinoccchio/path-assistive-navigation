"""Create deterministic annotation contact sheets for targeted semantic review."""

import argparse
import json
from pathlib import Path

from PIL import Image, ImageDraw

from phase1 import NAMES, ROOT


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset-name", default="public_phase1_v6_curated_candidate")
    parser.add_argument("--classes", type=int, nargs="+", default=[3, 4])
    parser.add_argument("--source", default="rod")
    parser.add_argument("--page-size", type=int, default=30)
    parser.add_argument("--v7-selected", action="store_true", help="Only images proposed for v7 bicycle correction")
    args = parser.parse_args()
    dataset = ROOT / "data" / "processed" / args.dataset_name
    rows = [json.loads(line) for line in (dataset / "dataset_manifest.jsonl").read_text(encoding="utf-8").splitlines()]
    if args.v7_selected:
        from build_v7_curated import INVALID_BICYCLE_IDS
        rows = [row for row in rows if row["id"] in INVALID_BICYCLE_IDS]
    output = ROOT / "runs" / args.dataset_name / "semantic_review"
    output.mkdir(parents=True, exist_ok=True)
    for class_id in args.classes:
        for split in ("train", "val", "test"):
            selected = [row for row in rows if row["split"] == split and class_id in row["class_ids"]
                        and row["source"].lower().startswith(args.source.lower())]
            for start in range(0, len(selected), args.page_size):
                sheet = Image.new("RGB", (1500, 900), "white")
                for offset, row in enumerate(selected[start:start + args.page_size]):
                    with Image.open(dataset / "images" / split / f"{row['id']}.jpg") as source:
                        image = source.convert("RGB")
                    draw = ImageDraw.Draw(image)
                    width, height = image.size
                    for line in (dataset / "labels" / split / f"{row['id']}.txt").read_text(encoding="utf-8").splitlines():
                        label, cx, cy, bw, bh = map(float, line.split())
                        if int(label) != class_id:
                            continue
                        xy = ((cx - bw / 2) * width, (cy - bh / 2) * height,
                              (cx + bw / 2) * width, (cy + bh / 2) * height)
                        draw.rectangle(xy, outline="red", width=max(2, width // 200))
                    image.thumbnail((296, 132))
                    col, row_index = offset % 5, offset // 5
                    x, y = col * 300, row_index * 150
                    sheet.paste(image, (x + (300 - image.width) // 2, y + 16))
                    ImageDraw.Draw(sheet).text((x + 3, y + 2), row["id"], fill="black")
                suffix = "_v7selected" if args.v7_selected else ""
                path = output / f"{NAMES[class_id]}_{split}_{args.source}{suffix}_{start // args.page_size + 1:02d}.jpg"
                sheet.save(path, quality=90)
                print(path)


if __name__ == "__main__":
    main()
