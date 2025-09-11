

# import uuid
# from typing import List, Optional
# from datetime import datetime
# from database import get_database
# from models import Chat, Message, MessageRole, FileInfo
# from services.ai_service import ai_service
# import logging

# logger = logging.getLogger(__name__)

# class ChatService:
#     def __init__(self):
#         self.db = None
    
#     def get_db(self):
#         if self.db is None:
#             self.db = get_database()
#         return self.db

#     async def create_chat(self, title: str = "New Chat") -> Chat:
#         """Create a new chat session"""
#         chat_id = str(uuid.uuid4())
#         chat = Chat(
#             id=chat_id,
#             title=title,
#             created_at=datetime.utcnow(),
#             updated_at=datetime.utcnow(),
#             message_count=0
#         )
        
#         db = self.get_db()
#         chat_dict = chat.model_dump(by_alias=True)
#         chat_dict["_id"] = chat_id  # Ensure _id is set correctly
#         await db.chats.insert_one(chat_dict)
        
#         logger.info(f"Created new chat: {chat_id}")
#         return chat

#     async def get_all_chats(self) -> List[Chat]:
#         """Get all chat sessions"""
#         db = self.get_db()
#         cursor = db.chats.find().sort("updated_at", -1)
#         chats = []
        
#         async for chat_doc in cursor:
#             # Handle MongoDB _id field
#             if "_id" in chat_doc:
#                 chat_doc["id"] = chat_doc["_id"]
#             chat = Chat(**chat_doc)
#             chats.append(chat)
        
#         return chats

#     async def get_chat(self, chat_id: str) -> Optional[Chat]:
#         """Get a specific chat"""
#         db = self.get_db()
#         chat_doc = await db.chats.find_one({"_id": chat_id})
        
#         if chat_doc:
#             # Handle MongoDB _id field
#             if "_id" in chat_doc:
#                 chat_doc["id"] = chat_doc["_id"]
#             return Chat(**chat_doc)
#         return None

#     async def get_chat_messages(self, chat_id: str) -> List[Message]:
#         """Get all messages for a chat"""
#         db = self.get_db()
#         cursor = db.messages.find({"chat_id": chat_id}).sort("timestamp", 1)
#         messages = []
        
#         async for msg_doc in cursor:
#             message = Message(**msg_doc)
#             messages.append(message)
        
#         return messages

#     async def add_message(self, chat_id: str, role: MessageRole, content: str, 
#                          file_info: Optional[FileInfo] = None) -> Message:
#         """Add a message to a chat"""
#         message = Message(
#             chat_id=chat_id,
#             role=role,
#             content=content,
#             file=file_info,
#             timestamp=datetime.utcnow()
#         )
        
#         db = self.get_db()
#         await db.messages.insert_one(message.model_dump())
        
#         # Update chat's updated_at and message count
#         await db.chats.update_one(
#             {"_id": chat_id},
#             {
#                 "$set": {"updated_at": datetime.utcnow()},
#                 "$inc": {"message_count": 1}
#             }
#         )
        
#         return message

#     async def rename_chat(self, chat_id: str, new_title: str) -> bool:
#         """Rename a chat"""
#         db = self.get_db()
#         result = await db.chats.update_one(
#             {"_id": chat_id},
#             {
#                 "$set": {
#                     "title": new_title,
#                     "updated_at": datetime.utcnow()
#                 }
#             }
#         )
        
#         return result.modified_count > 0

#     async def delete_chat(self, chat_id: str) -> bool:
#         """Delete a chat and all its messages"""
#         db = self.get_db()
        
#         # Delete all messages
#         await db.messages.delete_many({"chat_id": chat_id})
        
#         # Delete chat
#         result = await db.chats.delete_one({"_id": chat_id})
        
#         logger.info(f"Deleted chat: {chat_id}")
#         return result.deleted_count > 0

#     async def process_message(self, chat_id: str, content: str, 
#                             file_info: Optional[FileInfo] = None,
#                             image_path: Optional[str] = None) -> tuple[Message, Message]:
#         """Process a user message and generate AI response"""
#         # Add user message
#         user_message = await self.add_message(chat_id, MessageRole.USER, content, file_info)
        
#         # Get conversation history
#         messages = await self.get_chat_messages(chat_id)
        
#         # Generate AI response
#         ai_response_content = await ai_service.generate_response(messages, image_path)
        
#         # Add AI response
#         ai_message = await self.add_message(chat_id, MessageRole.ASSISTANT, ai_response_content)
        
#         # Auto-generate title for first message
#         if len(messages) <= 2:  # First user message + AI response
#             try:
#                 title = await ai_service.generate_chat_title(content, ai_response_content)
#                 await self.rename_chat(chat_id, title)
#             except Exception as e:
#                 logger.error(f"Error generating chat title: {e}")
        
#         return user_message, ai_message

# chat_service = ChatService()




import uuid
from typing import List, Optional
from datetime import datetime
from database import get_database
from models import Chat, Message, MessageRole, FileInfo
from services.ai_service import ai_service
import logging

logger = logging.getLogger(__name__)

class ChatService:
    def __init__(self):
        self.db = None
    
    def get_db(self):
        if self.db is None:
            self.db = get_database()
        return self.db

    async def create_chat(self, title: str = "New Chat") -> Chat:
        """Create a new chat session"""
        chat_id = str(uuid.uuid4())
        chat = Chat(
            id=chat_id,
            title=title,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            message_count=0
        )
        
        db = self.get_db()
        chat_dict = chat.model_dump(by_alias=True)
        chat_dict["_id"] = chat_id  # Ensure _id is set correctly
        await db.chats.insert_one(chat_dict)
        
        logger.info(f"Created new chat: {chat_id}")
        return chat

    async def get_all_chats(self) -> List[Chat]:
        """Get all chat sessions"""
        db = self.get_db()
        cursor = db.chats.find().sort("updated_at", -1)
        chats = []
        
        async for chat_doc in cursor:
            # Handle MongoDB _id field
            if "_id" in chat_doc:
                chat_doc["id"] = chat_doc["_id"]
            chat = Chat(**chat_doc)
            chats.append(chat)
        
        return chats

    async def get_chat(self, chat_id: str) -> Optional[Chat]:
        """Get a specific chat"""
        db = self.get_db()
        chat_doc = await db.chats.find_one({"_id": chat_id})
        
        if chat_doc:
            # Handle MongoDB _id field
            if "_id" in chat_doc:
                chat_doc["id"] = chat_doc["_id"]
            return Chat(**chat_doc)
        return None

    async def get_chat_messages(self, chat_id: str) -> List[Message]:
        """Get all messages for a chat"""
        db = self.get_db()
        cursor = db.messages.find({"chat_id": chat_id}).sort("timestamp", 1)
        messages = []
        
        async for msg_doc in cursor:
            message = Message(**msg_doc)
            messages.append(message)
        
        return messages

    async def add_message(self, chat_id: str, role: MessageRole, content: str, 
                         file_info: Optional[FileInfo] = None) -> Message:
        """Add a message to a chat"""
        message = Message(
            chat_id=chat_id,
            role=role,
            content=content,
            file=file_info,
            timestamp=datetime.utcnow()
        )
        
        db = self.get_db()
        await db.messages.insert_one(message.model_dump())
        
        # Update chat's updated_at and message count
        await db.chats.update_one(
            {"_id": chat_id},
            {
                "$set": {"updated_at": datetime.utcnow()},
                "$inc": {"message_count": 1}
            }
        )
        
        return message

    async def rename_chat(self, chat_id: str, new_title: str) -> bool:
        """Rename a chat"""
        db = self.get_db()
        result = await db.chats.update_one(
            {"_id": chat_id},
            {
                "$set": {
                    "title": new_title,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        return result.modified_count > 0

    async def delete_chat(self, chat_id: str) -> bool:
        """Delete a chat and all its messages"""
        db = self.get_db()
        
        # Delete all messages
        await db.messages.delete_many({"chat_id": chat_id})
        
        # Delete chat
        result = await db.chats.delete_one({"_id": chat_id})
        
        logger.info(f"Deleted chat: {chat_id}")
        return result.deleted_count > 0

    async def process_message(self, chat_id: str, content: str,
                               original_content: Optional[str] = None,  # the actual user input 
                            file_info: Optional[FileInfo] = None,
                            web_search_results: Optional[str] = None,  # ✅ new arg (optional)
                            image_path: Optional[str] = None) -> tuple[Message, Message]:
        """Process a user message and generate AI response"""
        # Add user message
        user_message = await self.add_message(chat_id, MessageRole.USER, original_content or content, file_info)

            # 2. Optional: Save web search results as a system message
        if web_search_results:
            await self.add_message(
                chat_id,
                MessageRole.SYSTEM,
                web_search_results
            )
        
        # Get conversation history
        messages = await self.get_chat_messages(chat_id)
        
        # Generate AI response
        ai_response_content = await ai_service.generate_response(messages, image_path)
        
        # Add AI response
        ai_message = await self.add_message(chat_id, MessageRole.ASSISTANT, ai_response_content)
        
        # Auto-generate title for first message
        if len(messages) <= 2:  # First user message + AI response
            try:
                title = await ai_service.generate_chat_title(content, ai_response_content)
                await self.rename_chat(chat_id, title)
            except Exception as e:
                logger.error(f"Error generating chat title: {e}")
        
        return user_message, ai_message

chat_service = ChatService()