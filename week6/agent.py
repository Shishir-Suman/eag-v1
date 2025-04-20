
from google.genai import types
import logging
import json

from src.utils.logger import configure_logger
import asyncio
import os
from src.clients.mcp_servers import PythonMCPClient
from src.components.memory import MemoryManager
from src.models.agent_components import MemoryItem
from src.clients.gemini import GeminiClient

from src.components.decision import generate_plan
from src.components.perception import extract_perception
from src.models.agent_components import MemoryItem

configure_logger()


logger = logging.getLogger(__name__)



# Initialize MCP client and servers
mcp_client = None
python_mcp_servers = {
    "calculator": os.path.join("servers", "calculator/mcp_server.py"),
    "keynote": os.path.join("servers", "keynote/mcp_server.py"),
    "email": os.path.join("servers", "email/mcp_server.py"),
}

from src.components.action import parse_function_call

async def run_agent_loop(): 
    """
    """
    mcp_client = PythonMCPClient()
    await mcp_client.connect_to_multiple_servers(python_mcp_servers)

    # mcp_client = # Initialize tool schemas and system instructions
    tool_schemas = mcp_client.get_tool_schemas()
    # if not mcp_client:
    #     logger.error("MCP client not provided")
    #     return None
    guidance_text = input("Enter the guideline of interaction: ")
    memory_manager = MemoryManager(guidance_text=guidance_text)

    query = input('Enter your query: ')

    
    max_tool_turns = 10
    turn_count = 0
    while turn_count < max_tool_turns:
        turn_count += 1
        perception = extract_perception(query)
        plan = generate_plan(guidance_text=guidance_text, perception=perception, memory_items=memory_manager.messages, tool_descriptions=tool_schemas)
        
        memory_manager.add(message=MemoryItem(text=query, type='user'))
        memory_manager.add(message=MemoryItem(text=plan, type='ai'))

        if "FINAL_ANSWER" in plan:
            logger.info(f"✅ FINAL RESULT: {plan}")
            return plan

        if "FUNCTION_CALL" in plan:
            tool_name, args = parse_function_call(plan)
            function_call = types.FunctionCall(name=tool_name, args=args)

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
        memory_manager.add(message=MemoryItem(text=json.dumps(tool_response), type='tool', tool_name=tool_name))
        # memory_manager.add(message=MemoryItem(text=tool_result.content[0].text, type='tool', tool_name=tool_name))
        # Get next model response
        query = f"Original task: {query}\nPrevious Tool response: {tool_result.content[0].text}\nWhat should I do next?"

        if turn_count >= max_tool_turns and function_call:
            logger.warning(f"Maximum tool turns ({max_tool_turns}) reached")
            break

    logger.info("Agent loop completed")
    # output = contents[-1].parts[0].text
    if "FINAL_ANSWER" in output:
        output = output.split("FINAL_ANSWER | ")[-1].strip()

    return output




if __name__ == "__main__":
    asyncio.run(run_agent_loop())