import re
# from src.clients.gemini import GeminiClient
from src.models.agent_components import PerceptionResult
from src.clients.gemini import GeminiClient
import logging
from src.utils.logger import configure_logger
import sys



logger = logging.getLogger(__name__)


def extract_perception(user_input: str="hello") -> PerceptionResult:
    """Extracts intent, entities, and tool hints using LLM"""

    prompt = f"""
You are an AI that extracts structured facts from user input.

Input: "{user_input}"

Return the response as a Python dictionary with keys:
- intent: (brief phrase about what the user wants)
- entities: a list of strings representing keywords or values (e.g., ["INDIA", "ASCII"])
- tool_hint: (name of the MCP tool that might be useful, if any)

Output should be a valid json string dump with following schema: "{PerceptionResult.model_json_schema()}"
    """

    try:
        # Initial Gemini Client
        gemini_client = GeminiClient()

        # Get the response
        content = gemini_client(prompt)
        logger.info(f"Perception Generated for the user input: {content}", extra={"stage": "PERCEPTION"})

        # Strip Markdown backticks if present
        content = re.sub(r"^```json|```$", "", content.strip(), flags=re.MULTILINE).strip()
        content = content.replace("null", "None")
        try:
            parsed_content = eval(content)
            parsed_content = PerceptionResult(**parsed_content)
        except Exception as e:
            err_msg = "⚠️ Failed to parse cleaned output or construct PerceptionResult"
            logger.error(err_msg, extra={"stage": "PERCEPTION"})
            raise ValueError(err_msg)

        return parsed_content

    except Exception as e:
        err_msg = "⚠️ Failed to generate perception from Gemini call"
        logger.error(err_msg, extra={"stage": "PERCEPTION"})
        raise RuntimeError(err_msg)