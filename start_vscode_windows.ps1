# This script will ask you to enter your Argus API key and set it as an environment variable.
# before starting Visual Studio Code (VSCode) in the current directory. This will ensure that
# code you run from VSCode can access the API key to authenticate with the Argus server.
#
# IMPORTANT: The reason we don't set the API key as a global environment variable or define it
# in an .env file is that we don't want to write it to disk and we don't want to  accidentally
# commit the API key to the repository. This way it stays in memory and is only available to
# the current shell session.

# Activate the virtual environment if it exists:
if (Test-Path .\.venv_win\Scripts\Activate.ps1) {
    Write-Host "## Activating virtual environment '.venv_win'..."
    # Source (.) the activate script to set the virtual environment in the current shell session:
    . .\.venv_win\Scripts\Activate.ps1
}
else {
    Write-Host "## The virtual environment was not found. Continuing without activation."
}

# Run the script to set the API key as an environment variable:
Write-Host "## Setting ARGUS_API_KEY environment variable..."
$env:ARGUS_API_KEY = [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR((Read-Host "Enter/paste the value for ARGUS_API_KEY" -AsSecureString)))

# Start Visual Studio Code in the current directory, which will inherit the ARGUS_API_KEY environment variable:
Write-Host "## Starting Visual Studio Code..."
code .
