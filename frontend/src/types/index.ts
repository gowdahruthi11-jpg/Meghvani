export interface Block {
  id: number;
  name: string;
  district: string;
  state: string;
  latitude: number;
  longitude: number;
  boundary_reference?: string;
  active: boolean;
}

export interface Village {
  id: number;
  name: string;
  district: string;
  state: string;
  block_id: number;
  pin_code: string;
  latitude: number;
  longitude: number;
  active: boolean;
}

export interface Crop {
  id: number;
  name: string;
  scientific_name?: string;
  season: string;
  water_requirement: string;
  duration_category: string;
  active: boolean;
}

export interface Farmer {
  id: number;
  phone_number_masked: string;
  preferred_language: string;
  pin_code: string;
  village_id: number;
  block_id: number;
  crop_id: number;
  communication_preference: string;
  consent: boolean;
  consent_timestamp?: string;
  created_at: string;
  active: boolean;
}

export interface WeatherObservation {
  id: number;
  block_id: number;
  observation_date: string;
  rainfall_mm: number;
  temperature_c?: number;
  humidity?: number;
  wind_speed?: number;
  soil_moisture?: number;
  source: string;
  created_at: string;
}

export interface ForecastOutput {
  block_id: number;
  forecast_date: string;
  horizon_days: number;
  prob_onset?: number | null;
  prob_false_onset?: number | null;
  prob_break?: number | null;
  prob_revival?: number | null;
  prob_heavy_rain?: number | null;
  expected_break_duration?: number | null;
  rainfall_anomaly_class?: string | null;
  confidence?: number | null;
  data_availability?: string | null;
  model_version?: string | null;
  is_live_prediction: boolean;
  disclaimer: string;
}

export interface FarmerObservation {
  id: number;
  farmer_id: number;
  block_id: number;
  observation_date: string;
  observation_type: 'RAIN' | 'DRY' | 'HEAVY_RAIN';
  value?: number | null;
  source: string;
  created_at: string;
}

export interface AlertLog {
  id: number;
  farmer_id: number;
  block_id: number;
  alert_type: string;
  risk_level: string;
  channel: string;
  message: string;
  provider_message_id?: string;
  status: string;
  attempt_number: number;
  sent_at?: string;
  created_at: string;
}

export interface RegistrationMessageResponse {
  reply_message: string;
  current_step: string;
  is_completed: boolean;
  registered_farmer_id?: number | null;
  note: string;
}

export interface SystemHealth {
  status: string;
  app: string;
  version: string;
  environment: string;
  database: string;
  ml_forecast_engine: string;
  communication_providers: string;
  weather_data: string;
}
