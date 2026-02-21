# src/app/endpoints/langchain.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from app.logger import logger

# LangChain imports

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

router = APIRouter()

class LangChainChatRequest(BaseModel):
    model: str
    messages: List[dict]
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = 1024

@router.post("/langchain/chat")
async def langchain_chat(request: LangChainChatRequest):
    """
    Flexible endpoint for advanced LLM workflows using LangChain.
    Supports both OpenAI and Gemini models.
    """
    try:
        # Build prompt from messages
        prompt = "\n".join([
            f"{msg['role'].capitalize()}: {msg['content']}" for msg in request.messages if 'content' in msg
        ])
        # Select LLM
        if request.model.lower().startswith("gemi"):
            raise HTTPException(status_code=501, detail="Gemini support in LangChain is not available in this environment. Please use an OpenAI-compatible model.")
        else:
            llm = ChatOpenAI(model=request.model, temperature=request.temperature)
        # Use LangChain's prompt template
        chat_prompt = ChatPromptTemplate.from_messages([
            (msg['role'], msg['content']) for msg in request.messages if 'content' in msg
        ])
        chain = chat_prompt | llm
        # Run the chain
        result = await chain.ainvoke({})
        return {"response": str(result)}
    except Exception as e:
        logger.error(f"LangChain chat error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"LangChain error: {str(e)}")
