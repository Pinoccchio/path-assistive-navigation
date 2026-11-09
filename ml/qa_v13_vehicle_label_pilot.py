"""Verify v13 differs from v12 only by two approved bicycle train boxes."""

from build_v13_vehicle_label_pilot import LEDGER, SOURCE, TARGET
from qa_v12_vehicle_label_pilot import verify


if __name__ == "__main__":
    verify(SOURCE, TARGET, LEDGER)
