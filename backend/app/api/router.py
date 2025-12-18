
from fastapi import APIRouter


router = APIRouter(prefix="/api/v1")

router.include_router(auth.router)
