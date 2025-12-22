import axios from "axios";
import { config } from "../config";
import { getSessionId, removeSessionId } from "../utils/helpers";

const api = axios.create({
    baseURL: config.apiUrl,
    headers:{
        'Content-Type' : "application/json"
    }
});

api.interceptors.request.use(
    (requestConfig) => {
        const sessionId = getSessionId();
        if (sessionId){
            requestConfig.headers.Authorization = `Bearer ${sessionId}`
        }
        return requestConfig
    },
    (error) => Promise.reject(error)
);

api.interceptors.response.use(
    (responseConfig) => responseConfig,
    (error) => {
        if (error.response?.status == 401){
            removeSessionId();
            window.location.href = "/login"
        }
        return Promise.reject(error)
    }
);

export default api;