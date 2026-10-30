import api from './api';

export const getAIGuide = async (requestData) => {
    try {
        const response = await api.post('/api/ai/guide', requestData);
        return response.data;
    } catch (error) {
        console.error('Error fetching AI guide:', error);
        throw error;
    }
};
