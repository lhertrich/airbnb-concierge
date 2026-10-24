import json
import logging
import ollama
from datetime import datetime
from ollama import ChatResponse

from src.models.enums import MessageType
from src.models.message import Message

logger = logging.getLogger(__name__)

class ConciergeAgent:

    def __init__(self, client: ollama.Client, system_prompt: str = None) -> None:
        self.client = client
        self.requests = []
        self.answers = []
        self.number_of_requests = 0
        if not system_prompt:
            self.system_prompt = self._create_system_prompt()
        else:
            self.system_prompt = system_prompt

    def _create_system_prompt(self) -> str:
        return (
            "You are a helpful and precise assistant for processing Airbnb emails. "
            "Extract the AirBnb user that is contacting via email, the type of request (problem, question, complaint, other)"
            "and the content of the request. Return the information in a JSON format with the following keys: name, type, message. "
            "If it is a booking request, also extract the check-in date, check-out date, number of guests and whether they have animals. "
        )

    def process_email(self, subject: str, body: str, date: datetime) -> Message | None:
        logger.info("Agent received email — subject: %r, date: %s", subject, date)
        chat_messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": f"Email subject: {subject}\nEmail body: {body}"},
        ]
        try:
            response: ChatResponse = self.client.chat(model="concierge", messages=chat_messages)
            data = json.loads(response.message.content)
            return Message(
                name=data.get("name", ""),
                message=data.get("message", ""),
                type=MessageType(data.get("type", "other")),
            )
        except Exception as e:
            logger.error("Failed to process email %r: %s", subject, e)
            return None
