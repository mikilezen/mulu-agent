import uuid
import hashlib
from typing import Dict, Any, Optional, List
from datetime import datetime
from app.models.schemas import WorldState, MuluPlan, ActionInput, WorldResponse
from app.firebase.database import database
from app.utils.logger import logger

class WorldKernel:
    """Deterministic world kernel managing concurrent world processes."""
    
    def __init__(self):
        self.active_worlds: Dict[str, Dict[str, Any]] = {}
        self.process_queue: List[str] = []
    
    async def create_world_process(self, owner_id: str, seed: Optional[int] = None) -> str:
        """Create a new world process."""
        world_id = str(uuid.uuid4())
        
        if seed is None:
            seed = int(hashlib.md5(f"{world_id}{datetime.utcnow()}".encode()).hexdigest(), 16)
        
        world_state: Dict[str, Any] = {
            "world_id": world_id,
            "owner_id": owner_id,
            "seed": seed,
            "status": "live",
            "tick_rate": "fast",
            "current_tick": 0,
            "players": {},
            "npcs": {},
            "environment": {
                "time_of_day": "day",
                "weather": "clear",
                "active_events": [],
            },
        }
        
        success = await database.create_world(world_id, owner_id, world_state)
        if success:
            self.active_worlds[world_id] = world_state
            logger.info(f"World process created", extra={"world_id": world_id, "seed": seed})
            return world_id
        
        raise Exception("Failed to create world process")
    
    async def get_world_state(self, world_id: str) -> Optional[Dict[str, Any]]:
        """Get current world state."""
        if world_id in self.active_worlds:
            return self.active_worlds[world_id]
        
        state = await database.get_world(world_id)
        if state:
            self.active_worlds[world_id] = state
        
        return state
    
    async def process_action(self, action: ActionInput) -> WorldResponse:
        """Process a player action through the kernel."""
        world_state = await self.get_world_state(action.world_id)
        if not world_state:
            raise Exception(f"World {action.world_id} not found")
        
        # Log action to replay log
        await database.append_replay_entry(action.world_id, {
            "tick": world_state["current_tick"],
            "intent": action.action,
            "parameters": action.parameters,
            "source": action.user_id,
        })
        
        # Build response (plan updates will come from AI agent)
        response = WorldResponse(
            status="accepted",
            world_updates={
                "tick": world_state["current_tick"],
                "player_updates": {},
                "environment": world_state["environment"],
            },
        )
        
        return response
    
    async def apply_plan(self, world_id: str, plan: MuluPlan) -> bool:
        """Apply AI-generated plan to world."""
        world_state = await self.get_world_state(world_id)
        if not world_state:
            return False
        
        try:
            # Update player states
            for user_id, updates in plan.player_updates.items():
                player = await database.get_player(world_id, user_id)
                if player:
                    player.update(updates)
                    await database.set_player(world_id, user_id, player)
            
            # Update NPCs
            for npc_event in plan.npc_events:
                npc_id = npc_event.get("npc_id")
                if npc_id:
                    npc = await database.get_npc(world_id, npc_id)
                    if npc:
                        if "action" in npc_event:
                            npc["last_action"] = npc_event["action"]
                        if "dialogue" in npc_event:
                            npc["last_dialogue"] = npc_event["dialogue"]
                        await database.set_npc(world_id, npc_id, npc)
            
            # Update environment
            if plan.environment_changes:
                world_state["environment"].update(plan.environment_changes)
            
            # Increment tick
            world_state["current_tick"] += 1
            world_state["updated_at"] = datetime.utcnow().isoformat()
            
            # Save updated state
            await database.update_world(world_id, world_state)
            self.active_worlds[world_id] = world_state
            
            # Log event
            await database.log_event(world_id, {
                "type": "plan_applied",
                "plan_id": plan.plan_id,
                "tick": plan.tick,
                "validity_score": plan.validity_score,
            })
            
            return True
        except Exception as e:
            logger.error(f"Failed to apply plan: {str(e)}", extra={"world_id": world_id, "plan_id": plan.plan_id})
            return False
    
    async def schedule_world(self, world_id: str, priority: str = "normal") -> bool:
        """Schedule world for processing."""
        if priority == "high":
            self.process_queue.insert(0, world_id)
        else:
            self.process_queue.append(world_id)
        
        return True
    
    async def get_next_world_to_process(self) -> Optional[str]:
        """Get next world to process from queue."""
        if self.process_queue:
            return self.process_queue.pop(0)
        return None

world_kernel = WorldKernel()
