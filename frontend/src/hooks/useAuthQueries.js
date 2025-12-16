import { useQuery, useQueryClient, useMutation } from "@tanstack/react-query"
import { authApi } from "../services/auth"
import { getToken } from "../services/api";

export const useUser = () => useQuery({
  queryKey: ['user'],
  queryFn: authApi.getMe,
  enabled: !!getToken(),
  retry: false,
});

export const useLogin = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: authApi.login,
    onSuccess: () => qc.invalidateQueries({ queryKey: ['user'] }),
  });
};

export const useRegister = () => useMutation({
  mutationFn: authApi.register
});

export const useLogout = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: authApi.logout,
    onSettled: () => qc.clear(),
  });
};
