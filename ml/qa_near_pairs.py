"""Render candidate train/test near-duplicate pairs for manual review."""

import argparse
import json
import math

from PIL import Image, ImageDraw

from phase1 import OUTPUT, ROOT


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", default="public_phase1_v1")
    parser.add_argument("--report", default="qa_inventory.json")
    parser.add_argument("--key", default="cross_split_dhash_pairs_at_most_13")
    args = parser.parse_args()
    report = json.loads((ROOT / "runs" / args.dataset / args.report).read_text(encoding="utf-8"))
    pairs = report[args.key][:40]
    target_dir = ROOT / "runs" / args.dataset / "qa_sheets"
    target_dir.mkdir(exist_ok=True)
    for page in range(math.ceil(len(pairs) / 10)):
        sheet = Image.new("RGB", (1000, 1250), "white")
        for offset, pair in enumerate(pairs[page * 10:(page + 1) * 10]):
            x, y = (offset % 2) * 500, (offset // 2) * 250
            for side, key in enumerate(("train", "test")):
                path = ROOT / "data" / "processed" / args.dataset / "images" / key / f"{pair[key]}.jpg"
                with Image.open(path) as source:
                    image = source.convert("RGB")
                image.thumbnail((245, 220))
                sheet.paste(image, (x + side * 250, y + 25))
            draw = ImageDraw.Draw(sheet)
            draw.text((x + 3, y + 2), f"d={pair['distance']} train:{pair['train'][-12:]} test:{pair['test'][-12:]}", fill="black")
        target = target_dir / f"near_pairs_{page + 1}.jpg"
        sheet.save(target, quality=90)
        print(target)


if __name__ == "__main__":
    main()
