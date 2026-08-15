$c = Get-NetTCPConnection -LocalPort 5000 -ErrorAction SilentlyContinue
if ($c) {
  $p = $c[0].OwningProcess
  $proc = Get-Process -Id $p -ErrorAction SilentlyContinue
  Write-Output "PORT 5000 -> PID $p -> $($proc.ProcessName) $($proc.Path)"
} else {
  Write-Output "PORT 5000 FREE"
}
