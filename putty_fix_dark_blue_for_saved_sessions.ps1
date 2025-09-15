# Open Powershell with admin rights and paste this script or execute:
# Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
# and run saved script

# Fix saved sessions for ANSI Blue too dark
# For new sessions open Putty in Windows - Colours - ANSI Blue set 61,148,254 and save as Default Settings

# Define the base registry path
$basePath = "HKCU:\SOFTWARE\SimonTatham\PuTTY\Sessions"

# Get all subkeys under the PuTTY Sessions key
$sessionKeys = Get-ChildItem -Path $basePath

foreach ($key in $sessionKeys) {
    $keyPath = $key.PSPath
    try {
        # Get the current value of Colour14
        $colour14 = Get-ItemProperty -Path $keyPath -Name "Colour14" -ErrorAction SilentlyContinue

        if ($colour14.Colour14 -eq "0,0,187") {
            # Update the value to the new color
            Set-ItemProperty -Path $keyPath -Name "Colour14" -Value "60,84,255"
            Write-Host "Updated Colour14 in $($key.PSChildName)"
        }
    } catch {
        Write-Host "Error accessing $($key.PSChildName): $_"
    }
}

