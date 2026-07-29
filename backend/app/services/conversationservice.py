import app.db.conversationdao as cd
import logging
from app.config import Settings

logger = logging.getLogger(__name__)

def build_messages(self, settings: Settings, summary: str | None = None, include_current_user: bool = True):
    messages = [{
        "role": "system",
        "content": "You are a helpful assistant."
    }]

    if summary is not None:
        messages.append({
            "role": "system",
            "content": "Conversation Summary: " + summary
        })
        messages.append({
            "role": "user",
            "content": self.message
        })
    else:
        history = cd.get_conversation_history(self.conversation_id)
        for role, content in history:
            messages.append({
                "role": role,
                "content": content
            })
        if include_current_user:
            messages.append({
                "role": "user",
                "content": self.message
            })

    logger.info(f"Built messages for conversation_id {self.conversation_id}: {messages}")
    return messages


       