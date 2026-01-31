# FileBrowser Monitor - Windows Task Scheduler Setup
# Run this script as Administrator to set up scheduled task

# Get the script directory
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$PythonPath = (Get-Command python).Source
$MonitorScript = Join-Path $ScriptDir "monitor.py"

# Check if running as admin
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")
if (-not $isAdmin) {
    Write-Host "ERROR: This script must be run as Administrator!" -ForegroundColor Red
    exit 1
}

# Create task action
$Action = New-ScheduledTaskAction `
    -Execute $PythonPath `
    -Argument $MonitorScript `
    -WorkingDirectory $ScriptDir

# Create task trigger (every 30 minutes starting now)
$Trigger = New-ScheduledTaskTrigger `
    -Once -At (Get-Date) `
    -RepetitionInterval (New-TimeSpan -Minutes 30) `
    -RepetitionDuration (New-TimeSpan -Days 9999)

# Create task settings
$Settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -RunOnlyIfNetworkAvailable

# Register the task
$TaskName = "FileBrowser Monitor"
$Principal = New-ScheduledTaskPrincipal -UserId "$env:COMPUTERNAME\$env:USERNAME" -RunLevel Limited

try {
    # Remove existing task if it exists
    Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue | Unregister-ScheduledTask -Confirm:$false

    # Create new task
    Register-ScheduledTask `
        -TaskName $TaskName `
        -Action $Action `
        -Trigger $Trigger `
        -Settings $Settings `
        -Principal $Principal `
        -Description "Monitor FileBrowser for new files and send Discord notifications"

    Write-Host "Successfully created scheduled task '$TaskName'" -ForegroundColor Green
    Write-Host "The task will run every 30 minutes."
    Write-Host ""
    Write-Host "To test or run immediately:"
    Write-Host "  Start-ScheduledTask -TaskName '$TaskName'"
    Write-Host ""
    Write-Host "To view task details:"
    Write-Host "  Get-ScheduledTask -TaskName '$TaskName' | Select-Object *"
    Write-Host ""
    Write-Host "To view task history:"
    Write-Host "  Get-ScheduledTask -TaskName '$TaskName' | Get-ScheduledTaskInfo"
}
catch {
    Write-Host "ERROR: Failed to create scheduled task: $_" -ForegroundColor Red
    exit 1
}
