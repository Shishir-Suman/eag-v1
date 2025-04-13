from typing import List, Dict, Optional, Tuple
from google.genai import types
import asyncio
import logging
from clients.gemini_mpc_client import GeminiMCPClient
import os
import json
from prompts.agent_system import AGENT_SYSTEM_INSTRUCTIONS
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Configure logging with a more detailed format
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

class ChatMessage(BaseModel):
    content: str

class ChatResponse(BaseModel):
    response: str

# Initialize MCP client and servers
mcp_client = None
python_mcp_servers = {
    "calculator": os.path.join("servers", "calculator/mcp_server.py"),
    "keynote": os.path.join("servers", "keynote/mcp_server.py"),
    "email": os.path.join("servers", "email/mcp_server.py"),
}

@app.on_event("startup")
async def startup_event():
    global mcp_client
    logger.info("Initializing Gemini MCP client")
    mcp_client = GeminiMCPClient()
    await mcp_client.connect_to_multiple_servers(python_mcp_servers)

@app.post("/chat", response_model=ChatResponse)
async def chat(message: ChatMessage):
    global mcp_client
    if not mcp_client:
        raise HTTPException(status_code=500, detail="MCP client not initialized")
    
    try:
        # Initialize tool schemas and system instructions
        tool_schemas = mcp_client.get_tool_schemas()
        system_instruction = AGENT_SYSTEM_INSTRUCTIONS.replace("{{tools}}", json.dumps(tool_schemas))
        
        # Process the message
        contents = [types.Content(role="user", parts=[types.Part(text=message.content)])]
        response = await run_agent_loop(system_instruction, contents, mcp_client)
        
        if response:
            return ChatResponse(response=response)
        else:
            return ChatResponse(response="No response generated")
            
    except Exception as e:
        logger.error(f"Error processing chat message: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

def parse_tool_call(tool_call_str: str) -> Tuple[Optional[str], Optional[Dict]]:
    """
    Parse a tool call string into its components.
    
    Args:
        tool_call_str (str): The string containing the tool call information.
        
    Returns:
        Tuple[Optional[str], Optional[Dict]]: A tuple containing the tool name and arguments,
            or (None, None) if parsing fails.
    """
    try:
        for line in tool_call_str.splitlines():
            if line.strip().startswith('TOOL_CALL'):
                parts = line.split('|')
                
                logger.debug(f"Parsing tool call: {line}")
                if len(parts) != 3 or parts[0].strip() != 'TOOL_CALL':
                    raise ValueError("Invalid TOOL_CALL format")
                
                tool_name = parts[1].strip()
                arguments_str = parts[2].strip()
                arguments = json.loads(arguments_str)

                if not isinstance(arguments, dict):
                    raise ValueError("Arguments must be a dictionary")

                return tool_name, arguments
                
        logger.warning("No TOOL_CALL found in input")
        return None, None
    except Exception as e:
        logger.error(f"Error parsing tool call: {str(e)}", exc_info=True)
        return None, None

async def run_agent_loop(
    system_instruction: str,
    contents: List[types.Content],
    mcp_client: Optional[GeminiMCPClient] = None
) -> Optional[types.Content]:
    """
    Execute the main agent loop for processing queries and tool interactions.
    
    Args:
        system_instruction (str): The system instructions for the agent.
        contents (List[types.Content]): The conversation history.
        mcp_client (Optional[GeminiMCPClient]): The MCP client instance.
            
    Returns:
        Optional[types.Content]: The final response content, or None if an error occurs.
    """
    if not mcp_client:
        logger.error("MCP client not provided")
        return None

    # Initial model call
    logger.info("Making initial model call")
    response = await mcp_client.client.aio.models.generate_content(
        model=mcp_client.model,
        contents=contents,
        config=types.GenerateContentConfig(
            system_instruction=system_instruction,
            temperature=0,
        ),
    )

    # Process initial response
    contents.append(response.candidates[0].content)
    response_text = response.candidates[0].content.parts[0].text
    logger.info(f"Initial model response: {response_text}")

    # Initialize tool calling loop
    function_call = None
    if "TOOL_CALL" in response_text:
        tool_name, args = parse_tool_call(response_text)
        function_call = types.FunctionCall(name=tool_name, args=args)
    
    validation_call = None
    if "VALIDATION" in response_text:
        validation_call = True


    # Tool interaction loop
    turn_count = 1
    max_tool_turns = 10

    while (function_call or validation_call) and turn_count < max_tool_turns:
        turn_count += 1
        if function_call:
            logger.info(f"Tool turn {turn_count}/{max_tool_turns}")

            # Process function call
            tool_name = function_call.name
            args = function_call.args or {}
            logger.info(f"Executing tool: '{tool_name}' with args: {args}")

            try:
                tool_result = await mcp_client.execute_tool(function_call)
                if tool_result.isError:
                    tool_response = {"error": tool_result.content[0].text}
                    logger.error(f"Tool execution failed: {tool_result.content[0].text}")
                else:
                    tool_response = {"result": tool_result.content[0].text}
                    logger.info("Tool execution successful")
            except Exception as e:
                tool_response = {"error": f"Tool execution failed: {type(e).__name__}: {str(e)}"}
                logger.error(f"Tool execution error: {str(e)}", exc_info=True)

            # Update conversation with tool response
            contents.append(types.Content(role="user", parts=[types.Part(text=json.dumps(tool_response))]))

        # Get next model response
        logger.info("Requesting model response with tool results/validation")
        response = await mcp_client.client.aio.models.generate_content(
            model=mcp_client.model,
            contents=contents,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=1.0,
            ),
        )

        # Process response
        response_text = response.candidates[0].content.parts[0].text
        logger.info(f"Model response: {response_text}")

        function_call = None
        if "TOOL_CALL" in response_text:
            tool_name, args = parse_tool_call(response_text)
            function_call = types.FunctionCall(name=tool_name, args=args)

        validation_call = None
        if "VALIDATION" in response_text:
            validation_call = True

        contents.append(response.candidates[0].content)
        if "FINAL_ANSWER" in response_text:
            break

    if turn_count >= max_tool_turns and function_call:
        logger.warning(f"Maximum tool turns ({max_tool_turns}) reached")

    logger.info("Agent loop completed")
    output = contents[-1].parts[0].text
    if "FINAL_ANSWER" in output:
        output = output.split("FINAL_ANSWER | ")[-1].strip()

    return output

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


