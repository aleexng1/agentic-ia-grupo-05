param(
    [ValidateRange(1, 65535)]
    [int]$Puerto = 8000
)

$comandoCloudflared = Get-Command cloudflared -ErrorAction SilentlyContinue
if (-not $comandoCloudflared) {
    Write-Host "cloudflared no está instalado. Instálalo con: winget install Cloudflare.cloudflared" -ForegroundColor Yellow
    exit 1
}

Write-Host "Abriendo un túnel al servidor local http://127.0.0.1:$Puerto" -ForegroundColor Cyan
Write-Host "Mantén esta terminal abierta mientras uses el túnel.`n"

$ultimaDireccion = $null
& cloudflared tunnel --url "http://127.0.0.1:$Puerto" 2>&1 | ForEach-Object {
    $linea = $_.ToString()
    Write-Host $linea
    $coincidencia = [regex]::Match($linea, 'https://[A-Za-z0-9.-]+\.trycloudflare\.com')
    if ($coincidencia.Success -and $coincidencia.Value -ne $ultimaDireccion) {
        $ultimaDireccion = $coincidencia.Value
        Write-Host "`n============================================================" -ForegroundColor Green
        Write-Host "                 DIRECCIÓN HTTPS PÚBLICA" -ForegroundColor Green
        Write-Host $ultimaDireccion -ForegroundColor Green
        Write-Host "============================================================" -ForegroundColor Green
        Write-Host 'Pega esta dirección en URL_PUBLICA de tu .env y reinicia tu agente; pásasela a tu compañero para que la ponga en su URLS_AGENTES.' -ForegroundColor Cyan
        Write-Host ""
    }
}

if ($LASTEXITCODE -ne 0) {
    exit $LASTEXITCODE
}
