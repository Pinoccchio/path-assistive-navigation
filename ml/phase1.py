"""Reproducible public-data stage for the seven-class detector.

Run from the workspace root with ``.venv/Scripts/python.exe ml/phase1.py --help``.
The historical pilot data and runs are never modified.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import random
import shutil
import platform
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import pyarrow.parquet as pq
import requests
from PIL import Image, ImageOps


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data" / "source" / "rod_public_phase1"
OUTPUT = ROOT / "data" / "processed" / "public_phase1_v1"
OI_SOURCE = ROOT / "data" / "source" / "oi_public_phase1"
HF = "https://huggingface.co/datasets/Abtinzandi/Obstacle-Detection-Dataset-YOLO/resolve/main"
PARQUET = "https://huggingface.co/datasets/Abtinzandi/Obstacle-Detection-Dataset-YOLO/resolve/refs%2Fconvert%2Fparquet/default"
REMOTE_SPLIT = {"train": "train", "validation": "valid", "test": "test"}
NAMES = ("person", "chair", "stairs", "car", "bicycle", "electrical_pole", "plant_pot")
ROD_TO_TARGET = {3: 0, 23: 1, 4: 2, 2: 3, 0: 4, 6: 5, 21: 6}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def get(session: requests.Session, url: str) -> bytes:
    response = session.get(url, timeout=90)
    response.raise_for_status()
    return response.content


def metadata(session: requests.Session, split: str) -> list[dict]:
    path = SOURCE / f"{split}.parquet"
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(get(session, f"{PARQUET}/{split}/0000.parquet"))
    return pq.read_table(path).to_pylist()


def labels(row: dict) -> list[tuple[int, float, float, float, float]]:
    selected = []
    for box in json.loads(row["bboxes_yolo"]):
        target = ROD_TO_TARGET.get(int(box["class_id"]))
        if target is None:
            continue
        x, y, w, h = (float(box[key]) for key in ("x_center", "y_center", "width", "height"))
        if w <= 0 or h <= 0 or not all(0 <= v <= 1 for v in (x, y, w, h)):
            continue
        if x - w / 2 < 0 or y - h / 2 < 0 or x + w / 2 > 1 or y + h / 2 > 1:
            continue
        selected.append((target, x, y, w, h))
    return selected


def valid_yolo_line(line: str) -> bool:
    try:
        parts = line.split()
        if len(parts) != 5:
            return False
        class_id, x, y, w, h = map(float, parts)
        return (class_id.is_integer() and 0 <= class_id < len(NAMES) and w > 0 and h > 0
                and x - w / 2 >= -1e-6 and y - h / 2 >= -1e-6
                and x + w / 2 <= 1 + 1e-6 and y + h / 2 <= 1 + 1e-6)
    except ValueError:
        return False


def choose(rows: list[dict], limit: int, seed: int, block_size: int = 5) -> list[dict]:
    """Round-robin across rare classes; sample one of each near-frame block."""
    rng = random.Random(seed)
    candidates = [row for row in rows if labels(row)]
    rng.shuffle(candidates)
    by_class: dict[int, list[dict]] = defaultdict(list)
    for row in candidates:
        for class_id in {box[0] for box in labels(row)}:
            by_class[class_id].append(row)
    selected, seen, blocks = [], set(), set()
    while len(selected) < limit and any(by_class.values()):
        for class_id in range(len(NAMES)):
            while by_class[class_id]:
                row = by_class[class_id].pop()
                name = Path(row["file_name"]).name
                number = int(Path(name).stem.split("_")[-1])
                block = number // block_size
                if name in seen or block in blocks:
                    continue
                selected.append(row)
                seen.add(name)
                blocks.add(block)
                break
            if len(selected) >= limit:
                break
    return selected


def acquire(args: argparse.Namespace) -> None:
    SOURCE.mkdir(parents=True, exist_ok=True)
    session = requests.Session()
    split_limits = {"train": args.train, "validation": args.val, "test": args.test}
    ledger_path = SOURCE / "manifest.jsonl"
    existing = {}
    if ledger_path.exists():
        for line in ledger_path.read_text(encoding="utf-8").splitlines():
            entry = json.loads(line)
            existing[(entry["source_split"], entry["source_id"])] = entry
    with ledger_path.open("a", encoding="utf-8") as ledger:
        for source_split, limit in split_limits.items():
            if limit == 0:
                continue
            rows = metadata(session, source_split)
            chosen = choose(rows, limit, args.seed + len(source_split),
                            args.test_block_size if source_split == "test" else 5)
            print(f"{source_split}: {len(chosen)} candidates", flush=True)
            pending = []
            for row in chosen:
                source_id = Path(row["file_name"]).stem
                key = (source_split, source_id)
                if key in existing:
                    continue
                pending.append(row)

            def fetch(row: dict) -> tuple[dict, bytes]:
                url = f"{HF}/{REMOTE_SPLIT[source_split]}/{row['file_name']}"
                content = requests.get(url, timeout=90)
                content.raise_for_status()
                data = content.content
                image = Image.open(io.BytesIO(data))
                image.verify()
                return row, data

            with ThreadPoolExecutor(max_workers=args.workers) as pool:
                futures = {pool.submit(fetch, row): row for row in pending}
                for index, future in enumerate(as_completed(futures), 1):
                    row = futures[future]
                    source_id = Path(row["file_name"]).stem
                    url = f"{HF}/{REMOTE_SPLIT[source_split]}/{row['file_name']}"
                    try:
                        _, content = future.result()
                    except (requests.RequestException, OSError) as exc:
                        print(f"skip {source_id}: {exc}", flush=True)
                        continue
                    dest = SOURCE / "images" / source_split / f"{source_id}.jpg"
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    dest.write_bytes(content)
                    entry = {
                        "source": "ROD", "source_split": source_split, "source_id": source_id,
                        "source_url": url, "sha256": sha256(content), "class_ids": sorted({b[0] for b in labels(row)}),
                        "boxes": labels(row), "license_status": "source_provenance_pending",
                        "group": f"{source_split}:{int(source_id.split('_')[-1]) // 5}",
                    }
                    ledger.write(json.dumps(entry) + "\n")
                    ledger.flush()
                    existing[(source_split, source_id)] = entry
                    if index % 100 == 0:
                        print(f"{source_split}: {index}/{len(pending)}", flush=True)
    print(f"manifest: {ledger_path}")


def dhash(path: Path) -> int:
    with Image.open(path) as image:
        image = ImageOps.exif_transpose(image).convert("L").resize((9, 8))
        pixels = list(image.getdata())
    bits = 0
    for row in range(8):
        for col in range(8):
            bits = (bits << 1) | int(pixels[row * 9 + col] > pixels[row * 9 + col + 1])
    return bits


def build(args: argparse.Namespace) -> None:
    manifest = SOURCE / "manifest.jsonl"
    if not manifest.exists():
        raise SystemExit("Run acquire first")
    entries = [json.loads(line) for line in manifest.read_text(encoding="utf-8").splitlines()]
    oi_manifest = OI_SOURCE / "manifest.jsonl"
    if oi_manifest.exists():
        entries.extend(json.loads(line) for line in oi_manifest.read_text(encoding="utf-8").splitlines())
    # Reserve test images before de-duplicating validation and training images.
    priority = {"test": 0, "validation": 1, "train": 2}
    entries.sort(key=lambda entry: (priority[entry["source_split"]], entry["source"], entry["source_id"]))
    prior = ROOT / "data" / "processed" / "rod_pilot_7class"
    # The pilot is retained as training evidence; the new build copies it.
    accepted, rejected, exact, hashes = [], [], {}, []
    for entry in entries:
        split = {"train": "train", "validation": "val", "test": "test"}[entry["source_split"]]
        source_root = SOURCE if entry["source"] == "ROD" else OI_SOURCE
        path = source_root / "images" / entry["source_split"] / f"{entry['source_id']}.jpg"
        if not path.exists():
            rejected.append((entry["source_id"], "missing_image"))
            continue
        if not entry["boxes"]:
            rejected.append((entry["source_id"], "no_valid_target_boxes"))
            continue
        digest = sha256(path.read_bytes())
        if digest != entry["sha256"]:
            rejected.append((entry["source_id"], "checksum_mismatch"))
            continue
        fingerprint = dhash(path)
        if digest in exact or any((fingerprint ^ old).bit_count() <= args.max_hash_distance for old, _ in hashes):
            rejected.append((entry["source_id"], "duplicate_or_near_duplicate"))
            continue
        exact[digest] = split
        hashes.append((fingerprint, split))
        accepted.append((entry, split, path))
    if OUTPUT.exists():
        raise SystemExit(f"Output exists: {OUTPUT}; move or version it explicitly before rebuilding")
    for split in ("train", "val", "test"):
        (OUTPUT / "images" / split).mkdir(parents=True)
        (OUTPUT / "labels" / split).mkdir(parents=True)
    processed_manifest = []
    for entry, split, source_path in accepted:
        name = f"{entry['source'].lower()}_{entry['source_split']}_{entry['source_id']}"
        shutil.copy2(source_path, OUTPUT / "images" / split / f"{name}.jpg")
        content = "\n".join(" ".join([str(int(box[0]))] + [f"{v:.7f}" for v in box[1:]]) for box in entry["boxes"])
        (OUTPUT / "labels" / split / f"{name}.txt").write_text(content + "\n", encoding="utf-8")
        processed_manifest.append({"id": name, "split": split, "source": entry["source"],
                                   "source_id": entry["source_id"], "sha256": entry["sha256"],
                                   "class_ids": entry["class_ids"], "group": entry["group"],
                                   "license_status": entry["license_status"]})
    # Include the old pilot only in train, avoiding its validation reuse as test.
    pilot_added = 0
    if args.include_pilot:
        for old_split in ("train", "val"):
            for path in (prior / "images" / old_split).glob("*.jpg"):
                label = prior / "labels" / old_split / f"{path.stem}.txt"
                if not label.exists():
                    continue
                original_lines = [line for line in label.read_text(encoding="utf-8").splitlines() if line.strip()]
                clean_lines = [line for line in original_lines if valid_yolo_line(line)]
                if len(clean_lines) != len(original_lines):
                    rejected.append((f"pilot_{old_split}_{path.stem}", "invalid_pilot_box_removed"))
                if not clean_lines:
                    continue
                digest = sha256(path.read_bytes())
                fingerprint = dhash(path)
                if digest in exact or any((fingerprint ^ old).bit_count() <= args.max_hash_distance for old, _ in hashes):
                    rejected.append((f"pilot_{old_split}_{path.stem}", "duplicate_or_near_duplicate"))
                    continue
                exact[digest] = "train"
                hashes.append((fingerprint, "train"))
                name = f"pilot_{old_split}_{path.stem}"
                shutil.copy2(path, OUTPUT / "images" / "train" / f"{name}.jpg")
                (OUTPUT / "labels" / "train" / f"{name}.txt").write_text("\n".join(clean_lines) + "\n", encoding="utf-8")
                pilot_added += 1
                class_ids = sorted({int(line.split()[0]) for line in clean_lines})
                processed_manifest.append({"id": name, "split": "train", "source": "ROD_pilot",
                                           "source_id": path.stem, "sha256": digest, "class_ids": class_ids,
                                           "group": f"pilot:{int(path.stem.split('_')[-1]) // 5}",
                                           "license_status": "source_provenance_pending"})
    (OUTPUT / "dataset.yaml").write_text(
        "path: " + OUTPUT.as_posix() + "\ntrain: images/train\nval: images/val\ntest: images/test\n"
        + "names:\n" + "".join(f"  {i}: {name}\n" for i, name in enumerate(NAMES)), encoding="utf-8")
    with (OUTPUT / "dataset_manifest.jsonl").open("w", encoding="utf-8") as file:
        for row in processed_manifest:
            file.write(json.dumps(row) + "\n")
    report = {"accepted": dict(Counter(split for _, split, _ in accepted)),
              "rejected": dict(Counter(reason for _, reason in rejected)),
              "pilot_copied_to_train": pilot_added,
              "final_split_counts": dict(Counter(row["split"] for row in processed_manifest)),
              "source_counts": dict(Counter(row["source"] for row in processed_manifest)),
              "class_image_counts": {split: {NAMES[class_id]: sum(row["split"] == split and class_id in row["class_ids"] for row in processed_manifest)
                                            for class_id in range(len(NAMES))} for split in ("train", "val", "test")},
              "near_duplicate_hash_distance": args.max_hash_distance,
              "rights_status": "ROD source provenance and Open Images original-image licenses require review before redistribution"}
    (OUTPUT / "build_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    with (OUTPUT / "rejected.csv").open("w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(("source_id", "reason"))
        writer.writerows(rejected)
    print(json.dumps(report, indent=2))


def audit(args: argparse.Namespace) -> None:
    """Check every generated label; --fix only changes generated copies."""
    manifest_path = OUTPUT / "dataset_manifest.jsonl"
    rows = [json.loads(line) for line in manifest_path.read_text(encoding="utf-8").splitlines()]
    kept, problems = [], []
    for row in rows:
        label = OUTPUT / "labels" / row["split"] / f"{row['id']}.txt"
        image = OUTPUT / "images" / row["split"] / f"{row['id']}.jpg"
        if not label.exists() or not image.exists():
            problems.append((row["id"], "missing_pair"))
            continue
        original = [line for line in label.read_text(encoding="utf-8").splitlines() if line.strip()]
        clean = [line for line in original if valid_yolo_line(line)]
        if len(clean) != len(original):
            problems.append((row["id"], f"invalid_boxes:{len(original) - len(clean)}"))
        if not clean:
            problems.append((row["id"], "no_valid_boxes"))
            if args.fix:
                label.unlink()
                image.unlink()
            continue
        if args.fix and len(clean) != len(original):
            label.write_text("\n".join(clean) + "\n", encoding="utf-8")
            row["class_ids"] = sorted({int(line.split()[0]) for line in clean})
        if "group" not in row:
            if row["source"] == "OpenImagesV7":
                row["group"] = f"openimages:{row['source_id']}"
            else:
                row["group"] = f"{row['source']}:{int(row['source_id'].split('_')[-1]) // 5}"
        kept.append(row)
    if args.fix:
        manifest_path.write_text("".join(json.dumps(row) + "\n" for row in kept), encoding="utf-8")
        review_path = OUTPUT / "stairs_and_poles_review.csv"
        with review_path.open("w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(("id", "split", "source", "classes", "image_path", "review_status", "correction_notes"))
            for row in kept:
                if 2 in row["class_ids"] or 5 in row["class_ids"]:
                    writer.writerow((row["id"], row["split"], row["source"],
                                     ";".join(NAMES[index] for index in row["class_ids"] if index in (2, 5)),
                                     str(OUTPUT / "images" / row["split"] / f"{row['id']}.jpg"), "pending", ""))
        report_path = OUTPUT / "build_report.json"
        report = json.loads(report_path.read_text(encoding="utf-8"))
        report["final_split_counts"] = dict(Counter(row["split"] for row in kept))
        report["source_counts"] = dict(Counter(row["source"] for row in kept))
        report["pilot_copied_to_train"] = sum(row["source"] == "ROD_pilot" for row in kept)
        report["class_image_counts"] = {split: {NAMES[class_id]: sum(row["split"] == split and class_id in row["class_ids"] for row in kept)
                                                for class_id in range(len(NAMES))} for split in ("train", "val", "test")}
        report["class_group_counts"] = {split: {NAMES[class_id]: len({row["group"] for row in kept if row["split"] == split and class_id in row["class_ids"]})
                                                for class_id in range(len(NAMES))} for split in ("train", "val", "test")}
        report["post_build_audit"] = {"problems": len(problems), "removed_empty_images": len(rows) - len(kept)}
        report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({"images": len(rows), "problems": len(problems), "removed_empty_images": len(rows) - len(kept) if args.fix else 0}, indent=2))
    if problems and not args.fix:
        raise SystemExit(1)


def train(args: argparse.Namespace) -> None:
    from ultralytics import YOLO
    from ultralytics import __version__ as ultralytics_version
    import torch
    dataset = OUTPUT / "dataset.yaml"
    if not dataset.exists():
        raise SystemExit("Run build first")
    run_root = ROOT / "runs" / "public_phase1_v1"
    run_root.mkdir(parents=True, exist_ok=True)
    environment = {"python": platform.python_version(), "torch": torch.__version__,
                   "cuda_runtime": torch.version.cuda, "cuda_available": torch.cuda.is_available(),
                   "gpu": torch.cuda.get_device_name(0) if torch.cuda.is_available() else None,
                   "ultralytics": ultralytics_version, "seed": 42, "epochs": args.epochs,
                   "batch": args.batch, "imgsz": 512,
                   "dataset_manifest_sha256": sha256((OUTPUT / "dataset_manifest.jsonl").read_bytes()),
                   "initial_weights_sha256": sha256((ROOT / "notebooks" / "yolov8n.pt").read_bytes())}
    (run_root / "environment.json").write_text(json.dumps(environment, indent=2), encoding="utf-8")
    model = YOLO(str(ROOT / "notebooks" / "yolov8n.pt"))
    model.train(data=str(dataset), epochs=args.epochs, imgsz=512, batch=args.batch,
                seed=42, deterministic=True, device=args.device, workers=2,
                project=str(ROOT / "runs" / "public_phase1_v1"), name="yolov8n", exist_ok=True)


def evaluate(args: argparse.Namespace) -> None:
    from ultralytics import YOLO
    evaluation_root = ROOT / "runs" / "public_phase1_v1"
    weights = {"candidate": args.weights}
    if args.baseline:
        weights["pilot"] = str(ROOT / "runs" / "yolov8n_pilot" / "finetune_7class_5epoch" / "weights" / "best.pt")
    for name, path in weights.items():
        model = YOLO(path)
        result = model.val(data=str(OUTPUT / "dataset.yaml"), split="test", imgsz=512,
                           batch=args.batch, device=args.device,
                           project=str(evaluation_root), name=f"public_test_{name}", exist_ok=True)
        by_index = {}
        for position, class_id in enumerate(result.box.ap_class_index):
            by_index[int(class_id)] = {"precision": float(result.box.p[position]),
                                       "recall": float(result.box.r[position]),
                                       "map50": float(result.box.ap50[position]),
                                       "map50_95": float(result.box.ap[position])}
        report = {"model": name, "weights": path, "test_split": str(OUTPUT / "images" / "test"),
                  "overall": {key: float(value) for key, value in result.results_dict.items()},
                  "per_class": {NAMES[index]: by_index.get(index) for index in range(len(NAMES))}}
        out = evaluation_root / f"public_test_{name}_summary.json"
        out.write_text(json.dumps(report, indent=2), encoding="utf-8")
        print(f"{name}: {out}")


def export(args: argparse.Namespace) -> None:
    from ultralytics import YOLO
    model = YOLO(args.weights)
    output = Path(model.export(format="tflite", imgsz=512, int8=args.int8,
                               data=str(OUTPUT / "dataset.yaml") if args.int8 else None))
    metadata = {"format": "tflite_int8" if args.int8 else "tflite_fp32",
                "file": str(output), "sha256": sha256(output.read_bytes()),
                "source_weights": args.weights, "source_weights_sha256": sha256(Path(args.weights).read_bytes()),
                "class_names": list(NAMES), "input_size": 512,
                "status": "desktop_export_only_phone_and_prediction_parity_pending"}
    record = ROOT / "runs" / "public_phase1_v1" / ("export_int8.json" if args.int8 else "export_fp32.json")
    record.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    print(record)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    acquire_parser = sub.add_parser("acquire")
    acquire_parser.add_argument("--train", type=int, default=3000)
    acquire_parser.add_argument("--val", type=int, default=400)
    acquire_parser.add_argument("--test", type=int, default=400)
    acquire_parser.add_argument("--seed", type=int, default=42)
    acquire_parser.add_argument("--workers", type=int, default=8)
    acquire_parser.add_argument("--test-block-size", type=int, default=5)
    build_parser = sub.add_parser("build")
    build_parser.add_argument("--max-hash-distance", type=int, default=4)
    build_parser.add_argument("--include-pilot", action="store_true")
    audit_parser = sub.add_parser("audit")
    audit_parser.add_argument("--fix", action="store_true")
    for command in ("train", "evaluate", "export"):
        item = sub.add_parser(command)
        item.add_argument("--device", default="0")
        item.add_argument("--batch", type=int, default=4)
        item.add_argument("--weights", default=str(ROOT / "runs" / "public_phase1_v1" / "yolov8n" / "weights" / "best.pt"))
        if command == "train":
            item.add_argument("--epochs", type=int, default=30)
        if command == "evaluate":
            item.add_argument("--baseline", action="store_true")
        if command == "export":
            item.add_argument("--int8", action="store_true")
    args = parser.parse_args()
    {"acquire": acquire, "build": build, "audit": audit, "train": train,
     "evaluate": evaluate, "export": export}[args.command](args)


if __name__ == "__main__":
    main()
