Write-Host "🧼 Initializing Universal Matrix Workspace Core Purge..." -ForegroundColor Cyan

# Define a collection tracking target background debugging artifacts
$temporary_files = @(
    "test_toroid_toolpath.gcode",
    "toroid_toolpath.gcode"
)

# Step 1: Programmatically sweep away matching loose file blocks
foreach ($file in $temporary_files) {
    if (Test-Path $file) {
        Remove-Item -Path $file -Force
        Write-Host "   Deleted temporary machine path asset: $file" -ForegroundColor Yellow
    }
}

# Step 2: Systematically clean hidden compiled execution python caches
Get-ChildItem -Path . -Recurse -Directory -Filter "__pycache__" -ErrorAction SilentlyContinue | ForEach-Object {
    Remove-Item -Path $_.FullName -Recurse -Force
    Write-Host "   Purged Python compiled runtime directory: $($_.RelativePath)" -ForegroundColor Yellow
}

Write-Host "✨ Workspace optimization sequence complete! Active tracking folders are completely pristine." -ForegroundColor Green
