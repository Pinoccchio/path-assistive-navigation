# path-assistive-navigation

[PATH quick guide: Test, Live, calibration, export, and progress](docs/05_Product/PATH_QUICK_GUIDE.md)

**PATH** is the Group 8 assistive-navigation thesis monorepo. It keeps the Flutter Android app, ML tooling, research notebooks, thesis documents, experiment reports, QA evidence, and development skills together in one repository.

The current manuscript title is **Development of a Mobile Assistive Navigation Prototype for Visually Impaired Users**. Start with [TEAM_START_HERE.md](TEAM_START_HERE.md) for the research journey and [apps/mobile/README.md](apps/mobile/README.md) for the app.

| Area | Repository path |
| --- | --- |
| Android app, runtime model, fonts and artwork | [`apps/mobile/`](apps/mobile/) |
| Dataset preparation, model training and evaluation | [`ml/`](ml/) |
| Research notebooks | [`notebooks/`](notebooks/) |
| Thesis manuscript, proposal, presentations and product requirements | [`docs/`](docs/) |
| Dataset manifests and reproducibility records | [`data/`](data/README.md) |
| Experiment reports, plots and export metadata | [`runs/`](runs/README.md) |
| UI screenshots and local QA resources | [`qa/`](qa/) |
| Figma export and presentation utilities | [`scripts/`](scripts/) |
| Project development skills | [`.agents/skills/`](.agents/skills/) |

Downloaded datasets, generated image/label copies, virtual environments, build caches, duplicate training checkpoints and raw Figma API exports remain local. The bundled model required by the Flutter app is included. See the data and experiment guides above for the artifact boundary. Credentials and machine-specific settings are excluded.

To work on the app, install a compatible Flutter SDK, run `flutter pub get` from `apps/mobile`, and follow its README. Python research dependencies are split into the root `requirements-*.txt` files; create your own virtual environment. A fresh clone contains source and records, not the multi-gigabyte dataset downloads.

## Research workspace

This workspace contains the Group 8 thesis documents, public-data detector experiments, and a Flutter Android **research test app**. Start with the [short team guide](TEAM_START_HERE.md) for the project journey, model comparisons, tools, phone status, and current limits. The app does not validate distance estimation or navigation safety.

| Location | Contents |
| --- | --- |
| `notebooks/01_yolov8n_training_pilot.ipynb` | Dataset preparation, baseline, five-epoch training, validation, and saved experiment record |
| `notebooks/02_training_progress_presenter.ipynb` | Meeting-friendly explanation and examples from the saved pilot |
| `data/source/` and `data/processed/` | Downloaded source metadata and prepared image/label datasets |
| `runs/yolov8n_pilot/` | Trained weights, metrics, plots, and prediction examples |
| `docs/` | Proposal, literature review, presentation, manuscript, and archives |
| `docs/05_Product/Assistive_Navigation_PRD.md` | Phased app, dataset, model, and evaluation requirements |
| `ml/` | Public-data acquisition, rights ledger, versioned label policies, split audits, model training, evaluation, and export workflow |
| `apps/mobile/` | Flutter Android prototype with live eight-class TFLite detection and bounding boxes; spoken alerts and distance estimates are not enabled |
| `scripts/` | Presentation generation and layout-audit scripts |

Use a Python environment with `requirements-training.txt` for the notebooks. Open them from the workspace root or a subfolder. The training notebook can download data, rewrite prepared data and results, and use the GPU, so do not rerun it merely to inspect the recorded findings. The presenter notebook reads saved metrics and generates example predictions.

For the current Phase 1 public-data work, follow [ml/README.md](ml/README.md). Its public test set is separate from the later campus test; no campus validation has been completed.

The Python slide generator also needs `requirements-presentations.txt`. Presentation scripts:

```powershell
python scripts/generate_ppt.py --output <temporary-or-final-pptx-path>
powershell -File scripts/build_training_progress.ps1 -OutputPath <temporary-or-final-pptx-path> -RenderDir <temporary-render-directory>
powershell -File scripts/audit_training_progress.ps1 -DeckPath <pptx-path>
```

The generators require `--force` or `-Force` to replace an existing deck. Both PowerShell scripts use Microsoft PowerPoint automation. Existing slides and research documents are historical material; verify their claims against the current manuscript before presenting them.
