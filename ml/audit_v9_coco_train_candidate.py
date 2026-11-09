"""Verify v9 preserves every v8 sample and adds only frozen COCO train images."""

import hashlib
import json
import zipfile

from build_v9_coco_train_candidate import DATA, MAP, SELECTION, SOURCE, TARGET, ZIP


def main():
    old = [json.loads(line) for line in (SOURCE / "dataset_manifest.jsonl").read_text(encoding="utf-8").splitlines()]
    new = [json.loads(line) for line in (TARGET / "dataset_manifest.jsonl").read_text(encoding="utf-8").splitlines()]
    selected = json.loads(SELECTION.read_text(encoding="utf-8"))["rows"]
    assert new[:len(old)] == old
    assert len(new) == len(old) + len(selected) == 3819
    for row in old:
        split, stem = row["split"], row["id"]
        a = SOURCE / "images" / split / f"{stem}.jpg"
        b = TARGET / "images" / split / f"{stem}.jpg"
        assert a.samefile(b)
        assert (SOURCE / "labels" / split / f"{stem}.txt").read_bytes() == (TARGET / "labels" / split / f"{stem}.txt").read_bytes()
    with zipfile.ZipFile(ZIP) as z:
        for row, actual in zip(selected, new[len(old):]):
            stem = "coco_train2017_" + row["image_id"]
            assert actual["id"] == stem and actual["split"] == "train"
            image = TARGET / "images" / "train" / f"{stem}.jpg"
            assert image.samefile(DATA / "train_images" / f'{row["image_id"]}.jpg')
            assert actual["sha256"] == hashlib.sha256(image.read_bytes()).hexdigest()
            label_path = f"coco/labels/train2017/{row['image_id']}.txt"
            raw = z.read(label_path).decode("utf-8").splitlines()
            mapped = [str(MAP[int(line.split()[0])]) + line[line.find(" "):] for line in raw
                      if line.strip() and int(line.split()[0]) in MAP]
            assert (TARGET / "labels" / "train" / f"{stem}.txt").read_text(encoding="utf-8").splitlines() == mapped
    assert len(list((TARGET / "images" / "train").glob("*.jpg"))) == 3012
    print(json.dumps({"old_images_preserved": len(old), "new_coco_train_images": len(selected),
                      "unexpected_changes": 0}))


if __name__ == "__main__":
    main()
