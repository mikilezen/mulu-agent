from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime

# World Process Status
class WorldStatus(str, Enum):
    BOOTING = "booting"
    LIVE = "live"
    PAUSED = "paused"
    MIGRATING = "migrating"
    TERMINATED = "terminated"

# Capability Verbs
class CapabilityVerb(str, Enum):
    SPAWN = "spawn"
    CHANGE_WORLD = "changeWorld"
    SET_CONTROLS = "setControls"
    SPEAK = "speak"
    MODIFY_NPC = "modifyNPC"
    CREATE_EVENT = "createEvent"
    MODIFY_INVENTORY = "modifyInventory"

class ResourceBudget(BaseModel):
    """Resource allocation for a world process."""
    max_tokens: int = 100000
    max_spawns: int = 50
    max_concurrent_actions: int = 10
    cpu_quota_ms: int = 5000
    memory_quota_mb: int = 512

class Capability(BaseModel):
    """Capability token for AI actions."""
    verb: CapabilityVerb
    scope: dict = Field(default_factory=dict)
    asset_tags: List[str] = Field(default_factory=list)
    zone_ids: List[str] = Field(default_factory=list)
    max_count: Optional[int] = None
    cooldown_ms: int = 0
    granted_by: str = "default"
    expires_at: Optional[datetime] = None

class PlayerState(BaseModel):
    """Player state snapshot."""
    user_id: str
    name: str
    location: str = "world_start"
    energy: float = 100.0
    money: float = 0.0
    inventory: dict = Field(default_factory=dict)
    stats: dict = Field(default_factory=dict)
    metadata: dict = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class NPCState(BaseModel):
    """NPC state snapshot."""
    npc_id: str
    name: str
    location: str
    mood: str = "neutral"
    memory: List[str] = Field(default_factory=list)
    metadata: dict = Field(default_factory=dict)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class WorldEnvironment(BaseModel):
    """World environment state."""
    time_of_day: str = "day"
    weather: str = "clear"
    active_events: List[str] = Field(default_factory=list)
    metadata: dict = Field(default_factory=dict)

class WorldState(BaseModel):
    """Complete world state."""
    world_id: str
    owner_id: str
    seed: int
    status: WorldStatus = WorldStatus.LIVE
    tick_rate: str = "fast"
    current_tick: int = 0
    players: dict = Field(default_factory=dict)  # user_id -> PlayerState
    npcs: dict = Field(default_factory=dict)     # npc_id -> NPCState
    environment: WorldEnvironment = Field(default_factory=WorldEnvironment)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class MuluPlan(BaseModel):
    """AI-generated world update plan."""
    plan_id: str
    world_id: str
    tick: int
    player_updates: dict = Field(default_factory=dict)
    npc_events: List[dict] = Field(default_factory=list)
    environment_changes: dict = Field(default_factory=dict)
    animations: List[str] = Field(default_factory=list)
    audio: List[str] = Field(default_factory=list)
    validity_score: float = 0.0

class ActionInput(BaseModel):
    """Player action input."""
    user_id: str
    world_id: str
    action: str
    parameters: dict = Field(default_factory=dict)
    context: dict = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class WorldResponse(BaseModel):
    """Response from world kernel."""
    status: str
    world_updates: dict
    animations: List[str] = Field(default_factory=list)
    audio: List[str] = Field(default_factory=list)
    next_tick_estimate_ms: float = 0.0
