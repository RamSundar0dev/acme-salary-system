from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_hr_manager, get_db
from app.models.user import User
from app.schemas.analytics import DashboardSummaryResponse, DistributionResponse
from app.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/analytics", tags=["Analytics & Insights"])


@router.get("/summary", response_model=DashboardSummaryResponse)
def get_analytics_summary(
    country_code: Optional[str] = Query(None, description="Filter by Country Code"),
    department_id: Optional[int] = Query(None, description="Filter by Department ID"),
    currency: Optional[str] = Query(None, description="Filter by Currency"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_hr_manager),
):
    return AnalyticsService.get_dashboard_summary(
        db=db,
        country_code=country_code,
        department_id=department_id,
        currency=currency,
    )


@router.get("/distribution", response_model=DistributionResponse)
def get_compensation_distribution(
    currency: Optional[str] = Query(None, description="Filter by Currency"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_hr_manager),
):
    return AnalyticsService.get_compensation_distribution(
        db=db,
        currency_filter=currency,
    )
