$hosts = "C:\Windows\System32\drivers\etc\hosts"
$line = "18.67.221.88 huggingface.co"
$content = Get-Content $hosts -ErrorAction SilentlyContinue
if ($content -notcontains $line) {
  Add-Content -Path $hosts -Value $line
  Write-Output "ADDED hosts entry"
} else {
  Write-Output "ALREADY EXISTS"
}
