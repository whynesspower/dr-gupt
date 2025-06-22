import os
import base64
import json
import logging
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import uvicorn
from dotenv import load_dotenv
from sarvamai import SarvamAI
import asyncio
import uuid
import tempfile
import shutil
import wave

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Dr. Gupt AI Assistant",
    description="An AI assistant that uses speech-to-text and text-to-speech capabilities",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create static directory if it doesn't exist
os.makedirs("static", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Initialize Sarvam AI client
sarvam_api_key = os.getenv("SARVAM_API")
if not sarvam_api_key:
    raise ValueError("SARVAM_API environment variable not set")

sarvam_client = SarvamAI(api_subscription_key=sarvam_api_key)

# Models for request/response
class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    model: str = "sarvam-m"
    temperature: float = 0.7
    max_tokens: Optional[int] = None

class AudioTranscriptionRequest(BaseModel):
    language_code: str = "en-IN"
    model: str = "sarvika:v2.5"

class TextToSpeechRequest(BaseModel):
    text: str
    target_language_code: str = "en-IN"
    speaker: str = "Anushka"
    pitch: float = 0.0
    pace: float = 1.0
    loudness: float = 1.0

# Connection manager for WebSockets
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        self.active_connections[client_id] = websocket
        logger.info(f"Client {client_id} connected. Total connections: {len(self.active_connections)}")

    def disconnect(self, client_id: str):
        if client_id in self.active_connections:
            del self.active_connections[client_id]
            logger.info(f"Client {client_id} disconnected. Total connections: {len(self.active_connections)}")

    async def send_message(self, client_id: str, message: str):
        if client_id in self.active_connections:
            await self.active_connections[client_id].send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections.values():
            await connection.send_text(message)

manager = ConnectionManager()

# Helper functions
def save_audio_file(audio_data: bytes, filename: str = None) -> str:
    """Save audio data to a file and return the file path"""
    if filename is None:
        filename = f"{uuid.uuid4()}.wav"
    
    file_path = os.path.join("static", filename)
    
    with open(file_path, "wb") as f:
        f.write(audio_data)
    
    return file_path

def base64_to_audio(base64_string: str) -> bytes:
    """Convert base64 string to audio bytes"""
    return base64.b64decode(base64_string)

def audio_to_base64(audio_bytes: bytes) -> str:
    """Convert audio bytes to base64 string"""
    return base64.b64encode(audio_bytes).decode("utf-8")

# API Routes
@app.get("/")
async def root():
    return {"message": "Welcome to Dr. Gupt AI Assistant API"}

@app.post("/api/chat")
async def chat_completion(request: ChatRequest):
    try:
        messages = [{"role": msg.role, "content": msg.content} for msg in request.messages]
        
        response = sarvam_client.chat.completions.create(
            model=request.model,
            messages=messages,
            temperature=request.temperature,
            max_tokens=request.max_tokens if request.max_tokens else None
        )
        
        return response
    except Exception as e:
        logger.error(f"Error in chat completion: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/speech-to-text")
async def speech_to_text(file: UploadFile = File(...), language_code: str = Form("en-IN"), model: str = Form("saarika:v2.5")):
    try:
        # Create a temporary file to store the uploaded audio
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
            # Copy the uploaded file to the temporary file
            shutil.copyfileobj(file.file, temp_file)
            temp_file_path = temp_file.name
        
        # Process the audio file
        with open(temp_file_path, "rb") as audio_file:
            response = sarvam_client.speech_to_text.transcribe(
                file=audio_file,
                model=model,
                language_code=language_code
            )
        
        # Clean up the temporary file
        os.unlink(temp_file_path)
        
        return response
    except Exception as e:
        logger.error(f"Error in speech-to-text: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/text-to-speech")
async def text_to_speech(request: TextToSpeechRequest):
    try:
        response = sarvam_client.text_to_speech.convert(
            text=request.text,
            target_language_code=request.target_language_code,
            speaker=request.speaker,
            pitch=request.pitch,
            pace=request.pace,
            loudness=request.loudness
        )
        
        # Save the audio to a file
        audio_data = base64.b64decode(response["audios"][0])
        filename = f"{uuid.uuid4()}.wav"
        file_path = save_audio_file(audio_data, filename)
        
        return {
            "audio_url": f"/static/{filename}",
            "request_id": response.get("request_id")
        }
    except Exception as e:
        logger.error(f"Error in text-to-speech: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# WebSocket endpoint for real-time communication
@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await manager.connect(websocket, client_id)
    conversation_history = []
    
    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)
            message_type = message_data.get("type", "")
            
            if message_type == "chat":
                # Handle text chat
                user_message = message_data.get("message", "")
                conversation_history.append({"role": "user", "content": user_message})
                
                # Get AI response
                try:
                    response = sarvam_client.chat.completions.create(
                        model="sarvam-m",
                        messages=conversation_history,
                        temperature=0.7
                    )
                    
                    ai_message = response.choices[0].message.content
                    conversation_history.append({"role": "assistant", "content": ai_message})
                    
                    await manager.send_message(
                        client_id,
                        json.dumps({
                            "type": "chat_response",
                            "message": ai_message
                        })
                    )
                except Exception as e:
                    logger.error(f"Error in chat completion via WebSocket: {str(e)}")
                    await manager.send_message(
                        client_id,
                        json.dumps({
                            "type": "error",
                            "message": f"Error processing chat: {str(e)}"
                        })
                    )
            
            elif message_type == "speech":
                # Handle speech-to-text
                try:
                    audio_base64 = message_data.get("audio", "")
                    audio_bytes = base64_to_audio(audio_base64)
                    
                    # Save audio to temporary file
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
                        temp_file.write(audio_bytes)
                        temp_file_path = temp_file.name
                    
                    # Process speech to text
                    with open(temp_file_path, "rb") as audio_file:
                        stt_response = sarvam_client.speech_to_text.transcribe(
                            file=audio_file,
                            model="saarika:v2.5",
                            language_code=message_data.get("language_code", "en-IN")
                        )
                    
                    # Clean up temporary file
                    os.unlink(temp_file_path)
                    
                    transcript = stt_response.get("transcript", "")
                    
                    # Add transcript to conversation history
                    if transcript:
                        conversation_history.append({"role": "user", "content": transcript})
                        
                        # Get AI response
                        response = sarvam_client.chat.completions.create(
                            model="sarvam-m",
                            messages=conversation_history,
                            temperature=0.7
                        )
                        
                        ai_message = response.choices[0].message.content
                        conversation_history.append({"role": "assistant", "content": ai_message})
                        
                        # Convert AI response to speech
                        tts_response = sarvam_client.text_to_speech.convert(
                            text=ai_message,
                            target_language_code=message_data.get("target_language_code", "en-IN"),
                            speaker="Anushka"
                        )
                        
                        # Send both text and audio back to client
                        await manager.send_message(
                            client_id,
                            json.dumps({
                                "type": "speech_response",
                                "transcript": transcript,
                                "message": ai_message,
                                "audio": tts_response["audios"][0]  # Base64 encoded audio
                            })
                        )
                    else:
                        await manager.send_message(
                            client_id,
                            json.dumps({
                                "type": "error",
                                "message": "Could not transcribe audio"
                            })
                        )
                        
                except Exception as e:
                    logger.error(f"Error in speech processing via WebSocket: {str(e)}")
                    await manager.send_message(
                        client_id,
                        json.dumps({
                            "type": "error",
                            "message": f"Error processing speech: {str(e)}"
                        })
                    )
            
            else:
                await manager.send_message(
                    client_id,
                    json.dumps({
                        "type": "error",
                        "message": f"Unknown message type: {message_type}"
                    })
                )
                
    except WebSocketDisconnect:
        manager.disconnect(client_id)
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
        manager.disconnect(client_id)

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
