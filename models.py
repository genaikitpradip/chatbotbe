

from pydantic import BaseModel, Field
from typing import Optional, List, Any
from datetime import datetime
from enum import Enum

class Reference(BaseModel):
    title: str
    url: str
    snippet: str

class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"  # ✅ ADD THIS LINE

class FileInfo(BaseModel):
    filename: str
    type: str
    url: str
    size: int

class Message(BaseModel):
    chat_id: str
    role: MessageRole
    content: str
    references: Optional[List[Reference]] = None  # ✅ Make optional
    file: Optional[FileInfo] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class Chat(BaseModel):
    id: str = Field(default_factory=lambda: "", alias="_id")
    title: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    message_count: int = 0
    
    class Config:
        populate_by_name = True

class ChatCreate(BaseModel):
    title: Optional[str] = "New Chat"

class ChatRename(BaseModel):
    title: str

class MessageCreate(BaseModel):
    content: str
    original_content: Optional[str] = None
    web_search_results: Optional[str] = None  # ✅ NEW

class ChatResponse(BaseModel):
    chat_id: str
    message: Message
    response: Message

class ChatListResponse(BaseModel):
    chats: List[Chat]

class ChatHistoryResponse(BaseModel):
    chat: Chat
    messages: List[Message]

class MessageRequest(BaseModel):
    question: str


class SearchQuery(BaseModel):
    query: str

class TTSRequest(BaseModel):
    text: str
    voice: str = "nova"
    model: str = "tts-hd"
    

