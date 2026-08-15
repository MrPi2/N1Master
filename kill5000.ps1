Stop-Process -Id 17648 -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2
$c = Get-NetTCPConnection -LocalPort 5000 -ErrorAction SilentlyContinue
if ($c) { Write-Output "STILL LISTENING: $($c.OwningProcess)" } else { Write-Output "PORT 5000 FREE" }
