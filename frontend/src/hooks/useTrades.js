import { useQuery } from "@tanstack/react-query";
import { tradesApi } from "../api/endpoint";

export function useTrades(skip = 0, limit = 50){
    return useQuery({
        queryKey:['trades', skip, limit],
        queryFn: () => tradesApi.getAll(skip, limit),
        staleTime: 30000
    });
}

