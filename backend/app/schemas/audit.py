from datetime import datetime
from typing import Any, Dict, Optional
from pydantic import BaseModel


class AuditLogResponse(BaseModel):
    id: int
    actor_id: Optional[int] = None
    actor_email: Optional[str] = None
    action: str
    entity_type: str
    entity_id: int
    change_data: Dict[str, Any]
    ip_address: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
