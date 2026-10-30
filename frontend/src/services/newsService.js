import api from './api';

export const newsService = {
  getNews: async (params = {}) => {
    try {
      const response = await api.get('/news', { params });
      return response.data;
    } catch (error) {
      console.error('Error fetching news:', error);
      throw error;
    }
  }
};
