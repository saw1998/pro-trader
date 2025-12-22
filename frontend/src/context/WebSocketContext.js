import { createContext, useCallback, useContext, useRef, useState } from "react";
import { getSessionId } from "../utils/helpers";
import { config } from "../config";
import { useEffect } from "react";

const WebSocketContext = createContext(null);

export function WebSocketProvider({children}){
    const ws = useRef<WebSocket | null>(null);
    const reconnectTimeout = useRef(null);
    const [isConnected, setIsConnected] = useState(false);
    const [prices, setPrices] = useState({});
    const [portfolio, setPortfolio] = useState(null);

    const connect = useCallback(() => {
        const sessionId = getSessionId();
        if(!sessionId) return;

        const wsUrl = `${config.wsUrl}/ws?session_id=${sessionId}`;
        ws.current  = new WebSocket(wsUrl);

        ws.current.onopen = () => {
            setIsConnected(true);
            console.log('Websocket connected');
        };

        ws.current.onmessage = (event) => {
            try{
                const message = JSON.parse(event.data);
/*
const key = "name";
const obj = { key: "Alice" };
console.log(obj); // { key: "Alice" } ❌
It will literally create a key called "key", not "name".

2️⃣ Computed property names
js
Copy code
const key = "name";
const obj = { [key]: "Alice" };
console.log(obj); // { name: "Alice" } ✅
By putting the variable inside [], JS evaluates it and uses its value as the key.
*/
                switch(message.type){
                    case 'price_update':
                        setPrices((prev) => ({
                            ...prev,
                            [message.data.symbol] : message.data
                        }));
                        break;
                    case 'pnl_update':
                    case 'portfolio_snapshot':
                        setPortfolio(message.data);
                        break;
                    case 'ping':
                        ws.current?.send(JSON.stringify({type : 'pong'}));
                        break;
                    default:
                        break;
                }
            } catch (e) {
                console.error('Websocket message error :',e)
            }
        };

        ws.current.onclose = () => {
            setIsConnected(false);
            console.log('Websocket disconnected');
            reconnectTimeout.current = setTimeout(connect, 3000);
        };

        ws.current.onerror = (error) => {
            console.log("Websocket error: ", error);
        }
    }, []);

    const disconnect = useCallback(() => {
        if(reconnectTimeout.current){
            clearTimeout(reconnectTimeout.current);
        }
        ws.current?.close();
    }, []);

    useEffect(() => {
        const sessionId = getSessionId();
        if(sessionId){
            connect();
        }
        return () => disconnect();
    }, [connect, disconnect]);

    const subscribe = useCallback((symbols) => {
        if(ws.current?.readyState === WebSocket.OPEN){
            ws.current.set(JSON.stringify({type : 'subscribe', symbols}))
        }
    }, []);

    const unsubscribe = useCallback((symbols) => {
        if(ws.current?.readyState === WebSocket.OPEN){
            ws.current.set(JSON.stringify({type : 'unsubscribe', symbols}))
        }
    }, []);

    return (
        <WebSocketContext.Provider
            value={{
                isConnected,
                prices,
                portfolio,
                subscribe,
                unsubscribe
            }}
        >
        </WebSocketContext.Provider>
    )
}

export function useWebSocket(){
    const context = useContext(WebSocketContext);
    if(!context){
        throw new Error('useWebSocket must be used within WebSocketProvider');
    }
    return context;
}
