import { QueryClient, useMutation, useQuery } from "@tanstack/react-query"
import { positionsApi } from "../api/endpoint"

export function usePositions(status){
    return useQuery({
        queryKey : ['position', status],
        queryFn : () => positionsApi.getAll(status),
        staleTime:10000,
    });
}

export function useOpenPosition() {
    const queryClient = QueryClient();

    return useMutation({
        mutationFn : (data) => positionsApi.open(data),
        onSuccess: () => {
            queryClient.invalidateQueries({queryKey : ['positions']});
            queryClient.invalidateQueries({queryKey: ['portfolio']});
        }
    });
}

export function useClosePosition() {
    const queryClient = QueryClient();

    return useMutation({
        onMutate : ({id, data}) => positionsApi.close(id, data),
        onSuccess: () => {
            queryClient.invalidateQueries({queryKey : ['positions']});
            queryClient.invalidateQueries({queryKey: ['portfolio']});
            queryClient.invalidateQueries({queryKey: ['trades']});
        } 
    });
}
