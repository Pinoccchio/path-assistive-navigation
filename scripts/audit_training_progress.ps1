param([string]$DeckPath)

$ErrorActionPreference = 'Stop'
$root = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..')).Path
$sourceDeck = if ($DeckPath) { [System.IO.Path]::GetFullPath($DeckPath) } else { Join-Path $root 'docs\03_Presentation\YOLOv8n_Training_Progress.pptx' }
$deck = Join-Path $env:TEMP ("yolov8n-training-progress-audit-{0}.pptx" -f [guid]::NewGuid().ToString('N'))
Copy-Item -LiteralPath $sourceDeck -Destination $deck
$msoTrue = -1
$ppt = $null
$presentation = $null
try {
    $ppt = New-Object -ComObject PowerPoint.Application
    $ppt.Visible = $msoTrue
    $ppt.WindowState = 2
    $presentation = $ppt.Presentations.Open($deck, $msoTrue, $msoTrue, 0)
    $slideWidth = $presentation.PageSetup.SlideWidth
    $slideHeight = $presentation.PageSetup.SlideHeight
    $issues = New-Object System.Collections.Generic.List[string]
    foreach ($slide in $presentation.Slides) {
        foreach ($shape in $slide.Shapes) {
            if ($shape.Left -lt -0.5 -or $shape.Top -lt -0.5 -or ($shape.Left + $shape.Width) -gt ($slideWidth + 0.5) -or ($shape.Top + $shape.Height) -gt ($slideHeight + 0.5)) {
                $issues.Add("Slide $($slide.SlideIndex): off-canvas shape '$($shape.Name)'")
            }
            try {
                if ($shape.HasTextFrame -eq $msoTrue -and $shape.TextFrame.HasText -eq $msoTrue) {
                    $boundHeight = $shape.TextFrame2.TextRange.BoundHeight
                    $boundWidth = $shape.TextFrame2.TextRange.BoundWidth
                    if ($boundHeight -gt ($shape.Height + 2) -or $boundWidth -gt ($shape.Width + 2)) {
                        $sample = $shape.TextFrame.TextRange.Text.Replace("`r", ' ').Replace("`n", ' ')
                        $issues.Add("Slide $($slide.SlideIndex): text overflow '$sample'")
                    }
                }
            } catch { }
        }
    }
    Write-Output "slides=$($presentation.Slides.Count) size=$slideWidth x $slideHeight"
    if ($issues.Count -eq 0) { Write-Output 'layout_issues=0' } else { $issues | ForEach-Object { Write-Output $_ }; exit 1 }
    $presentation.Close()
    $ppt.Quit()
} finally {
    if ($presentation) { try { [System.Runtime.InteropServices.Marshal]::ReleaseComObject($presentation) | Out-Null } catch { } }
    if ($ppt) { try { [System.Runtime.InteropServices.Marshal]::ReleaseComObject($ppt) | Out-Null } catch { } }
    if (Test-Path -LiteralPath $deck) { Remove-Item -LiteralPath $deck -Force }
}
