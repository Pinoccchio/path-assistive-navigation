# Held-out public-label review (2026-09-28)

This is a visual audit of the v3 public test split, not a new model evaluation. The reviewed contact sheets are [pole](../runs/public_phase1_v3_screened/pole_review/), [stairs](../runs/public_phase1_v3_screened/stairs_review/), and [plant pot](../runs/public_phase1_v3_screened/plant_pot_review/). No v3 label files were edited.

The pole ledger lists 24 crossing-button-post images across splits. Three are in test. Under the narrower `electrical_pole` meaning (utility or electrical-service pole), those boxes are proposed for removal in the next dataset version. The remaining 96 pole images still need closer review; some distant campus-column-looking boxes cannot be classified with confidence from a contact sheet alone.

The 127 stair-labeled test images show a second issue: the source mixes a single box around a staircase with multiple boxes around individual steps. For a walking-assistance detector, the dataset needs one documented annotation policy before retraining or scoring. At least `openimagesv7_test_412e3fddac13e4cf` shows a ladder labeled as stairs and should have that class box removed. Other unusual stair images need full-resolution review before editing.

The 23 plant-pot-labeled test images include `rod_test_IMG_19194`, which shows an empty pot. If `plant_pot` means a planted container, remove that box in the next version. If the class is intended to include empty pots as physical obstacles, rename and document the class instead. Most other reviewed test images show plants in containers, but box tightness and partial visibility vary.

Do not recompute or compare model metrics using these proposed corrections alone. Finish the class definitions, review train and validation labels, build a new version, and evaluate that version with a clearly described test protocol. Campus validation remains deferred.
