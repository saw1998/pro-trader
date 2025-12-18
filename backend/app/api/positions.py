
from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, status

from app.db.redis import RedisClient, get_redis
from app.dependencies import get_current_user_id, get_position_repo, get_trade_repo
from app.models.positions import PositionStatus
from app.repositories.position_repository import PositionRepository
from app.repositories.trade_repository import TradeRepository
from app.schemas.position import PositionClose, PositionCreate, PositionResponse
from app.services.position_service import PositionService


router = APIRouter(prefix="/positions", tags=["positions"])

async def get_position_service(
        position_repo : PositionRepository = Depends(get_position_repo),
        trade_repo : TradeRepository = Depends(get_trade_repo),
        redis : RedisClient = Depends(get_redis)
):
    return PositionService(position_repo, trade_repo, redis)

@router.get("/", response_model=list[PositionResponse])
async def get_positions(
    status: Optional[str] = None,
    user_id = Depends(get_current_user_id),
    service: PositionService = Depends(get_position_service)
):
    pos_status = PositionStatus(status) if status else None
    return await service.get_positions(user_id, pos_status)

@router.get("/{position_id}", response_model=PositionResponse)
async def get_position(
    position_id: UUID,
    user_id = Depends(get_current_user_id),
    service: PositionService = Depends(get_position_service)
):
    return await service.get_position(user_id, position_id)

@router.post("/", response_model=PositionResponse, status_code=status.HTTP_201_CREATED)
async def open_position(
    data: PositionCreate,
    user_id = Depends(get_current_user_id),
    service : PositionService = Depends(get_position_service)
):
    return await service.open_position(user_id, data)

@router.post("/{position_id}/close", response_model=PositionResponse)
async def close_position(
    position_id : UUID,
    data : PositionClose,
    user_id = Depends(get_current_user_id),
    service: PositionService = Depends(get_position_service)
):
    return await service.close_position(user_id, position_id, data.exit_price)

