import {
  Block,
  Village,
  Crop,
  Farmer,
  WeatherObservation,
  ForecastOutput,
  FarmerObservation,
  AlertLog,
  RegistrationMessageResponse,
  SystemHealth,
  HistoricalSummary,
  HistoricalRecord,
  HistoricalBlockTimeline,
  PredictionDatasetSummary,
  PredictionBlockResponse,
  BaselineModelMetadata,
  FalseOnsetForecastResponse,
  DecisionSupportResult,
  AdvisoryResult,
  AlertLogAudit,
  AlertPreviewResponse,
  AlertSimulationResult,
  FarmerObservationHistoryItem,
  ObservationSummary,
  DemoRunResult,
  DemoStatusResult,
  MultiYearValidationSummary,
  MultiEventForecastResponse,
  MultiEventSuiteSummary,
  FalseOnsetExplanationResponse,
  CommunicationGatewayStatus,
  CommunicationSummary,
  CommunicationTransaction,
  VoiceAlertResponse
} from '../types';


const API_BASE = '/api';
const DEFAULT_OFFICER_KEY = 'meghvani-officer-dev-key-2026';

async function request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const url = `${API_BASE}${endpoint}`;
  const response = await fetch(url, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      'X-API-Key': DEFAULT_OFFICER_KEY,
      ...options.headers,
    },
  });

  if (!response.ok) {
    let errMessage = `HTTP ${response.status}: ${response.statusText}`;
    try {
      const errData = await response.json();
      if (errData && errData.detail) {
        errMessage = typeof errData.detail === 'string' ? errData.detail : JSON.stringify(errData.detail);
      }
    } catch {
      // ignore json parse error
    }
    throw new Error(errMessage);
  }

  return response.json();
}

export const api = {
  // Health
  getHealth: () => request<SystemHealth>('/health'),

  // Location
  getBlocks: () => request<Block[]>('/blocks'),
  getBlock: (id: number) => request<Block>(`/blocks/${id}`),
  getVillages: () => request<Village[]>('/villages'),
  getVillagesByPin: (pin: string) => request<Village[]>(`/villages/by-pin/${pin}`),

  // Crops
  getCrops: () => request<Crop[]>('/crops'),

  // Farmers
  getFarmers: (limit = 100) => request<Farmer[]>(`/farmers?limit=${limit}`),
  getFarmer: (id: number) => request<Farmer>(`/farmers/${id}`),
  getFarmerByPhone: (phone: string) => request<Farmer>(`/farmers/by-phone/${encodeURIComponent(phone)}`),

  // Registration
  startRegistration: (phone_number: string, force_new: boolean = false) =>
    request<RegistrationMessageResponse>('/registration/start', {
      method: 'POST',
      body: JSON.stringify({ phone_number, force_new }),
    }),

  resetRegistration: (phone_number: string) =>
    request<RegistrationMessageResponse>('/registration/reset', {
      method: 'POST',
      body: JSON.stringify({ phone_number }),
    }),

  sendRegistrationMessage: (phone_number: string, message: string) =>
    request<RegistrationMessageResponse>('/registration/message', {
      method: 'POST',
      body: JSON.stringify({ phone_number, message }),
    }),

  simulateMissedCall: (phone_number: string) =>
    request<RegistrationMessageResponse>('/registration/missed-call', {
      method: 'POST',
      body: JSON.stringify({ phone_number }),
    }),

  // Observations
  getObservations: (blockId?: number) =>
    request<FarmerObservation[]>(blockId ? `/observations/${blockId}` : '/observations'),

  submitObservation: (data: {
    farmer_id: number;
    block_id?: number;
    village_id?: number;
    observation_date: string;
    observation_time?: string;
    observation_type: string;
    crop_id?: string;
    notes?: string;
    value?: number;
    source?: string;
  }) =>
    request<FarmerObservation>('/observations', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  getObservationSummary: (params?: {
    block_id?: number;
    village_id?: number;
    crop_id?: string;
    start_date?: string;
    end_date?: string;
  }) => {
    const q = new URLSearchParams();
    if (params?.block_id) q.set('block_id', params.block_id.toString());
    if (params?.village_id) q.set('village_id', params.village_id.toString());
    if (params?.crop_id) q.set('crop_id', params.crop_id);
    if (params?.start_date) q.set('start_date', params.start_date);
    if (params?.end_date) q.set('end_date', params.end_date);
    const qs = q.toString() ? `?${q.toString()}` : '';
    return request<ObservationSummary>(`/observations/summary${qs}`);
  },

  getObservationHistory: (params?: {
    farmer_id?: number;
    block_id?: number;
    village_id?: number;
    crop_id?: string;
    observation_type?: string;
    validation_status?: string;
    start_date?: string;
    end_date?: string;
    limit?: number;
  }) => {
    const q = new URLSearchParams();
    if (params?.farmer_id) q.set('farmer_id', params.farmer_id.toString());
    if (params?.block_id) q.set('block_id', params.block_id.toString());
    if (params?.village_id) q.set('village_id', params.village_id.toString());
    if (params?.crop_id) q.set('crop_id', params.crop_id);
    if (params?.observation_type) q.set('observation_type', params.observation_type);
    if (params?.validation_status) q.set('validation_status', params.validation_status);
    if (params?.start_date) q.set('start_date', params.start_date);
    if (params?.end_date) q.set('end_date', params.end_date);
    if (params?.limit) q.set('limit', params.limit.toString());
    const qs = q.toString() ? `?${q.toString()}` : '';
    return request<FarmerObservationHistoryItem[]>(`/observations/history${qs}`);
  },

  // Alerts
  getAlerts: () => request<AlertLog[]>('/alerts'),
  simulateAlert: (data: {
    farmer_id?: number;
    block_id?: number;
    crop_id?: string | number;
    alert_type?: string;
    risk_level?: string;
    override_message?: string;
    language?: string;
    severity?: string;
    channel_preference?: string;
    force_failure_channel?: string;
  }) =>
    request<AlertSimulationResult>('/alerts/simulate', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  dispatchAlert: (data: {
    farmer_id?: number;
    block_id?: number;
    crop_id?: string | number;
    alert_type?: string;
    risk_level?: string;
    override_message?: string;
    language?: string;
    severity?: string;
    channel_preference?: string;
    force_failure_channel?: string;
  }) =>
    request<AlertSimulationResult>('/alerts/dispatch', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  // Weather & Forecast
  getWeather: (blockId: number) => request<WeatherObservation[]>(`/weather/${blockId}`),
  getForecast: (blockId: number) => request<ForecastOutput>(`/weather/${blockId}/forecast`),

  // Historical Analysis (Phase 2)
  getHistoricalSummary: () => request<HistoricalSummary>('/historical/summary'),
  
  getHistoricalEvents: (params?: { block_id?: string; event_type?: string; start_date?: string; end_date?: string; limit?: number }) => {
    const q = new URLSearchParams();
    if (params?.block_id) q.set('block_id', params.block_id);
    if (params?.event_type) q.set('event_type', params.event_type);
    if (params?.start_date) q.set('start_date', params.start_date);
    if (params?.end_date) q.set('end_date', params.end_date);
    if (params?.limit) q.set('limit', params.limit.toString());
    const qs = q.toString() ? `?${q.toString()}` : '';
    return request<HistoricalRecord[]>(`/historical/events${qs}`);
  },

  getHistoricalBlockTimeline: (blockId: string, limit = 365) =>
    request<HistoricalBlockTimeline>(`/historical/${blockId}?limit=${limit}`),

  processHistoricalData: () =>
    request<{ status: string; message: string; summary: any }>('/historical/process', {
      method: 'POST',
    }),

  // Prediction Dataset (Phase 3A)
  getPredictionSummary: () =>
    request<PredictionDatasetSummary>('/prediction-dataset/summary'),

  getPredictionRecords: (blockId: string, limit = 100, offset = 0, qualityFilter?: string) => {
    const q = new URLSearchParams();
    q.set('limit', limit.toString());
    q.set('offset', offset.toString());
    if (qualityFilter) q.set('quality_filter', qualityFilter);
    return request<PredictionBlockResponse>(`/prediction-dataset/${blockId}?${q.toString()}`);
  },

  // Baseline Model (Phase 3B)
  getBaselineSummary: () =>
    request<BaselineModelMetadata>('/forecast/baseline-summary'),

  getFalseOnsetForecast: (blockId: string) =>
    request<FalseOnsetForecastResponse>(`/forecast/${blockId}/false-onset`),

  getFalseOnsetDecision: (blockId: string) =>
    request<DecisionSupportResult>(`/forecast/${blockId}/false-onset/decision`),

  getFalseOnsetExplanation: (blockId: string) =>
    request<FalseOnsetExplanationResponse>(`/forecast/${blockId}/false-onset/explain`),


  // Multi-Event Prediction Suite
  getMultiEventForecast: (blockId: string, horizonDays = 7) =>
    request<MultiEventForecastResponse>(`/forecast/${blockId}/multi-event?horizon_days=${horizonDays}`),

  getMultiEventSuiteSummary: () =>
    request<MultiEventSuiteSummary>('/forecast/suite-summary'),

  // Advisory Rule Framework (Phase 5A)
  getBlockAdvisory: (blockId: string, cropId = 'soybean', language = 'en') => {
    const q = new URLSearchParams();
    if (cropId) q.set('crop_id', cropId);
    if (language) q.set('language', language);
    return request<AdvisoryResult>(`/advisory/${blockId}?${q.toString()}`);
  },

  // Alerts & Communication Simulation (Phase 6A)
  previewAlert: (data: {
    farmer_id: number;
    crop_id?: string;
    language?: string;
    severity?: string;
    channel?: string;
  }) =>
    request<AlertPreviewResponse>('/alerts/preview', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  getAlertHistory: (params?: {
    farmer_id?: number;
    block_id?: number;
    crop_id?: string;
    status?: string;
    channel?: string;
    severity?: string;
    limit?: number;
  }) => {
    const q = new URLSearchParams();
    if (params?.farmer_id) q.set('farmer_id', params.farmer_id.toString());
    if (params?.block_id) q.set('block_id', params.block_id.toString());
    if (params?.crop_id) q.set('crop_id', params.crop_id);
    if (params?.status) q.set('status', params.status);
    if (params?.channel) q.set('channel', params.channel);
    if (params?.severity) q.set('severity', params.severity);
    if (params?.limit) q.set('limit', params.limit.toString());
    const qs = q.toString() ? `?${q.toString()}` : '';
    return request<AlertLogAudit[]>(`/alerts/history${qs}`);
  },

  // SIH Demonstration (Phase 7A)
  runDemo: (data?: { probability?: number; language?: string; observation_type?: string }) =>
    request<DemoRunResult>('/demo/run', {
      method: 'POST',
      body: JSON.stringify(data || {}),
    }),

  getDemoStatus: () => request<DemoStatusResult>('/demo/status'),

  resetDemo: () =>
    request<{ status: string; observations_cleared?: number; alerts_cleared?: number }>('/demo/reset', {
      method: 'POST',
    }),

  // Multi-Year Scientific Validation (Phase 7B)
  getMultiYearValidationSummary: () =>
    request<MultiYearValidationSummary>('/validation/multiyear/summary'),

  getMultiYearValidationYear: (year: number) =>
    request<any>(`/validation/multiyear/year/${year}`),

  getMultiYearValidationBlock: (blockId: string) =>
    request<any>(`/validation/multiyear/block/${blockId}`),

  getMultiYearValidationHorizon: (days: number) =>
    request<any>(`/validation/multiyear/horizon/${days}`),

  getMultiYearEventSummary: () =>
    request<{ status: string; total_records: number; records: any[] }>('/validation/multiyear/events'),

  // IMD Historical Data Integration (Phase 7C)
  getIMDIngestionStatus: () =>
    request<any>('/validation/multiyear/imd/status'),

  getSpatialMappingReport: () =>
    request<any>('/validation/multiyear/spatial/report'),

  getValidationGateStatus: () =>
    request<{ validation_gate: string; validation_status: string; statement: string; imd_status: string }>('/validation/multiyear/gate'),

  // Probability Calibration & Rolling-Origin (Phase 8A)
  getCalibrationSummary: () =>
    request<any>('/validation/calibration/summary'),

  getCalibrationReliability: () =>
    request<any>('/validation/calibration/reliability'),

  getRollingOriginSummary: () =>
    request<any>('/validation/rolling-origin/summary'),

  // Communication & Real SMS Gateway
  getCommunicationStatus: () =>
    request<CommunicationGatewayStatus>('/communication/status'),

  getCommunicationSummary: () =>
    request<CommunicationSummary>('/communication/summary'),

  getCommunicationTimeline: (limit: number = 50) =>
    request<CommunicationTransaction[]>(`/communication/timeline?limit=${limit}`),

  testIncomingSMS: (payload: { from_phone: string; body: string; message_sid?: string }) =>
    request<any>('/communication/test-incoming', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),

  // AI Voice Alert System (Sarvam AI Bulbul v3 & Demo Fallback)
  triggerVoiceAlert: (payload: {
    farmer_id?: number;
    alert_id?: number;
    language?: string;
    force_high_risk?: boolean;
    alert_type?: string;
  }) =>
    request<VoiceAlertResponse>('/communication/voice-alert', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),

  sendVoiceEvent: (payload: {
    farmer_id?: number;
    alert_id?: number;
    event: string;
    duration_seconds?: number;
  }) =>
    request<any>('/communication/voice-event', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),
};



