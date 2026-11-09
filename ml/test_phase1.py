"""Data-contract checks for the public-data pipeline."""

import json
import unittest

from phase1 import NAMES, choose, labels, valid_yolo_line
from openimages import MIDS, valid_box


class ClassMapTests(unittest.TestCase):
    def test_rod_seven_class_mapping_and_out_of_bounds_rejection(self):
        row = {"bboxes_yolo": json.dumps([
            {"class_id": 6, "x_center": .5, "y_center": .5, "width": .2, "height": .8},
            {"class_id": 4, "x_center": .9, "y_center": .5, "width": .4, "height": .2},
            {"class_id": 13, "x_center": .5, "y_center": .5, "width": .2, "height": .2},
        ])}
        self.assertEqual([box[0] for box in labels(row)], [5])
        self.assertEqual(NAMES[5], "electrical_pole")

    def test_open_images_mappings_do_not_invent_pole_or_pot(self):
        self.assertEqual(set(MIDS.values()), {0, 1, 2, 3, 4})
        row = {"LabelName": "/m/01lynh", "IsDepiction": "0", "IsGroupOf": "0",
               "XMin": "0.1", "XMax": "0.7", "YMin": "0.2", "YMax": "0.8"}
        self.assertEqual(valid_box(row)[0], 2)
        row["IsDepiction"] = "1"
        self.assertIsNone(valid_box(row))

    def test_rod_sampling_keeps_one_near_frame_block(self):
        box = json.dumps([{"class_id": 4, "x_center": .5, "y_center": .5,
                           "width": .2, "height": .2}])
        rows = [{"file_name": f"images/0/IMG_{number:05d}.jpg", "bboxes_yolo": box}
                for number in (10, 11, 12, 20)]
        self.assertEqual(len(choose(rows, 3, 42)), 2)

    def test_pilot_boxes_outside_image_are_rejected(self):
        self.assertTrue(valid_yolo_line("2 0.5 0.5 0.2 0.2"))
        self.assertFalse(valid_yolo_line("2 0.9 0.5 0.8 0.2"))
        self.assertFalse(valid_yolo_line("6 0.5 1.0 0.2 0.4"))


if __name__ == "__main__":
    unittest.main()
