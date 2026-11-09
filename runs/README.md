# Experiment records

This part of the monorepo retains existing metrics, CSV/JSON reports, plots, configuration, prediction examples and export/parity metadata.

Training checkpoints and duplicate exported model files (`.pt`, `.onnx`, `.tflite`, accelerator binaries and tensor dumps) remain local rather than duplicating hundreds of megabytes in Git. Nothing was deleted locally. The app's required runtime checkpoint remains versioned under [`apps/mobile/assets/model/`](../apps/mobile/assets/model/).

Use the experiment-specific reports and [ml/README.md](../ml/README.md) to identify the dataset version, training settings and export path. Saved reports are research evidence; loading the repository is not a reason to rerun training or overwrite the recorded experiments.
