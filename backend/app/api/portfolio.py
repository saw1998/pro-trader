
from fastapi import APIRouter, Depends

from app.db.redis import RedisClient, get_redis
from app.dependencies import get_current_user_id, get_position_repo
from app.repositories.position_repository import PositionRepository
from app.schemas.position import PortfolioResponse
from app.services.pnl_service import PnLService


router = APIRouter(prefix="/portfolio", tags=['portfolio'])

async def get_pnl_service(
        position_repo : PositionRepository = Depends(get_position_repo),
        redis: RedisClient = Depends(get_redis)
) -> PnLService:
    return PnLService(position_repo, redis)

@router.get("/", response_model=PortfolioResponse)
async def get_portfolio(
    user_id = Depends(get_current_user_id),
    service: PnLService = Depends(get_pnl_service)
):
    return await service.get_portfolio(user_id)
    