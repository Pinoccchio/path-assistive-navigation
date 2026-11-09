"""Freeze and download a COCO train2017 small-bicycle annotation review batch."""

import hashlib
import json
import random
import urllib.request
import zipfile
from pathlib import Path

from PIL import Image, ImageDraw

from build_v9_coco_train_candidate import DATA, SELECTION, ZIP


OUT = DATA / "small_bicycle_review_v1"


def main():
    OUT.mkdir(exist_ok=True)
    selection_path = OUT / "selection.json"
    if selection_path.exists():
        selection = json.loads(selection_path.read_text(encoding="utf-8"))
        rows = selection["rows"]
    else:
        prior = {row["image_id"] for row in json.loads(SELECTION.read_text())["rows"]}
        pools = {"12_24": [], "24_40": []}
        with zipfile.ZipFile(ZIP) as archive:
            for path in archive.namelist():
                if not path.startswith("coco/labels/train2017/") or not path.endswith(".txt"):
                    continue
                image_id = path.rsplit("/", 1)[-1][:-4]
                if image_id in prior:
                    continue
                raw = archive.read(path)
                labels = [line.split() for line in raw.decode().splitlines() if line.strip()]
                if 58 in {int(row[0]) for row in labels}:
                    continue
                sizes = [max(float(row[3]), float(row[4])) * 512 for row in labels if int(row[0]) == 1]
                group = "12_24" if any(12 <= side < 24 for side in sizes) else "24_40" if any(24 <= side < 40 for side in sizes) else None
                if group:
                    pools[group].append({"image_id": image_id, "group": group,
                                         "label_sha256": hashlib.sha256(raw).hexdigest()})
        rng = random.Random(20261003)
        rows = [row for group in pools for row in rng.sample(sorted(pools[group], key=lambda r: r["image_id"]), 40)]
        selection = {"seed": 20261003, "purpose": "human review only; not training-approved",
                     "source": "COCO train2017", "annotation_source": "local third-party YOLO conversion",
                     "labels_zip_sha256": hashlib.sha256(ZIP.read_bytes()).hexdigest(),
                     "prior_coco_train_images_excluded": len(prior), "rows": rows}
        selection_path.write_text(json.dumps(selection, indent=2) + "\n", encoding="utf-8")
    images = OUT / "images"
    images.mkdir(exist_ok=True)
    for index, row in enumerate(rows, 1):
        dest = images / f'{row["image_id"]}.jpg'
        if not dest.exists():
            url = f'http://images.cocodataset.org/train2017/{row["image_id"]}.jpg'
            temp = dest.with_suffix(".part")
            urllib.request.urlretrieve(url, temp)
            with Image.open(temp) as image:
                image.verify()
            temp.replace(dest)
        if index % 20 == 0:
            print(f"downloaded/verified {index}/{len(rows)}", flush=True)
    with zipfile.ZipFile(ZIP) as archive:
        for page_start in range(0, len(rows), 20):
            sheet = Image.new("RGB", (1200, 5 * 230), "white")
            draw = ImageDraw.Draw(sheet)
            for slot, row in enumerate(rows[page_start:page_start + 20]):
                image_id = row["image_id"]
                with Image.open(images / f"{image_id}.jpg") as source:
                    source = source.convert("RGB")
                    source.thumbnail((285, 195))
                    x, y = (slot % 4) * 300, (slot // 4) * 230
                    sheet.paste(source, (x, y + 20))
                    label_path = f"coco/labels/train2017/{image_id}.txt"
                    for line in archive.read(label_path).decode().splitlines():
                        fields = line.split()
                        if fields and int(fields[0]) in (1, 3):
                            cx, cy, w, h = map(float, fields[1:5])
                            sx = source.width / Image.open(images / f"{image_id}.jpg").width
                            sy = source.height / Image.open(images / f"{image_id}.jpg").height
                            with Image.open(images / f"{image_id}.jpg") as original:
                                left = (cx - w / 2) * original.width * sx
                                top = (cy - h / 2) * original.height * sy
                                right = (cx + w / 2) * original.width * sx
                                bottom = (cy + h / 2) * original.height * sy
                            draw.rectangle((x + left, y + 20 + top, x + right, y + 20 + bottom),
                                           outline="lime" if int(fields[0]) == 1 else "red", width=2)
                    draw.text((x + 3, y + 3), f"{image_id} {row['group']}", fill="black")
            sheet.save(OUT / f"review_sheet_{page_start // 20 + 1}.jpg", quality=90)
    print(json.dumps({"candidates": len(rows), "review_sheets": 4,
                      "status": "pending full-resolution human annotation and image-license review"}))


if __name__ == "__main__":
    main()
