# Run as Administrator and Execute following command:
# Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

# Variables
$username = "ScanUser"
$password = ConvertTo-SecureString "!!!CHANGEME!!!" -AsPlainText -Force
$folderPath = "C:\Scan"
$shareName = "Scan"

# Create a new user account with password set to never expire
New-LocalUser -Name $username -Password $password -FullName "Share Access User" -Description "User for share access only" -PasswordNeverExpires $true


# Add the user to the Guests group (optional: adjust based on your needs)
Add-LocalGroupMember -Group "Guests" -Member $username

# Deny local logon for the user
# Get the current state of SeDenyInteractiveLogonRight
$currentPolicy = secedit /export /areas USER_RIGHTS /cfg "$env:TEMP\current_policy.inf"
$currentPolicyContent = Get-Content "$env:TEMP\current_policy.inf"

# Find the SeDenyInteractiveLogonRight line
$denyInteractiveLogonLine = $currentPolicyContent | Where-Object { $_ -match '^SeDenyInteractiveLogonRight' }

# If the line exists, append the new user, otherwise create a new entry
if ($denyInteractiveLogonLine) {
    $updatedPolicyLine = $denyInteractiveLogonLine + ",$username"
    $currentPolicyContent = $currentPolicyContent -replace $denyInteractiveLogonLine, $updatedPolicyLine
} else {
    $currentPolicyContent += "SeDenyInteractiveLogonRight = $username"
}

# Write the updated policy to a new file
$updatedPolicyPath = "$env:TEMP\updated_policy.inf"
$currentPolicyContent | Set-Content -Path $updatedPolicyPath

# Apply the updated policy
secedit /configure /db secedit.sdb /cfg $updatedPolicyPath /areas USER_RIGHTS

# Cleanup temporary files
Remove-Item -Path "$env:TEMP\current_policy.inf"
Remove-Item -Path $updatedPolicyPath

# Hide the user from the logon screen
# Add the user to the registry key for hidden users
$regPath = "HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon\SpecialAccounts\UserList"
New-Item -Path $regPath -Force | Out-Null
New-ItemProperty -Path $regPath -Name $username -Value 0 -PropertyType DWORD -Force | Out-Null

# Create the folder if it doesn't exist
if (-Not (Test-Path -Path $folderPath)) {
    New-Item -ItemType Directory -Path $folderPath | Out-Null
    Write-Output "Folder '$folderPath' created."
}

# Grant full access to the created user on the folder
$acl = Get-Acl -Path $folderPath
$accessRule = New-Object System.Security.AccessControl.FileSystemAccessRule($username, "FullControl", "ContainerInherit,ObjectInherit", "None", "Allow")
$acl.SetAccessRule($accessRule)
Set-Acl -Path $folderPath -AclObject $acl
Write-Output "Granted full access to user '$username' on folder '$folderPath'."

# Share the folder with full access for the user
New-SmbShare -Name $shareName -Path $folderPath -FullAccess $username
Write-Output "Folder '$folderPath' shared as '$shareName' with full access for user '$username'."

Write-Output "User account '$username' created for share access only, with local login disabled, hidden from logon screen, and shared folder set up."
