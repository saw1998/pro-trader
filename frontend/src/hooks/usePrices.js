import { useEffect } from "react";
import { useWebSocket } from "../context/WebSocketContext";
import { config } from "../config";

export function usePrices(symbols){
    const {prices, subscribe, unsubscribe, isConnected} = useWebSocket();

    useEffect(() => {
        const symbosToSubscribe = symbols || config.defaultSymbols;
        if(isConnected){
            subscribe(symbosToSubscribe);
        }

        return () => {
            if(isConnected){
                unsubscribe(symbosToSubscribe);
            }
        };
    }, [symbols, isConnected, subscribe, unsubscribe]);

    return {prices, isConnected};
}