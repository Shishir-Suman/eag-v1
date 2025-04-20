from src.components.perception import PerceptionResult
from src.components.memory import MemoryItem
from typing import List, Optional
from dotenv import load_dotenv
from src.clients.gemini import GeminiClient
import logging


logger = logging.getLogger(__name__)

def generate_plan(
    guidance_text: str, 
    perception: PerceptionResult,
    memory_items: List[MemoryItem],
    tool_descriptions: Optional[str] = None
) -> str:
    """Generates a plan (tool call or final answer) using LLM based on structured perception and memory."""
    memory_texts = "\n".join(f"{m.type}: {m.tool_name}:  {m.text}" for m in memory_items) or "None"

    tool_context = f"\nYou have access to the following tools:\n{tool_descriptions}" if tool_descriptions else ""

    prompt = f"""
You are a reasoning-driven AI agent with access to tools. 
You should strictly follow the guidance when giving final responses
guidance text: {guidance_text}  

Your job is to solve the user's request step-by-step by reasoning through the problem, selecting a tool if needed, and continuing until the FINAL_ANSWER is produced.

{tool_context}

Always follow this loop:

1. Think step-by-step about the problem.
2. If a tool is needed, respond using the format.
   FUNCTION_CALL: tool_name|param1=value1|param2=value2
3. When the final answer is known or available, always respond using the exact format below
   FINAL_ANSWER: [your final result]

Guidelines:
- Respond using EXACTLY ONE of the formats above per step.
- Do NOT include extra text, explanation, or formatting.
- Use nested keys (e.g., input.string) and square brackets for lists.
- You can reference these relevant memories of steps executed so far
{memory_texts}

Input Summary:
- User input: "{perception.user_input}"
- Intent: {perception.intent}
- Entities: {', '.join(perception.entities)}

✅ Examples:
- FUNCTION_CALL: add|a=5|b=3
- FUNCTION_CALL: strings_to_chars_to_int|input.string=INDIA
- FUNCTION_CALL: int_list_to_exponential_sum|input.int_list=[73,78,68,73,65]
- FINAL_ANSWER: [42]

IMPORTANT:
- 🚫 Do NOT invent tools. Use only the tools listed below.
- 🧮 If the question is mathematical or needs calculation, use the appropriate math tool.
- ❌ Do NOT repeat function calls with the same parameters.
- ❌ Do NOT output unstructured responses.
- 🧠 Think before each step. Verify intermediate results mentally before proceeding.
- 💥 If unsure or no tool fits, skip to FINAL_ANSWER: [unknown]
"""
    
    try:
        # Initial Gemini Client
        gemini_client = GeminiClient()

        # Get the response
        content = gemini_client(prompt)
        logger.info(f"Decision plan Generated for the user input", extra={"stage": "DECISION"})

        # Identify any function in the response
        for line in content.splitlines():
            if line.strip().startswith("FUNCTION_CALL:") or line.strip().startswith("FINAL_ANSWER:"):
                return line.strip()
        return content

    except Exception as e:
        err_msg = "⚠️ Decision generation failed:"
        logger.error(err_msg, extra={"stage": "DECISION"})
        raise RuntimeError(err_msg)