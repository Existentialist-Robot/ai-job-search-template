# Setup linkedin-cli for ai-job-search
# Run from repo root: .\.agents\vendor\setup_linkedin_cli.ps1

$ErrorActionPreference = "Stop"
$dir = ".agents\vendor\linkedin-cli"

Write-Host "Setting up linkedin-cli..."

# Create venv inside the skill dir
python -m venv "$dir\.venv"

# Install editable from the submodule (NAT mirror — do NOT use PyPI)
& "$dir\.venv\Scripts\python.exe" -m pip install -e "$dir" --quiet

# Install Chromium for Playwright
& "$dir\.venv\Scripts\python.exe" -m playwright install chromium

# Set UTF-8 permanently (Windows only — prevents UnicodeEncodeError)
[System.Environment]::SetEnvironmentVariable("PYTHONUTF8", "1", "User")
$env:PYTHONUTF8 = "1"

Write-Host ""
Write-Host "Done. Next steps:"
Write-Host "  1. Copy .agents\vendor\linkedin-cli\.env.example to .agents\vendor\linkedin-cli\.env"
Write-Host "  2. Fill in LINKEDIN_USERNAME and LINKEDIN_PASSWORD in .env"
Write-Host "  3. Run: .agents\vendor\linkedin-cli\.venv\Scripts\linkedin-cli.exe session open --session work"
Write-Host "  4. Then: .agents\vendor\linkedin-cli\.venv\Scripts\linkedin-cli.exe login"
