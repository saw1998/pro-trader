import { createContext, useCallback, useContext, useState } from "react";
import { getSessionId, removeSessionId, setSessionId } from "../utils/helpers";
import { authApi } from "../api/endpoint";
import { useEffect } from "react";

const AuthContext = createContext(null);

export function AuthProvider({children}){
    const [user, setUser] = useState(null);
    const [isLoading, setIsLoading] = useState(true);

    const fetchUser = useCallback(async () => {
        const session_id = getSessionId();
        if(!session_id){
            setIsLoading(false);
            return;
        }

        try{
            const userData = await authApi.getMe();
            setUser(userData);
        } catch (error) {
            removeSessionId();
        } finally {
            setIsLoading(false);
        }
    }, []);

    useEffect(() => {
        fetchUser();
    }, [fetchUser]);

    const login = async (data) => {
        const response = await authApi.login(data);
        setSessionId(response.session_id);
        await fetchUser();
    };

    const register = async (data) => {
        await authApi.register(data);
    }

    const logout = async () => {
        try{
            await authApi.logout();
        } catch(error){
            // ignore
        }
        removeSessionId();
        setUser(null);
    };

    return(
        <AuthContext.Provider
            value={
                {
                    user,
                    isAuthenticated : !!user,
                    isLoading,
                    login,
                    register,
                    logout
                }
            }
        >
            {children}
        </AuthContext.Provider>
    );
}


export function useAuth(){
    const context = useContext(AuthContext);
    if(!context){
        throw new Error('useAuth must be used within authprovider');
    }
    return context;
}