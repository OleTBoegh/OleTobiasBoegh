#!/bin/bash

# This script will ask you to enter your Argus API key and set it as an environment variable
# before starting Visual Studio Code (VSCode) in the current directory. This will ensure that
# code you run from VSCode can access the API key to authenticate with the Argus server.
#
# IMPORTANT: The reason we don't set the API key as a global environment variable or define it
# in an .env file is that we don't want to write it to disk and we don't want to accidentally
# commit the API key to the repository. This way it stays in memory and is only available to
# the current shell session.

# Activate the virtual environment if it exists:
if [ -f "./.venv_linux/bin/activate" ]; then
    echo "## Activating virtual environment '.venv'..."
    # Source the activate script to set the virtual environment in the current shell session:
    source ./.venv_linux/bin/activate
else
    echo "## The virtual environment was not found. Continuing without activation."
fi

# Run the script to set the API key as an environment variable:
echo "## Setting ARGUS_API_KEY environment variable..."
# Read the API key from the user input and export it as an environment variable
read -sp "Enter/paste the value for ARGUS_API_KEY: " ARGUS_API_KEY
export ARGUS_API_KEY
echo ""  # Move to a new line after entering the password

# Start Visual Studio Code in the current directory, which will inherit the ARGUS_API_KEY environment variable:
echo "## Starting Visual Studio Code..."
code .
