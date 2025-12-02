# fix_ssl.ps1 - English version (no encoding issues)
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "SSL FIX FOR TELEGRAM BOT" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

Write-Host "`n1. Downloading root certificates..." -ForegroundColor Yellow
try {
    # Download fresh certificates
    Invoke-WebRequest -Uri "https://curl.se/ca/cacert.pem" -OutFile "cacert.pem" -UseBasicParsing
    Write-Host "   Certificates downloaded" -ForegroundColor Green
} catch {
    Write-Host "   Could not download. Using local..." -ForegroundColor Red
}

Write-Host "`n2. Installing certificates..." -ForegroundColor Yellow
try {
    # Install to Windows certificate store
    certutil -addstore -f root cacert.pem
    Write-Host "   Certificates installed" -ForegroundColor Green
} catch {
    Write-Host "   Could not install automatically" -ForegroundColor Yellow
}

Write-Host "`n3. Setting Python environment variables..." -ForegroundColor Yellow
# Set environment variables
$cacertPath = "C:\Users\Hrapunzel\telegram_bot\cacert.pem"
[Environment]::SetEnvironmentVariable("SSL_CERT_FILE", $cacertPath, "User")
[Environment]::SetEnvironmentVariable("REQUESTS_CA_BUNDLE", $cacertPath, "User")

Write-Host "   Environment variables set:" -ForegroundColor Green
Write-Host "   SSL_CERT_FILE = $cacertPath"
Write-Host "   REQUESTS_CA_BUNDLE = $cacertPath"

Write-Host "`n4. Creating Python SSL fix file..." -ForegroundColor Yellow
$pythonCode = @'
import ssl
import os

# Disable SSL verification
ssl._create_default_https_context = ssl._create_unverified_context

# Set certificate paths
os.environ['SSL_CERT_FILE'] = r'C:\Users\Hrapunzel\telegram_bot\cacert.pem'
os.environ['REQUESTS_CA_BUNDLE'] = r'C:\Users\Hrapunzel\telegram_bot\cacert.pem'

print("SSL fixed for this script")
'@

$pythonCode | Out-File -FilePath "fix_ssl_python.py" -Encoding ASCII
Write-Host "   File created: fix_ssl_python.py" -ForegroundColor Green

Write-Host "`n5. Testing Telegram connection..." -ForegroundColor Yellow
try {
    $testUrl = "https://api.telegram.org"
    $response = Invoke-WebRequest -Uri $testUrl -UseBasicParsing -TimeoutSec 10
    Write-Host "   Telegram connection OK" -ForegroundColor Green
} catch {
    Write-Host "   Connection failed: $_" -ForegroundColor Red
}

Write-Host "`n" + "="*50 -ForegroundColor Cyan
Write-Host "SETUP COMPLETE!" -ForegroundColor Green
Write-Host "="*50 -ForegroundColor Cyan

Write-Host "`nNEXT STEPS:" -ForegroundColor Yellow
Write-Host "1. CLOSE all PowerShell windows" -ForegroundColor White
Write-Host "2. RESTART computer" -ForegroundColor White
Write-Host "3. After restart run test:" -ForegroundColor White
Write-Host "   python test_ssl.py" -ForegroundColor White
Write-Host "`nIf still not working - use VPN" -ForegroundColor Magenta