from fastapi import APIRouter, HTTPException, Depends, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import json
import logging
import asyncio
from app.sexual_wellness_agent import SexualWellnessAgent, SexualWellnessQuery, SexualWellnessResponse

# Configure logging
logger = logging.getLogger(__name__)

# Initialize router
router = APIRouter(prefix="/api/sexual-wellness", tags=["Sexual Wellness"])

# Initialize agent
wellness_agent = SexualWellnessAgent()

# WebSocket connection manager
class WellnessConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        
    async def connect(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        self.active_connections[client_id] = websocket
        logger.info(f"Wellness client {client_id} connected. Total connections: {len(self.active_connections)}")
        
    def disconnect(self, client_id: str):
        if client_id in self.active_connections:
            del self.active_connections[client_id]
            logger.info(f"Wellness client {client_id} disconnected. Total connections: {len(self.active_connections)}")
            
    async def send_message(self, client_id: str, message: str):
        if client_id in self.active_connections:
            await self.active_connections[client_id].send_text(message)

# Initialize connection manager
wellness_manager = WellnessConnectionManager()

# Models for request/response
class AddKnowledgeRequest(BaseModel):
    question: str
    answer: str
    api_key: Optional[str] = None

# Routes
@router.post("/query", response_model=SexualWellnessResponse)
async def query_wellness_agent(query: SexualWellnessQuery):
    """
    Query the sexual wellness agent
    """
    try:
        response = wellness_agent.process_query(query)
        return response
    except Exception as e:
        logger.error(f"Error processing wellness query: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")

@router.post("/add-knowledge")
async def add_knowledge(request: AddKnowledgeRequest):
    """
    Add new knowledge to the sexual wellness agent
    Requires an API key for security (should be set in environment variables)
    """
    # In a real application, validate the API key here
    try:
        success = wellness_agent.add_knowledge(request.question, request.answer)
        if success:
            return {"status": "success", "message": "Knowledge added successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to add knowledge")
    except Exception as e:
        logger.error(f"Error adding knowledge: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error adding knowledge: {str(e)}")

@router.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    """
    WebSocket endpoint for real-time interaction with the sexual wellness agent
    """
    await wellness_manager.connect(websocket, client_id)
    try:
        while True:
            data = await websocket.receive_text()
            try:
                message_data = json.loads(data)
                message_type = message_data.get("type", "")
                
                if message_type == "query":
                    query_text = message_data.get("query", "")
                    user_id = message_data.get("user_id", client_id)
                    context = message_data.get("context", {})
                    
                    # Process the query
                    query = SexualWellnessQuery(query=query_text, user_id=user_id, context=context)
                    response = wellness_agent.process_query(query)
                    
                    # Send response back
                    await wellness_manager.send_message(
                        client_id,
                        json.dumps({
                            "type": "response",
                            "data": response.dict()
                        })
                    )
                else:
                    await wellness_manager.send_message(
                        client_id,
                        json.dumps({
                            "type": "error",
                            "message": f"Unknown message type: {message_type}"
                        })
                    )
            except json.JSONDecodeError:
                await wellness_manager.send_message(
                    client_id,
                    json.dumps({
                        "type": "error",
                        "message": "Invalid JSON format"
                    })
                )
            except Exception as e:
                logger.error(f"Error processing WebSocket message: {str(e)}")
                await wellness_manager.send_message(
                    client_id,
                    json.dumps({
                        "type": "error",
                        "message": f"Error processing message: {str(e)}"
                    })
                )
    except WebSocketDisconnect:
        wellness_manager.disconnect(client_id)
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
        wellness_manager.disconnect(client_id)
