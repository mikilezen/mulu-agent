from firebase_admin import firestore
from typing import Dict, Any, Optional, List
from app.firebase.client import firebase_client
from app.utils.logger import logger
from datetime import datetime

class FirestoreDatabase:
    """Firestore database operations."""
    
    def __init__(self):
        self.db = firebase_client.db
    
    # World Operations
    async def create_world(self, world_id: str, owner_id: str, world_data: Dict[str, Any]) -> bool:
        """Create a new world document."""
        try:
            self.db.collection("worlds").document(world_id).set({
                **world_data,
                "owner_id": owner_id,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
            })
            logger.info(f"World created: {world_id}", extra={"world_id": world_id})
            return True
        except Exception as e:
            logger.error(f"Failed to create world: {str(e)}", extra={"world_id": world_id})
            return False
    
    async def get_world(self, world_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve world state."""
        try:
            doc = self.db.collection("worlds").document(world_id).get()
            return doc.to_dict() if doc.exists else None
        except Exception as e:
            logger.error(f"Failed to get world: {str(e)}", extra={"world_id": world_id})
            return None
    
    async def update_world(self, world_id: str, updates: Dict[str, Any]) -> bool:
        """Update world state."""
        try:
            updates["updated_at"] = datetime.utcnow()
            self.db.collection("worlds").document(world_id).update(updates)
            return True
        except Exception as e:
            logger.error(f"Failed to update world: {str(e)}", extra={"world_id": world_id})
            return False
    
    # Player Operations
    async def set_player(self, world_id: str, user_id: str, player_data: Dict[str, Any]) -> bool:
        """Set player state in a world."""
        try:
            self.db.collection("worlds").document(world_id).collection("players").document(user_id).set(player_data)
            return True
        except Exception as e:
            logger.error(f"Failed to set player: {str(e)}", extra={"user_id": user_id, "world_id": world_id})
            return False
    
    async def get_player(self, world_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """Get player state."""
        try:
            doc = self.db.collection("worlds").document(world_id).collection("players").document(user_id).get()
            return doc.to_dict() if doc.exists else None
        except Exception as e:
            logger.error(f"Failed to get player: {str(e)}", extra={"user_id": user_id, "world_id": world_id})
            return None
    
    async def get_all_players(self, world_id: str) -> Dict[str, Dict[str, Any]]:
        """Get all players in a world."""
        try:
            docs = self.db.collection("worlds").document(world_id).collection("players").stream()
            return {doc.id: doc.to_dict() for doc in docs}
        except Exception as e:
            logger.error(f"Failed to get players: {str(e)}", extra={"world_id": world_id})
            return {}
    
    # NPC Operations
    async def set_npc(self, world_id: str, npc_id: str, npc_data: Dict[str, Any]) -> bool:
        """Set NPC state."""
        try:
            self.db.collection("worlds").document(world_id).collection("npcs").document(npc_id).set(npc_data)
            return True
        except Exception as e:
            logger.error(f"Failed to set NPC: {str(e)}", extra={"npc_id": npc_id, "world_id": world_id})
            return False
    
    async def get_npc(self, world_id: str, npc_id: str) -> Optional[Dict[str, Any]]:
        """Get NPC state."""
        try:
            doc = self.db.collection("worlds").document(world_id).collection("npcs").document(npc_id).get()
            return doc.to_dict() if doc.exists else None
        except Exception as e:
            logger.error(f"Failed to get NPC: {str(e)}", extra={"npc_id": npc_id, "world_id": world_id})
            return None
    
    async def get_all_npcs(self, world_id: str) -> Dict[str, Dict[str, Any]]:
        """Get all NPCs in a world."""
        try:
            docs = self.db.collection("worlds").document(world_id).collection("npcs").stream()
            return {doc.id: doc.to_dict() for doc in docs}
        except Exception as e:
            logger.error(f"Failed to get NPCs: {str(e)}", extra={"world_id": world_id})
            return {}
    
    # Event Operations
    async def log_event(self, world_id: str, event_data: Dict[str, Any]) -> bool:
        """Log an event to event stream."""
        try:
            self.db.collection("worlds").document(world_id).collection("events").add({
                **event_data,
                "timestamp": datetime.utcnow(),
            })
            return True
        except Exception as e:
            logger.error(f"Failed to log event: {str(e)}", extra={"world_id": world_id})
            return False
    
    # Replay Log Operations
    async def append_replay_entry(self, world_id: str, entry: Dict[str, Any]) -> bool:
        """Append to world replay log."""
        try:
            entry["timestamp"] = datetime.utcnow()
            self.db.collection("worlds").document(world_id).collection("replay_log").add(entry)
            return True
        except Exception as e:
            logger.error(f"Failed to append replay entry: {str(e)}", extra={"world_id": world_id})
            return False
    
    async def get_replay_log(self, world_id: str) -> List[Dict[str, Any]]:
        """Get complete replay log for a world."""
        try:
            docs = self.db.collection("worlds").document(world_id).collection("replay_log").order_by("timestamp").stream()
            return [doc.to_dict() for doc in docs]
        except Exception as e:
            logger.error(f"Failed to get replay log: {str(e)}", extra={"world_id": world_id})
            return []

database = FirestoreDatabase()
