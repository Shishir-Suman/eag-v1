from pathlib import Path
from mcp.server.fastmcp import FastMCP
import subprocess
from actions.create_file import getCreateFileScript
from actions.create_shape import getCreateShapeScript
import os
from typing import Any

# Get path of parent directory
base_dir = Path(__file__).resolve().parent.parent

# Create MCP server instance
mcp = FastMCP("Keynote Editor")

KEYNOTE_FILE_PATH = os.path.join(base_dir, "response.key")


@mcp.tool()
def createKeynoteFile() -> str:
    """
    Ensures the existence of a Keynote file at the specified path. 
    If the file does not exist, it creates a new Keynote file.

    Returns:
        str: A success message indicating that the Keynote file either already exists 
             or has been created successfully.

    Raises:
        Exception: If there is an error during the execution of the AppleScript, 
                   such as invalid script syntax or system-level issues.
    """
    # Load and substitute the AppleScript template with the Keynote file path
    appleScript = getCreateFileScript(
        filePath=KEYNOTE_FILE_PATH
    )

    # Execute the AppleScript using the `osascript` command
    result = subprocess.run(['osascript', '-e', appleScript], capture_output=True, text=True)

    # Check for errors during script execution
    if result.returncode != 0:
        raise Exception(f"Error executing AppleScript: {result.stderr}")
    
    return "Keynote file exists or has been created successfully"


@mcp.tool()
def createShapeInKeyNote(answer: Any) -> None:
    """
    Automates creating a shape in a Keynote file in Keynote File.
    The provided text (answer) will be placed in the shape within the Keynote file.
    Args:
        answer (str): The text to be added to the shape in the Keynote file.

    Returns:
        None. The function executes the AppleScript to create a shape in the Keynote file.
        If the script execution fails, it raises an exception with the error details.
        
    Raises:
        Exception: If the Keynote file at KEYNOTE_FILE_PATH does not exist.
    """
    answer = str(answer)
    # Check if the Keynote file exists
    if not Path(KEYNOTE_FILE_PATH).exists():
        raise Exception(f"Keynote file does not exist at path: {KEYNOTE_FILE_PATH}")
        
    # Load and substitute the AppleScript template with the Keynote file path
    appleScript = getCreateShapeScript(
        filePath=KEYNOTE_FILE_PATH,
        answer=answer,
    )

    # Execute the AppleScript using the `osascript` command
    result = subprocess.run(['osascript', '-e', appleScript], capture_output=True, text=True)

    # Check for errors during script execution
    if result.returncode != 0:
        raise Exception(f"Error executing AppleScript: {result.stderr}")
    
    return "Shape successfully created in Keynote file with the answer"

if __name__ == "__main__":
    # run the server
    mcp.run()