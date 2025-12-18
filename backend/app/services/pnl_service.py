
from datetime import datetime
from decimal import Decimal
from uuid import UUID
from zoneinfo import ZoneInfo
from app.db.redis import RedisClient
from app.repositories.position_repository import PositionRepository
from app.schemas.position import PortfolioResponse, PositionPnL


class PnLService:
    def __init__(self, position_repo: PositionRepository, redis: RedisClient):
        self.position_repo = position_repo
        self.redis = redis

    async def get_portfolio(self, user_id: UUID) -> PortfolioResponse:
        cached = await self.redis.get_user_pnl(str(user_id))
        if cached:
            return PortfolioResponse(**cached)

        positions = await self.position_repo.get_user_open_positions(user_id)

        if not positions:
            return PortfolioResponse(
                positions=[],
                total_invested=Decimal("0"),
                total_current_value=Decimal("0"),
                total_unrealized_pnl=Decimal("0"),
                total_pnl_percentage=Decimal("0"),
                timestamp=datetime.now(tz=ZoneInfo("UTC"))
            )
        symbols = list(set(p.symbol for p in positions))
        prices = await self.redis.get_prices_bulk(symbols=symbols)

        position_pnls = []
        total_invested = Decimal("0")
        total_current_value = Decimal("0")

        for position in positions:
            current_price = prices.get(position.symbol)
            if current_price is None:
                current_price = float(position.entry_price)
            
            qty = Decimal(str(position.quantity))
            entry = Decimal(str(position.entry_price))
            current = Decimal(str(current_price))

            invested = qty * entry
            current_val = qty * current
            unrealized_pnl = position.calculate_unrealized_pnl(current_price)
            pnl_pct = (Decimal(str(unrealized_pnl))/invested)*100 if invested else Decimal("0")

            position_pnls.append(PositionPnL(
                id=position.id,
                symbol=position.symbol,
                quantity=qty,
                entry_price=entry,
                current_price=current,
                position_type=position.position_type.value,
                unrealized_pnl=Decimal(str(round(unrealized_pnl, 4))),
                pnl_percentage=round(pnl_pct, 2)
            ))

            total_invested += invested
            total_current_value += current_val
        
        total_unrealized_pnl = total_current_value - total_invested
        total_pnl_pct = (total_unrealized_pnl/ total_invested) * 100 if total_invested else Decimal("0")

        portfolio = PortfolioResponse(
            positions=position_pnls,
            total_invested=round(total_invested, 4),
            total_current_value=round(total_current_value, 4),
            total_unrealized_pnl=round(total_unrealized_pnl, 4),
            total_pnl_percentage=round(total_pnl_pct, 2),
            timestamp=datetime.now(tz=ZoneInfo("UTC"))
        )

        await self.redis.cache_user_pnl(str(user_id), portfolio.model_dump())

        return portfolio

    async def calculate_portfolio_for_users(self, user_ids: set[str]) -> dict[str, PortfolioResponse]:
        results = {}
        for user_id in user_ids:
            await self.redis.invalidate_user_pnl(user_id)
            results[user_id] = await self.get_portfolio(UUID(user_id))
        return results
        
        
