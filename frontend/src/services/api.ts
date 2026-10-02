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
  SystemHealth
} from '../types';

const API_BASE = '/api';

async function request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const url = `${API_BASE}${endpoint}`;
  const response = await fetch(url, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
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
  startRegistration: (phone_number: string) =>
    request<RegistrationMessageResponse>('/registration/start', {
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

  submitObservation: (data: { farmer_id: number; block_id: number; observation_date: string; observation_type: string; value?: number }) =>
    request<FarmerObservation>('/observations', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  // Alerts
  getAlerts: () => request<AlertLog[]>('/alerts'),
  simulateAlert: (data: { block_id: number; alert_type: string; risk_level: string; crop_id?: number; override_message?: string }) =>
    request<{ total_farmers_targeted: number; dispatches: AlertLog[]; disclaimer: string }>('/alerts/simulate', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  // Weather & Forecast
  getWeather: (blockId: number) => request<WeatherObservation[]>(`/weather/${blockId}`),
  getForecast: (blockId: number) => request<ForecastOutput>(`/weather/${blockId}/forecast`),
};
