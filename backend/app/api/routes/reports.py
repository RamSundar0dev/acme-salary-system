from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.api.deps import get_current_hr_manager, get_db
from app.models.user import User
from app.services.export_service import ExportService

router = APIRouter(prefix="/reports", tags=["Reports & Export"])


@router.get("/employees.csv")
def export_employees_csv(
    country_code: Optional[str] = Query(None),
    department_id: Optional[int] = Query(None),
    employment_status: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_hr_manager),
):
    csv_generator = ExportService.stream_employees_csv(
        db=db,
        country_code=country_code,
        department_id=department_id,
        employment_status=employment_status,
        search=search,
    )

    filename = f"acme_employees_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv"
    return StreamingResponse(
        csv_generator,
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
