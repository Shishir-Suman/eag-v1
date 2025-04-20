from mcp import ClientSession
import ast
from src.models.agent_components import ToolCallResult
from typing import Any, Dict
import logging
from google.genai import types


logger = logging.getLogger(__name__)


def parse_function_call(response: str) -> tuple[str, Dict[str, Any]]:
    """Parses FUNCTION_CALL string into tool name and arguments."""

    try:
        _, function_info = response.split(":", 1)
        parts = [p.strip() for p in function_info.split("|")]
        func_name, param_parts = parts[0], parts[1:]

        if param_parts[0].strip() == "":
            return func_name, {}
        params = {}
        for part in param_parts:
            if "=" not in part:
                raise ValueError(f"Invalid param: {part}")
            key, value = part.split("=", 1)

            try:
                parsed_value = ast.literal_eval(value)
            except Exception:
                parsed_value = value.strip()
            params[key.strip()] = parsed_value
        logger.info(f"Parsed {func_name} with {params}", extra={"stage": "ACTION"})
        return func_name, params

    except Exception as e:
        err_msg = f"❌ Failed to parse FUNCTION_CALL: {e}"
        logger.error(err_msg, extra={"stage": "ACTION"})
        raise ValueError(err_msg)


# async def execute_tool(mcp_client, tools: list[Any], text: str) -> ToolCallResult:
#     """Executes a FUNCTION_CALL via MCP tool session."""
#     try:

#         tool_name, arguments = parse_function_call(text)
#         function_call = types.FunctionCall(name=tool_name, args=args)
#         tool = next((t for t in tools if t.name == tool_name), None)
#         if not tool:
#             raise ValueError(f"Tool '{tool_name}' not found in registered tools")

#         logger.info(f"Calling '{tool_name}' with: {arguments}", extra={"stage": "ACTION"})
#         result = await mcp_client.execute_tool(function_call)

#         logger.info(f"✅ {tool_name} result: {result}", extra={"stage": "ACTION"})
#         return ToolCallResult(
#             tool_name=tool_name,
#             arguments=arguments,
#             result=result
#         )

#     except Exception as e:
#         err_msg = f"❌ Failed to parse FUNCTION_CALL: {text}"
#         logger.error(err_msg, extra={"stage": "ACTION"})
#         raise ValueError(err_msg)
