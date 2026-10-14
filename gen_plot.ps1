
Add-Type -AssemblyName System.Drawing
$w = 65
$h = 34
$bmp = New-Object System.Drawing.Bitmap $w, $h
$g = [System.Drawing.Graphics]::FromImage($bmp)
$g.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::AntiAlias
$g.Clear([System.Drawing.Color]::FromArgb(255, 18, 22, 28))

# Draw Grid Lines
$gridPen = New-Object System.Drawing.Pen([System.Drawing.Color]::FromArgb(255, 35, 42, 54), 1)
for ($x = 0; $x -lt $w; $x += 10) {
    $g.DrawLine($gridPen, $x, 0, $x, $h)
}
for ($y = 0; $y -lt $h; $y += 6) {
    $g.DrawLine($gridPen, 0, $y, $w, $y)
}

# Draw X and Y Axes
$axisPen = New-Object System.Drawing.Pen([System.Drawing.Color]::FromArgb(255, 120, 140, 165), 1)
$centerX = [int]($w / 2)
$centerY = [int]($h / 2)
$g.DrawLine($axisPen, 0, $centerY, $w, $centerY)
$g.DrawLine($axisPen, $centerX, 0, $centerX, $h)

# Plot Points for Function f(x)
$curvePen = New-Object System.Drawing.Pen([System.Drawing.Color]::FromArgb(255, 0, 235, 180), 2)
$fillBrush = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::FromArgb(80, 0, 180, 255))

$prevPt = $null
$points = New-Object System.Collections.Generic.List[System.Drawing.Point]

for ($px = 0; $px -lt $w; $px++) {
    $mathX = ($px - $centerX) / ($w / 8.0) # Domain roughly [-4, 4]
    
    # Evaluate sample function e.g. x^2 - 2 or (x^3+1)/(x+1) -> x^2 - x + 1
    # For test: f(x) = (x^3 + 1)/(x + 1) = x^2 - x + 1
    $mathY = [math]::Pow($mathX, 2) - $mathX + 1.0
    
    if (-not [double]::IsNaN($mathY) -and -not [double]::IsInfinity($mathY) -and [math]::Abs($mathY) -lt 25) {
        $py = [int]($centerY - ($mathY * ($h / 12.0)))
        if ($py -ge 0 -and $py -lt $h) {
            $currPt = New-Object System.Drawing.Point $px, $py
            $points.Add($currPt)
            if ($prevPt -ne $null -and [math]::Abs($currPt.Y - $prevPt.Y) -lt ($h / 2)) {
                $g.DrawLine($curvePen, $prevPt, $currPt)
            }
            $prevPt = $currPt
        } else {
            $prevPt = $null
        }
    } else {
        $prevPt = $null
    }
}

# Draw Shaded Integral Area under curve between x=-1 and x=2
for ($px = [int]($centerX - ($w / 8.0)); $px -le [int]($centerX + 2.0*($w / 8.0)); $px++) {
    $mathX = ($px - $centerX) / ($w / 8.0)
    $mathY = [math]::Pow($mathX, 2) - $mathX + 1.0
    if ($mathY -gt 0) {
        $topY = [int]($centerY - ($mathY * ($h / 12.0)))
        $topY = [math]::Max(0, [math]::Min($h - 1, $topY))
        if ($topY -lt $centerY) {
            $g.DrawLine((New-Object System.Drawing.Pen([System.Drawing.Color]::FromArgb(100, 0, 160, 255), 1)), $px, $topY, $px, $centerY)
        }
    }
}

# Draw Origin Marker
$dotBrush = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::FromArgb(255, 255, 215, 0))
$g.FillEllipse($dotBrush, $centerX - 2, $centerY - 2, 4, 4)

$g.Dispose()
$bmp.Save('math_plot.bmp', [System.Drawing.Imaging.ImageFormat]::Bmp)
$bmp.Dispose()
Write-Output "OK"
