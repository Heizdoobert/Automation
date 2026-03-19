param (
    # Input 1: The Android Package or Component Name (Required, Position 0)
    [Parameter(Mandatory=$true, Position=0, HelpMessage="The target package or component (e.g., com.pool.match.puzzle3d)")]
    [string]$Component,

    # Input 2: The JSON File Path (Optional)
    [Parameter(Mandatory=$false)]
    [Alias("json")]
    [string]$JsonFile
)

# Check if ADB is available before doing anything
if (-Not (Get-Command "adb" -ErrorAction SilentlyContinue)) {
    Write-Error "ADB is not recognized as a command. Make sure it is installed and added to your System PATH."
    exit
}

# --- NEW LOGIC: Fallback to default Unity Activity ---
if (-not $Component.Contains("/")) {
    $Component = "$Component/com.unity3d.player.UnityPlayerActivity"
    Write-Host "No activity specified. Defaulting target to: $Component" -ForegroundColor Yellow
}
# -----------------------------------------------------

if ([string]::IsNullOrWhiteSpace($JsonFile)) {
    # NO JSON PROVIDED: Just launch the app normally
    Write-Host "No JSON file provided. Launching app..." -ForegroundColor Cyan
    adb shell "am start -n $Component"
} else {
    # JSON PROVIDED: Read, encode, and send
    if (Test-Path $JsonFile) {
        Write-Host "Reading JSON data from '$JsonFile'..." -ForegroundColor Cyan
        
        # Read the file and convert it to Base64
        $rawBytes = [IO.File]::ReadAllBytes((Resolve-Path $JsonFile).Path)
        $b64String = [Convert]::ToBase64String($rawBytes)
        
        Write-Host "Sending Base64 payload to device..." -ForegroundColor Cyan
        
        # Note: We are using "teststring" as the extra key based on your Java code
        adb shell "am start -n $Component --es json '$b64String'"
        
        Write-Host "Done!" -ForegroundColor Green
    } else {
        Write-Error "Could not find the JSON file at path: $JsonFile"
    }
}