def getCreateShapeScript(answer: str, filePath: str) -> str:
    """
    Generates an AppleScript to create a shape in a Keynote file.
    This script opens a Keynote file, deletes the first slide, creates a new blank slide,
    and adds a rectangle shape with the specified text.
    Parameters:
        answer (str): The text to be added to the shape.
        filePath (str): The path to the Keynote file.
    Returns:
        str: The generated AppleScript.
    """
    appleScript = f'''
    -- Define the file path first
    set keynoteFilePath to "{filePath}"

    tell application "Keynote"
        -- Open the presentation (adjust the path as needed)
        open POSIX file keynoteFilePath
        
        tell front document
            -- Replace slide 1 with a new blank slide
            delete slide 1
            make new slide with properties {{base layout:slide layout "Blank"}} at beginning
            
            tell slide 1
                -- Create a rectangle shape on the first slide
                set newShape to make new shape at end of shapes with properties {{width:400, height:200, position:{{100, 100}}, object text: "{answer}"}}
            end tell

            -- Save the document
            save
            
            -- Close the document
            close
        end tell
        
        activate
    end tell
    '''
    return appleScript