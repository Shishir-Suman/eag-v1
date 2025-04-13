from typing import List, Dict, Optional, Tuple
from google.genai import types
import asyncio
import logging
from clients.gemini_mpc_client import GeminiMCPClient
import os
import json
from prompts.agent_system import AGENT_SYSTEM_INSTRUCTIONS

# Configure logging with a more detailed format
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


async def process_query(python_mcp_servers: Dict[str, str] = {}) -> dict:
    """
    Process user queries through the Gemini MCP client.
    
    Args:
        python_mcp_servers (Dict[str, str]): Dictionary mapping server names to their Python file paths.
            Defaults to empty dictionary.
            
    Returns:
        dict: The result of processing the query.
    """
    logger.info("Initializing Gemini MCP client")
    mcp_client = GeminiMCPClient()
    await mcp_client.connect_to_multiple_servers(python_mcp_servers)

    # Initialize tool schemas and system instructions
    logger.info("Setting up tool schemas and system instructions")
    tool_schemas = mcp_client.get_tool_schemas()
    system_instruction = AGENT_SYSTEM_INSTRUCTIONS.replace("{{tools}}", json.dumps(tool_schemas))

    # Main interaction loop
    query = input("Enter your query (or 'exit' to quit): ")
    contents = [types.Content(role="user", parts=[types.Part(text=query)])]
    
    while query.lower() != 'exit':
        try:
            logger.info(f"Processing query: {query}")
            _ = await run_agent_loop(system_instruction, contents, mcp_client)
            
            query = input("Awaiting user input: ")
            contents.append(types.Content(role="user", parts=[types.Part(text=query)]))
                
        except Exception as e:
            logger.error(f"Error processing query: {str(e)}", exc_info=True)
        
    logger.info("Session ended by user")
    return {}


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

    # Tool interaction loop
    turn_count = 1
    max_tool_turns = 10

    while function_call and turn_count < max_tool_turns:
        turn_count += 1
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
        logger.info("Requesting model response with tool results")
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

        contents.append(response.candidates[0].content)

    if turn_count >= max_tool_turns and function_call:
        logger.warning(f"Maximum tool turns ({max_tool_turns}) reached")

    logger.info("Agent loop completed")
    return 


async def main() -> None:
    """
    Main entry point for the application.
    Sets up MCP servers and initiates the query processing loop.
    """
    logger.info("Starting application")
    SERVERS_DIR = "servers"

    python_mcp_servers = {
        "calculator": os.path.join(SERVERS_DIR, "calculator/mcp_server.py"),
        "keynote": os.path.join(SERVERS_DIR, "keynote/mcp_server.py"),
        "email": os.path.join(SERVERS_DIR, "email/mcp_server.py"),
    }

    logger.info("Initializing MCP servers")
    _ = await process_query(python_mcp_servers)
    logger.info("Application completed")


if __name__ == "__main__":
    logger.info("Starting application in standalone mode")
    asyncio.run(main())


