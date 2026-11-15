# Mulu v6 Architecture Documentation

## System Overview

The Mulu AI Agent Backend implements the v6 architecture described in the unified spec, creating a deterministic, capability-secured platform for hosting concurrent AI-driven worlds.

```
┌──────────────────────────────────────────────────────────────┐
│  CLIENTS        Unity · Web · Mobile · AR        (any device) │
├──────────────────────────────────────────────────────────────┤
│  SENSES         WebSocket bidirectional communication         │
├──────────────────────────────────────────────────────────────┤
│  AI AGENT       Director Brain (reasoning + planning)          │
│                 ├─ Reasoner (intent analysis)                  │
│                 ├─ Planner (plan generation)                   │
│                 └─ Validator (plan repair)                     │
├──────────────────────────────────────────────────────────────┤
│  WORLD KERNEL   Deterministic core engine                      │
│                 ├─ Scheduler (multi-world process model)       │
│                 ├─ Action Router (capability-checked)          │
│                 ├─ Replay Log (bit-identical replay)           │
│                 └─ Tick Manager (deterministic sim)            │
├──────────────────────────────────────────────────────────────┤
│  PERSISTENCE    Firebase Firestore (world state storage)       │
│                 ├─ World State                                 │
│                 ├─ Player Profiles                             │
│                 ├─ NPC State & Memory                          │
│                 ├─ Event Logs                                  │
│                 └─ Replay Logs                                 │
└──────────────────────────────────────────────────────────────┘
```

## Core Components

### 1. World Kernel (`app/core/world_kernel.py`)

The deterministic core that manages world processes as concurrent entities.

**Responsibilities:**
- Create and manage world processes (world IDs, seeds)
- Process player actions through the action pipeline
- Apply AI-generated plans to world state
- Schedule worlds for processing
- Maintain replay logs for deterministic replay

**Key Methods:**
```python
async def create_world_process(owner_id, seed=None) -> world_id
async def get_world_state(world_id) -> WorldState
async def process_action(action: ActionInput) -> WorldResponse
async def apply_plan(world_id, plan: MuluPlan) -> bool
async def schedule_world(world_id, priority) -> bool
```

### 2. Capability Manager (`app/core/capability.py`)

Implements formal capability security ensuring AI can only escalate within granted permissions.

**Capabilities:**
- `SPAWN` - Create NPCs or objects
- `SPEAK` - NPC dialogue
- `CHANGE_WORLD` - Modify world state
- `MODIFY_NPC` - Change NPC properties
- `CREATE_EVENT` - Generate world events

**Key Methods:**
```python
def has_capability(agent_id, verb, scope=None) -> bool
def validate_plan_capability(plan, capabilities) -> bool
def grant_capability(agent_id, capability) -> bool
def revoke_capability(agent_id, verb) -> bool
```

### 3. AI Agent (`app/ai/agent.py`)

The reasoning and planning engine following the Mulu Constitution.

**Architecture:**
1. **Reasoner** - Analyzes player intent, context, emotional state
2. **Planner** - Generates executable Mulu Plans
3. **Validator** - Validates plans against constitution and capabilities
4. **Auto-Repair** - Fixes invalid plans or falls back to safe defaults

**Key Methods:**
```python
async def reason_about_action(action, world_state, context) -> Dict
async def generate_plan(reasoning, world_state, user_id) -> Dict
async def validate_and_repair(plan, world_state) -> (Dict, bool)
async def process_action(action, user_id, world_state, context) -> Dict
```

### 4. Firebase Integration (`app/firebase/`)

Persistent storage layer using Firestore.

**Collections:**
- `worlds/{world_id}` - World metadata and state
- `worlds/{world_id}/players/{user_id}` - Player states
- `worlds/{world_id}/npcs/{npc_id}` - NPC states
- `worlds/{world_id}/events/{event_id}` - Event logs
- `worlds/{world_id}/replay_log/{entry_id}` - Replay entries

**Key Methods:**
```python
async def create_world(world_id, owner_id, data) -> bool
async def get_world(world_id) -> Dict
async def update_world(world_id, updates) -> bool
async def set_player(world_id, user_id, data) -> bool
async def append_replay_entry(world_id, entry) -> bool
```

### 5. Determinism & Replay (`app/core/replay_log.py`)

Enables bit-identical world replay for debugging, cheating prevention, and learning.

**Replay Log Structure:**
```python
{
  "world_id": str,
  "seed": int,
  "registry_version": str,
  "entries": [
    {
      "tick": int,
      "intent": str,
      "plan_id": str,
      "source": str,  # user_id or agent_id
      "timestamp": datetime
    }
  ]
}
```

**Key Property:** Same seed + registry version + plan log = bit-identical world

## Data Flow

### Player Action Processing

```
1. Client sends action via WebSocket
   → ActionInput(user_id, world_id, action, parameters)

2. FastAPI receives and validates input
   → ActionInput schema validation

3. World Kernel processes action
   → Load world state from Firebase
   → Check action rate limits
   → Route to AI agent

4. AI Agent reasons and plans
   → Reasoner analyzes context
   → Planner generates Mulu Plan
   → Validator checks compliance

5. Plan execution
   → Capability validation
   → Apply to world state
   → Update Firebase
   → Log to replay

6. Response to client
   → World state updates
   → Animations/audio triggers
   → Broadcast via WebSocket

7. State persistence
   → Append to replay log
   → Event logging
   → Cache invalidation
```

## API Endpoints

### World Management

**POST /api/world/init**
```
Query: owner_id: str
Response: { world_id, status }
```

**GET /api/world/{world_id}/state**
```
Response: { world: WorldState }
```

**POST /api/world/{world_id}/players/{user_id}/join**
```
Body: { name, profile }
Response: { player: PlayerState }
```

### Action Execution

**POST /api/action/execute**
```
Body: ActionInput
Response: { plan_id, tick, updates }
```

### WebSocket

**WS /ws/{user_id}**
```
Message types:
- action: { world_id, action, parameters }
- ping: {} (keep-alive)
- subscribe_world: { world_id }
```

## Security Model

### Capability-Based Access Control

```
┌─────────────────┐
│  Untrusted      │
│  • Player input │
│  • LLM output   │
└────────┬────────┘
         ↓
┌─────────────────┐
│  Bridge         │
│  • Validator    │
│  • Capability   │
│    checker      │
└────────┬────────┘
         ↓
┌─────────────────┐
│  Trusted        │
│  • World Kernel │
│  • Firestore    │
└─────────────────┘
```

### The Mulu Constitution

Every AI model call has this as the system prompt:

```
1. SAFETY OVER DELIGHT
2. REGISTRY IS LAW
3. RESPECT THE PLAYER
4. CONTINUITY
5. HUMILITY
6. TRANSPARENCY
```

Plans violating the constitution are rejected before execution.

## Performance Considerations

### Caching
- Active world states cached in-memory
- LRU eviction for inactive worlds
- Replay logs indexed by tick

### Concurrency
- Async/await throughout
- Non-blocking I/O to Firebase
- WebSocket connection pooling

### Scalability
- World processes are independent
- Scheduler can handle 100+ worlds per node
- Firestore provides auto-scaling

## Deployment Architecture

### Development
```
Local Python + FastAPI + Firebase Emulator
```

### Production
```
Docker Container
├─ FastAPI app (workers=4)
├─ Firebase Client (pooled connections)
└─ Structured logging (JSON)
```

### Scaling
```
Kubernetes Pod
├─ Multiple replicas (HPA)
├─ Service mesh (Istio)
├─ Firebase connection pooling
└─ Prometheus metrics
```

## Extension Points

### Custom LLM Providers

Modify `app/ai/agent.py`:
```python
async def call_llm(prompt, model, temperature):
    # Implement provider-specific logic
    # OpenAI, Anthropic, local LLM, etc.
    pass
```

### World Mechanics

Extend `app/core/world_kernel.py`:
```python
async def apply_custom_mechanic(world_id, mechanic_type, params):
    # Add game-specific logic
    pass
```

### Custom Capabilities

Add to `app/core/capability.py`:
```python
Capability(
    verb=CapabilityVerb.CUSTOM_ACTION,
    scope={"specific_zones": ["zone_id"]},
    ...
)
```

## Testing Strategy

- **Unit Tests**: Individual components (`tests/test_*.py`)
- **Integration Tests**: API flows with mocked Firebase
- **Load Tests**: Concurrent world processing
- **Replay Tests**: Determinism validation

```bash
pytest tests/ --cov=app
```

## Monitoring & Observability

### Structured Logging (JSON)
```json
{
  "timestamp": "2024-01-15T10:30:00Z",
  "level": "INFO",
  "message": "Plan applied",
  "world_id": "abc123",
  "plan_id": "def456",
  "validity_score": 0.95
}
```

### Metrics to Track
- Actions per second
- Plan validity rate
- Average latency
- World process count
- Firebase operation costs

### Error Handling
- Graceful degradation (fallback plans)
- Automatic error recovery
- Detailed error logging
- Circuit breaker patterns
