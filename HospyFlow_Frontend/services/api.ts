import axios, { AxiosError } from 'axios';
import Constants from 'expo-constants';
import authService from './auth';
import type {
    // Auth types
    LoginRequest,
    LoginResponse,
    RegisterRequest,
    TokenRefreshResponse,
    ChangePasswordRequest,
    User,
    // Event types
    MicroEvent,
    CreateEventRequest,
    EventCategory,
    ResolveEventRequest,
    AddCommentRequest,
    EventStatistics,
    // Alert types
    Alert,
    AcknowledgeAlertRequest,
    ResolveAlertRequest,
    AlertRule,
    // Workflow types
    WorkflowType,
    WorkflowInstance,
    WorkflowStep,
    StartWorkflowRequest,
    AdvanceWorkflowRequest,
    // Analytics types
    Dashboard,
    Bottleneck,
    DepartmentMetrics,
    GlobalStatistics,
    Report,
    GenerateReportRequest,
    // Service types
    Service,
    ServiceSummary,
    Department,
    PaginatedResponse,
} from './types';

// Configuration dynamique de l'URL de l'API depuis .env
// Par défaut: http://localhost:8000/api
const API_BASE_URL = Constants.expoConfig?.extra?.apiUrl || process.env.EXPO_PUBLIC_API_URL || 'http://localhost:8000/api';

console.log('[API] Base URL configured:', API_BASE_URL);

export const apiClient = axios.create({
    baseURL: API_BASE_URL,
    timeout: 10000,
    headers: {
        'Content-Type': 'application/json',
    },
});

// Request interceptor - Add JWT token to requests
apiClient.interceptors.request.use(
    async (config) => {
        console.log(`[API Request] ${config.method?.toUpperCase()} ${config.url}`);

        // Add JWT token if available
        const token = await authService.getAccessToken();
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }

        return config;
    },
    (error) => {
        console.error('[API Request Error]:', error);
        return Promise.reject(error);
    }
);

// Response interceptor - Handle token refresh and errors
apiClient.interceptors.response.use(
    (response) => {
        console.log(`[API Response] ${response.status} from ${response.config.url}`);
        return response;
    },
    async (error: AxiosError) => {
        const originalRequest = error.config as any;

        // Handle 401 Unauthorized - Try to refresh token
        if (error.response?.status === 401 && !originalRequest._retry) {
            originalRequest._retry = true;

            try {
                const refreshToken = await authService.getRefreshToken();
                if (refreshToken) {
                    const response = await axios.post<TokenRefreshResponse>(
                        `${API_BASE_URL}/auth/refresh/`,
                        { refresh: refreshToken }
                    );

                    const { access } = response.data;
                    await authService.updateAccessToken(access);

                    // Retry original request with new token
                    originalRequest.headers.Authorization = `Bearer ${access}`;
                    return apiClient(originalRequest);
                }
            } catch (refreshError) {
                // Refresh failed - logout user
                console.error('[API] Token refresh failed:', refreshError);
                await authService.logout();
                // You might want to redirect to login screen here
            }
        }

        // Log error details
        if (error.response) {
            console.error(`[API Error] ${error.response.status}:`, error.response.data);
        } else if (error.request) {
            console.error('[API Error] No response received:', error.message);
        } else {
            console.error('[API Error]:', error.message);
        }

        return Promise.reject(error);
    }
);

// ============================================================================
// API Service
// ============================================================================

export const apiService = {
    // ==========================================================================
    // Authentication
    // ==========================================================================

    /**
     * Login user and store tokens
     */
    login: async (credentials: LoginRequest): Promise<LoginResponse> => {
        const response = await apiClient.post<LoginResponse>('/auth/login/', credentials);
        await authService.saveLoginData(response.data);
        return response.data;
    },

    /**
     * Register new user
     */
    register: async (userData: RegisterRequest): Promise<User> => {
        const response = await apiClient.post<User>('/auth/register/', userData);
        return response.data;
    },

    /**
     * Refresh JWT token
     */
    refreshToken: async (): Promise<string> => {
        const refreshToken = await authService.getRefreshToken();
        if (!refreshToken) {
            throw new Error('No refresh token available');
        }
        const response = await apiClient.post<TokenRefreshResponse>('/auth/refresh/', {
            refresh: refreshToken,
        });
        await authService.updateAccessToken(response.data.access);
        return response.data.access;
    },

    /**
     * Get current user profile
     */
    getUserProfile: async (): Promise<User> => {
        const response = await apiClient.get<User>('/auth/me/');
        await authService.saveUser(response.data);
        return response.data;
    },

    /**
     * Change user password
     */
    changePassword: async (passwordData: ChangePasswordRequest): Promise<void> => {
        await apiClient.post('/auth/me/change-password/', passwordData);
    },

    /**
     * Toggle duty status
     */
    toggleDutyStatus: async (): Promise<User> => {
        const response = await apiClient.post<User>('/auth/me/toggle-duty/');
        await authService.saveUser(response.data);
        return response.data;
    },

    /**
     * Logout user
     */
    logout: async (): Promise<void> => {
        await authService.logout();
    },

    // ==========================================================================
    // Departments
    // ==========================================================================

    /**
     * Get all departments
     */
    getDepartments: async (): Promise<Department[]> => {
        const response = await apiClient.get<Department[]>('/auth/departments/');
        return response.data;
    },

    /**
     * Get department by ID
     */
    getDepartment: async (id: number): Promise<Department> => {
        const response = await apiClient.get<Department>(`/auth/departments/${id}/`);
        return response.data;
    },

    /**
     * Get staff by department
     */
    getDepartmentStaff: async (departmentId: number): Promise<User[]> => {
        const response = await apiClient.get<User[]>(`/auth/departments/${departmentId}/staff/`);
        return response.data;
    },

    // ==========================================================================
    // Events (Micro-événements)
    // ==========================================================================

    /**
     * Get all events
     */
    getEvents: async (): Promise<MicroEvent[]> => {
        const response = await apiClient.get<MicroEvent[]>('/events/');
        return response.data;
    },

    /**
     * Get event by ID
     */
    getEvent: async (id: number): Promise<MicroEvent> => {
        const response = await apiClient.get<MicroEvent>(`/events/${id}/`);
        return response.data;
    },

    /**
     * Get my events
     */
    getMyEvents: async (): Promise<MicroEvent[]> => {
        const response = await apiClient.get<MicroEvent[]>('/events/mes-evenements/');
        return response.data;
    },

    /**
     * Get critical events
     */
    getCriticalEvents: async (): Promise<MicroEvent[]> => {
        const response = await apiClient.get<MicroEvent[]>('/events/critiques/');
        return response.data;
    },

    /**
     * Get recent events
     */
    getRecentEvents: async (): Promise<MicroEvent[]> => {
        const response = await apiClient.get<MicroEvent[]>('/events/recents/');
        return response.data;
    },

    /**
     * Create/report new event
     */
    createEvent: async (eventData: CreateEventRequest): Promise<MicroEvent> => {
        const response = await apiClient.post<MicroEvent>('/events/signaler/', eventData);
        return response.data;
    },

    /**
     * Take charge of an event
     */
    takeChargeOfEvent: async (id: number): Promise<MicroEvent> => {
        const response = await apiClient.post<MicroEvent>(`/events/${id}/prendre-en-charge/`);
        return response.data;
    },

    /**
     * Resolve an event
     */
    resolveEvent: async (id: number, data?: ResolveEventRequest): Promise<MicroEvent> => {
        const response = await apiClient.post<MicroEvent>(`/events/${id}/resoudre/`, data);
        return response.data;
    },

    /**
     * Add comment to event
     */
    addEventComment: async (id: number, comment: AddCommentRequest): Promise<void> => {
        await apiClient.post(`/events/${id}/commenter/`, comment);
    },

    /**
     * Mark event as recurrent
     */
    markEventRecurrent: async (id: number): Promise<MicroEvent> => {
        const response = await apiClient.post<MicroEvent>(`/events/${id}/marquer-recurrent/`);
        return response.data;
    },

    /**
     * Get event categories
     */
    getEventCategories: async (): Promise<EventCategory[]> => {
        const response = await apiClient.get<EventCategory[]>('/events/categories/');
        return response.data;
    },

    /**
     * Get event statistics
     */
    getEventStatistics: async (): Promise<EventStatistics> => {
        const response = await apiClient.get<EventStatistics>('/events/statistiques/');
        return response.data;
    },

    /**
     * Get event trends
     */
    getEventTrends: async (): Promise<any> => {
        const response = await apiClient.get('/events/tendances/');
        return response.data;
    },

    // ==========================================================================
    // Alerts
    // ==========================================================================

    /**
     * Get all alerts
     */
    getAlerts: async (): Promise<Alert[]> => {
        const response = await apiClient.get<Alert[]>('/alerts/');
        return response.data;
    },

    /**
     * Get alert by ID
     */
    getAlert: async (id: number): Promise<Alert> => {
        const response = await apiClient.get<Alert>(`/alerts/${id}/`);
        return response.data;
    },

    /**
     * Get my alerts
     */
    getMyAlerts: async (): Promise<Alert[]> => {
        const response = await apiClient.get<Alert[]>('/alerts/mes-alertes/');
        return response.data;
    },

    /**
     * Get active alerts (alias for getAlerts with active filter)
     */
    getActiveAlerts: async (): Promise<Alert[]> => {
        const response = await apiClient.get<Alert[]>('/alerts/', {
            params: { statut: 'ACTIVE' }
        });
        return response.data;
    },

    /**
     * Acknowledge an alert
     */
    acknowledgeAlert: async (id: number, data?: AcknowledgeAlertRequest): Promise<Alert> => {
        const response = await apiClient.post<Alert>(`/alerts/${id}/acquitter/`, data);
        return response.data;
    },

    /**
     * Resolve an alert
     */
    resolveAlert: async (id: number, data?: ResolveAlertRequest): Promise<Alert> => {
        const response = await apiClient.post<Alert>(`/alerts/${id}/resoudre/`, data);
        return response.data;
    },

    /**
     * Ignore an alert
     */
    ignoreAlert: async (id: number): Promise<Alert> => {
        const response = await apiClient.post<Alert>(`/alerts/${id}/ignorer/`);
        return response.data;
    },

    /**
     * Get alert rules
     */
    getAlertRules: async (): Promise<AlertRule[]> => {
        const response = await apiClient.get<AlertRule[]>('/alerts/regles/');
        return response.data;
    },

    /**
     * Evaluate alert rules
     */
    evaluateAlertRules: async (): Promise<any> => {
        const response = await apiClient.post('/alerts/regles/evaluer/');
        return response.data;
    },

    // ==========================================================================
    // Workflows
    // ==========================================================================

    /**
     * Get workflow types
     */
    getWorkflowTypes: async (): Promise<WorkflowType[]> => {
        const response = await apiClient.get<WorkflowType[]>('/workflows/types/');
        return response.data;
    },

    /**
     * Get workflow type by ID
     */
    getWorkflowType: async (id: number): Promise<WorkflowType> => {
        const response = await apiClient.get<WorkflowType>(`/workflows/types/${id}/`);
        return response.data;
    },

    /**
     * Get workflow steps for a type
     */
    getWorkflowSteps: async (typeId: number): Promise<WorkflowStep[]> => {
        const response = await apiClient.get<WorkflowStep[]>(`/workflows/types/${typeId}/etapes/`);
        return response.data;
    },

    /**
     * Get workflow instances
     */
    getWorkflowInstances: async (): Promise<WorkflowInstance[]> => {
        const response = await apiClient.get<WorkflowInstance[]>('/workflows/instances/');
        return response.data;
    },

    /**
     * Get workflow instance by ID
     */
    getWorkflowInstance: async (id: number): Promise<WorkflowInstance> => {
        const response = await apiClient.get<WorkflowInstance>(`/workflows/instances/${id}/`);
        return response.data;
    },

    /**
     * Get workflow progression
     */
    getWorkflowProgression: async (id: number): Promise<any> => {
        const response = await apiClient.get(`/workflows/instances/${id}/progression/`);
        return response.data;
    },

    /**
     * Start a new workflow
     */
    startWorkflow: async (data: StartWorkflowRequest): Promise<WorkflowInstance> => {
        const response = await apiClient.post<WorkflowInstance>('/workflows/demarrer/', data);
        return response.data;
    },

    /**
     * Advance workflow to next step
     */
    advanceWorkflow: async (id: number, data?: AdvanceWorkflowRequest): Promise<WorkflowInstance> => {
        const response = await apiClient.post<WorkflowInstance>(`/workflows/instances/${id}/avancer/`, data);
        return response.data;
    },

    /**
     * Abandon a workflow
     */
    abandonWorkflow: async (id: number): Promise<WorkflowInstance> => {
        const response = await apiClient.post<WorkflowInstance>(`/workflows/instances/${id}/abandonner/`);
        return response.data;
    },

    /**
     * Pause or resume a workflow
     */
    pauseResumeWorkflow: async (id: number, action: 'pause' | 'resume'): Promise<WorkflowInstance> => {
        const response = await apiClient.post<WorkflowInstance>(`/workflows/instances/${id}/${action}/`);
        return response.data;
    },

    /**
     * Get delayed workflows
     */
    getDelayedWorkflows: async (): Promise<WorkflowInstance[]> => {
        const response = await apiClient.get<WorkflowInstance[]>('/workflows/en-retard/');
        return response.data;
    },

    // ==========================================================================
    // Analytics
    // ==========================================================================

    /**
     * Get main dashboard data
     */
    getDashboard: async (): Promise<Dashboard> => {
        const response = await apiClient.get<Dashboard>('/analytics/tableau-de-bord/');
        return response.data;
    },

    /**
     * Get bottlenecks
     */
    getBottlenecks: async (): Promise<Bottleneck[]> => {
        const response = await apiClient.get<Bottleneck[]>('/analytics/goulots/');
        return response.data;
    },

    /**
     * Get bottleneck by ID
     */
    getBottleneck: async (id: number): Promise<Bottleneck> => {
        const response = await apiClient.get<Bottleneck>(`/analytics/goulots/${id}/`);
        return response.data;
    },

    /**
     * Detect bottlenecks
     */
    detectBottlenecks: async (): Promise<Bottleneck[]> => {
        const response = await apiClient.post<Bottleneck[]>('/analytics/goulots/detecter/');
        return response.data;
    },

    /**
     * Confirm a bottleneck
     */
    confirmBottleneck: async (id: number): Promise<Bottleneck> => {
        const response = await apiClient.post<Bottleneck>(`/analytics/goulots/${id}/confirmer/`);
        return response.data;
    },

    /**
     * Resolve a bottleneck
     */
    resolveBottleneck: async (id: number): Promise<Bottleneck> => {
        const response = await apiClient.post<Bottleneck>(`/analytics/goulots/${id}/resoudre/`);
        return response.data;
    },

    /**
     * Mark bottleneck as false positive
     */
    markBottleneckFalsePositive: async (id: number): Promise<Bottleneck> => {
        const response = await apiClient.post<Bottleneck>(`/analytics/goulots/${id}/faux-positif/`);
        return response.data;
    },

    /**
     * Get department metrics
     */
    getDepartmentMetrics: async (): Promise<DepartmentMetrics[]> => {
        const response = await apiClient.get<DepartmentMetrics[]>('/analytics/metriques/');
        return response.data;
    },

    /**
     * Get metrics for specific department
     */
    getMetricsForDepartment: async (departmentId: number): Promise<DepartmentMetrics> => {
        const response = await apiClient.get<DepartmentMetrics>(`/analytics/metriques/departement/${departmentId}/`);
        return response.data;
    },

    /**
     * Get global statistics
     */
    getStatistics: async (): Promise<GlobalStatistics> => {
        const response = await apiClient.get<GlobalStatistics>('/analytics/statistiques/');
        return response.data;
    },

    /**
     * Generate statistics
     */
    generateStatistics: async (): Promise<GlobalStatistics> => {
        const response = await apiClient.post<GlobalStatistics>('/analytics/statistiques/generer/');
        return response.data;
    },

    /**
     * Get reports
     */
    getReports: async (): Promise<Report[]> => {
        const response = await apiClient.get<Report[]>('/analytics/rapports/');
        return response.data;
    },

    /**
     * Generate a new report
     */
    generateReport: async (reportData: GenerateReportRequest): Promise<Report> => {
        const response = await apiClient.post<Report>('/analytics/rapports/', reportData);
        return response.data;
    },

    // ==========================================================================
    // Services
    // ==========================================================================

    /**
     * Get all services
     */
    getServices: async (): Promise<Service[]> => {
        const response = await apiClient.get<Service[]>('/services/');
        return response.data;
    },

    /**
     * Get service by ID
     */
    getService: async (id: number): Promise<Service> => {
        const response = await apiClient.get<Service>(`/services/${id}/`);
        return response.data;
    },

    /**
     * Get services summary
     */
    getServicesSummary: async (): Promise<ServiceSummary> => {
        const response = await apiClient.get<ServiceSummary>('/services/summary/');
        return response.data;
    },

    // ==========================================================================
    // Legacy aliases (for backward compatibility)
    // ==========================================================================

    /**
     * @deprecated Use getServicesSummary instead
     */
    getSummary: async (): Promise<ServiceSummary> => {
        return apiService.getServicesSummary();
    },

    /**
     * @deprecated Use createEvent instead
     */
    createSignal: async (signalData: CreateEventRequest): Promise<MicroEvent> => {
        return apiService.createEvent(signalData);
    },

    /**
     * @deprecated Use getReports instead
     */
    getRapports: async (): Promise<Report[]> => {
        return apiService.getReports();
    },

    /**
     * @deprecated Use generateReport instead
     */
    generateRapport: async (reportData: GenerateReportRequest): Promise<Report> => {
        return apiService.generateReport(reportData);
    },
};

export default apiService;
