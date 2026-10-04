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
  id?: number;
  observation_id?: number;
  farmer_id: number;
  block_id?: number;
  village_id?: number;
  observation_date: string;
  observation_time?: string;
  observation_type: 'RAIN' | 'DRY' | 'HEAVY_RAIN';
  value?: number | null;
  crop_id?: string | null;
  notes?: string | null;
  source: string;
  status?: string;
  validation_status?: string;
  reference_rainfall_mm?: number | null;
  comparison_notes?: string | null;
  reason?: string;
  is_operational?: boolean;
  created_at?: string;
}

export interface FarmerObservationHistoryItem {
  id: number;
  observation_id: number;
  farmer_id: number;
  masked_phone?: string;
  block_id: number;
  block_name?: string;
  village_id?: number;
  village_name?: string;
  crop_id?: string;
  observation_date: string;
  observation_time?: string;
  observation_type: 'RAIN' | 'DRY' | 'HEAVY_RAIN';
  source: string;
  validation_status: string;
  reference_rainfall_mm?: number | null;
  comparison_notes?: string | null;
  notes?: string;
  created_at?: string;
}

export interface ObservationSummary {
  total_observations: number;
  event_distribution: {
    rain_count: number;
    dry_count: number;
    heavy_rain_count: number;
  };
  validation_distribution: {
    agreement_count: number;
    disagreement_count: number;
    reference_data_unavailable: number;
    reference_threshold_unavailable: number;
    pending_review: number;
  };
  reference_comparisons_count: number;
  agreement_rate: number | null;
  agreement_rate_pct: number | null;
  metric_description: string;
  disclaimer: string;
  is_operational: boolean;
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

export interface AlertLogAudit {
  id: number;
  farmer_id: number;
  masked_phone?: string;
  block_id: number;
  crop_id?: string;
  decision?: string;
  severity?: string;
  channel: string;
  status: string;
  provider?: string;
  provider_message_id?: string;
  fallback_used: boolean;
  fallback_channel?: string;
  message: string;
  reason?: string;
  external_dispatch: boolean;
  created_at: string;
}

export interface AlertPreviewResponse {
  alert_status: string;
  farmer_id?: number;
  masked_phone?: string;
  block_id?: number;
  crop_id?: string;
  decision?: string;
  probability?: number;
  severity?: string;
  routing_policy?: string;
  channel_plan?: string[];
  advisory_status?: string;
  source_institution?: string;
  source_title?: string;
  message_preview?: string;
  language?: string;
  is_operational: boolean;
  external_dispatch: boolean;
  prototype_warning?: string;
  reason?: string;
  error?: string;
}

export interface AlertSimulationResult {
  alert_id?: number;
  status: string;
  farmer_id?: number;
  masked_phone?: string;
  block_id?: number;
  crop_id?: string;
  decision?: string;
  severity?: string;
  routing_policy?: string;
  channel_plan?: string[];
  fallback_used?: boolean;
  total_farmers_targeted?: number;
  disclaimer?: string;
  dispatches?: Array<{
    provider: string;
    channel: string;
    provider_message_id: string;
    status: string;
    success: boolean;
    external_dispatch: boolean;
    recipient_masked?: string;
    error?: string | null;
  }>;
  source_institution?: string;
  source_title?: string;
  message?: string;
  language?: string;
  external_dispatch: boolean;
  is_operational: boolean;
  prototype_warning?: string;
  reason?: string;
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

export interface HistoricalSummary {
  blocks: number;
  records: number;
  onset_triggers: number;
  false_onsets: number;
  break_spell_days_count: number;
  distinct_break_episodes: number;
  break_events: number;
  heavy_rain_events: number;
  revival_events: number;
  date_range: {
    start: string | null;
    end: string | null;
  };
  quality_counts?: Record<string, number>;
  disclaimer: string;
}

export interface HistoricalRecord {
  block_id: string;
  date: string;
  rainfall_mm: number;
  rainfall_1d: number;
  rainfall_3d: number;
  rainfall_5d: number;
  rainfall_7d: number;
  rainfall_14d: number;
  rainfall_30d: number;
  dry_spell_days: number;
  wet_spell_days: number;
  rainfall_intensity_class: string;
  rainfall_anomaly?: string | null;
  onset_trigger: number;
  false_onset: number;
  break_event: number;
  heavy_rain_event: number;
  revival_event: number;
  onset_trigger_date?: string | null;
  false_onset_date?: string | null;
  dry_spell_start?: string | null;
  dry_spell_end?: string | null;
  dry_spell_length?: number | null;
  break_start?: string | null;
  break_end?: string | null;
  break_duration_days?: number | null;
  break_episode_id?: string | null;
  heavy_rain_date?: string | null;
  heavy_rainfall_mm?: number | null;
  revival_date?: string | null;
  revival_rainfall_mm?: number | null;
  data_quality_flag: string;
  source: string;
}

export interface HistoricalBlockTimeline {
  block_id: string;
  count: number;
  records: HistoricalRecord[];
  disclaimer: string;
}

export interface TargetDistributionItem {
  horizon_days: number;
  event_type: string;
  positive_count: number;
  negative_count: number;
  positive_rate_pct: number;
}

export interface PredictionDatasetSummary {
  rows: number;
  blocks: string[];
  block_count: number;
  years: number[];
  date_range: { start: string | null; end: string | null };
  horizons: number[];
  target_distributions: Record<string, TargetDistributionItem>;
  quality_statistics: {
    quality_flags: Record<string, number>;
    insufficient_history_rows: number;
    missing_features: Record<string, number>;
  };
  leakage_status: string;
  model_trained: boolean;
  disclaimer: string;
}

export interface PredictionRecord {
  block_id: string;
  prediction_date: string;
  rainfall_mm: number;
  rainfall_3d: number;
  rainfall_5d: number;
  rainfall_7d: number;
  rainfall_14d: number;
  rainfall_30d: number;
  dry_spell_days: number;
  wet_spell_days: number;
  rainfall_change_3d?: number | null;
  rainfall_change_7d?: number | null;
  rainfall_ratio_3d_7d?: number | null;
  month: number;
  day_of_year: number;
  monsoon_month_flag: number;
  days_since_last_onset?: number | null;
  days_since_last_break?: number | null;
  days_since_last_heavy_rain?: number | null;
  days_since_last_revival?: number | null;
  target_onset_7d: number;
  target_onset_14d: number;
  target_onset_21d: number;
  target_onset_30d: number;
  target_false_onset_7d: number;
  target_false_onset_14d: number;
  target_false_onset_21d: number;
  target_false_onset_30d: number;
  target_break_7d: number;
  target_break_14d: number;
  target_break_21d: number;
  target_break_30d: number;
  target_heavy_rain_7d: number;
  target_heavy_rain_14d: number;
  target_heavy_rain_21d: number;
  target_heavy_rain_30d: number;
  target_revival_7d: number;
  target_revival_14d: number;
  target_revival_21d: number;
  target_revival_30d: number;
  data_quality_flag: string;
  source: string;
}

export interface PredictionBlockResponse {
  block_id: string;
  total_records: number;
  offset: number;
  limit: number;
  returned_records: number;
  records: PredictionRecord[];
  model_trained: boolean;
  disclaimer: string;
}

export interface CalibrationBin {
  bin_index: number;
  bin_range: string;
  lower_bound: number;
  upper_bound: number;
  sample_count: number;
  mean_predicted_probability: number | null;
  observed_event_frequency: number | null;
}

export interface FeatureContribution {
  feature_name: string;
  coefficient: number;
  absolute_coefficient: number;
  interpretation: string;
}

export interface ChronologicalEvaluation {
  evaluation_type: string;
  status: string;
  train_start: string;
  train_end: string;
  test_start: string;
  test_end: string;
  train_rows: number;
  test_rows: number;
  train_positive_count: number;
  test_positive_count: number;
  test_negative_count: number;
  brier_score: number;
  brier_skill_score: number | null;
  brier_skill_status: string;
  roc_auc: number | string;
  pr_auc: number | string;
  explanation: string;
}

export interface DiagnosticEvaluation {
  evaluation_type: string;
  status: string;
  total_diagnostic_rows: number;
  positive_count: number;
  negative_count: number;
  positive_rate: number;
  brier_score: number;
  roc_auc: number | string;
  pr_auc: number | string;
  calibration_bins?: CalibrationBin[];
  not_operational: boolean;
  explanation: string;
}

export interface CalibrationMetadata {
  method: string;
  status: string;
  training_period: string;
  calibration_period: string;
  evaluation_period: string;
  train_row_count?: number;
  positive_count?: number;
  calibration_row_count?: number;
  calibration_positive_count?: number;
  evaluation_row_count?: number;
  evaluation_positive_count?: number;
  raw_brier_score?: number | null;
  calibrated_brier_score?: number | null;
  improvement?: number | null;
  explanation?: string;
  scientific_warning?: string;
  is_operational_forecast: boolean;
  calibration_curve_raw?: CalibrationBin[];
  calibration_curve_calibrated?: CalibrationBin[] | null;
}

export interface BaselineModelMetadata {
  model_name: string;
  target: string;
  horizon_days: number;
  feature_names: string[];
  evaluation_status: string;
  brier_score: number;
  brier_skill_score: number | null;
  brier_skill_status: string;
  roc_auc: number | string;
  pr_auc: number | string;
  chronological_evaluation: ChronologicalEvaluation;
  diagnostic_evaluation: DiagnosticEvaluation;
  calibration?: CalibrationMetadata;
  calibration_bins?: CalibrationBin[];
  feature_contributions: FeatureContribution[];
  scientific_warning: string;
  dataset_version: string;
  created_at: string;
  disclaimer: string;
}

export interface FalseOnsetForecastResponse {
  block_id: string;
  prediction_date: string;
  target: string;
  horizon_days: number;
  raw_probability: number;
  calibrated_probability: number | null;
  probability: number;
  model: string;
  calibration_method?: string;
  calibration_status?: string;
  evaluation_type: string;
  evaluation_status?: string;
  is_operational_forecast: boolean;
  scientific_warning?: string;
}

export interface DecisionThresholds {
  low_risk_max: number;
  high_risk_min: number;
}

export interface DecisionSupportResult {
  block_id: string;
  prediction_date: string;
  target: string;
  horizon_days: number;
  probability: number | null;
  probability_status: string;
  decision: 'SOW_NOW' | 'SOW_PART_NOW' | 'WAIT' | 'UNAVAILABLE';
  decision_status: string;
  thresholds: DecisionThresholds;
  reason_codes: string[];
  explanation: string;
  scientific_warning: string;
  is_operational: boolean;
}

export interface RuleSource {
  source_name?: string | null;
  source_reference?: string | null;
  source_version?: string | null;
  source_date?: string | null;
}

export interface AdvisoryResult {
  block_id?: string | null;
  crop_id?: string | null;
  decision?: string | null;
  probability?: number | null;
  probability_status: string;
  decision_status: string;
  advisory_status: 'NO_VALIDATED_RULE' | 'RULE_MATCHED' | 'UNAVAILABLE';
  action_type?: string | null;
  advisory_text?: string | null;
  reason?: string | null;
  rule_id?: string | null;
  source?: RuleSource | null;
  validation_status: 'UNVALIDATED' | 'REVIEW_REQUIRED' | 'VALIDATED' | 'UNAVAILABLE';
  language: string;
  is_operational: boolean;
  scientific_warning: string;
}

export interface DemoRunResult {
  status: string;
  demo_id: string;
  timestamp: string;
  stages: {
    '1_farmer': {
      farmer_id: number;
      masked_phone: string;
      village: string;
      block: string;
      district: string;
      state: string;
      crop: string;
      preferred_language: string;
      consent: boolean;
      active: boolean;
      verification: string;
    };
    '2_forecast': {
      block_id: string;
      horizon_days: number;
      event_type: string;
      probability: number;
      probability_pct: string;
      source: string;
      mode: string;
      is_operational: boolean;
      scientific_status: string;
      calibration_status: string;
    };
    '3_decision': {
      decision: string;
      probability: number;
      thresholds: Record<string, number>;
      reason_codes: string[];
      explanation: string;
      scientific_warning: string;
      decision_engine_status: string;
    };
    '4_advisory': {
      rule_id: string;
      advisory_status: string;
      validation_status: string;
      source_institution: string;
      source_title: string;
      source_supported_condition: string;
      meghvani_prototype_condition: string;
    };
    '5_message': {
      language: string;
      language_name: string;
      channel: string;
      message_text: string;
      prototype_warning: string;
      source_institution?: string;
      source_title?: string;
    };
    '6_communication': {
      alert_id: number;
      status: string;
      channel_plan: string[];
      routing_policy: string;
      provider: string;
      dispatches: any[];
      external_dispatch: boolean;
      is_operational: boolean;
    };
    '7_observation': {
      observation_id: number;
      observation_type: string;
      observation_date: string;
      source: string;
      notes: string;
      reference_rainfall_mm: number;
      validation_status: string;
      comparison_notes: string;
      automated_retraining_triggered: boolean;
    };
  };
  status_indicators: Record<string, string>;
  officer_record: any;
  is_operational: boolean;
  external_dispatch: boolean;
  disclaimer: string;
}

export interface DemoStatusResult {
  status_indicators: Record<string, string>;
  demo_farmer: {
    id: number | null;
    masked_phone: string;
    language: string;
    crop: string;
    block: string;
  };
  latest_run: {
    last_alert_id: number | null;
    last_alert_status: string | null;
    last_observation_id: number | null;
    last_validation_status: string | null;
  };
  safeguards: {
    is_operational: boolean;
    external_dispatch: boolean;
    automatic_retraining: boolean;
    ml_artifacts_locked: boolean;
  };
}

export interface DataCoverageInfo {
  historical_years: number;
  complete_years: number;
  incomplete_years: number;
  available_years_list: number[];
  blocks_count: number;
  block_ids: string[];
  total_observations: number;
  missing_dates_count: number;
  missing_rainfall_count: number;
  duplicate_records_count: number;
  suspicious_values_count: number;
  date_continuity: boolean;
}

export interface YearWiseValidationResult {
  evaluation_year: number;
  training_years: number[];
  evaluation_rows: number;
  training_rows: number;
  positive_events: number;
  negative_events: number;
  brier_score: number | null;
  climatology_brier: number | null;
  brier_skill_score: number | null;
  bss_status: string;
  roc_auc: number | null;
  pr_auc: number | null;
  discrimination_status: string;
  status: string;
  reason?: string;
}

export interface MultiYearValidationSummary {
  validation_status: string;
  validation_gate?: string;
  statement: string;
  data_coverage: DataCoverageInfo;
  provenance?: {
    dataset_name: string;
    provider: string;
    source_url_or_reference: string;
    coverage_start: string;
    coverage_end: string;
    checksum_sha256?: string;
    verification_status: string;
  } | null;
  imd_status?: {
    ingestion_status: string;
    data_source: string;
    official_url: string;
    resolution: string;
    raw_files_found: number;
    available_years: number[];
    complete_years: number[];
    incomplete_years: number[];
    missing_years: number[];
    spatial_mapping: {
      status: string;
      chosen_method: string;
      available_methods: string[];
      geometry_requirement_notes: string;
      mapped_blocks: Record<string, any>;
    };
    data_quality_report_csv: string;
    data_quality_status: string;
    validation_gate: string;
    message: string;
  };
  horizons: Record<string, any>;
  blocks: Record<string, any>;
  loyo_7d: any;
  is_operational: boolean;
  feedback_retraining: boolean;
}

export interface MultiEventForecastResponse {
  block_id: string;
  prediction_date: string;
  horizon_days: number;
  prob_onset: number;
  prob_break: number;
  prob_heavy_rain: number;
  prob_false_onset: number;
  confidence: number;
  is_operational: boolean;
  model_architecture: string;
  events_evaluated: string[];
  disclaimer: string;
}

export interface MultiEventSuiteSummary {
  [eventKey: string]: {
    name: string;
    target: string;
    horizon_days: number;
    positives: number;
    metrics: {
      brier_score_raw: number;
      brier_score_calibrated: number;
      brier_score_climatology: number;
      brier_skill_score: number;
      roc_auc: number;
      pr_auc: number;
    };
    status: string;
  };
}


