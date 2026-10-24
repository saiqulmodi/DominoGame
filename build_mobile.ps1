# build_mobile.ps1 - build Domino Game for phones and test it on this laptop
#
#   .\build_mobile.ps1            web + installable app (PWA) into docs\, then a local test server
#   .\build_mobile.ps1 -Android   also builds the Android .apk (WSL Ubuntu) into bin\
#   .\build_mobile.ps1 -Release   also builds the signed Google Play bundle (.aab) into bin\
#                                 (see PLAY_STORE.md; the upload key is made the first time)
#   .\build_mobile.ps1 -NoServe   build only
#
# If PowerShell refuses to run scripts, start it with:
#   powershell -ExecutionPolicy Bypass -File .\build_mobile.ps1

param(
    [switch]$Android,
    [switch]$Release,
    [switch]$NoServe,
    [int]$Port = 8000
)

$ErrorActionPreference = "Stop"
Set-Location -LiteralPath $PSScriptRoot

Write-Host "=== 1. Cleaning previous build artifacts ===" -ForegroundColor Cyan
foreach ($dir in @("build", "dist")) {
    if (Test-Path $dir) { Remove-Item -Recurse -Force $dir }
}

Write-Host "=== 2. App icons and splash ===" -ForegroundColor Cyan
python tools\make_icons.py
if ($LASTEXITCODE -ne 0) { throw "make_icons.py failed" }

Write-Host "=== 3. Web game + installable app (pygbag, manifest, offline) ===" -ForegroundColor Cyan
# build_web.py copies only the game files (never venv\, docs\ or tools\) and writes docs\
python tools\build_web.py
if ($LASTEXITCODE -ne 0) { throw "build_web.py failed" }

function Invoke-AndroidBuild($mode, $pattern, $label) {
    # Java prints harmless notes on stderr; "Stop" would treat them as errors
    $ErrorActionPreference = "Continue"
    wsl -e bash -l tools/build_android.sh $mode
    if ($LASTEXITCODE -ne 0) { throw "Android build failed - see the messages above" }
    Get-ChildItem "bin\$pattern" | Sort-Object LastWriteTime -Descending | Select-Object -First 1 |
        ForEach-Object { Write-Host "${label}: $($_.FullName)" -ForegroundColor Green }
}

if ($Android) {
    Write-Host "=== 4. Android app (.apk) in WSL Ubuntu - the first build takes 20-40 minutes ===" -ForegroundColor Cyan
    Invoke-AndroidBuild "debug" "*.apk" "APK"
}

if ($Release) {
    Write-Host "=== 5. Google Play bundle (.aab), signed with the upload key ===" -ForegroundColor Cyan
    Invoke-AndroidBuild "release" "*.aab" "Play Store bundle"
    Write-Host "Back up C:\Users\saiqu\DominoGame-signing - every update needs that key." -ForegroundColor Yellow
}

if ($NoServe) { return }

# Never assume the port is free: move on to the next free one
while (Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue) {
    Write-Host "Port $Port is busy, trying $($Port + 1)" -ForegroundColor DarkYellow
    $Port++
}

$lan = Get-NetIPAddress -AddressFamily IPv4 -ErrorAction SilentlyContinue |
    Where-Object { $_.IPAddress -notlike "127.*" -and $_.IPAddress -notlike "169.254.*" -and
                   $_.PrefixOrigin -in @("Dhcp", "Manual") } |
    Select-Object -First 1 -ExpandProperty IPAddress

Write-Host ""
Write-Host "=== Local test server (Ctrl+C to stop) ===" -ForegroundColor Green
Write-Host "  On this laptop : http://localhost:$Port" -ForegroundColor Yellow
if ($lan) {
    Write-Host "  On your phone  : http://${lan}:$Port   (same Wi-Fi)" -ForegroundColor Yellow
}
Write-Host "  First load takes about 30 seconds; then tap the page to start."
Write-Host "  'Install app' / 'Add to Home Screen' with offline play needs https:"
Write-Host "  use https://saiqulmodi.github.io/DominoGame/ on the phone for that."
python -m http.server $Port --bind 0.0.0.0 --directory docs
