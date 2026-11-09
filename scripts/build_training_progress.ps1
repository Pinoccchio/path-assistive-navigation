param(
    [string]$OutputPath,
    [string]$RenderDir,
    [switch]$Force
)

$ErrorActionPreference = 'Stop'

$root = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..')).Path
$output = if ($OutputPath) { [System.IO.Path]::GetFullPath($OutputPath) } else { Join-Path $root 'docs\03_Presentation\YOLOv8n_Training_Progress.pptx' }
$renderDir = if ($RenderDir) { [System.IO.Path]::GetFullPath($RenderDir) } else { Join-Path $root '.tmp\ppt_build\rendered' }
if ((Test-Path -LiteralPath $output) -and -not $Force) {
    throw "Output already exists: $output. Pass -Force to replace it."
}
New-Item -ItemType Directory -Force (Split-Path -Path $output -Parent) | Out-Null
$heroImage = Join-Path $root 'runs\yolov8n_pilot\presenter_examples\IMG_20825.jpg'
$montageImage = Join-Path $root 'runs\yolov8n_pilot\presenter_prediction_montage.png'

$msoFalse = 0
$msoTrue = -1
$msoTextOrientationHorizontal = 1
$msoShapeRectangle = 1
$ppLayoutBlank = 12
$ppSaveAsOpenXMLPresentation = 24

function RGB([int]$r, [int]$g, [int]$b) {
    return $r + ($g * 256) + ($b * 65536)
}

$ink = RGB 20 28 38
$muted = RGB 94 105 119
$blue = RGB 31 111 235
$paleBlue = RGB 229 241 255
$panel = RGB 244 246 248
$rule = RGB 210 216 224
$white = RGB 255 255 255
$green = RGB 24 128 91
$amber = RGB 180 103 15
$red = RGB 186 55 42

function Add-TextBox($slide, [string]$text, [float]$left, [float]$top, [float]$width, [float]$height, [float]$fontSize, [int]$color, [bool]$bold = $false, [int]$alignment = 1) {
    $shape = $slide.Shapes.AddTextbox($msoTextOrientationHorizontal, $left, $top, $width, $height)
    $shape.Line.Visible = $msoFalse
    $shape.Fill.Visible = $msoFalse
    $shape.TextFrame.MarginLeft = 0
    $shape.TextFrame.MarginRight = 0
    $shape.TextFrame.MarginTop = 0
    $shape.TextFrame.MarginBottom = 0
    $shape.TextFrame.WordWrap = $msoTrue
    $shape.TextFrame.TextRange.Text = $text
    $shape.TextFrame.TextRange.Font.Name = 'Aptos'
    $shape.TextFrame.TextRange.Font.Size = $fontSize
    $shape.TextFrame.TextRange.Font.Bold = $(if ($bold) { $msoTrue } else { $msoFalse })
    $shape.TextFrame.TextRange.Font.Color.RGB = $color
    $shape.TextFrame.TextRange.ParagraphFormat.Alignment = $alignment
    return $shape
}

function Add-Rect($slide, [float]$left, [float]$top, [float]$width, [float]$height, [int]$fillColor, [int]$lineColor = -1) {
    $shape = $slide.Shapes.AddShape($msoShapeRectangle, $left, $top, $width, $height)
    $shape.Fill.ForeColor.RGB = $fillColor
    if ($lineColor -eq -1) {
        $shape.Line.Visible = $msoFalse
    } else {
        $shape.Line.ForeColor.RGB = $lineColor
        $shape.Line.Weight = 0.75
    }
    return $shape
}

function Add-Rule($slide, [float]$left, [float]$top, [float]$width, [int]$color, [float]$height = 1.2) {
    return Add-Rect $slide $left $top $width $height $color
}

function Add-SlideChrome($slide, [string]$section, [int]$page) {
    Add-TextBox $slide $section.ToUpperInvariant() 42 21 500 14 10 $muted $true | Out-Null
    Add-TextBox $slide ([string]$page) 895 505 24 14 10 $muted $false 3 | Out-Null
}

function Add-SlideTitle($slide, [string]$title, [int]$page, [string]$section) {
    Add-SlideChrome $slide $section $page
    Add-TextBox $slide $title 42 45 870 62 35 $ink $true | Out-Null
    Add-Rule $slide 42 108 876 $rule 0.8 | Out-Null
}

function Add-Notes($slide, [string]$text) {
    try {
        $notes = $slide.NotesPage.Shapes
        for ($i = 1; $i -le $notes.Count; $i++) {
            $shape = $notes.Item($i)
            try {
                if ($shape.PlaceholderFormat.Type -eq 2) {
                    $shape.TextFrame.TextRange.Text = $text
                    return
                }
            } catch { }
        }
    } catch { }
}

function Add-StatRow($slide, [string]$label, [string]$value, [string]$meaning, [float]$top, [int]$valueColor = $ink) {
    Add-TextBox $slide $label 530 $top 150 24 16 $muted $true | Out-Null
    Add-TextBox $slide $value 675 ($top - 5) 160 33 24 $valueColor $true 3 | Out-Null
    Add-TextBox $slide $meaning 530 ($top + 27) 305 54 16 $muted $false | Out-Null
    Add-Rule $slide 530 ($top + 84) 305 $rule 0.7 | Out-Null
}

$ppt = $null
$presentation = $null
try {
    $ppt = New-Object -ComObject PowerPoint.Application
    $ppt.Visible = $msoTrue
    $ppt.WindowState = 2
    $presentation = $ppt.Presentations.Add()
    $presentation.PageSetup.SlideWidth = 960
    $presentation.PageSetup.SlideHeight = 540

    # Slide 1 - restrained cover
    $slide = $presentation.Slides.Add(1, $ppLayoutBlank)
    $slide.Background.Fill.ForeColor.RGB = $white
    Add-Rect $slide 0 0 8 540 $blue | Out-Null
    Add-TextBox $slide 'THESIS PROGRESS REPORT' 48 42 400 18 12 $blue $true | Out-Null
    Add-TextBox $slide 'YOLOv8n Training Progress' 48 108 455 145 50 $ink $true | Out-Null
    Add-TextBox $slide 'Preliminary obstacle-detection pilot for a mobile assistive navigation system' 48 264 420 72 20 $muted $false | Out-Null
    Add-TextBox $slide 'Group 8 - Assistive Navigation for Visually Impaired' 48 445 430 22 14 $ink $true | Out-Null
    Add-TextBox $slide 'September 2026' 48 474 200 18 12 $muted | Out-Null
    Add-Rect $slide 524 54 382 432 $panel | Out-Null
    $slide.Shapes.AddPicture($heroImage, $msoFalse, $msoTrue, 557, 79, 316, 316) | Out-Null
    Add-TextBox $slide 'A validation image excluded from model training' 557 412 316 38 14 $muted $false | Out-Null
    Add-Notes $slide "[Sources]`r`nLocal training evidence: $root\runs\yolov8n_pilot\pilot_summary.json`r`nLocal prediction: $heroImage"

    # Slide 2 - experiment setup
    $slide = $presentation.Slides.Add(2, $ppLayoutBlank)
    $slide.Background.Fill.ForeColor.RGB = $white
Add-SlideTitle $slide 'We trained YOLOv8n on a focused ROD dataset' 2 'Experiment setup'
    Add-TextBox $slide '2,400' 50 155 385 82 54 $blue $true | Out-Null
    Add-TextBox $slide 'images used in this pilot' 52 242 360 30 21 $ink $true | Out-Null
    Add-TextBox $slide 'ROD Obstacle Detection Dataset' 52 292 350 30 20 $ink $true | Out-Null
    Add-TextBox $slide 'YOLO format - Source: Hugging Face' 52 329 350 26 16 $blue $true | Out-Null
    Add-TextBox $slide 'Seven classes: person, chair, stairs, car, bicycle, electrical pole, and plant pot.' 52 374 350 75 16 $muted | Out-Null
    Add-StatRow $slide 'MODEL' 'YOLOv8n' 'A small object-detection model suitable for mobile development' 148 $ink
    Add-StatRow $slide 'DATA SPLIT' '2,000 / 400' 'training / validation images' 237 $ink
    Add-StatRow $slide 'TRAINING' '5 epochs' 'five passes through the training subset' 326 $ink
    Add-StatRow $slide 'HARDWARE' 'RTX 3050' 'NVIDIA laptop GPU' 415 $ink
    Add-Notes $slide "[Sources]`r`nDataset: ROD Obstacle Detection Dataset, https://huggingface.co/datasets/Abtinzandi/Obstacle-Detection-Dataset-YOLO`r`nPilot configuration: $root\runs\yolov8n_pilot\pilot_summary.json"

    # Slide 3 - headline metrics
    $slide = $presentation.Slides.Add(3, $ppLayoutBlank)
    $slide.Background.Fill.ForeColor.RGB = $white
    Add-SlideTitle $slide 'What the validation numbers mean' 3 'Validation results'
    Add-TextBox $slide '71.9%' 50 160 395 95 60 $blue $true | Out-Null
    Add-TextBox $slide 'mAP@0.5' 54 255 250 30 22 $ink $true | Out-Null
    Add-TextBox $slide 'mAP means Mean Average Precision. It combines correct object classification and bounding-box placement across all seven classes. @0.5 means at least 50% box overlap is required.' 54 298 360 130 17 $muted | Out-Null
    Add-StatRow $slide 'PRECISION' '77.5%' 'Of all objects the model said it detected, around 77.5% were correct. Higher means fewer false detections.' 150 $green
    Add-StatRow $slide 'RECALL' '62.7%' 'Of all actual obstacles, around 62.7% were detected. Approximately 37.3% were missed.' 247 $amber
    Add-StatRow $slide 'STRICTER mAP' '50.6%' 'The same mAP test uses 50%-95% box-overlap rules. It is harder than mAP@0.5, so the score is normally lower.' 344 $ink
    Add-Rect $slide 50 444 775 48 $paleBlue | Out-Null
    Add-TextBox $slide 'Main takeaway: detections are often correct, but the model still misses some obstacles.' 68 457 740 24 16 $blue $true | Out-Null
    Add-Notes $slide "[Sources]`r`nValidation metrics: $root\runs\yolov8n_pilot\final_overall_metrics.csv`r`nMetrics were calculated by Ultralytics YOLOv8 on the 400-image validation subset."

    # Slide 4 - per-class evidence table
    $slide = $presentation.Slides.Add(4, $ppLayoutBlank)
    $slide.Background.Fill.ForeColor.RGB = $white
    Add-SlideTitle $slide 'Electrical poles need more training data' 4 'Class performance'
    Add-TextBox $slide 'mAP@0.5 by obstacle class' 50 130 330 24 17 $muted $true | Out-Null
    $classes = @('Chair','Plant pot','Car','Stairs','Bicycle','Person','Electrical pole')
    $scores = @('92.0%','91.6%','82.5%','79.0%','72.1%','68.0%','18.1%')
    Add-Rect $slide 50 165 505 38 $ink | Out-Null
    Add-TextBox $slide 'Class' 60 174 280 20 16 $white $true | Out-Null
    Add-TextBox $slide 'mAP@0.5' 365 174 178 20 16 $white $true 3 | Out-Null
    for ($i = 0; $i -lt $classes.Count; $i++) {
        $rowTop = 203 + ($i * 37)
        if ($i % 2 -eq 0) { Add-Rect $slide 50 $rowTop 505 37 $panel | Out-Null }
        $rowColor = $(if ($i -eq 6) { $red } else { $ink })
        Add-TextBox $slide $classes[$i] 60 ($rowTop + 8) 285 22 16 $rowColor ($i -eq 6) | Out-Null
        Add-TextBox $slide $scores[$i] 365 ($rowTop + 8) 178 22 16 $rowColor ($i -eq 6) 3 | Out-Null
    }
    Add-TextBox $slide 'Strongest' 620 173 130 20 14 $green $true | Out-Null
    Add-TextBox $slide 'Chair and plant pot' 620 201 260 32 23 $ink $true | Out-Null
    Add-TextBox $slide 'Both exceeded 91% mAP@0.5.' 620 239 255 42 16 $muted | Out-Null
    Add-Rule $slide 620 303 250 $rule 0.8 | Out-Null
    Add-TextBox $slide 'Priority improvement' 620 329 170 20 14 $red $true | Out-Null
    Add-TextBox $slide 'Electrical poles' 620 357 260 32 23 $ink $true | Out-Null
    Add-TextBox $slide 'More varied campus examples are needed before longer training.' 620 395 260 63 16 $muted | Out-Null
    Add-Notes $slide "[Sources]`r`nPer-class validation metrics: $root\runs\yolov8n_pilot\final_per_class_metrics.csv"

    # Slide 5 - actual examples
    $slide = $presentation.Slides.Add(5, $ppLayoutBlank)
    $slide.Background.Fill.ForeColor.RGB = $white
    Add-SlideTitle $slide 'The model detected all seven target classes' 5 'Validation examples'
    $slide.Shapes.AddPicture($montageImage, $msoFalse, $msoTrue, 120, 126, 720, 361) | Out-Null
    Add-TextBox $slide 'Individual held-out examples; overall class performance is shown on the previous slide.' 122 496 718 17 12 $muted | Out-Null
    Add-Notes $slide "[Sources]`r`nGenerated validation montage: $montageImage`r`nDataset: ROD Obstacle Detection Dataset, https://huggingface.co/datasets/Abtinzandi/Obstacle-Detection-Dataset-YOLO"

    # Slide 6 - conclusion and next steps
    $slide = $presentation.Slides.Add(6, $ppLayoutBlank)
    $slide.Background.Fill.ForeColor.RGB = $white
    Add-SlideTitle $slide 'Pilot complete; refinement comes next' 6 'Conclusion'
    Add-TextBox $slide 'What this pilot proves' 52 143 300 25 17 $blue $true | Out-Null
    Add-TextBox $slide 'We can prepare data, train YOLOv8n, validate performance, and produce a reusable model file on the available laptop.' 52 181 350 130 25 $ink $true | Out-Null
    Add-TextBox $slide 'This covers object detection only. Distance estimation, alert prioritization, and mobile integration remain separate stages.' 52 337 345 74 16 $muted | Out-Null
    Add-TextBox $slide 'NEXT' 520 145 80 20 14 $blue $true | Out-Null
    $steps = @(
        @('01','Collect campus images, doors, and tables'),
        @('02','Add more electrical-pole examples'),
        @('03','Run longer training and an independent test'),
        @('04','Convert the best model for Android use')
    )
    $top = 172
    foreach ($step in $steps) {
        Add-TextBox $slide $step[0] 520 $top 40 28 15 $blue $true | Out-Null
        Add-TextBox $slide $step[1] 575 $top 300 46 18 $ink $true | Out-Null
        Add-Rule $slide 520 ($top + 54) 355 $rule 0.7 | Out-Null
        $top += 68
    }
    Add-Rect $slide 52 452 823 41 $ink | Out-Null
    Add-TextBox $slide 'Current status: a validated preliminary model, not a finished navigation system.' 70 462 785 22 16 $white $true | Out-Null
    Add-Notes $slide "[Sources]`r`nPresenter notebook: $root\notebooks\02_training_progress_presenter.ipynb`r`nThesis scope: $root\docs\01_Proposal\Topic_6_Assistive_Navigation.md"

    if (Test-Path -LiteralPath $output) { Remove-Item -LiteralPath $output -Force }
    $presentation.SaveAs($output, $ppSaveAsOpenXMLPresentation)
    New-Item -ItemType Directory -Force $renderDir | Out-Null
    $presentation.Export($renderDir, 'PNG', 1600, 900)
    $presentation.Close()
    $ppt.Quit()
    [System.Runtime.InteropServices.Marshal]::ReleaseComObject($presentation) | Out-Null
    [System.Runtime.InteropServices.Marshal]::ReleaseComObject($ppt) | Out-Null
    Write-Output "PPTX=$output"
    Write-Output "RENDERS=$renderDir"
} catch {
    if ($presentation) { try { $presentation.Close() } catch { } }
    if ($ppt) { try { $ppt.Quit() } catch { } }
    throw
}
