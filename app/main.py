from fastapi import FastAPI, WebSocket, HTTPException, WebSocketDisconnect
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from typing import Dict, List, Set
from app.config import settings
from app.utils.logger import logger, setup_logging
from app.models.schemas import ActionInput, WorldResponse
from app.core.world_kernel import world_kernel
from app.ai.agent import ai_agent
from app.firebase.database import database
import json
from datetime import datetime
import asyncio

# Setup logging
setup_logging(settings.LOG_LEVEL, settings.LOG_FORMAT)

# Connection manager for WebSockets
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}
    
    async def connect(self, user_id: str, websocket: WebSocket):
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = []
        self.active_connections[user_id].append(websocket)
        logger.info(f"Client connected", extra={"user_id": user_id})
    
    async def disconnect(self, user_id: str, websocket: WebSocket):
        if user_id in self.active_connections:
            self.active_connections[user_id].remove(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
        logger.info(f"Client disconnected", extra={"user_id": user_id})
    
    async def broadcast(self, user_id: str, message: dict):
        if user_id in self.active_connections:
            for connection in self.active_connections[user_id]:
                try:
                    await connection.send_json(message)
                except Exception as e:
                    logger.error(f"Failed to send message: {str(e)}")

manager = ConnectionManager()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown."""
    logger.info("Mulu AI Agent Backend starting up")
    yield
    logger.info("Mulu AI Agent Backend shutting down")

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan,
)

# Health Check
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "version": settings.APP_VERSION,
        "timestamp": datetime.utcnow().isoformat(),
    }

# API Routes
@app.post("/api/world/init")
async def initialize_world(owner_id: str):
    """Initialize a new world process."""
    try:
        world_id = await world_kernel.create_world_process(owner_id)
        return {
            "status": "success",
            "world_id": world_id,
            "message": "World initialized successfully",
        }
    except Exception as e:
        logger.error(f"World initialization failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/world/{world_id}/state")
async def get_world_state(world_id: str):
    """Get current world state."""
    try:
        state = await world_kernel.get_world_state(world_id)
        if not state:
            raise HTTPException(status_code=404, detail=f"World {world_id} not found")
        return {
            "status": "success",
            "world": state,
        }
    except Exception as e:
        logger.error(f"Failed to get world state: {str(e)}", extra={"world_id": world_id})
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/action/execute")
async def execute_action(action_input: ActionInput):
    """Process a player action."""
    try:
        # Get world state
        world_state = await world_kernel.get_world_state(action_input.world_id)
        if not world_state:
            raise HTTPException(status_code=404, detail=f"World {action_input.world_id} not found")
        
        # Process action through kernel
        kernel_response = await world_kernel.process_action(action_input)
        
        # Use AI agent to generate plan
        agent_result = await ai_agent.process_action(
            action_input.action,
            action_input.user_id,
            world_state,
            action_input.context
        )
        
        plan = agent_result["plan"]
        
        # Apply plan to world
        success = await world_kernel.apply_plan(action_input.world_id, plan)
        
        if success:
            # Broadcast update to all connected clients
            await manager.broadcast(action_input.user_id, {
                "type": "world_update",
                "world_id": action_input.world_id,
                "tick": plan["tick"],
                "updates": plan,
            })
            
            return {
                "status": "success",
                "plan_id": plan["plan_id"],
                "tick": plan["tick"],
                "updates": plan,
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to apply plan")
    
    except Exception as e:
        logger.error(f"Action execution failed: {str(e)}", extra={"world_id": action_input.world_id, "user_id": action_input.user_id})
        raise HTTPException(status_code=500, detail=str(e))

# WebSocket endpoint
@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    """WebSocket endpoint for real-time communication."""
    await manager.connect(user_id, websocket)
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            logger.info(f"WebSocket message received", extra={"user_id": user_id, "message_type": message.get("type")})
            
            # Handle different message types
            if message.get("type") == "action":
                action = ActionInput(
                    user_id=user_id,
                    world_id=message.get("world_id"),
                    action=message.get("action"),
                    parameters=message.get("parameters", {}),
                    context=message.get("context", {}),
                )
                
                try:
                    world_state = await world_kernel.get_world_state(action.world_id)
                    agent_result = await ai_agent.process_action(
                        action.action,
                        user_id,
                        world_state,
                        action.context
                    )
                    
                    plan = agent_result["plan"]
                    await world_kernel.apply_plan(action.world_id, plan)
                    
                    await manager.broadcast(user_id, {
                        "type": "action_response",
                        "status": "success",
                        "plan": plan,
                    })
                except Exception as e:
                    logger.error(f"WebSocket action failed: {str(e)}")
                    await websocket.send_json({
                        "type": "error",
                        "message": str(e),
                    })
            
            elif message.get("type") == "ping":
                await websocket.send_json({"type": "pong"})
    
    except WebSocketDisconnect:
        await manager.disconnect(user_id, websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}", extra={"user_id": user_id})
        await manager.disconnect(user_id, websocket)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=settings.HOST,
        port=settings.PORT,
        workers=settings.WORKERS,
    )
