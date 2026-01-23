/**
 * TypeScript type definitions for HospyFlow API
 */

// ============================================================================
// Authentication & User Types
// ============================================================================

export interface User {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  role: 'NURSE' | 'DOCTOR' | 'LAB_TECH' | 'ADMIN';
  department: number | null;
  is_on_duty: boolean;
  phone_number?: string;
  created_at: string;
  updated_at: string;
}

export interface LoginRequest {
  username: string;
  password: string;
}

export interface LoginResponse {
  access: string;
  refresh: string;
  user: User;
}

export interface RegisterRequest {
  username: string;
  email: string;
  password: string;
  first_name: string;
  last_name: string;
  role: 'NURSE' | 'DOCTOR' | 'LAB_TECH' | 'ADMIN';
  department?: number;
  phone_number?: string;
}

export interface TokenRefreshRequest {
  refresh: string;
}

export interface TokenRefreshResponse {
  access: string;
}

export interface ChangePasswordRequest {
  old_password: string;
  new_password: string;
}

// ============================================================================
// Department Types
// ============================================================================

export interface Department {
  id: number;
  nom: string;
  description?: string;
  capacite_lits?: number;
  nombre_personnel?: number;
  created_at: string;
  updated_at: string;
}

// ============================================================================
// Event Types
// ============================================================================

export type EventSeverity = 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
export type EventStatus = 'PENDING' | 'IN_PROGRESS' | 'RESOLVED' | 'CLOSED';

export interface EventCategory {
  id: number;
  nom: string;
  description?: string;
  couleur?: string;
}

export interface MicroEvent {
  id: number;
  personnel: number;
  personnel_details?: User;
  service: number;
  service_details?: Department;
  type_flux: number;
  categorie?: EventCategory;
  description: string;
  niveau_gravite: EventSeverity;
  statut: EventStatus;
  date_signalement: string;
  date_resolution?: string;
  resolu_par?: number;
  resolu_par_details?: User;
  temps_resolution_minutes?: number;
  est_recurrent: boolean;
  nombre_occurrences: number;
  created_at: string;
  updated_at: string;
}

export interface CreateEventRequest {
  personnel: number;
  service: number;
  type_flux: number;
  description: string;
  niveau_gravite: EventSeverity;
}

export interface ResolveEventRequest {
  resolution_notes?: string;
}

export interface AddCommentRequest {
  commentaire: string;
}

export interface EventStatistics {
  total_events: number;
  by_severity: Record<EventSeverity, number>;
  by_status: Record<EventStatus, number>;
  average_resolution_time: number;
  recurrent_events: number;
}

// ============================================================================
// Alert Types
// ============================================================================

export type AlertSeverity = 'INFO' | 'WARNING' | 'CRITICAL';
export type AlertStatus = 'ACTIVE' | 'ACKNOWLEDGED' | 'RESOLVED' | 'IGNORED';

export interface Alert {
  id: number;
  titre: string;
  message: string;
  severite: AlertSeverity;
  statut: AlertStatus;
  type_alerte: string;
  departement?: number;
  departement_details?: Department;
  personnel_cible?: number;
  personnel_cible_details?: User;
  evenement_lie?: number;
  goulot_lie?: number;
  date_creation: string;
  date_acquittement?: string;
  acquitte_par?: number;
  acquitte_par_details?: User;
  date_resolution?: string;
  resolu_par?: number;
  resolu_par_details?: User;
  created_at: string;
  updated_at: string;
}

export interface AcknowledgeAlertRequest {
  notes?: string;
}

export interface ResolveAlertRequest {
  resolution_notes?: string;
}

export interface AlertRule {
  id: number;
  nom: string;
  description?: string;
  condition: string;
  severite: AlertSeverity;
  est_active: boolean;
  created_at: string;
  updated_at: string;
}

// ============================================================================
// Workflow Types
// ============================================================================

export type WorkflowStatus = 'NOT_STARTED' | 'IN_PROGRESS' | 'PAUSED' | 'COMPLETED' | 'ABANDONED';

export interface WorkflowType {
  id: number;
  nom: string;
  description?: string;
  duree_estimee_minutes: number;
  est_actif: boolean;
  created_at: string;
  updated_at: string;
}

export interface WorkflowStep {
  id: number;
  type_workflow: number;
  nom: string;
  description?: string;
  ordre: number;
  duree_estimee_minutes: number;
  departement_responsable?: number;
  est_obligatoire: boolean;
  created_at: string;
  updated_at: string;
}

export interface WorkflowInstance {
  id: number;
  type_workflow: number;
  type_workflow_details?: WorkflowType;
  patient_id?: string;
  statut: WorkflowStatus;
  date_debut: string;
  date_fin?: string;
  duree_totale_minutes?: number;
  etape_courante?: number;
  etape_courante_details?: WorkflowStep;
  progression_pourcent: number;
  est_en_retard: boolean;
  created_at: string;
  updated_at: string;
}

export interface StartWorkflowRequest {
  type_workflow: number;
  patient_id?: string;
}

export interface AdvanceWorkflowRequest {
  notes?: string;
}

// ============================================================================
// Analytics Types
// ============================================================================

export interface Dashboard {
  total_events_today: number;
  critical_events: number;
  active_alerts: number;
  active_workflows: number;
  delayed_workflows: number;
  average_resolution_time: number;
  bottlenecks_detected: number;
  departments_overview: DepartmentMetrics[];
}

export interface Bottleneck {
  id: number;
  departement: number;
  departement_details?: Department;
  type_goulot: string;
  description: string;
  severite: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  statut: 'DETECTED' | 'CONFIRMED' | 'RESOLVED' | 'FALSE_POSITIVE';
  date_detection: string;
  date_confirmation?: string;
  date_resolution?: string;
  impact_estime?: string;
  evenements_lies: number[];
  created_at: string;
  updated_at: string;
}

export interface DepartmentMetrics {
  departement_id: number;
  departement_nom: string;
  nombre_evenements: number;
  temps_moyen_resolution: number;
  taux_occupation?: number;
  nombre_workflows_actifs: number;
  nombre_alertes_actives: number;
}

export interface GlobalStatistics {
  periode_debut: string;
  periode_fin: string;
  total_evenements: number;
  evenements_par_severite: Record<EventSeverity, number>;
  evenements_par_departement: Record<string, number>;
  temps_moyen_resolution: number;
  taux_resolution: number;
  goulots_detectes: number;
  workflows_completes: number;
}

export interface Report {
  id: number;
  titre: string;
  type_rapport: string;
  plage_date: string;
  donnees_metriques: any;
  format: 'pdf' | 'csv';
  genere_par: number;
  genere_par_details?: User;
  date_generation: string;
  fichier_url?: string;
  created_at: string;
  updated_at: string;
}

export interface GenerateReportRequest {
  plage_date: string;
  donnees_metriques: any;
  format: 'pdf' | 'csv';
}

// ============================================================================
// Service Types
// ============================================================================

export interface Service {
  id: number;
  nom: string;
  description?: string;
  departement?: number;
  est_actif: boolean;
  created_at: string;
  updated_at: string;
}

export interface ServiceSummary {
  total_services: number;
  active_services: number;
  services_by_department: Record<string, number>;
}

// ============================================================================
// Common Types
// ============================================================================

export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

export interface ApiError {
  detail?: string;
  message?: string;
  errors?: Record<string, string[]>;
}
