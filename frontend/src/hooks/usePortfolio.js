import { useQueryClient, useQuery } from "@tanstack/react-query";
import { useWebSocket } from "../context/WebSocketContext";
import { portfolioApi } from "../api/endpoint";
import { useEffect } from "react";

export function usePortfolio(){
    const queryClient = useQueryClient();
    const {portfolio : wsPortfolio} = useWebSocket();
    
    const query = useQuery({
        queryKey : ['portfolio'],
        queryFn : portfolioApi.get,
        staleTime: 5000,
        refetchInterval: 30000
    });

    useEffect(() => {
        if(wsPortfolio){
            queryClient.setQueriesData(['portfolio'], wsPortfolio);
        }
    }, [wsPortfolio, queryClient]);

    return{
        portfolio: wsPortfolio || query.data,
        isLoading : query.isLoading,
        error : query.error,
        refresh :query.refetch
    };
}