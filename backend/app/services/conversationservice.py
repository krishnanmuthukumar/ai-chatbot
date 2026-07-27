import app.db.conversationdao as cd
import logging

logger = logging.getLogger(__name__)

def build_messages(self):
       messages = [{
              "role": "system",
                "content": "You are a helpful assistant."
       }]

       history = cd.get_conversation_history(self.conversation_id)

       for msg in history:
              messages.append({
                     "role": msg[0],
                     "content": msg[1]
              })
        
       logger.info(f"Built messages for conversation_id {self.conversation_id}: {messages}")   
       return messages