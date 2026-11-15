from typing import Dict, Any, Optional, List
from app.firebase.database import database
from app.utils.logger import logger
from datetime import datetime

class WorldService:
    """Business logic for world operations."""
    
    @staticmethod
    async def initialize_world(owner_id: str, world_name: str = "New World") -> Dict[str, Any]:
        """Initialize a new world with full setup."""
        from app.core.world_kernel import world_kernel
        import uuid
        
        world_id = await world_kernel.create_world_process(owner_id)
        
        world_data = {
            "world_id": world_id,
            "owner_id": owner_id,
            "name": world_name,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
        }
        
        return world_data
    
    @staticmethod
    async def get_world_overview(world_id: str) -> Dict[str, Any]:
        """Get world overview with player and NPC counts."""
        world = await database.get_world(world_id)
        if not world:
            return None
        
        players = await database.get_all_players(world_id)
        npcs = await database.get_all_npcs(world_id)
        
        return {
            "world_id": world["world_id"],
            "owner_id": world["owner_id"],
            "current_tick": world.get("current_tick", 0),
            "player_count": len(players),
            "npc_count": len(npcs),
            "environment": world.get("environment", {}),
            "created_at": world.get("created_at"),
            "updated_at": world.get("updated_at"),
        }

class PlayerService:
    """Business logic for player operations."""
    
    @staticmethod
    async def create_player(world_id: str, user_id: str, player_name: str) -> Dict[str, Any]:
        """Create a new player in the world."""
        from app.utils.validators import PlayerValidator
        
        if not PlayerValidator.validate_player_name(player_name):
            raise ValueError(f"Invalid player name: {player_name}")
        
        player_data = {
            "user_id": user_id,
            "name": player_name,
            "location": "world_start",
            "energy": 100.0,
            "health": 100.0,
            "money": 0.0,
            "inventory": {},
            "stats": {
                "level": 1,
                "experience": 0,
                "kills": 0,
                "deaths": 0,
            },
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
        }
        
        success = await database.set_player(world_id, user_id, player_data)
        if success:
            logger.info(f"Player created", extra={"world_id": world_id, "user_id": user_id})
        
        return player_data
    
    @staticmethod
    async def get_player_profile(world_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """Get player profile."""
        return await database.get_player(world_id, user_id)
    
    @staticmethod
    async def update_player_stats(world_id: str, user_id: str, stat_updates: Dict[str, Any]) -> bool:
        """Update player statistics."""
        player = await database.get_player(world_id, user_id)
        if not player:
            return False
        
        # Update stats, ensuring bounds
        if "energy" in stat_updates:
            player["energy"] = max(0, min(100, stat_updates["energy"]))
        if "health" in stat_updates:
            player["health"] = max(0, min(100, stat_updates["health"]))
        if "money" in stat_updates:
            player["money"] = max(0, stat_updates["money"])
        
        if "stats" in stat_updates:
            player["stats"].update(stat_updates["stats"])
        
        player["updated_at"] = datetime.utcnow().isoformat()
        
        return await database.set_player(world_id, user_id, player)

class NPCService:
    """Business logic for NPC operations."""
    
    @staticmethod
    async def create_npc(world_id: str, npc_id: str, npc_name: str, location: str = "world_start") -> Dict[str, Any]:
        """Create a new NPC in the world."""
        npc_data = {
            "npc_id": npc_id,
            "name": npc_name,
            "location": location,
            "mood": "neutral",
            "memory": [],
            "dialogue_history": [],
            "last_action": None,
            "last_dialogue": None,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
        }
        
        success = await database.set_npc(world_id, npc_id, npc_data)
        if success:
            logger.info(f"NPC created", extra={"world_id": world_id, "npc_id": npc_id})
        
        return npc_data
    
    @staticmethod
    async def get_npc_profile(world_id: str, npc_id: str) -> Optional[Dict[str, Any]]:
        """Get NPC profile."""
        return await database.get_npc(world_id, npc_id)
    
    @staticmethod
    async def update_npc_memory(world_id: str, npc_id: str, memory: str) -> bool:
        """Add memory to NPC."""
        npc = await database.get_npc(world_id, npc_id)
        if not npc:
            return False
        
        if "memory" not in npc:
            npc["memory"] = []
        
        npc["memory"].append({
            "text": memory,
            "timestamp": datetime.utcnow().isoformat(),
        })
        
        # Keep last 10 memories only
        npc["memory"] = npc["memory"][-10:]
        
        npc["updated_at"] = datetime.utcnow().isoformat()
        
        return await database.set_npc(world_id, npc_id, npc)
    
    @staticmethod
    async def get_nearby_npcs(world_id: str, location: str, radius: int = 1) -> List[Dict[str, Any]]:
        """Get NPCs at a location."""
        all_npcs = await database.get_all_npcs(world_id)
        
        # Simple location matching (can be improved with actual location system)
        nearby = [npc for npc in all_npcs.values() if npc.get("location") == location]
        
        return nearby

class EventService:
    """Business logic for event operations."""
    
    @staticmethod
    async def log_world_event(world_id: str, event_type: str, event_data: Dict[str, Any]) -> bool:
        """Log an event to the world event stream."""
        event = {
            "type": event_type,
            "data": event_data,
            "timestamp": datetime.utcnow().isoformat(),
        }
        
        return await database.log_event(world_id, event)
    
    @staticmethod
    async def log_player_action(world_id: str, user_id: str, action: str, parameters: Dict[str, Any]) -> bool:
        """Log a player action."""
        event = {
            "type": "player_action",
            "user_id": user_id,
            "action": action,
            "parameters": parameters,
        }
        
        return await EventService.log_world_event(world_id, "player_action", event)
    
    @staticmethod
    async def log_npc_interaction(world_id: str, npc_id: str, user_id: str, interaction_type: str, details: Dict[str, Any]) -> bool:
        """Log NPC interaction."""
        event = {
            "type": "npc_interaction",
            "npc_id": npc_id,
            "user_id": user_id,
            "interaction": interaction_type,
            "details": details,
        }
        
        return await EventService.log_world_event(world_id, "npc_interaction", event)
