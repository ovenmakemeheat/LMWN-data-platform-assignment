# Get Airflow credentials from docker compose logs
$logs = docker compose logs airflow 2>$null

$pattern = 'Login with username:\s*(\S+)\s+password:\s*(\S+)'

$match = $logs | Select-String -Pattern $pattern | Select-Object -Last 1

if ($match) {
    $username = $match.Matches[0].Groups[1].Value
    $password = $match.Matches[0].Groups[2].Value

    Write-Host "Airflow Credentials Found:" -ForegroundColor Green
    Write-Host "Username: $username"
    Write-Host "Password: $password"
} else {
    Write-Host "No Airflow credentials found in logs." -ForegroundColor Yellow
}