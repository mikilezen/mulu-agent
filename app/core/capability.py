from typing import Dict, Any, Optional, List
from app.models.schemas import Capability, CapabilityVerb
from app.utils.logger import logger
from datetime import datetime

class CapabilityManager:
    """Manage AI agent capabilities and enforce security."""
    
    def __init__(self):
        self.default_capabilities = self._get_default_capabilities()
    
    def _get_default_capabilities(self) -> List[Capability]:
        """Get default capabilities for all agents."""
        return [
            Capability(
                verb=CapabilityVerb.SPEAK,
                scope={"zones": ["*"]},
                max_count=None,
                granted_by="default",
            ),
            Capability(
                verb=CapabilityVerb.SPAWN,
                scope={"asset_tags": ["npc", "object"]},
                max_count=50,
                granted_by="default",
            ),
            Capability(
                verb=CapabilityVerb.CHANGE_WORLD,
                scope={"zones": ["*"]},
                max_count=None,
                cooldown_ms=100,
                granted_by="default",
            ),
        ]
    
    def grant_capability(self, agent_id: str, capability: Capability) -> bool:
        """Grant a capability to an agent."""
        try:
            if capability.expires_at and capability.expires_at < datetime.utcnow():
                logger.warning(f"Capability expired", extra={"agent_id": agent_id})
                return False
            
            logger.info(f"Capability granted", extra={
                "agent_id": agent_id,
                "verb": capability.verb,
                "granted_by": capability.granted_by,
            })
            return True
        except Exception as e:
            logger.error(f"Failed to grant capability: {str(e)}")
            return False
    
    def revoke_capability(self, agent_id: str, verb: CapabilityVerb) -> bool:
        """Revoke a capability from an agent."""
        try:
            logger.info(f"Capability revoked", extra={"agent_id": agent_id, "verb": verb})
            return True
        except Exception as e:
            logger.error(f"Failed to revoke capability: {str(e)}")
            return False
    
    def has_capability(self, agent_id: str, verb: CapabilityVerb, scope: Optional[Dict[str, Any]] = None) -> bool:
        """Check if agent has a specific capability."""
        # In production, fetch from database
        # For now, return True for default capabilities
        return verb in [cap.verb for cap in self.default_capabilities]
    
    def validate_plan_capability(self, plan: Dict[str, Any], capabilities: List[Capability]) -> bool:
        """Validate that a plan only uses granted capabilities."""
        try:
            capability_verbs = [cap.verb for cap in capabilities]
            
            # Check player updates
            if plan.get("player_updates"):
                if CapabilityVerb.CHANGE_WORLD not in capability_verbs:
                    logger.warning("Plan requires CHANGE_WORLD capability")
                    return False
            
            # Check NPC events
            if plan.get("npc_events"):
                if CapabilityVerb.SPEAK not in capability_verbs and CapabilityVerb.MODIFY_NPC not in capability_verbs:
                    logger.warning("Plan requires SPEAK or MODIFY_NPC capability")
                    return False
            
            # Check spawning
            if any(event.get("action") == "spawn" for event in plan.get("npc_events", [])):
                if CapabilityVerb.SPAWN not in capability_verbs:
                    logger.warning("Plan requires SPAWN capability")
                    return False
            
            return True
        except Exception as e:
            logger.error(f"Capability validation failed: {str(e)}")
            return False

capability_manager = CapabilityManager()
