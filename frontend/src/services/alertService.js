import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

// Create a basic axios instance without auth headers for alerts since they are public
const alertApi = axios.create({
  baseURL: API_URL,
});

export const alertService = {
  getAlerts: async (params = {}) => {
    try {
      const response = await alertApi.get('/alerts', { params });
      return response.data;
    } catch (error) {
      console.error('Error fetching alerts:', error);
      throw error;
    }
  },

  getNearbyAlerts: async (lat, lon) => {
    try {
      const response = await alertApi.get('/alerts/nearby', {
        params: { lat, lon }
      });
      return response.data;
    } catch (error) {
      console.error('Error fetching nearby alerts:', error);
      throw error;
    }
  },
  
  explainAlert: async (alertData, token) => {
    try {
      // Explain alert requires auth based on the dependency in ai.py
      const response = await axios.post(`${API_URL}/ai/explain-alert`, alertData, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      return response.data;
    } catch (error) {
      console.error('Error explaining alert:', error);
      throw error;
    }
  }
};
