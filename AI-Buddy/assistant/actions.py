from dataclasses import dataclass, field
from typing import Optional, Dict, Any

@dataclass
class ActionResult:
    """Structured result returned by all assistant actions."""
    success: bool
    message: str
    detail: Optional[str] = None
    data: Dict[str, Any] = field(default_factory=dict)
