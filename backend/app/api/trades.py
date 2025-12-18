
from fastapi import APIRouter, Depends

from app.dependencies import get_current_user_id, get_trade_repo
from app.repositories.trade_repository import TradeRepository
from app.schemas.trade import TradeResponse


router = APIRouter(prefix="/trades", tags=['trades'])

@router.get("/", response_model=list[TradeResponse])
async def get_trades(
    skip : int = 0,
    limit : int = 50,
    user_id = Depends(get_current_user_id),
    trade_repo: TradeRepository = Depends(get_trade_repo)
):
    return await trade_repo.get_user_trades(user_id, skip, limit)

