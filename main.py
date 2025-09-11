

import os
import uuid
import shutil
from typing import List, Optional
from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Depends,Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from langchain_core.documents import Document
from contextlib import asynccontextmanager
from fastapi import FastAPI
from datetime import datetime

from io import BytesIO
from fastapi.responses import StreamingResponse

from config import settings
from database import connect_to_mongo, close_mongo_connection
from models import (
    Chat, ChatCreate, ChatRename, MessageCreate,ChatResponse, 
    ChatListResponse, ChatHistoryResponse, FileInfo,
    MessageRequest, SearchQuery, TTSRequest
)

from services.chat_service import chat_service
from services.file_processor import file_processor
import logging
from datetime import datetime
from database import get_database
from bson import ObjectId
import httpx
from config import Settings



settings = Settings()


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await connect_to_mongo()
    yield
    # Shutdown
    await close_mongo_connection()

app = FastAPI(
    title="ChatGPT Clone API",
    description="FastAPI backend with Azure GPT-4o, LangChain, and MongoDB",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)



# Serve uploaded files
app.mount("/uploads", StaticFiles(directory=settings.upload_dir), name="uploads")

@app.get("/")
async def root():
    return {"message": "ChatGPT Clone API is running"}

@app.post("/api/chat/new", response_model=Chat)
async def create_new_chat(chat_data: ChatCreate):
    """Create a new chat session"""
    try:
        chat = await chat_service.create_chat(chat_data.title)
        return chat
    except Exception as e:
        logger.error(f"Error creating chat: {e}")
        raise HTTPException(status_code=500, detail="Failed to create chat")

@app.get("/api/chat", response_model=ChatListResponse)
async def get_all_chats():
    """Get all chat sessions"""
    try:
        chats = await chat_service.get_all_chats()
        return ChatListResponse(chats=chats)
    except Exception as e:
        logger.error(f"Error fetching chats: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch chats")

@app.get("/api/chat/{chat_id}", response_model=ChatHistoryResponse)
async def get_chat_history(chat_id: str):
    """Get chat history with all messages"""
    try:
        chat = await chat_service.get_chat(chat_id)
        if not chat:
            raise HTTPException(status_code=404, detail="Chat not found")
        
        messages = await chat_service.get_chat_messages(chat_id)
        return ChatHistoryResponse(chat=chat, messages=messages)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching chat history: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch chat history")

@app.put("/api/chat/{chat_id}/rename")
async def rename_chat(chat_id: str, rename_data: ChatRename):
    """Rename a chat"""
    try:
        success = await chat_service.rename_chat(chat_id, rename_data.title)
        if not success:
            raise HTTPException(status_code=404, detail="Chat not found")
        return {"message": "Chat renamed successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error renaming chat: {e}")
        raise HTTPException(status_code=500, detail="Failed to rename chat")

@app.delete("/api/chat/{chat_id}")
async def delete_chat(chat_id: str):
    """Delete a chat and all its messages"""
    try:
        success = await chat_service.delete_chat(chat_id)
        if not success:
            raise HTTPException(status_code=404, detail="Chat not found")
        return {"message": "Chat deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting chat: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete chat")

@app.post("/api/chat/{chat_id}/message", response_model=ChatResponse)
async def send_message(chat_id: str, message_data: MessageCreate):
    """Send a message and get AI response"""

    print("🔥 Incoming message data:", message_data)
    try:
        # Verify chat exists
        chat = await chat_service.get_chat(chat_id)
        if not chat:
            raise HTTPException(status_code=404, detail="Chat not found")
        
        web_search_results = message_data.web_search_results  # <-- Optional string
        # Process message and generate response
        user_message, ai_message = await chat_service.process_message(
            chat_id, message_data.content,
            original_content=message_data.original_content,
            web_search_results=web_search_results
        )
        
        return ChatResponse(
            chat_id=chat_id,
            message=user_message,
            response=ai_message
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing message: {e}")
        raise HTTPException(status_code=500, detail="Failed to process message")
    


@app.post("/api/web-search")
async def web_search(payload: SearchQuery):
    query = payload.query

    if not query:
        return {"results": []}

    api_key = settings.google_api_key
    cx = settings.google_search_engine_id

    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "key": api_key,
        "cx": cx,
        "q": query,
        "num": 3
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            result = response.json()

        items = result.get("items", [])
        web_results = [
            {
                "name": item.get("title"),
                "url": item.get("link"),
                "snippet": item.get("snippet")
            }
            for item in items
        ]

        return {"results": web_results}

    except Exception as e:
        return {"error": str(e), "results": []}


@app.post("/api/chat/{chat_id}/upload", response_model=ChatResponse)
async def upload_file(
    chat_id: str,
    file: UploadFile = File(...),
    message: Optional[str] = Form(None),
    original_content: Optional[str] = Form(None),  # ✅ Add this
    web_search_results: Optional[str] = Form(None),  # ✅ Add this
):
    """Upload file and get AI analysis"""

    try:
        chat = await chat_service.get_chat(chat_id)
        if not chat:
            raise HTTPException(status_code=404, detail="Chat not found")

        if file.size > settings.max_file_size:
            raise HTTPException(status_code=413, detail="File too large")

        # Save file
        file_id = str(uuid.uuid4())
        file_extension = os.path.splitext(file.filename)[1]
        filename = f"{file_id}{file_extension}"
        file_path = os.path.join(settings.upload_dir, filename)

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Analyze file
        processed_content, file_type = await file_processor.process_file(file_path, file.filename)

        # File info for DB
        file_info = FileInfo(
            filename=file.filename,
            type=file.content_type,
            url=f"/uploads/{filename}",
            size=file.size,
        )

        combined_message = f"{message or ''}\n\n{processed_content}".strip()

        # Only send image path if vision is needed
        image_path = file_path if file_type == "image" else None

        # ✅ Call with proper arguments
        user_msg, ai_msg = await chat_service.process_message(
            chat_id=chat_id,
            content=combined_message,
            original_content=original_content,
            file_info=file_info,
            web_search_results=web_search_results,
            image_path=image_path
        )

        return ChatResponse(chat_id=chat_id, message=user_msg, response=ai_msg)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing file upload: {e}")
        raise HTTPException(status_code=500, detail="Failed to process file upload")

@app.post("/api/tts")
async def generate_speech(data: TTSRequest):
    url = f"{settings.azure_tts_openai_api_endpoint}/openai/deployments/{settings.azure_tts_openai_api_deployment_name}/audio/speech?api-version={settings.azure_tts_openai_api_version}"

    headers = {
        "api-key":settings.azure_tts_openai_api_key,
        "Content-Type": "application/json"
    }

    payload = {
        "model": data.model,
        "input": data.text,
        "voice": data.voice
    }

    async with httpx.AsyncClient(timeout=30) as client:
        try:
            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()
        except httpx.HTTPError as e:
            raise HTTPException(status_code=500, detail=f"TTS failed: {str(e)}")

    audio_stream = BytesIO(response.content)
    return StreamingResponse(audio_stream, media_type="audio/mpeg")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)