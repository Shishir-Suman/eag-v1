from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Union
from enum import Enum
from datetime import datetime

class PerceptionResult(BaseModel):
    user_input: str = Field(..., description="The user's input message or query.")
    intent: Optional[str] = Field(None, description="The detected intent behind the user's input.")
    entities: List[str] = Field(default_factory=list, description="List of entities extracted from the user input.")
    tool_hint: Optional[str] = Field(None, description="Hint for which tool or API to use, if applicable.")


class MessageType(str, Enum):
    TOOL = "tool"
    USER = "user"
    AI = "ai"


class MemoryItem(BaseModel):
    text: str = Field(..., description="The actual content or message stored in memory.")
    type: MessageType = Field(..., description="The source or category of the message (tool, user, or system).")
    timestamp: Optional[str] = Field(default_factory=lambda: datetime.now().isoformat(),
                                     description="The ISO timestamp when the memory item was recorded.")
    tool_name: Optional[str] = Field(None, description="The name of the tool that generated the message, if applicable.")


class ToolCallResult(BaseModel):
    tool_name: str = Field(..., description="The name of the tool that was invoked.")
    arguments: Dict[str, Any] = Field(..., description="The input arguments provided to the tool.")
    result: Union[str, list, dict] = Field(..., description="The output returned by the tool. Can be a string, list, or dictionary.")