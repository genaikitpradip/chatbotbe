# import base64
# from typing import List, Optional
# from langchain_openai import AzureChatOpenAI
# from langchain.schema import HumanMessage, AIMessage, SystemMessage
# from config import settings
# from models import Message, MessageRole
# import logging

# logger = logging.getLogger(__name__)

# class AIService:
#     def __init__(self):
#         self.llm = AzureChatOpenAI(
#             azure_endpoint=settings.azure_openai_endpoint,
#             api_key=settings.azure_openai_api_key,
#             api_version=settings.azure_openai_api_version,
#             deployment_name=settings.azure_openai_deployment_name,
#             temperature=0.7,
#             max_tokens=2000,
#         )
        
#         self.system_prompt = """You are a helpful AI assistant similar to ChatGPT. You can:
# - Answer questions and have conversations
# - Analyze and summarize documents (PDF, Word, text files)
# - Describe and analyze images
# - Maintain context across conversations
# - Provide detailed, helpful responses

# Always be helpful, accurate, and maintain context from previous messages in the conversation.
# Use markdown formatting when appropriate for better readability."""

#     async def generate_response(self, messages: List[Message], image_path: Optional[str] = None) -> str:
#         """Generate AI response based on conversation history"""
#         try:
#             # Convert messages to LangChain format
#             langchain_messages = [SystemMessage(content=self.system_prompt)]
            
#             for msg in messages:
#                 if msg.role == MessageRole.USER:
#                     if image_path and msg == messages[-1]:  # Latest message with image
#                         # Handle image input
#                         content = await self._create_image_message(msg.content, image_path)
#                         langchain_messages.append(HumanMessage(content=content))
#                     else:
#                         langchain_messages.append(HumanMessage(content=msg.content))
#                 else:
#                     langchain_messages.append(AIMessage(content=msg.content))
            
#             # Generate response
#             response = await self.llm.ainvoke(langchain_messages)
#             return response.content
            
#         except Exception as e:
#             logger.error(f"Error generating AI response: {e}")
#             return "I apologize, but I encountered an error while processing your request. Please try again."

#     async def _create_image_message(self, text_content: str, image_path: str) -> List[dict]:
#         """Create message content with image for vision model"""
#         try:
#             with open(image_path, "rb") as image_file:
#                 image_data = base64.b64encode(image_file.read()).decode('utf-8')
            
#             # Determine image type
#             image_type = "jpeg"
#             if image_path.lower().endswith('.png'):
#                 image_type = "png"
#             elif image_path.lower().endswith('.gif'):
#                 image_type = "gif"
#             elif image_path.lower().endswith('.webp'):
#                 image_type = "webp"
            
#             content = [
#                 {
#                     "type": "text",
#                     "text": text_content or "Please describe this image."
#                 },
#                 {
#                     "type": "image_url",
#                     "image_url": {
#                         "url": f"data:image/{image_type};base64,{image_data}"
#                     }
#                 }
#             ]
            
#             return content
#         except Exception as e:
#             logger.error(f"Error processing image: {e}")
#             return [{"type": "text", "text": f"{text_content}\n\n[Error: Could not process the uploaded image]"}]

#     async def generate_chat_title(self, first_message: str, response: str) -> str:
#         """Generate a suitable title for the chat"""
#         try:
#             prompt = f"""Based on this conversation, generate a short, descriptive title (max 50 characters):

# User: {first_message}
# Assistant: {response[:200]}...

# Generate only the title, nothing else."""

#             title_response = await self.llm.ainvoke([HumanMessage(content=prompt)])
#             title = title_response.content.strip().strip('"').strip("'")
            
#             # Ensure title is not too long
#             if len(title) > 50:
#                 title = title[:47] + "..."
            
#             return title
#         except Exception as e:
#             logger.error(f"Error generating chat title: {e}")
#             # Fallback to simple title generation
#             words = first_message.split()[:4]
#             return " ".join(words) + ("..." if len(words) >= 4 else "")

# ai_service = AIService()

import base64
from typing import List, Optional
from langchain_openai import AzureChatOpenAI
from langchain.schema import HumanMessage, AIMessage, SystemMessage
from config import settings
from models import Message, MessageRole
import logging

logger = logging.getLogger(__name__)

class AIService:
    def __init__(self):
        self.llm = AzureChatOpenAI(
            azure_endpoint=settings.azure_openai_endpoint,
            api_key=settings.azure_openai_api_key,
            api_version=settings.azure_openai_api_version,
            deployment_name=settings.azure_openai_deployment_name,
            temperature=0.7,
            max_tokens=2000,
        )
        
        self.system_prompt = """आप एक सहायक AI सहायक हैं। आप केवल भारतीय भाषाओं में ही उत्तर देंगे 
(जैसे हिंदी, तमिल, तेलुगु, बंगाली, मराठी, कन्नड़, मलयालम, पंजाबी, गुजराती आदि)।
अंग्रेज़ी में उत्तर बिल्कुल न दें।

आप कर सकते हैं:
- प्रश्नों का उत्तर देना और बातचीत करना
- दस्तावेज़ों का विश्लेषण और सारांश बनाना (PDF, Word, text files)
- चित्रों का वर्णन और विश्लेषण करना
- वार्तालाप के दौरान संदर्भ बनाए रखना
- विस्तृत और सहायक उत्तर प्रदान करना

हमेशा भारतीय भाषाओं का प्रयोग करें। उपयोगकर्ता की भाषा पहचानकर उसी भाषा में उत्तर दें।"""

    async def generate_response(self, messages: List[Message], image_path: Optional[str] = None) -> str:
        """Generate AI response based on conversation history"""
        try:
            # Convert messages to LangChain format
            langchain_messages = [SystemMessage(content=self.system_prompt)]
            
            for msg in messages:
                if msg.role == MessageRole.USER:
                    if image_path and msg == messages[-1]:  # Latest message with image
                        # Handle image input
                        content = await self._create_image_message(msg.content, image_path)
                        langchain_messages.append(HumanMessage(content=content))
                    else:
                        langchain_messages.append(HumanMessage(content=msg.content))
                else:
                    langchain_messages.append(AIMessage(content=msg.content))
            
            # Generate response
            response = await self.llm.ainvoke(langchain_messages)
            return response.content
            
        except Exception as e:
            logger.error(f"Error generating AI response: {e}")
            return "I apologize, but I encountered an error while processing your request. Please try again."

    async def _create_image_message(self, text_content: str, image_path: str) -> List[dict]:
        """Create message content with image for vision model"""
        try:
            with open(image_path, "rb") as image_file:
                image_data = base64.b64encode(image_file.read()).decode('utf-8')
            
            # Determine image type
            image_type = "jpeg"
            if image_path.lower().endswith('.png'):
                image_type = "png"
            elif image_path.lower().endswith('.gif'):
                image_type = "gif"
            elif image_path.lower().endswith('.webp'):
                image_type = "webp"
            
            content = [
                {
                    "type": "text",
                    "text": text_content or "Please describe this image."
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/{image_type};base64,{image_data}"
                    }
                }
            ]
            
            return content
        except Exception as e:
            logger.error(f"Error processing image: {e}")
            return [{"type": "text", "text": f"{text_content}\n\n[Error: Could not process the uploaded image]"}]

    async def generate_chat_title(self, first_message: str, response: str) -> str:
        """Generate a suitable title for the chat"""
        try:
            prompt = f"""Based on this conversation, generate a short, descriptive title (max 50 characters):

User: {first_message}
Assistant: {response[:200]}...

Generate only the title, nothing else."""

            title_response = await self.llm.ainvoke([HumanMessage(content=prompt)])
            title = title_response.content.strip().strip('"').strip("'")
            
            # Ensure title is not too long
            if len(title) > 50:
                title = title[:47] + "..."
            
            return title
        except Exception as e:
            logger.error(f"Error generating chat title: {e}")
            # Fallback to simple title generation
            words = first_message.split()[:4]
            return " ".join(words) + ("..." if len(words) >= 4 else "")

ai_service = AIService()