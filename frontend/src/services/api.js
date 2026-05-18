import axios from 'axios';

const apiClient = axios.create({
  baseURL: 'http://localhost:8000/api',
});

export const WS_URL = 'ws://localhost:8000/ws/alerts';

export const getAlerts = async () => (await apiClient.get('/alerts/')).data;
export const getProcesses = async () => (await apiClient.get('/monitoring/processes')).data;
export const getSystemLogs = async () => (await apiClient.get('/monitoring/logs')).data;
export const getSystemStats = async () => (await apiClient.get('/monitoring/system-stats')).data;

// Fixed: Corrected path from '/monitoring/network/connections' to '/monitoring/connections'[cite: 16, 20]
export const getNetworkConnections = async () => (await apiClient.get('/monitoring/connections')).data;

export const createTestAlert = () => apiClient.post('/alerts/test');