# To create the documentation for this script, run the following command:
# pydoc-markdown -I . -m start_new_investigation --render-toc

# IMPORTS:
import os
import re
import argparse
import shutil
from datetime import datetime
from pathlib import Path
from typing import List, Optional

# CONFIG FLAGS:
DRYRUN=False # Will prevent any changes to be made to files etc. Note: Implies DEBUG for certain code paths.
DEFAULT_VERBOSITY="WARNING" # Set the verbosity level for the script. Must match one of the MSG levels.

# CONFIG PARAMETERS:
PLAYBOOKS_DIR = Path('./Playbooks')
INVESTIGATIONS_DIR = Path('./Investigations')
PLAYBOOK_IGNORE_DIRS: list = ['.ipynb_checkpoints', '__pycache__', '.git', '.venv', 'venv', 'build', 'dist', '.cache', 'cache', '.vscode', '.idea', '.pytest_cache', 'node_modules', '.env', 'env', 'logs', 'tmp', 'temp']

# Error codes
RETURN_SUCCESS = 0
RETURN_ERROR = 1
RETURN_INVALID = 2
RETURN_NOT_IMPLEMENTED = 3

# -----------------------------------------------------------------------------
# Class MSG: Class to handle logging at a configurable verbosity level.
# -----------------------------------------------------------------------------
class MSG:
    """ Class to handle logging at a configurable verbosity level."""
    # Constants for verbosity levels:
    SILENT = 1      # Turns off all logging.
    CRITICAL = 2    # Only critical errors are logged.
    ERROR = 3       # Errors and critical messages are logged.
    WARNING = 4     # Warnings, errors, and critical messages are logged.
    INFO = 5        # Informational messages, warnings, errors, and critical messages are logged.
    VERBOSE = 6     # Verbose messages, informational messages, warnings, errors, and critical messages are logged.
    DEBUG = 7       # Debug messages, verbose messages, informational messages, warnings, errors, and critical messages are logged.
    
    # Default verbosity level if not specific level is set by the setLevel function:
    DEFAULT_LEVEL = WARNING
    
    # Configured verbosity level set by the setLevel function:
    CONFIGURED_LEVEL = None
    
    # Dictionary to map verbosity level values to names:
    _level_to_name_lookup = {
        SILENT: "SILENT",
        CRITICAL: "CRITICAL",
        ERROR: "ERROR",
        WARNING: "WARNING",
        INFO: "INFO",
        DEBUG: "DEBUG",
        VERBOSE: "VERBOSE"
    }

    # Dictionary to map verbosity level names to values:
    _name_to_level_lookup = {
        "SILENT": SILENT,
        "CRITICAL": CRITICAL,
        "ERROR": ERROR,
        "WARNING": WARNING,
        "INFO": INFO,
        "DEBUG": DEBUG,
        "VERBOSE": VERBOSE
    }

    # Function getName: Get the name of a given verbosity level.
    @classmethod
    def getName(cls, level: int):
        """ Get the name of a verbosity level by looking up a level in the _name_lookup  dictionary. Returning the None empty value if the level is not found in the _level_to_name_lookup dictionary."""
        if type(level) is not int:
            print(f"[ERROR::MSG.getName] Invalid verbosity level: '{level}'. The 'level' parameter must be an integer.")
            return None
        if not level in cls._level_to_name_lookup:
            return None
        return cls._level_to_name_lookup[level]
    # End function getName

    # Function getLevel: Get the verbosity level by name.
    @classmethod
    def getLevel(cls, name: str):
        """ Get the verbosity level by name by looking up a name in the _level_lookup dictionary. Returning the DEFAULT_LEVEL if the name is not found in the _level_lookup dictionary."""
        # Check that the input parameter is a string:
        if type(name) is not str:
            print(f"[ERROR::MSG.getLevel] Invalid verbosity level name: '{name}'. The 'name' parameter must be a string.")
            return None
        # Check if the name is in the lookup dictionary:
        if not name in cls._name_to_level_lookup:
            return None
        # Return the verbosity level by name:
        return cls._name_to_level_lookup[name]
    # End function getLevel

    # Function setLevelByName: Set the verbosity level for the script.
    # Intended to be used with the initial configuration parameter of the
    # verbosity level (VERBOSITY="<LEVEL>") before the MSG class is defined.
    @classmethod
    def setLevelByName(cls, name: str):
        """ Set the verbosity level for the script. Example: MSG.setLevelByName('DEBUG')"""
        if type(name) is not str:
            print(f"[ERROR::MSG.setLevelByName] Invalid verbosity level name: '{name}'. The 'name' parameter must be a string.")
            return False
        if name in cls._name_to_level_lookup:
            cls.CONFIGURED_LEVEL = cls._name_to_level_lookup[name]
            return True
        else:
            print(f"[ERROR::MSG.setLevelByName] Invalid verbosity level name: '{name}'. New verbosity level not set.")
            return False
    # End function setLevelByName

    # Function setLevel: Set the verbosity level for the script. Use it to change the verbosity level after the MSG class is defined.
    @classmethod
    def setLevel(cls, level: int):
        """ Set the verbosity level for the script by level. Example: MSG.setLevel(MSG.DEBUG)"""
        if type(level) is not int:
            print(f"[ERROR::MSG.setLevel] Invalid verbosity level: '{level}'. The 'level' parameter must be an integer.")
            return
        if not level in cls._name_lookup:
            print(f"[ERROR::MSG.setLevel] Invalid verbosity level: '{level}'. New verbosity level not set.")
            return
        cls.CONFIGURED_LEVEL = level
    # End function setLevel

    # Function log: Log a message with the specified verbosity level.
    @classmethod
    def log(cls, verbosity_level: int, function_name: str, message: str):
        """ Log a message with the specified verbosity level."""
        if type(verbosity_level) is not int:
            print(f"[ERROR::MSG.log] Invalid verbosity level: '{verbosity_level}'. The 'verbosity_level' parameter must be an integer.")
            return
        verbosity_string = cls.getName(verbosity_level)
        if verbosity_level <= cls.CONFIGURED_LEVEL:
            print(f"[{verbosity_string}::{function_name}] {message}")
    # End function log
# -----------------------------------------------------------------------------
# End class MSG
# -----------------------------------------------------------------------------

# Function get_list_of_notebooks: List all Jupyter notebooks recursively in the playbooks directory.
def get_list_of_notebooks(playbooks_dir: Path) -> Optional[List[Path]]:
    """
    List all Jupyter notebooks recursively in the specified playbooks directory.

    Args:
        playbooks_dir (str):  The path to the directory containing playbooks. This
                              should be a string representing the path where the
                              Jupyter notebooks are stored.
    Returns:
        Optional[List[Path]]: A list of Path objects representing the Jupyter notebooks found,
                              or None if the directory is not valid or no notebooks are found.
      """
    
    MSG.log(MSG.VERBOSE, "get_list_of_notebooks", f"Fetching all Jupyter Notebook (*.ipynb) files in the '{playbooks_dir}' directory.")
    
    # Check that directory is readable:
    if not playbooks_dir.is_dir():
        MSG.log(MSG.ERROR, "get_list_of_notebooks", f"Directory string '{playbooks_dir}' does not point to a valid directory.")
        return None
    
    # Read the directory and get all Jupyter notebook files recursive while ignoring certain directories:
    # playbooks = list(playbooks_dir.rglob('*.ipynb')) # old way, would include notebooks in to .ipybn_checkpoints dir
    playbooks = []
    # Most efficient way to deal with directory traversal with an ignore list is to use a recursive function:
    def recursive_search(current_dir: Path):
        for item in current_dir.iterdir():
            if item.is_dir():
                if item.name not in PLAYBOOK_IGNORE_DIRS:
                    recursive_search(item)
            elif item.is_file() and item.suffix == ".ipynb":
                playbooks.append(item) # Add the file to the list of playbooks.
    # Kick off the  recursive search:
    recursive_search(playbooks_dir)
    # Playbooks should now contain all the Jupyter notebooks in the directory and subdirectories that are not in the ignore list.
    
    # Check if we got any files back:
    if not playbooks:
        MSG.log(MSG.WARNING, "get_list_of_notebooks", f"No Jupyter notebooks found in '{playbooks_dir}'.")
        return None
    return playbooks
# End function get_list_of_notebooks

# Function create_directory: Create a new directory based on current date, time, notebook name, and incident ID.
def create_directory(investigations_dir: Path, case_id: Optional[str] = None, folder_name: Optional[str] = None) -> Optional[Path]:
    """
    Create a new directory based on current date, time, notebook name, and incident ID.

    Args:
        investigations_dir (Path): The path to the investigations directory where the new directory will be created.
        case_id (Optional[str]): An optional incident ID to include in the directory name.
        folder_name (Optional[str]): An optional folder name to include in the directory name.
    
    Returns:
        Optional[Path]: The Path object representing the newly created directory, or None if the directory could not be created.
    """
    
    # Check if the investigations directory exists:
    if not investigations_dir.exists():
        MSG.log(MSG.ERROR, "create_directory", f"Investigations directory '{investigations_dir}' does not exist.")
        return None
    
    # Create the name for the new directory:
    current_time = datetime.now().strftime('%Y-%m-%dT%H.%M')
    new_dir_name = f"{current_time}"
    if case_id: new_dir_name += f" {case_id}"
    if folder_name: new_dir_name += f" - {folder_name}"
    else: new_dir_name += " - New Investigation"
    MSG.log(MSG.INFO, "create_directory", f"New directory name: '{new_dir_name}'")

    # Check that the name only uses allowed characters:
    if not re.match(r"^[a-zA-Z0-9 \.\-_#\(\)]{1,75}$", new_dir_name):
        MSG.log(MSG.ERROR, "create_directory", f"Invalid directory name: '{new_dir_name}'.")
        return None
    
    # Construct the new directory path:
    new_dir_path = investigations_dir / new_dir_name # / operator is used to join paths by the Path object.

    # Check if the directory already exists:
    if new_dir_path.exists():
        MSG.log(MSG.ERROR, "create_directory", f"Directory '{new_dir_path}' already exists.")
        return None

    # If it's a dryrun, just log the action and return None:
    if DRYRUN:
        MSG.log(MSG.DEBUG, "create_directory", f"DRYRUN: Would have created directory '{new_dir_path}'.")
        return None
    
    # Create the directory:
    new_dir_path.mkdir(parents=True, exist_ok=False)
    # Check if the directory was created:
    if not new_dir_path.exists():
        MSG.log(MSG.ERROR, "create_directory", f"Failed to create directory '{new_dir_path}'.")
        return None
    else:
        MSG.log(MSG.INFO, "create_directory", f"Created directory '{new_dir_path}'.")
    return new_dir_path
# End function create_directory

# Function main: Main function to start a new investigation.
def main():
    """
    Main function that will run the code to start a new investigation.
    It will list available notebooks, prompt for selection, prompt for an incident ID,
    create a new directory based on the current date, time, notebook name, and incident ID,
    and copy the selected notebook template to the new directory.
    """
    # Check if the playbooks directory exists and is not empty
    if not PLAYBOOKS_DIR.exists() or not any(PLAYBOOKS_DIR.iterdir()):
        MSG.log(MSG.ERROR, "main", f"Playbooks directory '{PLAYBOOKS_DIR}' does not exist or is empty.")
        return RETURN_ERROR
    
    MSG.log(MSG.VERBOSE, "main", f"Playbooks directory '{PLAYBOOKS_DIR}' exists.")
    
    # List available notebooks
    playbooks = get_list_of_notebooks(PLAYBOOKS_DIR)
    if not playbooks:
        MSG.log(MSG.ERROR, "main", f"No Jupyter notebooks found in the Playbooks directory. Exiting.")
        return RETURN_ERROR
    MSG.log(MSG.VERBOSE, "main", f"Found {len(playbooks)} Jupyter notebooks in the Playbooks directory.")
    
    # Display notebooks and prompt for selection
    print("SELECT> Available Jupyter notebooks:")
    for i, notebook in enumerate(playbooks, 1):
        print(f"{i}. {notebook}")
    
    playbook_index = -1
    while True:
        raw_input = input("SELECT> Select a notebook by number: ")
        if raw_input and re.match(r"^\s*\d+\s*$", raw_input):
            playbook_index = int(str(raw_input).strip()) - 1
            if playbook_index >= 0 and playbook_index < len(playbooks) and playbooks[playbook_index]:
                # We got our index, break out of the loop and continue:
                break
            else:
                # We got input, but it's not a valid index, prompt again:
                print("SELECT> Invalid input. Please enter a number corresponding to the notebook.")
        else:
            # We got no input or invalid input, prompt again:
            print("SELECT> Invalid input. Please enter a number corresponding to the notebook.")
    # End while loop

    # Get the selected notebook name and folder
    selected_notebook = playbooks[playbook_index] if playbook_index >= 0 and playbook_index < len(playbooks) else None
    notebook_name = playbooks[playbook_index] if selected_notebook and selected_notebook.name else None
    notebook_folder = selected_notebook.parent.name if selected_notebook and selected_notebook.parent and selected_notebook.parent.name else None
    # Check if we got valid notebook and folder values:
    if not selected_notebook or not notebook_name or not notebook_folder:
        MSG.log(MSG.ERROR, "main", f"Error determining notebook name and folder. Exiting.")
        MSG.log(MSG.DEBUG, "main", f"Selected notebook: {selected_notebook}")
        MSG.log(MSG.DEBUG, "main", f"Notebook name: {notebook_name}")
        MSG.log(MSG.DEBUG, "main", f"Notebook folder: {notebook_folder}")
        return RETURN_ERROR
    # Print the selected notebook and folder:
    MSG.log(MSG.INFO, "main", f"Selected notebook: [{playbook_index+1}] {selected_notebook.name}")

    # Prompt for incident ID. Expect a 9 digit number matching an Argus case ID.
    print("ID ref> Enter an Argus or Remedy case ID reference.")
    print("ID ref> Press Enter to leave the reference empty for now.")
    case_id = None
    while True:
        case_id = input("ID ref> Enter case ID: ")
        case_id = case_id.strip()
        # If case id not given, use an empty one:
        if not case_id:
            case_id = None
            break
        # If it's given as a number, add a hash in front of it if it's not there:
        elif re.match(r"^#?\d+$", case_id):
            if not case_id.startswith("#"):
                case_id = f"#{case_id}"
            break
        # Otherwise wrap it in #{}:
        elif re.match(r"^[a-zA-Z0-9 \.\-_#\(\)]{1,20}$", case_id):
            case_id = f"#({case_id})"
            break
        else:
            MSG.log(MSG.WARNING, "main", f"Invalid input. Please enter a valid case ID reference or leave it empty.")
            MSG.log(MSG.INFO, "main", f"ID ref explanation> The case ID can be 20 characters long and contain letters [a-z], numbers [0-9].")
            MSG.log(MSG.INFO, "main", f"ID ref explanation> It can also contain space and some special characters: . - _ # ( )")

    MSG.log(MSG.INFO, "main", f"Case ID reference: {case_id}")

    # Create the investigation directory
    try:
        new_dir = create_directory(INVESTIGATIONS_DIR, case_id, notebook_folder)
    except Exception as e:
        MSG.log(MSG.ERROR, "main", f"Failed to create directory: {e}")
        return RETURN_ERROR
    
    # Check if we got a valid directory:
    if not new_dir or not new_dir.exists():
        MSG.log(MSG.ERROR, "main", f"Failed to create directory for the new investigation.")
        return RETURN_ERROR
    
    # Copy the notebook to the new directory
    try:
        # Try to copy the notebook to the new directory:
        new_filename = "inv_" + selected_notebook.name
        new_notebook_path = new_dir / new_filename
        shutil.copy(selected_notebook, new_notebook_path)
    except Exception as e:
        MSG.log(MSG.ERROR, "main", f"Failed to copy the notebook: {e}")
        return RETURN_ERROR
    # Verify that the notebook was copied:
    new_notebook_path = new_dir / f"inv_{selected_notebook.name}"
    if not new_notebook_path.exists():
        MSG.log(MSG.ERROR, "main", f"Failed to copy the notebook to the new directory.")
        return RETURN_ERROR
    MSG.log(MSG.INFO, "main", f"Copied notebook to the new directory: {new_notebook_path}")
# End function main

# Script entry point when run from the command line.
if __name__ == "__main__":
    # Create the argument parser
    parser = argparse.ArgumentParser(description="Run the new investigation script with configurable verbosity.")
    # Define boolean flags for each verbosity level
    parser.add_argument("--silent", action="store_true", help="set verbosity to SILENT")
    parser.add_argument("--critical", action="store_true", help="set verbosity to CRITICAL")
    parser.add_argument("--error", action="store_true", help="set verbosity to ERROR")
    parser.add_argument("--warning", action="store_true", help="set verbosity to WARNING")
    parser.add_argument("--info", action="store_true", help="set verbosity to INFO")
    parser.add_argument("--verbose", action="store_true", help="set verbosity to VERBOSE")
    parser.add_argument("--debug", action="store_true", help="set verbosity to DEBUG")
    parser.add_argument("--dryrun", action="store_true", help="run the script without making any changes")

    # Parse arguments
    args = parser.parse_args()
    # Convert args to a dictionary
    args_dict = vars(args)

    # Determine the verbosity level based on the flags
    verbosity = DEFAULT_VERBOSITY  # Default verbosity level
    for level_flag, is_set in args_dict.items():
        if is_set and re.match(r"^(silent|critical|error|warning|info|verbose|debug)$", level_flag):
            verbosity = level_flag.upper()  # Extract the verbosity level from the flag name
            break  # Assuming only one flag can be set at a time
    
    # Set the verbosity level for the script and throw an error if the level is invalid.
    try:
        if verbosity:
            if not MSG.setLevelByName(verbosity):
                print(f"[ERROR::__main__] Invalid logging verbosity level in configuration: {verbosity}. Exiting.")
                exit(1)
            MSG.log(MSG.VERBOSE, "__main__", f"Set verbosity level to {verbosity}.")
        else:
            # Default behavior or handle no verbosity argument provided
            MSG.setLevelByName('WARNING')  # Default le vel, can adjust as needed
            MSG.log(MSG.VERBOSE, "__main__", "No verbosity level specified; using default level WARNING.")
    except Exception as e:
        print(f"[ERROR::__main__] Error setting logging verbosity level: {e}. Exiting.")
        exit(1)

    # Determine if it's a dryrun
    if args.dryrun:
        MSG.log(MSG.VERBOSE, "__main__", f"Enabling DRYRUN mode.")
        DRYRUN = True
        MSG.log(MSG.VERBOSE, "__main__", f"Running in dryrun mode with verbosity level {verbosity}. No changes will be made.")
    else:
        MSG.log(MSG.VERBOSE, "__main__", f"Running with verbosity level {verbosity}.")
    
    # We have set up the environment, now we can run the main function of the script.
    r = main()
    if r:
        if r == RETURN_ERROR:
            MSG.log(MSG.ERROR, "__main__", "Script execution failed. Exiting with error.")
            exit(1)
        elif r == RETURN_NOT_IMPLEMENTED:
            MSG.log(MSG.ERROR, "__main__", "Script execution ended with 'NOT IMPLEMENTED'. Exiting with error.")
            exit(1)
        else:
            MSG.log(MSG.ERROR, "__main__", "Script execution ended with an unknown error. Exiting with error.")
            exit(1)
    else:
        MSG.log(MSG.INFO, "__main__", "Script execution completed successfully. Exiting normally.")
        exit(0)
# End of script entry point.
