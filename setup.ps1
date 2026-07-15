# Week 1 Setup Script
# Run this to set up your environment

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Week 1: Python + LLM Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check Python
Write-Host "Checking Python installation..." -ForegroundColor Yellow
$pythonVersion = python --version 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Found: $pythonVersion" -ForegroundColor Green
} else {
    Write-Host "✗ Python not found. Please install Python 3.8+" -ForegroundColor Red
    exit 1
}

# Create virtual environment
Write-Host ""
Write-Host "Creating virtual environment..." -ForegroundColor Yellow
if (Test-Path "venv") {
    Write-Host "✓ Virtual environment already exists" -ForegroundColor Green
} else {
    python -m venv venv
    Write-Host "✓ Virtual environment created" -ForegroundColor Green
}

# Activate virtual environment
Write-Host ""
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"
Write-Host "✓ Virtual environment activated" -ForegroundColor Green

# Install dependencies
Write-Host ""
Write-Host "Installing dependencies..." -ForegroundColor Yellow
Write-Host "(This may take a few minutes)" -ForegroundColor Gray
pip install -q --upgrade pip
pip install -q -r requirements.txt
Write-Host "✓ Dependencies installed" -ForegroundColor Green

# Check for .env file
Write-Host ""
Write-Host "Checking .env file..." -ForegroundColor Yellow
if (Test-Path ".env") {
    Write-Host "✓ .env file exists" -ForegroundColor Green
} else {
    Write-Host "⚠ .env file not found" -ForegroundColor Yellow
    Copy-Item ".env.template" ".env"
    Write-Host "✓ Created .env from template" -ForegroundColor Green
    Write-Host ""
    Write-Host "ACTION REQUIRED:" -ForegroundColor Red
    Write-Host "Edit .env file and add your API keys:" -ForegroundColor Yellow
    Write-Host "  - OPENAI_API_KEY=sk-your-key-here" -ForegroundColor Gray
    Write-Host "  - ANTHROPIC_API_KEY=sk-ant-your-key-here" -ForegroundColor Gray
}

# Summary
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Setup Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "  1. Edit .env file with your API keys" -ForegroundColor Gray
Write-Host "  2. Read QUICK_START.md for learning path" -ForegroundColor Gray
Write-Host "  3. Start with Day 1:" -ForegroundColor Gray
Write-Host "     python quick-references/python-essentials.py" -ForegroundColor Cyan
Write-Host ""
Write-Host "Quick Test:" -ForegroundColor Yellow
Write-Host "  python -c `"import openai, anthropic, httpx; print('✓ All imports OK')`"" -ForegroundColor Cyan
Write-Host ""
Write-Host "Happy learning! 🚀" -ForegroundColor Green
Write-Host ""
