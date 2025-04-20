from src.models.agent_components import MemoryItem
import logging


logger = logging.getLogger(__name__)

class MemoryManager:
    def __init__(self, guidance_text: str = "You are a helpful assistant."):
        self.guidance_text = guidance_text
        self.messages = []


    def add(self, message: MemoryItem):
        """
        Adds a memory item to the memory manage
        """
        self.messages.append(message)
        logger.info(f"Message added to memory", extra={"stage": "MEMORY"})
