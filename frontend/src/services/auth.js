import { setToken, api } from "./api";

export const authApi = {
  register: (data) => api.post('/register', data).then(r => r.data),

  login: ({ email, password }) => {
    const form = new URLSearchParams();
    form.append('username', email);  //TODO: this might fail
    form.append('password', password);
    return api.post('/login', form, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
    }).then(r => {
      setToken(r.data.access_token)
      return r.data;
    });
  },

  logout: () => api.post('/logout').finally(() => setToken(null)),

  getMe: () => api.get('/me').then(r => r.data),
};
