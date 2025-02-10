from typing import List, Dict, Any, Optional

class UsageLimitExceededError(Exception):
    def __init__(self, message: str):
        super().__init__(message)

class BadRequestError(Exception):
    def __init__(self, message: str):
        super().__init__(message)

class ForbiddenError(Exception):
    def __init__(self, message: str):
        super().__init__(message)
        
class UnauthorizedKeyError(Exception):
    def __init__(self,  message: Optional[str] = "Unauthorized: Missing API key."):
        super().__init__(message)
