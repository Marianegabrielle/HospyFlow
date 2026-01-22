import axios from 'axios';

// Change this to your local network IP if testing on a real device
// On Android Emulator, 10.0.2.2 is the host machine
const API_BASE_URL = 'http://localhost:8000/api';

export const apiClient = axios.create({
    baseURL: API_BASE_URL,
    timeout: 10000,
    headers: {
        'Content-Type': 'application/json',
    },
});

export const apiService = {
    // Services
    getServices: async () => {
        const response = await apiClient.get('/services/');
        return response.data;
    },

    getSummary: async () => {
        const response = await apiClient.get('/services/summary/');
        return response.data;
    },

    // Micro-événements (Signals)
    createSignal: async (signalData: {
        personnel: number;
        service: number;
        type_flux: number;
        description: string;
        niveau_gravite: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
    }) => {
        try {
            const response = await apiClient.post('/evenements/', signalData);
            return response.data;
        } catch (error) {
            console.error("API Error creating signal:", error);
            throw error;
        }
    },

    // Alertes
    getActiveAlerts: async () => {
        const response = await apiClient.get('/alertes/');
        return response.data;
    },

    // Rapports
    getRapports: async () => {
        const response = await apiClient.get('/rapports/');
        return response.data;
    },

    generateRapport: async (reportData: {
        plage_date: string;
        donnees_metriques: any;
        format: 'pdf' | 'csv';
    }) => {
        const response = await apiClient.post('/rapports/', reportData);
        return response.data;
    },
};

export default apiService;
