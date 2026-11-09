"""Verify v14 differs from v13 only by approved motorcycle train boxes."""

from build_v14_motorcycle_label_pilot import LEDGER, SOURCE, TARGET
from qa_v12_vehicle_label_pilot import verify


if __name__ == "__main__":
    verify(SOURCE, TARGET, LEDGER)
