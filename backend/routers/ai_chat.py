"""
AI Chat API Endpoints
Handles natural language interactions with the CrewAI Master Agent system
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import json
import asyncio
from datetime import datetime

from ..ai.unified_agent import get_unified_agent, UnifiedFinancialAgent
from ..core.auth import get_current_user, User
from ..core.ai_security import get_ai_security_filter, get_privacy_manager
from ..services.conversation_service import get_conversation_service, ConversationService

router = APIRouter()

# Request/Response Models
class ChatMessage(BaseModel):
    message: str = Field(..., description="User's natural language query")
    conversation_id: Optional[str] = Field(None, description="Conversation ID for context")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context data")

class ChatResponse(BaseModel):
    response: str = Field(..., description="AI assistant's response")
    conversation_id: str = Field(..., description="Conversation ID")
    timestamp: datetime = Field(..., description="Response timestamp")
    agent_used: Optional[str] = Field(None, description="Primary agent that handled the query")
    confidence: Optional[float] = Field(None, description="Response confidence score")

class ConversationHistory(BaseModel):
    conversation_id: str
    messages: List[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime

class AgentStatus(BaseModel):
    agents: Dict[str, str] = Field(..., description="Status of each agent")
    system_status: str = Field(..., description="Overall system status")
    last_updated: datetime = Field(..., description="Last status update")

@router.post("/chat", response_model=ChatResponse)
async def chat_with_ai(
    chat_request: ChatMessage,
    current_user: User = Depends(get_current_user),
    unified_agent: UnifiedFinancialAgent = Depends(get_unified_agent),
    conversation_service: ConversationService = Depends(get_conversation_service),
):
    """
    Send a message to the AI Financial Assistant and get a response.

    This endpoint processes natural language queries about personal finances
    and returns intelligent responses from the Unified Financial Agent.
    """
    try:
        # Generate conversation ID if not provided
        conversation_id = chat_request.conversation_id or f"conv_{current_user.id}_{int(datetime.utcnow().timestamp())}"

        # Persist user's message
        try:
            await conversation_service.create_message(
                conversation_id=conversation_id,
                user_id=current_user.id,
                sender="user",
                content=chat_request.message
            )
        except Exception:
            # Log and continue if persistence fails
            pass

        # Process query through Unified Agent
        agent_response = await unified_agent.process_query(
            user_input=chat_request.message,
            context=chat_request.context or {},
            user_id=current_user.id
        )

        # Persist AI response
        try:
            await conversation_service.create_message(
                conversation_id=conversation_id,
                user_id=current_user.id,
                sender="ai",
                content=agent_response.response_text
            )
        except Exception:
            # Log and continue if persistence fails
            pass

        return ChatResponse(
            response=agent_response.response_text,
            conversation_id=conversation_id,
            timestamp=datetime.utcnow(),
            agent_used="unified_financial_agent",
            confidence=agent_response.confidence
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing chat request: {str(e)}"
        )

@router.get("/chat/stream/{conversation_id}")
async def stream_chat_response(
    conversation_id: str,
    message: str,
    current_user: User = Depends(get_current_user),
    unified_agent: UnifiedFinancialAgent = Depends(get_unified_agent)
):
    """
    Stream AI responses in real-time for better user experience.

    This endpoint provides streaming responses for long-running AI queries,
    allowing users to see responses as they are generated.
    """
    async def generate_response():
        try:
            # Process query through unified agent
            agent_response = await unified_agent.process_query(
                user_input=message,
                context={"conversation_id": conversation_id},
                user_id=current_user.id
            )

            # Simulate streaming by yielding chunks
            words = agent_response.response_text.split()
            for i, word in enumerate(words):
                chunk = {
                    "type": "content",
                    "data": word + " ",
                    "index": i
                }
                yield f"data: {json.dumps(chunk)}\n\n"
                await asyncio.sleep(0.1)  # Simulate processing delay
            
            # Send completion signal
            completion = {
                "type": "complete",
                "data": "Response complete",
                "conversation_id": conversation_id
            }
            yield f"data: {json.dumps(completion)}\n\n"
            
        except Exception as e:
            error = {
                "type": "error",
                "data": str(e)
            }
            yield f"data: {json.dumps(error)}\n\n"
    
    return StreamingResponse(
        generate_response(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )

@router.get("/conversations", response_model=List[ConversationHistory])
async def get_conversations(
    limit: int = 20,
    offset: int = 0,
    current_user: User = Depends(get_current_user)
):
    """
    Get user's conversation history with the AI assistant.

    Returns a list of conversations with message history for context
    and conversation management.
    """
    # For MVP, return empty list - conversation persistence will be added later
    return []

@router.get("/conversations/{conversation_id}", response_model=ConversationHistory)
async def get_conversation(
    conversation_id: str,
    conversation_service: ConversationService = Depends(get_conversation_service),
    current_user = Depends(get_current_user)
):
    """
    Get a specific conversation with full message history.
    
    Useful for loading conversation context when resuming a chat session.
    """
    try:
        conversation = await conversation_service.get_conversation(
            conversation_id=conversation_id,
            user_id=current_user.id
        )
        
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        return ConversationHistory(
            conversation_id=conversation.id,
            messages=conversation.messages,
            created_at=conversation.created_at,
            updated_at=conversation.updated_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving conversation: {str(e)}"
        )

@router.delete("/conversations/{conversation_id}")
async def delete_conversation(
    conversation_id: str,
    conversation_service: ConversationService = Depends(get_conversation_service),
    current_user = Depends(get_current_user)
):
    """
    Delete a conversation and all its messages.
    
    This action is irreversible and will permanently remove the conversation
    from the user's history.
    """
    try:
        success = await conversation_service.delete_conversation(
            conversation_id=conversation_id,
            user_id=current_user.id
        )
        
        if not success:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        return {"message": "Conversation deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error deleting conversation: {str(e)}"
        )

@router.get("/agents/status", response_model=AgentStatus)
async def get_agent_status(
    crew_manager: CrewAIManager = Depends(get_crew_manager)
):
    """
    Get the current status of all AI agents in the system.
    
    Useful for monitoring system health and debugging agent issues.
    """
    try:
        agent_status = crew_manager.get_agent_status()
        
        return AgentStatus(
            agents=agent_status,
            system_status="operational" if all(
                status == "active" for status in agent_status.values()
            ) else "degraded",
            last_updated=datetime.utcnow()
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving agent status: {str(e)}"
        )

@router.post("/agents/reset")
async def reset_agents(
    background_tasks: BackgroundTasks,
    current_user = Depends(get_current_user)
):
    """
    Reset all AI agents and clear conversation memory.
    
    This endpoint reinitializes the CrewAI system and clears any
    accumulated context or memory. Use with caution.
    """
    try:
        # TODO: Implement agent reset functionality
        background_tasks.add_task(reset_crew_system)
        
        return {"message": "Agent reset initiated"}
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error resetting agents: {str(e)}"
        )

async def reset_crew_system():
    """Background task to reset the CrewAI system."""
    # TODO: Implement actual reset logic
    pass
