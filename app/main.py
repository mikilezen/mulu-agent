from fastapi import FastAPI, WebSocket, HTTPException, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from contextlib import asynccontextmanager
from typing import Dict, List
from pydantic import BaseModel, Field
from app.config import settings
from app.utils.logger import logger, setup_logging
from app.models.schemas import ActionInput
from app.core.world_kernel import world_kernel
from app.ai.agent import ai_agent
from app.services.language_review import review_text
from app.reviewer_ui import HTML as REVIEWER_HTML
import json
from datetime import datetime

setup_logging(settings.LOG_LEVEL, settings.LOG_FORMAT)


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, user_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.setdefault(user_id, []).append(websocket)
        logger.info("Client connected", extra={"user_id": user_id})

    async def disconnect(self, user_id: str, websocket: WebSocket):
        if user_id in self.active_connections:
            self.active_connections[user_id].remove(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
        logger.info("Client disconnected", extra={"user_id": user_id})

    async def broadcast(self, user_id: str, message: dict):
        if user_id in self.active_connections:
            for connection in self.active_connections[user_id]:
                try:
                    await connection.send_json(message)
                except Exception as exc:
                    logger.error("Failed to send message: %s", exc)


manager = ConnectionManager()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Mulu AI Agent Backend starting up")
    yield
    logger.info("Mulu AI Agent Backend shutting down")


app = FastAPI(title=settings.APP_NAME, version=settings.APP_VERSION, lifespan=lifespan)


class LanguageReviewRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=100_000)
    language: str = Field(default="auto", pattern="^(auto|am|om)$")


@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": settings.APP_VERSION, "timestamp": datetime.utcnow().isoformat()}


@app.get("/reviewer", response_class=HTMLResponse)
async def language_reviewer():
    """Serve the browser-based Amharic and Afaan Oromo review tool."""
    return HTMLResponse(REVIEWER_HTML)


@app.post("/api/language/review")
async def language_review(request: LanguageReviewRequest):
    """Run transparent, local quality checks against generated language copy."""
    try:
        return review_text(request.text, request.language)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/api/world/init")
async def initialize_world(owner_id: str):
    try:
        world_id = await world_kernel.create_world_process(owner_id)
        return {"status": "success", "world_id": world_id, "message": "World initialized successfully"}
    except Exception as exc:
        logger.error("World initialization failed: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.get("/api/world/{world_id}/state")
async def get_world_state(world_id: str):
    try:
        state = await world_kernel.get_world_state(world_id)
        if not state:
            raise HTTPException(status_code=404, detail=f"World {world_id} not found")
        return {"status": "success", "world": state}
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Failed to get world state: %s", exc, extra={"world_id": world_id})
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.post("/api/action/execute")
async def execute_action(action_input: ActionInput):
    try:
        world_state = await world_kernel.get_world_state(action_input.world_id)
        if not world_state:
            raise HTTPException(status_code=404, detail=f"World {action_input.world_id} not found")
        await world_kernel.process_action(action_input)
        agent_result = await ai_agent.process_action(action_input.action, action_input.user_id, world_state, action_input.context)
        plan = agent_result["plan"]
        if await world_kernel.apply_plan(action_input.world_id, plan):
            await manager.broadcast(action_input.user_id, {"type": "world_update", "world_id": action_input.world_id, "tick": plan["tick"], "updates": plan})
            return {"status": "success", "plan_id": plan["plan_id"], "tick": plan["tick"], "updates": plan}
        raise HTTPException(status_code=500, detail="Failed to apply plan")
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Action execution failed: %s", exc, extra={"world_id": action_input.world_id, "user_id": action_input.user_id})
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    await manager.connect(user_id, websocket)
    try:
        while True:
            message = json.loads(await websocket.receive_text())
            logger.info("WebSocket message received", extra={"user_id": user_id, "message_type": message.get("type")})
            if message.get("type") == "action":
                action = ActionInput(user_id=user_id, world_id=message.get("world_id"), action=message.get("action"), parameters=message.get("parameters", {}), context=message.get("context", {}))
                try:
                    world_state = await world_kernel.get_world_state(action.world_id)
                    agent_result = await ai_agent.process_action(action.action, user_id, world_state, action.context)
                    plan = agent_result["plan"]
                    await world_kernel.apply_plan(action.world_id, plan)
                    await manager.broadcast(user_id, {"type": "action_response", "status": "success", "plan": plan})
                except Exception as exc:
                    logger.error("WebSocket action failed: %s", exc)
                    await websocket.send_json({"type": "error", "message": str(exc)})
            elif message.get("type") == "ping":
                await websocket.send_json({"type": "pong"})
    except WebSocketDisconnect:
        await manager.disconnect(user_id, websocket)
    except Exception as exc:
        logger.error("WebSocket error: %s", exc, extra={"user_id": user_id})
        await manager.disconnect(user_id, websocket)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.HOST, port=settings.PORT, workers=settings.WORKERS)
