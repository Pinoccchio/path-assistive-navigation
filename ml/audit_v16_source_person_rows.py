"""Explain missing person labels by comparing quarantined IDs with raw OI rows."""

import csv
import json
from collections import Counter

from build_v16_person_quarantine import LEDGER, ROOT

SOURCE = ROOT / "data/source/oi_public_phase1/train_boxes.csv"
OUT = ROOT / "runs/public_phase1_v15_oi_quarantine/source_person_row_audit.json"


def main():
    ids = set(json.loads(LEDGER.read_text(encoding="utf-8"))["excluded"])
    by_image = {image_id: Counter() for image_id in ids}
    with SOURCE.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            image_id = row["ImageID"]
            if image_id not in ids or row["LabelName"] != "/m/01g317":
                continue
            if row["IsDepiction"] == "1":
                key = "depiction"
            elif row["IsGroupOf"] == "1":
                key = "group_of"
            else:
                key = "ordinary"
            by_image[image_id][key] += 1
    totals = Counter()
    for counts in by_image.values():
        totals.update(counts)
    report = {"raw_csv": str(SOURCE), "images": len(ids),
              "images_with_no_person_row": sum(not counts for counts in by_image.values()),
              "images_with_group_of_person_row": sum(counts["group_of"] > 0 for counts in by_image.values()),
              "images_with_depiction_person_row": sum(counts["depiction"] > 0 for counts in by_image.values()),
              "person_rows_by_type": dict(totals),
              "by_image": {key: dict(value) for key, value in sorted(by_image.items())}}
    OUT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: value for key, value in report.items() if key != "by_image"}, indent=2))


if __name__ == "__main__":
    main()
