from typing import Dict

from fastapi import APIRouter

router = APIRouter()


@router.get("/", tags=["health"])
async def index() -> Dict[str, str]:
    return {
        "status": "success",
        "message": "hey there",
    }
