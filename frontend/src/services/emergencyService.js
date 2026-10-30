import api from './api';

const CACHE_KEYS = {
  EMERGENCY_NUMBERS: 'awakin_emergency_numbers',
  DEPARTMENTS: 'awakin_departments'
};

export const fetchEmergencyNumbers = async () => {
  try {
    const response = await api.get('/api/emergency-numbers/');
    localStorage.setItem(CACHE_KEYS.EMERGENCY_NUMBERS, JSON.stringify(response.data));
    return response.data;
  } catch (error) {
    const cached = localStorage.getItem(CACHE_KEYS.EMERGENCY_NUMBERS);
    if (cached) {
      console.warn('Network error or API unavailable. Using cached emergency numbers.');
      return JSON.parse(cached);
    }
    throw error;
  }
};

export const fetchDepartments = async () => {
  try {
    const response = await api.get('/api/departments/');
    localStorage.setItem(CACHE_KEYS.DEPARTMENTS, JSON.stringify(response.data));
    return response.data;
  } catch (error) {
    const cached = localStorage.getItem(CACHE_KEYS.DEPARTMENTS);
    if (cached) {
      console.warn('Network error or API unavailable. Using cached departments.');
      return JSON.parse(cached);
    }
    throw error;
  }
};
