from typing import Optional, Dict, Any
from pydantic import validator, BaseModel

class CustomException(Exception):
    """Base custom exception."""
    def __init__(self, message: str, code: str = "INTERNAL_ERROR", status_code: int = 500):
        self.message = message
        self.code = code
        self.status_code = status_code
        super().__init__(self.message)

class WorldNotFoundException(CustomException):
    """Raised when world is not found."""
    def __init__(self, world_id: str):
        super().__init__(
            message=f"World {world_id} not found",
            code="WORLD_NOT_FOUND",
            status_code=404
        )

class InvalidActionException(CustomException):
    """Raised when action is invalid."""
    def __init__(self, reason: str):
        super().__init__(
            message=f"Invalid action: {reason}",
            code="INVALID_ACTION",
            status_code=400
        )

class CapabilityDeniedException(CustomException):
    """Raised when action exceeds capabilities."""
    def __init__(self, required: str, granted: str):
        super().__init__(
            message=f"Capability denied. Required: {required}, Granted: {granted}",
            code="CAPABILITY_DENIED",
            status_code=403
        )

class FirebaseOperationException(CustomException):
    """Raised when Firebase operation fails."""
    def __init__(self, operation: str, reason: str):
        super().__init__(
            message=f"Firebase {operation} failed: {reason}",
            code="FIREBASE_ERROR",
            status_code=500
        )

class LLMException(CustomException):
    """Raised when LLM call fails."""
    def __init__(self, reason: str):
        super().__init__(
            message=f"LLM error: {reason}",
            code="LLM_ERROR",
            status_code=502
        )
