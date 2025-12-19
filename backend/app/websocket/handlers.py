

from fastapi import WebSocket, WebSocketDisconnect
import json

from app.websocket.manager import ws_manager
from app.db.redis import redis_client
from app.services.pnl_service import PnLService
from app.repositories.position_repository import PositionRepository
from app.db.database import db




async def websocket_endpoint(websocket: WebSocket, session_id: str):
    session_data = await redis_client.get_session(session_id)
    print("#######################")
    print(session_data)
    print("#######################")
    if not session_data:
        await websocket.close(code=4001, reason="Invalid session")
        return
    
    user_id = session_data["user_id"]
    
    connected = await ws_manager.connect(websocket, user_id)
    if not connected:
        return
    
    try:
        async with db.session_factory() as session:
            position_repo = PositionRepository(session)
            pnl_service = PnLService(position_repo, redis_client)
            
            symbols = await position_repo.get_user_symbols(user_id)
            if symbols:
                await ws_manager.subscribe(user_id, symbols)
            
            portfolio = await pnl_service.get_portfolio(user_id)
            await websocket.send_json({
                "type": "portfolio_snapshot",
                "data": portfolio.model_dump(mode="json")
            })
        
        while True:
            try:
                data = await websocket.receive_json()
                await handle_client_message(websocket, user_id, data)
            except json.JSONDecodeError:
                await websocket.send_json({"type": "error", "message": "Invalid JSON"})
    
    except WebSocketDisconnect:
        pass
    finally:
        await ws_manager.disconnect(websocket, user_id)


async def handle_client_message(websocket: WebSocket, user_id: str, data: dict):
    msg_type = data.get("type")
    
    if msg_type == "subscribe":
        symbols = data.get("symbols", [])
        await ws_manager.subscribe(user_id, symbols)
        await websocket.send_json({"type": "subscribed", "symbols": symbols})
    
    elif msg_type == "unsubscribe":
        symbols = data.get("symbols", [])
        await ws_manager.unsubscribe(user_id, symbols)
        await websocket.send_json({"type": "unsubscribed", "symbols": symbols})
    
    elif msg_type == "ping":
        await websocket.send_json({"type": "pong"})
    
    elif msg_type == "get_portfolio":
        async with db.session_factory() as session:
            position_repo = PositionRepository(session)
            pnl_service = PnLService(position_repo, redis_client)
            portfolio = await pnl_service.get_portfolio(user_id)
            await websocket.send_json({
                "type": "portfolio_snapshot",
                "data": portfolio.model_dump(mode="json")
            })
    
    else:
        await websocket.send_json({"type": "error", "message": f"Unknown type: {msg_type}"})