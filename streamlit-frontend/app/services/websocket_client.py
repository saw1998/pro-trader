import streamlit as st
import json
import threading
from typing import Callable, Optional

import websocket

from app.config import WS_BASE_URL


class WebSocketClient:
    def __init__(self):
        self.ws: Optional[websocket.WebSocketApp] = None
        self.thread: Optional[threading.Thread] = None
        self.connected = False
        self.callbacks : dict[str, list[Callable]] = {
            "price_update" : [],
            "pnl_update" : [],
            "portfolio_snapshop" : []
        }

    def connect(self, session_id: str):
        if self.connected:
            return

        url = f"{WS_BASE_URL}/ws?session_id={session_id}" 

        self.ws = websocket.WebSocketApp(
            url,
            on_open=self._on_open,
            on_message=self._on_message,
            on_error=self._on_error,
            on_close=self._on_close
        )

        self.thread = threading.Thread(target=self.ws.run_forever, daemon=True)
        self.thread.start()
    
    def disconnect(self):
        if self.ws:
            self.ws.close()
        self.connected = False

    def subscribe(self, symbols: list[str]):
        if self.ws and self.connected:
            self.ws.send(json.dumps({"type":"subscribe", "symbols": symbols}))

    def unsubscribe(self, symbols: list[str]):
        if self.ws and self.connected:
            self.ws.send(json.dumps({"type":"unsubscribe", "symbols":symbols}))
    
    def on(self, event: str, callback:Callable):
        if event in self.callbacks:
            self.callbacks[event].append(callback)

    def _on_open(self, ws):
        self.connected = True

    def _on_message(self, ws, message):
        try:
            data = json.loads(message)
            msg_type = data.get("type")

            if msg_type in self.callbacks:
                for callback in self.callbacks[msg_type]:
                    callback(data.get("data"))
            
            # store in session state for Streamlit access
            if msg_type == "price_update":
                if "prices" not in st.session_state:
                    st.session_state.prices = {}
                price_data = data.get("data", {})
                st.session_state.prices[price_data.get("symbol")] = price_data

            elif msg_type == "pnl_update" or msg_type == "portfolio_snapshot":
                st.session_state.portfolio = data.get("data")

        except Exception as e:
            print(f"Websocket message error: {e}")
    
    def _on_error(self, ws, error):
        print(f"Websocket error : {error}")

    def _on_close(self, ws, close_status_code, close_msg):
        self.connected = False


ws_client = WebSocketClient()