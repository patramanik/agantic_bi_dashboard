import axios from 'axios';

const api = axios.create({
  baseURL: '/api'
});

// Automatically add Token to every request
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('bi_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Auth endpoints
export const loginUser = (username, password) => {
    const formData = new FormData();
    formData.append('username', username);
    formData.append('password', password);
    return api.post('/auth/login', formData);
};
export const registerUser = (userData) => api.post('/auth/register', userData);
export const getMe = () => api.get('/me');

// Data endpoints
export const uploadFile = (formData) => api.post('/upload', formData);
export const queryData = (query, fileId) => api.post('/query', null, { 
  params: { query, file_id: fileId } 
});
export const getSuggestions = (fileId) => api.get(`/suggestions/${fileId}`);

// Management endpoints
export const getDatasets = () => api.get('/datasets');
export const getHistory = (fileId) => api.get('/history', { params: { file_id: fileId } });
export const deleteDataset = (filename) => api.delete(`/datasets/${filename}`);

export default api;
