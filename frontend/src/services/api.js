import axios from "axios"

let token = null;

export const setToken = (t) => {
  token = t;
  if(t){
    sessionStorage.setItem('token', t);
  } else {
    sessionStorage.removeItem('token');
  }
}

export const getToken = () => token || sessionStorage.getItem('token');

export const api = axios.create({
  baseURL: "http://localhost:8000"
});

api.interceptors.request.use((config) => {
  const t = getToken();
  if(t) config.headers.Authorization = `Bearer ${t}`
  return config;
})
