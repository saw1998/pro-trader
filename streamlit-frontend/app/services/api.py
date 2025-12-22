from typing import Optional
import requests
import streamlit as st
from app.config import API_BASE_URL


class APIClient:
    def __init__(self):
        self.base_url = API_BASE_URL
    
    def _get_headers(self) -> dict:
        headers = {"Content-Type" : "application/json"}
        if "session_id" in st.session_state:
            headers["Authorization"] = f"Bearer {st.session_state.session_id}"
        return headers

    def _handle_response(self, response: requests.Response) -> dict:
        if response.status_code == 401:
            st.session_state.clear()
            st.error("Session expired, Please login again")
            st.rerun()
    
        if response.status_code >= 400:
            error = response.json().get("details", "An error occoured")
            raise Exception(error)

        return response.json()

    # Auth
    def register(self, email: str, username: str, password: str) -> dict:
        response = requests.post(
            f"{self.base_url}/auth/register",
            json={"email":email, "username":username, "password":password}
        )
        return self._handle_response(response)

    def login(self, email:str, password: str) -> dict:
        response = requests.post(
            f"{self.base_url}/auth/login",
            json={"email": email, "password":password}
        )
        return self._handle_response(response)
    
    def logout(self) -> None:
        try:
            requests.post(
                f"{self.base_url}/auth/logout",
                headers=self._get_headers()
            )
        except:
            pass
        st.session_state.clear()
    
    def get_me(self) -> dict:
        response = requests.get(
            f"{self.base_url}/auth/me",
            headers=self._get_headers()
        )
        return self._handle_response(response)

    # Position
    def get_position(self, status: Optional[str] = None) -> list:
        params = {"status": status} if status else {}
        response = requests.get(
            f"{self.base_url}/positions",
            headers=self._get_headers(),
            params=params
        )
        return self._handle_response(response)

    def open_position(self, symbol: str, quantity: float, entry_price: float, position_type: str) -> dict:
        response = requests.post(
            f"{self.base_url}/positions",
            headers=self._get_headers(),
            json={
                "symbol" : symbol,
                "quantity" : quantity,
                "entry_price" : entry_price,
                "position_type" : position_type
            }
        )
        return self._handle_response(response)

    def close_position(self, position_id: str, exit_price: Optional[float] = None) -> dict:
        data = {"exit_price": exit_price} if exit_price else {}
        response = requests.post(
            f"{self.base_url}/positions/{position_id}/close",
            headers=self._get_headers(),
            json=data
        )
        return self._handle_response(response)
    
    # Portfolio
    def get_portfolio(self) -> dict:
        response = requests.get(
            f"{self.base_url}/portfolio",
            headers=self._get_headers()
        )
        return self._handle_response(response)
    
    # Trades
    def get_trades(self, skip: int = 0, limit: int = 50) -> list:
        response = requests.get(
            f"{self.base_url}/trades",
            headers=self._get_headers(),
            params={"skip": skip, "limit": limit}
        )
        return self._handle_response(response)

api_client = APIClient()