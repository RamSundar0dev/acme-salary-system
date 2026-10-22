from typing import Any, Dict, Optional
from sqlalchemy.orm import Session
from app.models.audit_log import AuditLog
from app.models.user import User


class AuditService:
    @staticmethod
    def log_action(
        db: Session,
        actor: Optional[User],
        action: str,
        entity_type: str,
        entity_id: int,
        change_data: Dict[str, Any],
        ip_address: Optional[str] = None,
    ) -> AuditLog:
        audit_entry = AuditLog(
            actor_id=actor.id if actor else None,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            change_data=change_data,
            ip_address=ip_address,
        )
        db.add(audit_entry)
        # We don't commit here - it participates in caller's transaction
        return audit_entry
