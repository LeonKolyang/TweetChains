from fastapi import APIRouter, Depends

from app.core.di import get_service
from app.service.service import Service
from app.routes.models import ApiResponse

router = APIRouter()


@router.get("/", tags=["api"])
async def service(service: Service = Depends(get_service)) -> ApiResponse:
    return ApiResponse()
