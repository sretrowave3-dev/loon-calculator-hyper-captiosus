
Add-Type -AssemblyName System.Drawing
$bmp = New-Object System.Drawing.Bitmap 50, 20, [System.Drawing.Imaging.PixelFormat]::Format24bppRgb
$g = [System.Drawing.Graphics]::FromImage($bmp)
$g.Clear([System.Drawing.Color]::FromArgb(255, 30, 144, 255)) # Dodger Blue
$g.Dispose()
$bmp.Save('test_24bpp.bmp', [System.Drawing.Imaging.ImageFormat]::Bmp)
$bmp.Dispose()
Write-Output "SAVED"
