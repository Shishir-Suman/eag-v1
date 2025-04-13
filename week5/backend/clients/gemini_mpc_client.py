from typing import List
from google import genai
from google.genai import types
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import os
import asyncio
from dotenv import load_dotenv
import traceback
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
# Set the logging level to INFO
logger.setLevel(logging.INFO)


# Load environment variables from .env file
load_dotenv()

# Session timeout
SESSION_TIMEOUT = 10  # seconds

class GeminiMCPClient:
    def __init__(self, model_name: str="gemini-2.0-flash")-> None:
        """
        Initialize Gemini client with MCP tool integration.
        
        Args:
            model_name: The Gemini model to use
            mcp_servers: List of MCP server names to connect to {"name": "filepath"}
        """
        self.model = model_name
        self.client = genai.Client(
            api_key=os.getenv("GEMINI_API_KEY", None),
        )  # Replace with your actual API key setup

        self.available_tools = {}
        self.server_params = {}
    
    async def connect_to_multiple_servers(self, mcp_servers: dict=None) -> None:
        """Connect to multiple MCP servers concurrently."""
        if mcp_servers:
            server_params = [self.create_server_params(filepath) for _, filepath in mcp_servers.items()]
            
            # Run connections with better error handling
            for name, params in zip(mcp_servers.keys(), server_params):
                try:
                    await self.connect_to_server(name, params)
                except Exception as e:
                    logging.error(f"Error connecting to MCP server '{name}': {e}")
                    logging.error(f"Exception details: {traceback.format_exc()}")
            
            logging.info("All connection attempts completed")
    
    def create_server_params(self, server_filepath: str) -> StdioServerParameters:
        """Create StdioServerParameters for a server."""
        # Check if the file exists
        if not os.path.exists(server_filepath):
            logger.warn(f"WARNING: Server file does not exist: {server_filepath}")
        
        return StdioServerParameters(
            command="uv",  # Executable
            args=[
                "run",
                "python",
                f"{server_filepath}",
            ],
            # env=None,  # Optional environment variables
        )
    
    async def connect_to_server(self, server_name: str, server_params: StdioServerParameters) -> None:
        """Connect to an MCP server and register its tools using stdio_client."""
        # Store server parameters for later use
        self.server_params[server_name] = server_params
        
        try:
            # Add a timeout to prevent hanging indefinitely
            async with asyncio.timeout(SESSION_TIMEOUT):  # 10-second timeout
                try:
                    logger.info(f"Opening stdio client for {server_name}...")
                    async with stdio_client(server_params) as (read, write):
                        try:
                            async with ClientSession(read, write) as session:
                                try:
                                    logger.info(f"Initializing session for {server_name}...")
                                    await session.initialize()
                                    
                                    tools_result = await session.list_tools()
                                    tools = tools_result.tools
                                    
                                    logger.info(f"Registering {len(tools)} tools from {server_name}...")
                                    for tool in tools:
                                        self.available_tools[tool.name] = {
                                            "server": server_name,
                                            "description": tool.description,
                                            "parameters": tool.inputSchema
                                        }
        
                                except Exception as e:
                                    logger.error(f"Error in session for {server_name}: {e}")
                                    logger.error(f"Session exception details: {traceback.format_exc()}")
                                    raise
                        except Exception as e:
                            logger.error(f"Error creating ClientSession for {server_name}: {e}")
                            raise
                except Exception as e:
                    logger.error(f"Error with stdio_client for {server_name}: {e}")
                    raise
        except asyncio.TimeoutError:
            logger.error(f"Timeout connecting to MCP server '{server_name}'")
            raise
        except Exception as e:
            logger.error(f"Error connecting to MCP server '{server_name}': {e}")
            raise

    def get_tool_schemas(self)-> List[dict]:
        """Get tool schemas in the format expected by Gemini."""
        schemas = []
        for name, tool_info in self.available_tools.items():
            schemas.append({
                "name": name,
                "description": tool_info["description"],
                "parameters": tool_info["parameters"]
            })
        return schemas

    async def execute_tool(self, tool_call: types.FunctionCall) -> str:
        """Execute a tool call using the appropriate MCP server."""
        tool_name = tool_call.name
        arguments = tool_call.args
        
        if tool_name not in self.available_tools:
            return f"Error: Tool '{tool_name}' not found"
        
        server_name = self.available_tools[tool_name]["server"]
        server_params = self.server_params[server_name]
        
        try:
            async with asyncio.timeout(SESSION_TIMEOUT):  # 10 second timeout
                async with stdio_client(server_params) as (read, write):
                    async with ClientSession(read, write) as session:
                        # Initialize the connection
                        await session.initialize()                        
                        # Call the tool using the MCP session
                        result = await session.call_tool(
                            name=tool_name,
                            arguments=arguments
                        )
                        return result
        except asyncio.TimeoutError:
            return f"Tool execution timed out for '{tool_name}'"
        except Exception as e:
            return f"Error executing tool '{tool_name}': {str(e)}"