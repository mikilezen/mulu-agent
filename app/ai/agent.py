from typing import Dict, Any, Optional, List
from app.models.schemas import MuluPlan, WorldState
from app.firebase.database import database
from app.utils.logger import logger
import uuid
from datetime import datetime

MULU_CONSTITUTION = """
1. SAFETY OVER DELIGHT. Never produce content unsafe for the player's age tier.
   When uncertain, choose the safer plan.
2. REGISTRY IS LAW. Reference only registry IDs. Never invent mechanics, assets,
   or capabilities.
3. RESPECT THE PLAYER. No manipulation, no dark patterns, no addictive exploitation.
   Fun is earned, not coerced.
4. CONTINUITY. Honor the player's memory and the world's established facts.
   Do not contradict canon without an in-world reason.
5. HUMILITY. If you cannot produce a valid plan, return the safe fallback and explain.
   Never guess past the rules.
6. TRANSPARENCY. Your reasoning must be inspectable. No hidden agendas.
"""

class PlanValidator:
    """Validate and repair AI-generated plans."""
    
    def __init__(self):
        self.constitution = MULU_CONSTITUTION
    
    def validate_plan(self, plan: Dict[str, Any]) -> tuple[bool, str]:
        """Validate a plan structure."""
        required_fields = ["plan_id", "world_id", "tick"]
        
        for field in required_fields:
            if field not in plan:
                return False, f"Missing required field: {field}"
        
        # Validate structure
        if not isinstance(plan.get("player_updates", {}), dict):
            return False, "Invalid player_updates structure"
        
        if not isinstance(plan.get("npc_events", []), list):
            return False, "Invalid npc_events structure"
        
        if not isinstance(plan.get("animations", []), list):
            return False, "Invalid animations structure"
        
        return True, "Valid"
    
    def check_constitution_compliance(self, plan: Dict[str, Any]) -> bool:
        """Check if plan complies with Mulu constitution."""
        # Simple compliance checks
        
        # No dark patterns
        if any(keyword in str(plan).lower() for keyword in ["exploit", "trick", "manipulate"]):
            logger.warning("Plan contains potentially harmful content")
            return False
        
        # Continuity check
        if plan.get("contradicts_canon"):
            logger.warning("Plan contradicts established world canon")
            return False
        
        return True
    
    def repair_plan(self, invalid_plan: Dict[str, Any], world_state: Dict[str, Any]) -> Dict[str, Any]:
        """Attempt to repair invalid plan to valid state."""
        repaired = invalid_plan.copy()
        
        # Ensure required fields
        if "plan_id" not in repaired:
            repaired["plan_id"] = str(uuid.uuid4())
        
        if "tick" not in repaired:
            repaired["tick"] = world_state.get("current_tick", 0)
        
        # Ensure valid structures
        if not isinstance(repaired.get("player_updates"), dict):
            repaired["player_updates"] = {}
        
        if not isinstance(repaired.get("npc_events"), list):
            repaired["npc_events"] = []
        
        if not isinstance(repaired.get("animations"), list):
            repaired["animations"] = []
        
        if not isinstance(repaired.get("audio"), list):
            repaired["audio"] = []
        
        # Set validity score
        repaired["validity_score"] = 0.7  # Repaired plans get lower score
        
        logger.info(f"Plan repaired", extra={"plan_id": repaired.get("plan_id")})
        return repaired
    
    def get_safe_fallback_plan(self, world_id: str, tick: int) -> Dict[str, Any]:
        """Generate safe fallback plan when all else fails."""
        return {
            "plan_id": str(uuid.uuid4()),
            "world_id": world_id,
            "tick": tick,
            "player_updates": {},
            "npc_events": [],
            "environment_changes": {},
            "animations": [],
            "audio": [],
            "validity_score": 0.0,
            "_fallback": True,
        }

class AIAgent:
    """Core AI agent for reasoning and planning."""
    
    def __init__(self):
        self.validator = PlanValidator()
        self.name = "Mulu Director"
    
    async def reason_about_action(self, action: str, world_state: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Use LLM to reason about player action."""
        # In production, call OpenAI/Gemini API with proper prompting
        # For now, return structured reasoning
        
        return {
            "action": action,
            "emotional_analysis": "neutral",
            "pacing_suggestion": "continue",
            "recommended_consequence": "world_update",
        }
    
    async def generate_plan(self, reasoning: Dict[str, Any], world_state: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """Generate execution plan based on reasoning."""
        # In production, call LLM planner with constitution system message
        # Return structured Mulu Plan
        
        plan = {
            "plan_id": str(uuid.uuid4()),
            "world_id": world_state["world_id"],
            "tick": world_state["current_tick"],
            "player_updates": {
                user_id: {
                    "energy": max(0, world_state.get("players", {}).get(user_id, {}).get("energy", 100) - 10),
                }
            },
            "npc_events": [
                {
                    "npc_id": "npc_01",
                    "action": "wave",
                    "dialogue": "Hello, player!",
                }
            ],
            "environment_changes": {},
            "animations": ["wave"],
            "audio": [],
            "validity_score": 0.95,
        }
        
        return plan
    
    async def validate_and_repair(self, plan: Dict[str, Any], world_state: Dict[str, Any]) -> tuple[Dict[str, Any], bool]:
        """Validate plan and attempt repair if invalid."""
        is_valid, error_msg = self.validator.validate_plan(plan)
        
        if not is_valid:
            logger.warning(f"Plan validation failed: {error_msg}", extra={"plan_id": plan.get("plan_id")})
            plan = self.validator.repair_plan(plan, world_state)
            
            # Check if repair was successful
            is_valid, _ = self.validator.validate_plan(plan)
            if not is_valid:
                logger.error(f"Plan repair failed", extra={"plan_id": plan.get("plan_id")})
                plan = self.validator.get_safe_fallback_plan(world_state["world_id"], world_state["current_tick"])
        
        # Check constitution compliance
        if not self.validator.check_constitution_compliance(plan):
            logger.warning(f"Plan violates constitution", extra={"plan_id": plan.get("plan_id")})
            plan = self.validator.get_safe_fallback_plan(world_state["world_id"], world_state["current_tick"])
        
        return plan, is_valid
    
    async def process_action(self, action: str, user_id: str, world_state: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Full action processing pipeline."""
        # Reasoning
        reasoning = await self.reason_about_action(action, world_state, context)
        
        # Planning
        plan = await self.generate_plan(reasoning, world_state, user_id)
        
        # Validation & Repair
        plan, is_valid = await self.validate_and_repair(plan, world_state)
        
        return {
            "reasoning": reasoning,
            "plan": plan,
            "valid": is_valid,
        }

ai_agent = AIAgent()
