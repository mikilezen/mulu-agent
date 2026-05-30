from typing import Optional, Dict, Any
from app.utils.logger import logger
from app.utils.errors import InvalidActionException

class ActionValidator:
    """Validate player actions."""
    
    VALID_ACTIONS = {
        "move": {"required_params": ["direction"], "energy_cost": 5},
        "interact": {"required_params": ["target_id"], "energy_cost": 3},
        "speak": {"required_params": ["message"], "energy_cost": 1},
        "rest": {"required_params": [], "energy_cost": -20},  # Negative = gain
        "use_item": {"required_params": ["item_id"], "energy_cost": 5},
    }
    
    @staticmethod
    def validate_action(action: str, parameters: Dict[str, Any]) -> bool:
        """Validate action and parameters."""
        if action not in ActionValidator.VALID_ACTIONS:
            raise InvalidActionException(f"Unknown action: {action}")
        
        required = ActionValidator.VALID_ACTIONS[action]["required_params"]
        provided = set(parameters.keys())
        missing = set(required) - provided
        
        if missing:
            raise InvalidActionException(f"Missing parameters: {missing}")
        
        return True
    
    @staticmethod
    def get_energy_cost(action: str) -> int:
        """Get energy cost for action."""
        return ActionValidator.VALID_ACTIONS.get(action, {}).get("energy_cost", 0)

class WorldValidator:
    """Validate world state."""
    
    @staticmethod
    def is_valid_location(location: str) -> bool:
        """Check if location is valid."""
        valid_locations = [
            "world_start", "city_center", "forest", "mountain",
            "beach", "village", "temple", "dungeon", "castle"
        ]
        return location in valid_locations
    
    @staticmethod
    def is_valid_stat(stat: str) -> bool:
        """Check if stat is valid."""
        valid_stats = ["energy", "health", "mana", "stamina", "sanity"]
        return stat in valid_stats

class PlayerValidator:
    """Validate player data."""
    
    @staticmethod
    def validate_player_name(name: str) -> bool:
        """Validate player name."""
        if not name or len(name) < 1 or len(name) > 50:
            return False
        if not all(c.isalnum() or c in "-_ " for c in name):
            return False
        return True
