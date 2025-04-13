def getCreateFileScript(filePath: str) -> str:
    """
    Generates an AppleScript to checks if the specified Keynote file exists.
    If it doesn't exist, it creates a new Keynote file at the specified path.
    Parameters:
        filePath (str): The path to the Keynote file.
    Returns:
        str: The generated AppleScript.
    """
    appleScript = f'''
    -- Define the file path first
    set keynoteFilePath to "{filePath}"
    -- Check if the file exists
    tell application "System Events"
        set fileExists to exists file keynoteFilePath
    end tell

    -- If the file doesn't exist, create a new presentation
    if not fileExists then
        tell application "Keynote"
            -- Create a new document
            set newPresentation to make new document
            -- Save the new presentation as the specified file
            save newPresentation in POSIX file keynoteFilePath
            
            -- Close the document after saving
            close newPresentation
        end tell
    end if
    '''
    return appleScript