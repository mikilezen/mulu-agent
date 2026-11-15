from typing import Dict, Any, List
from pydantic import BaseModel, Field
from datetime import datetime
import uuid

class ReplayEntry(BaseModel):
    """Single entry in replay log."""
    tick: int
    intent: str
    plan_id: str
    source: str  # user_id or agent_id
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class ReplayLog(BaseModel):
    """Complete replay log for a world."""
    world_id: str
    seed: int
    registry_version: str
    entries: List[ReplayEntry] = Field(default_factory=list)

class DeterminismValidator:
    """Validate and manage deterministic replay contract."""
    
    def __init__(self):
        self.replay_logs: Dict[str, ReplayLog] = {}
    
    def create_replay_log(self, world_id: str, seed: int, registry_version: str = "1.0.0") -> ReplayLog:
        """Create a new replay log."""
        log = ReplayLog(
            world_id=world_id,
            seed=seed,
            registry_version=registry_version,
        )
        self.replay_logs[world_id] = log
        return log
    
    def append_entry(self, world_id: str, entry: ReplayEntry) -> bool:
        """Append entry to replay log."""
        if world_id not in self.replay_logs:
            return False
        
        self.replay_logs[world_id].entries.append(entry)
        return True
    
    def get_log(self, world_id: str) -> ReplayLog:
        """Get replay log for world."""
        return self.replay_logs.get(world_id)
    
    def generate_replay_checksum(self, world_id: str) -> str:
        """Generate checksum of replay log for integrity verification."""
        if world_id not in self.replay_logs:
            return None
        
        import hashlib
        import json
        
        log = self.replay_logs[world_id]
        data = json.dumps({
            "world_id": log.world_id,
            "seed": log.seed,
            "registry_version": log.registry_version,
            "entries_count": len(log.entries),
        })
        
        return hashlib.sha256(data.encode()).hexdigest()

determinism_validator = DeterminismValidator()
