$hosts = "C:\Windows\System32\drivers\etc\hosts"
$line = "20.205.243.166 github.com"
$content = Get-Content $hosts -ErrorAction SilentlyContinue
if ($content -notcontains $line) {
  Add-Content -Path $hosts -Value $line
  Write-Output "ADDED github hosts entry"
} else {
  Write-Output "ALREADY EXISTS"
}
