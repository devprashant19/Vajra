Write-Host "Starting Vajra Demo (No-Docker Mode)"
Write-Host "Starting API..."
Start-Process "uv" -ArgumentList "run uvicorn api.main:app --port 8000" -WorkingDirectory "apps/api" -NoNewWindow
Write-Host "Starting Web UI..."
Start-Process "pnpm.cmd" -ArgumentList "run dev" -WorkingDirectory "apps/web" -NoNewWindow
Write-Host "Demo started! API on :8000, Web on :5173"
