import api from "./axios";

export const authApi = {
    login : async (data) => {
        const response = await api.post('/auth/login', data);
        return response.data;
    },

    logout : async () => {
        const response = await api.post('/auth/logout');
    },

    register : async (data) => {
        const response = await api.post('/auth/register', data);
        return response.data;
    },

    getMe : async () => {
        const response = await api.post('/auth/getMe');
        return response.data;
    },
};

export const positionsApi = {
    getAll : async (status) => {
        const params = status ? {status} : {}
        const response = await api.get('/positions', {params});
        return response.data;
    },

    getById : async (id) => {
        const response = await api.get(`/position/${id}`);
        return response.data;
    },

    open : async (data) => {
        const response = await api.post(`/positions` , data);
        return response.data;
    },

    close : async (id, data) => {
        const response = await api.post(`/position/${id}/close`,  data || {});
        return response.data;
    },
};

export const portfolioApi = {
  get: async () => {
    const response = await api.get('/portfolio');
    return response.data;
  }
};

export const tradesApi = {
  getAll: async (skip = 0, limit = 50) => {
    const response = await api.get('/trades', { params: { skip, limit } });
    return response.data;
  }
};