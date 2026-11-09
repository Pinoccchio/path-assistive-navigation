"""Render v3 images of a selected class for manual semantic review."""

import argparse
import csv
from pathlib import Path

from PIL import Image, ImageDraw

from phase1 import ROOT


DATASET = ROOT / "data" / "processed" / "public_phase1_v3_screened"
NAMES = {2: "stairs", 5: "electrical_pole", 6: "plant_pot"}


def render(row, class_id):
    path = Path(row["image_path"])
    with Image.open(path) as source:
        canvas = source.convert("RGB")
    width, height = canvas.size
    draw = ImageDraw.Draw(canvas)
    label = DATASET / "labels" / row["split"] / f"{row['id']}.txt"
    for line in label.read_text(encoding="utf-8").splitlines():
        cls, cx, cy, bw, bh = map(float, line.split())
        if int(cls) != class_id:
            continue
        box = ((cx - bw / 2) * width, (cy - bh / 2) * height,
               (cx + bw / 2) * width, (cy + bh / 2) * height)
        draw.rectangle(box, outline="#00ff40", width=max(3, width // 160))
    canvas.thumbnail((390, 320))
    tile = Image.new("RGB", (400, 360), "white")
    tile.paste(canvas, ((400 - canvas.width) // 2, 30 + (320 - canvas.height) // 2))
    ImageDraw.Draw(tile).text((5, 5), f"{row['split']} | {row['id']}", fill="black")
    return tile


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--class-id", type=int, choices=sorted(NAMES), default=5)
    parser.add_argument("--split", choices=("train", "val", "test"), default=None)
    args = parser.parse_args()
    output = ROOT / "runs" / "public_phase1_v3_screened" / f"{NAMES[args.class_id]}_review"
    with (DATASET / "semantic_review_queue.csv").open(newline="", encoding="utf-8") as file:
        rows = [row for row in csv.DictReader(file)
                if NAMES[args.class_id] in row["classes"] and
                (args.split is None or row["split"] == args.split)]
    output.mkdir(parents=True, exist_ok=True)
    for start in range(0, len(rows), 12):
        sheet = Image.new("RGB", (1600, 1080), "white")
        for index, row in enumerate(rows[start:start + 12]):
            sheet.paste(render(row, args.class_id), ((index % 4) * 400, (index // 4) * 360))
        suffix = f"{args.split}_" if args.split else ""
        path = output / f"{suffix}{NAMES[args.class_id]}_{start // 12 + 1:02d}.jpg"
        sheet.save(path, quality=92)
        print(path)


if __name__ == "__main__":
    main()
