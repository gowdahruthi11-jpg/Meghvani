import React, { useState, useEffect } from 'react';
import {
  BrainCircuit,
  Sliders,
  AlertTriangle,
  BarChart3,
  Scale,
  Percent,
  TrendingDown,
  Info,
  Calendar,
  Layers,
  Sparkles,
  ShieldAlert,
  HelpCircle,
  Activity,
  Compass,
  CheckCircle2,
  Clock,
  BookOpen
} from 'lucide-react';
import { api } from '../services/api';
import {
  BaselineModelMetadata,
  FalseOnsetForecastResponse,
  DecisionSupportResult,
  AdvisoryResult,
  CalibrationBin,
  FeatureContribution
} from '../types';

export const BaselineModelPage: React.FC = () => {
  const [metadata, setMetadata] = useState<BaselineModelMetadata | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [selectedBlock, setSelectedBlock] = useState<string>('BLK001');
  const [forecast, setForecast] = useState<FalseOnsetForecastResponse | null>(null);
  const [forecastLoading, setForecastLoading] = useState<boolean>(false);
  const [decision, setDecision] = useState<DecisionSupportResult | null>(null);
  const [decisionLoading, setDecisionLoading] = useState<boolean>(false);
  const [selectedCrop, setSelectedCrop] = useState<string>('soybean');
  const [advisory, setAdvisory] = useState<AdvisoryResult | null>(null);
  const [advisoryLoading, setAdvisoryLoading] = useState<boolean>(false);

  const blockOptions = [
    { id: 'BLK001', name: 'Nagpur Rural (BLK001)' },
    { id: 'BLK002', name: 'Wardha East (BLK002)' },
    { id: 'BLK003', name: 'Amravati Central (BLK003)' },
  ];

  const cropOptions = [
    { id: 'soybean', name: 'Soybean (Glycine max)' },
    { id: 'cotton', name: 'Cotton (Gossypium hirsutum)' },
    { id: 'pigeonpea', name: 'Pigeonpea / Tur (Cajanus cajan)' },
  ];

  const fetchModelMetadata = async () => {
    try {
      const data = await api.getBaselineSummary();
      setMetadata(data);
    } catch (err) {
      console.error('Failed to load baseline summary:', err);
    }
  };

  const fetchBlockForecast = async (blockId: string) => {
    setForecastLoading(true);
    try {
      const data = await api.getFalseOnsetForecast(blockId);
      setForecast(data);
    } catch (err) {
      console.error(`Failed to load false onset forecast for ${blockId}:`, err);
    } finally {
      setForecastLoading(false);
    }
  };

  const fetchBlockDecision = async (blockId: string) => {
    setDecisionLoading(true);
    try {
      const data = await api.getFalseOnsetDecision(blockId);
      setDecision(data);
    } catch (err) {
      console.error(`Failed to load false onset decision for ${blockId}:`, err);
    } finally {
      setDecisionLoading(false);
    }
  };

  const fetchBlockAdvisory = async (blockId: string, cropId: string) => {
    setAdvisoryLoading(true);
    try {
      const data = await api.getBlockAdvisory(blockId, cropId);
      setAdvisory(data);
    } catch (err) {
      console.error(`Failed to load advisory for ${blockId} / ${cropId}:`, err);
    } finally {
      setAdvisoryLoading(false);
    }
  };

  useEffect(() => {
    const load = async () => {
      setLoading(true);
      await fetchModelMetadata();
      await fetchBlockForecast(selectedBlock);
      await fetchBlockDecision(selectedBlock);
      await fetchBlockAdvisory(selectedBlock, selectedCrop);
      setLoading(false);
    };
    load();
  }, []);

  useEffect(() => {
    fetchBlockForecast(selectedBlock);
    fetchBlockDecision(selectedBlock);
    fetchBlockAdvisory(selectedBlock, selectedCrop);
  }, [selectedBlock, selectedCrop]);

  const chrono = metadata?.chronological_evaluation;
  const diag = metadata?.diagnostic_evaluation;

  return (
    <div className="space-y-8 pb-16">
      {/* Header Banner */}
      <div className="relative overflow-hidden rounded-2xl bg-gradient-to-br from-slate-900 via-indigo-950 to-slate-900 p-6 sm:p-8 border border-indigo-700/40 shadow-xl">
        <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div className="space-y-3">
            <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-amber-500/10 border border-amber-400/30 text-amber-300 text-xs font-semibold">
              <AlertTriangle className="w-3.5 h-3.5" />
              <span>PROTOTYPE — SINGLE-YEAR DEMO EVALUATION (PHASE 3B.1)</span>
            </div>
            <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
              False-Onset 7-Day Baseline Model
            </h1>
            <p className="text-sm text-slate-300 max-w-2xl leading-relaxed">
              Evaluation integrity architecture: rigorous separation between temporal chronological holdout
              and event-focused historical diagnostic evaluation.
            </p>
          </div>

          {/* Model Specification Card */}
          <div className="bg-slate-950/80 backdrop-blur-md px-5 py-4 rounded-xl border border-slate-700/80 space-y-1.5 min-w-[240px]">
            <div className="text-[11px] font-semibold uppercase tracking-wider text-slate-400">
              Model Configuration
            </div>
            <div className="text-sm font-bold text-sky-400">
              Logistic Regression (Balanced)
            </div>
            <div className="text-xs text-slate-300 flex items-center justify-between">
              <span>Target:</span>
              <span className="font-mono text-emerald-400 font-semibold">target_false_onset_7d</span>
            </div>
            <div className="text-xs text-slate-300 flex items-center justify-between">
              <span>Horizon:</span>
              <span className="font-mono text-sky-300">7 Calendar Days</span>
            </div>
          </div>
        </div>
      </div>

      {/* Prominent Scientific Limitation Banner */}
      <div className="p-4 sm:p-5 rounded-xl bg-amber-950/40 border border-amber-500/40 flex items-start space-x-3.5 shadow-lg">
        <ShieldAlert className="w-5 h-5 text-amber-400 flex-shrink-0 mt-0.5" />
        <div className="space-y-1 text-xs text-amber-200/90 leading-relaxed">
          <div className="font-bold text-amber-300 text-sm">Scientific Limitation: Single-Year Prototype Dataset</div>
          <div>
            Meghvani currently has one calendar year of demonstration data (2025). Multi-year temporal validation
            is required before claiming verified forecast skill. All 6 false-onset events occurred during early June (train period);
            the chronological test period contains zero events.
          </div>
        </div>
      </div>

      {/* SECTION 1: CHRONOLOGICAL HOLDOUT */}
      <div className="glass-panel rounded-2xl p-6 border border-slate-800 space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-800 pb-4">
          <div>
            <div className="inline-flex items-center space-x-1.5 px-2.5 py-0.5 rounded-md bg-sky-950/80 border border-sky-800 text-sky-300 text-[10px] font-semibold uppercase tracking-wider mb-1">
              <span>Evaluation Mode 1</span>
            </div>
            <h2 className="text-lg font-bold text-white flex items-center space-x-2">
              <Calendar className="w-5 h-5 text-sky-400" />
              <span>Chronological Holdout Evaluation</span>
            </h2>
            <p className="text-xs text-slate-400">
              Strictly chronological split: earlier 70% for model fitting, later 30% for out-of-time evaluation.
            </p>
          </div>

          <div className="inline-flex items-center px-3 py-1 rounded-full bg-rose-950/60 border border-rose-500/40 text-rose-300 text-xs font-semibold">
            Status: {chrono?.status || 'INSUFFICIENT_EVENT_VARIATION'}
          </div>
        </div>

        {/* Chronological Warning Callout */}
        <div className="p-3.5 rounded-lg bg-slate-900/80 border border-slate-700/60 text-xs text-slate-300 flex items-start space-x-2.5">
          <AlertTriangle className="w-4 h-4 text-amber-400 flex-shrink-0 mt-0.5" />
          <span>
            <strong className="text-white">Zero Test Events Notice: </strong>
            No false-onset events occurred in the chronological test period ({chrono?.test_start} to {chrono?.test_end}).
            These results do not establish verified forecast skill. Brier Skill Score is not interpretable for skill.
          </span>
        </div>

        {/* Chronological Metric Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 space-y-1">
            <div className="text-[11px] font-semibold uppercase tracking-wider text-slate-400">
              Training Period
            </div>
            <div className="text-sm font-mono font-bold text-white">
              {chrono?.train_start} &rarr; {chrono?.train_end}
            </div>
            <div className="text-xs text-slate-400">
              {chrono?.train_rows} rows | <span className="text-emerald-400 font-semibold">{chrono?.train_positive_count} positives</span>
            </div>
          </div>

          <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 space-y-1">
            <div className="text-[11px] font-semibold uppercase tracking-wider text-slate-400">
              Test Period
            </div>
            <div className="text-sm font-mono font-bold text-white">
              {chrono?.test_start} &rarr; {chrono?.test_end}
            </div>
            <div className="text-xs text-slate-400">
              {chrono?.test_rows} rows | <span className="text-rose-400 font-semibold">{chrono?.test_positive_count} positives (0.0%)</span>
            </div>
          </div>

          <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 space-y-1">
            <div className="text-[11px] font-semibold uppercase tracking-wider text-slate-400">
              Test Brier Score
            </div>
            <div className="text-2xl font-bold font-mono text-emerald-400">
              {chrono?.brier_score !== undefined ? chrono.brier_score.toFixed(4) : '--'}
            </div>
            <div className="text-[11px] text-slate-500">
              Mean squared error on all-zero test targets
            </div>
          </div>

          <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 space-y-1">
            <div className="text-[11px] font-semibold uppercase tracking-wider text-slate-400">
              Brier Skill Score (BSS)
            </div>
            <div className="text-lg font-bold font-mono text-amber-400">
              Not interpretable
            </div>
            <div className="text-[11px] text-slate-500">
              Reference skill undefined when test has 0 events
            </div>
          </div>
        </div>

        {/* Discrimination Status Row */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-1">
          <div className="p-3.5 rounded-lg bg-slate-950/60 border border-slate-800 flex items-center justify-between">
            <span className="text-xs font-medium text-slate-300">Test ROC-AUC:</span>
            <span className="text-xs font-mono font-bold text-slate-400 bg-slate-900 px-2 py-0.5 rounded border border-slate-800">
              Not available — insufficient class variation
            </span>
          </div>

          <div className="p-3.5 rounded-lg bg-slate-950/60 border border-slate-800 flex items-center justify-between">
            <span className="text-xs font-medium text-slate-300">Test PR-AUC:</span>
            <span className="text-xs font-mono font-bold text-slate-400 bg-slate-900 px-2 py-0.5 rounded border border-slate-800">
              Not available — insufficient class variation
            </span>
          </div>
        </div>
      </div>

      {/* SECTION 2: HISTORICAL EVENT DIAGNOSTIC */}
      <div className="glass-panel rounded-2xl p-6 border border-slate-800 space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-800 pb-4">
          <div>
            <div className="inline-flex items-center space-x-1.5 px-2.5 py-0.5 rounded-md bg-emerald-950/80 border border-emerald-800 text-emerald-300 text-[10px] font-semibold uppercase tracking-wider mb-1">
              <span>Evaluation Mode 2</span>
            </div>
            <h2 className="text-lg font-bold text-white flex items-center space-x-2">
              <Activity className="w-5 h-5 text-emerald-400" />
              <span>Historical Event Diagnostic Evaluation</span>
            </h2>
            <p className="text-xs text-slate-400">
              Diagnostic analysis of baseline capacity to discriminate historical false-onset cases from non-events.
            </p>
          </div>

          <div className="inline-flex items-center px-3 py-1 rounded-full bg-emerald-950/60 border border-emerald-500/40 text-emerald-300 text-xs font-semibold">
            Diagnostic only — not operational validation
          </div>
        </div>

        {/* Diagnostic Metric Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 space-y-1">
            <div className="text-[11px] font-semibold uppercase tracking-wider text-slate-400">
              Diagnostic Sample
            </div>
            <div className="text-2xl font-bold font-mono text-white">
              {diag?.total_diagnostic_rows || 366}
            </div>
            <div className="text-xs text-slate-400">
              {diag?.positive_count || 6} Positives | {diag?.negative_count || 360} Negatives ({((diag?.positive_rate || 0.0164) * 100).toFixed(2)}%)
            </div>
          </div>

          <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 space-y-1">
            <div className="text-[11px] font-semibold uppercase tracking-wider text-slate-400">
              Diagnostic Brier Score
            </div>
            <div className="text-2xl font-bold font-mono text-emerald-400">
              {diag?.brier_score !== undefined ? diag.brier_score.toFixed(4) : '0.0279'}
            </div>
            <div className="text-[11px] text-slate-500">
              Mean squared probability error across sample
            </div>
          </div>

          <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 space-y-1">
            <div className="text-[11px] font-semibold uppercase tracking-wider text-slate-400">
              Diagnostic ROC-AUC
            </div>
            <div className="text-2xl font-bold font-mono text-sky-400">
              {typeof diag?.roc_auc === 'number' ? diag.roc_auc.toFixed(4) : '0.9931'}
            </div>
            <div className="text-[11px] text-slate-500">
              Separation capacity on historical cases
            </div>
          </div>

          <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 space-y-1">
            <div className="text-[11px] font-semibold uppercase tracking-wider text-slate-400">
              Diagnostic PR-AUC
            </div>
            <div className="text-2xl font-bold font-mono text-indigo-400">
              {typeof diag?.pr_auc === 'number' ? diag.pr_auc.toFixed(4) : '0.6327'}
            </div>
            <div className="text-[11px] text-slate-500">
              Precision-recall area for rare event class
            </div>
          </div>
        </div>

        {/* Diagnostic Calibration Table */}
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-bold text-white flex items-center space-x-2">
              <Sliders className="w-4 h-4 text-emerald-400" />
              <span>Reliability Information (Binned Probability Table)</span>
            </h3>
            <span className="text-[11px] text-slate-400">10 probability intervals (0.0 to 1.0)</span>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs text-slate-300">
              <thead className="bg-slate-900 text-slate-400 border-b border-slate-800 uppercase font-semibold">
                <tr>
                  <th className="py-2.5 px-3">Bin Range</th>
                  <th className="py-2.5 px-3">Count</th>
                  <th className="py-2.5 px-3">Mean Predicted P</th>
                  <th className="py-2.5 px-3">Observed Frequency</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 font-mono">
                {diag?.calibration_bins?.map((bin: CalibrationBin) => (
                  <tr key={bin.bin_index} className="hover:bg-slate-900/40">
                    <td className="py-2 px-3 text-slate-200">{bin.bin_range}</td>
                    <td className="py-2 px-3">{bin.sample_count}</td>
                    <td className="py-2 px-3">
                      {bin.mean_predicted_probability !== null
                        ? bin.mean_predicted_probability.toFixed(4)
                        : '-'}
                    </td>
                    <td className="py-2 px-3">
                      {bin.observed_event_frequency !== null
                        ? bin.observed_event_frequency.toFixed(4)
                        : '-'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      {/* SECTION 3: PROBABILITY CALIBRATION — PROTOTYPE */}
      <div className="glass-panel rounded-2xl p-6 border border-slate-800 space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-800 pb-4">
          <div>
            <div className="inline-flex items-center space-x-1.5 px-2.5 py-0.5 rounded-md bg-purple-950/80 border border-purple-800 text-purple-300 text-[10px] font-semibold uppercase tracking-wider mb-1">
              <span>Prototype Experiment (Phase 4A)</span>
            </div>
            <h2 className="text-lg font-bold text-white flex items-center space-x-2">
              <Scale className="w-5 h-5 text-purple-400" />
              <span>Probability Calibration — Prototype</span>
            </h2>
            <p className="text-xs text-slate-400">
              Experimental Platt / Sigmoid calibration layer evaluated on temporal split integrity.
            </p>
          </div>

          <div className="inline-flex items-center px-3 py-1 rounded-full bg-amber-950/60 border border-amber-500/40 text-amber-300 text-xs font-semibold">
            Status: Calibration not validated ({metadata?.calibration?.status || 'INSUFFICIENT_CALIBRATION_DATA'})
          </div>
        </div>

        {/* Small Data Warning */}
        <div className="p-3.5 rounded-lg bg-amber-950/30 border border-amber-500/40 text-xs text-amber-200/90 flex items-start space-x-2.5">
          <AlertTriangle className="w-4 h-4 text-amber-400 flex-shrink-0 mt-0.5" />
          <div className="space-y-1">
            <span className="font-bold text-amber-300">Calibration Limitation Notice:</span>
            <p>
              Only six false-onset events are available in the current single-year dataset. A reliable temporal calibration experiment requires substantially more historical events.
              Because all 6 positive events occur in early June, subsequent temporal calibration and evaluation slices contain zero positive events. Calibration parameters cannot be reliably fitted without manufacturing fake data.
            </p>
          </div>
        </div>

        {/* Calibration Experiment Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 space-y-1">
            <div className="text-[11px] font-semibold uppercase tracking-wider text-slate-400">
              Calibration Method
            </div>
            <div className="text-sm font-mono font-bold text-purple-400">
              {metadata?.calibration?.method ? `${metadata.calibration.method.toUpperCase()} (Platt Scaling)` : 'SIGMOID (Platt Scaling)'}
            </div>
            <div className="text-[11px] text-slate-500">
              Logistic probability mapping
            </div>
          </div>

          <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 space-y-1">
            <div className="text-[11px] font-semibold uppercase tracking-wider text-slate-400">
              Temporal Splits (Positives)
            </div>
            <div className="text-xs font-mono font-semibold text-slate-300">
              Train: {metadata?.calibration?.positive_count ?? 6} | Cal: {metadata?.calibration?.calibration_positive_count ?? 0} | Eval: {metadata?.calibration?.evaluation_positive_count ?? 0}
            </div>
            <div className="text-[11px] text-rose-400 font-semibold">
              Zero positives in calibration slice
            </div>
          </div>

          <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 space-y-1">
            <div className="text-[11px] font-semibold uppercase tracking-wider text-slate-400">
              Raw Brier Score
            </div>
            <div className="text-2xl font-bold font-mono text-emerald-400">
              {metadata?.calibration?.raw_brier_score !== null && metadata?.calibration?.raw_brier_score !== undefined
                ? metadata.calibration.raw_brier_score.toFixed(4)
                : '0.0000'}
            </div>
            <div className="text-[11px] text-slate-500">
              Uncalibrated logistic baseline
            </div>
          </div>

          <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 space-y-1">
            <div className="text-[11px] font-semibold uppercase tracking-wider text-slate-400">
              Calibrated Brier Score
            </div>
            <div className="text-lg font-bold font-mono text-amber-400">
              {metadata?.calibration?.calibrated_brier_score !== null && metadata?.calibration?.calibrated_brier_score !== undefined
                ? metadata.calibration.calibrated_brier_score.toFixed(4)
                : 'Not available'}
            </div>
            <div className="text-[11px] text-slate-500">
              Not fitted due to zero calibration positives
            </div>
          </div>
        </div>

        {/* Temporal Partition Table */}
        <div className="p-4 rounded-xl bg-slate-950/60 border border-slate-800 space-y-2">
          <div className="text-xs font-semibold text-slate-300">Three-Way Chronological Partition Details:</div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-3 font-mono text-xs">
            <div className="p-2.5 rounded bg-slate-900 border border-slate-800">
              <span className="text-slate-400 block text-[10px] uppercase font-sans">1. Model Fitting</span>
              <span className="text-sky-300 font-semibold">{metadata?.calibration?.training_period || '2025-06-01 to 2025-07-31'}</span>
              <span className="text-slate-400 block text-[11px]">Rows: {metadata?.calibration?.train_row_count || 183} | Positives: {metadata?.calibration?.positive_count || 6}</span>
            </div>
            <div className="p-2.5 rounded bg-slate-900 border border-slate-800">
              <span className="text-slate-400 block text-[10px] uppercase font-sans">2. Calibration Fitting</span>
              <span className="text-purple-300 font-semibold">{metadata?.calibration?.calibration_period || '2025-08-01 to 2025-08-30'}</span>
              <span className="text-rose-400 block text-[11px]">Rows: {metadata?.calibration?.calibration_row_count || 90} | Positives: {metadata?.calibration?.calibration_positive_count || 0}</span>
            </div>
            <div className="p-2.5 rounded bg-slate-900 border border-slate-800">
              <span className="text-slate-400 block text-[10px] uppercase font-sans">3. Out-of-Time Evaluation</span>
              <span className="text-emerald-300 font-semibold">{metadata?.calibration?.evaluation_period || '2025-08-31 to 2025-09-30'}</span>
              <span className="text-slate-400 block text-[11px]">Rows: {metadata?.calibration?.evaluation_row_count || 93} | Positives: {metadata?.calibration?.evaluation_positive_count || 0}</span>
            </div>
          </div>
        </div>
      </div>

      {/* SECTION 4: MODEL FEATURE CONTRIBUTIONS */}
      <div className="glass-panel rounded-2xl p-6 border border-slate-800 space-y-4">
        <div>
          <h3 className="text-base font-bold text-white flex items-center space-x-2">
            <BarChart3 className="w-4 h-4 text-indigo-400" />
            <span>Model Feature Contributions</span>
          </h3>
          <p className="text-xs text-slate-400">
            These coefficients indicate model association within the prototype dataset. They are not causal effects.
          </p>
        </div>

        <div className="overflow-x-auto max-h-[320px] overflow-y-auto">
          <table className="w-full text-left text-xs text-slate-300">
            <thead className="sticky top-0 bg-slate-900 text-slate-400 border-b border-slate-800 uppercase font-semibold">
              <tr>
                <th className="py-2.5 px-3">Feature Name</th>
                <th className="py-2.5 px-3">Coefficient</th>
                <th className="py-2.5 px-3">Magnitude</th>
                <th className="py-2.5 px-3">Non-Causal Contribution Notice</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 font-mono">
              {metadata?.feature_contributions?.map((feat: FeatureContribution) => (
                <tr key={feat.feature_name} className="hover:bg-slate-900/40">
                  <td className="py-2 px-3 text-slate-200">{feat.feature_name}</td>
                  <td
                    className={`py-2 px-3 font-semibold ${
                      feat.coefficient > 0 ? 'text-emerald-400' : feat.coefficient < 0 ? 'text-rose-400' : 'text-slate-400'
                    }`}
                  >
                    {feat.coefficient > 0 ? `+${feat.coefficient.toFixed(4)}` : feat.coefficient.toFixed(4)}
                  </td>
                  <td className="py-2 px-3 text-slate-400">
                    {feat.absolute_coefficient.toFixed(4)}
                  </td>
                  <td className="py-2 px-3 text-[11px] font-sans text-slate-400">
                    Linear association in prototype dataset (not a causal effect)
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* SECTION 5: BLOCK INFERENCE PROTOTYPE CHECK */}
      <div className="glass-panel rounded-2xl p-6 border border-slate-800 space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h2 className="text-lg font-bold text-white flex items-center space-x-2">
              <BrainCircuit className="w-5 h-5 text-sky-400" />
              <span>Block-Level Baseline Inference Check</span>
            </h2>
            <p className="text-xs text-slate-400">
              Evaluates latest available predictor features through the fitted chronological baseline. Preserves raw vs calibrated probability.
            </p>
          </div>

          <div className="flex items-center space-x-3">
            <span className="text-xs text-slate-400 font-medium">Select Block:</span>
            <select
              value={selectedBlock}
              onChange={(e) => setSelectedBlock(e.target.value)}
              className="bg-slate-900 border border-slate-700 rounded-lg px-3 py-1.5 text-xs text-slate-200 focus:outline-none focus:border-sky-500"
            >
              {blockOptions.map((b) => (
                <option key={b.id} value={b.id}>
                  {b.name}
                </option>
              ))}
            </select>
          </div>
        </div>

        {forecastLoading ? (
          <div className="p-8 text-center text-slate-400 text-xs">Computing baseline probability...</div>
        ) : forecast ? (
          <div className="p-5 rounded-xl bg-slate-900/60 border border-slate-800 flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div className="space-y-1.5">
              <div className="text-xs text-slate-400">
                Prediction Date: <span className="text-white font-mono">{forecast.prediction_date}</span>
              </div>
              <div className="text-xs text-slate-400">
                Target: <span className="text-sky-300 font-semibold">{forecast.target} (7-Day Horizon)</span>
              </div>
              <div className="text-[11px] text-slate-500">
                Evaluation Status: <span className="text-amber-400 font-semibold">{forecast.evaluation_status || 'INSUFFICIENT_EVENT_VARIATION'}</span> | Operational Forecast: NO (PROTOTYPE ONLY)
              </div>
              <div className="text-[11px] text-purple-400">
                Calibration Status: <span className="font-semibold">{forecast.calibration_status || 'INSUFFICIENT_CALIBRATION_DATA'}</span> (Sigmoid Platt Scaling)
              </div>
              <div className="text-[11px] text-slate-400 max-w-xl">
                {forecast.scientific_warning || 'Prototype model evaluation only.'}
              </div>
            </div>

            <div className="flex flex-col sm:flex-row items-end sm:items-center gap-4">
              <div className="text-right p-3 rounded-lg bg-slate-950/80 border border-slate-800">
                <div className="text-[10px] uppercase tracking-wider font-semibold text-slate-400">
                  Raw Probability
                </div>
                <div className="text-2xl font-extrabold text-sky-400 font-mono">
                  {((forecast.raw_probability ?? forecast.probability) * 100).toFixed(1)}%
                </div>
              </div>

              <div className="text-right p-3 rounded-lg bg-slate-950/80 border border-slate-800">
                <div className="text-[10px] uppercase tracking-wider font-semibold text-slate-400">
                  Calibrated Probability
                </div>
                <div className="text-xl font-bold text-amber-400 font-mono">
                  {forecast.calibrated_probability !== null && forecast.calibrated_probability !== undefined
                    ? `${(forecast.calibrated_probability * 100).toFixed(1)}%`
                    : 'Not available'}
                </div>
                <div className="text-[10px] text-slate-500">
                  {forecast.calibrated_probability !== null ? 'Calibrated' : 'Insufficient data'}
                </div>
              </div>
            </div>
          </div>
        ) : null}
      </div>

      {/* SECTION 6: PROTOTYPE DECISION SUPPORT */}
      <div className="glass-panel rounded-2xl p-6 border border-slate-800 space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-800 pb-4">
          <div>
            <div className="inline-flex items-center space-x-1.5 px-2.5 py-0.5 rounded-md bg-emerald-950/80 border border-emerald-800 text-emerald-300 text-[10px] font-semibold uppercase tracking-wider mb-1">
              <span>Decision Support Layer (Phase 4B)</span>
            </div>
            <h2 className="text-lg font-bold text-white flex items-center space-x-2">
              <Compass className="w-5 h-5 text-emerald-400" />
              <span>Prototype Decision Support</span>
            </h2>
            <p className="text-xs text-slate-400">
              Deterministic, explainable translation of prototype false-onset risk into demonstration sowing posture.
            </p>
          </div>

          <div className="inline-flex items-center px-3 py-1 rounded-full bg-amber-950/60 border border-amber-500/40 text-amber-300 text-xs font-semibold">
            Status: {decision?.decision_status || 'PROTOTYPE_ONLY'} (Not Operational)
          </div>
        </div>

        {decisionLoading ? (
          <div className="p-8 text-center text-slate-400 text-xs">Evaluating prototype decision rules...</div>
        ) : decision ? (
          <div className="space-y-6">
            {/* Visual Hierarchy: Decision -> Probability -> Reason -> Scientific limitations */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {/* Decision Result Card */}
              <div
                className={`p-5 rounded-xl border flex flex-col justify-between ${
                  decision.decision === 'SOW_NOW'
                    ? 'bg-emerald-950/40 border-emerald-500/50 text-emerald-200'
                    : decision.decision === 'SOW_PART_NOW'
                    ? 'bg-amber-950/40 border-amber-500/50 text-amber-200'
                    : decision.decision === 'WAIT'
                    ? 'bg-rose-950/40 border-rose-500/50 text-rose-200'
                    : 'bg-slate-900 border-slate-700 text-slate-300'
                }`}
              >
                <div>
                  <div className="text-[10px] uppercase tracking-wider font-semibold opacity-75">
                    Demonstration Posture
                  </div>
                  <div className="text-2xl font-extrabold font-mono mt-1">
                    Prototype: {decision.decision}
                  </div>
                </div>
                <div className="text-[11px] mt-3 opacity-80">
                  {decision.decision === 'SOW_NOW'
                    ? 'Low false-onset risk detected under prototype thresholds.'
                    : decision.decision === 'SOW_PART_NOW'
                    ? 'Moderate false-onset risk: split sowing posture.'
                    : decision.decision === 'WAIT'
                    ? 'Elevated false-onset risk: delay sowing until sustained rain.'
                    : 'Decision inputs unavailable.'}
                </div>
              </div>

              {/* Underlying Probability Card */}
              <div className="p-5 rounded-xl bg-slate-900/60 border border-slate-800 flex flex-col justify-between">
                <div>
                  <div className="text-[10px] uppercase tracking-wider font-semibold text-slate-400">
                    Current Prototype Probability
                  </div>
                  <div className="text-2xl font-extrabold font-mono text-sky-400 mt-1">
                    {decision.probability !== null ? `${(decision.probability * 100).toFixed(1)}%` : '--'}
                  </div>
                </div>
                <div className="text-[11px] text-slate-400 mt-3 space-y-0.5">
                  <div>Probability Status: <span className="text-sky-300 font-semibold">{decision.probability_status}</span></div>
                  <div>Horizon: <span className="text-slate-200 font-semibold">{decision.horizon_days} Calendar Days</span></div>
                </div>
              </div>

              {/* Threshold Definition Card */}
              <div className="p-5 rounded-xl bg-slate-900/60 border border-slate-800 flex flex-col justify-between">
                <div>
                  <div className="text-[10px] uppercase tracking-wider font-semibold text-slate-400">
                    Configured Decision Thresholds
                  </div>
                  <div className="text-xs font-mono space-y-1 mt-2 text-slate-300">
                    <div className="flex justify-between">
                      <span className="text-emerald-400 font-semibold">SOW_NOW:</span>
                      <span>&lt; {(decision.thresholds.low_risk_max * 100).toFixed(0)}%</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-amber-400 font-semibold">SOW_PART_NOW:</span>
                      <span>{(decision.thresholds.low_risk_max * 100).toFixed(0)}% – {(decision.thresholds.high_risk_min * 100 - 1).toFixed(0)}%</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-rose-400 font-semibold">WAIT:</span>
                      <span>&ge; {(decision.thresholds.high_risk_min * 100).toFixed(0)}%</span>
                    </div>
                  </div>
                </div>
                <div className="text-[10px] text-slate-500 mt-2">
                  Demonstration thresholds; require agronomic validation.
                </div>
              </div>
            </div>

            {/* Why This Decision? & Reason Codes */}
            <div className="p-4 rounded-xl bg-slate-950/60 border border-slate-800 space-y-3">
              <div className="text-xs font-bold text-white uppercase tracking-wider flex items-center space-x-2">
                <HelpCircle className="w-4 h-4 text-emerald-400" />
                <span>Why This Decision?</span>
              </div>
              <div className="text-xs text-slate-200 leading-relaxed">
                {decision.explanation}
              </div>
              <div className="flex flex-wrap gap-2 pt-1">
                {decision.reason_codes.map((code: string) => (
                  <span
                    key={code}
                    className="px-2.5 py-1 rounded-md bg-slate-900 border border-slate-700/80 text-[11px] font-mono text-slate-300"
                  >
                    {code}
                  </span>
                ))}
              </div>
            </div>

            {/* System Status & Scientific Limitations */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs font-mono">
              <div className="p-2.5 rounded-lg bg-slate-900/60 border border-slate-800">
                <span className="text-slate-500 block text-[10px] uppercase font-sans">Probability Status</span>
                <span className="text-sky-300 font-semibold">RAW PROTOTYPE</span>
              </div>
              <div className="p-2.5 rounded-lg bg-slate-900/60 border border-slate-800">
                <span className="text-slate-500 block text-[10px] uppercase font-sans">Calibration</span>
                <span className="text-amber-400 font-semibold">NOT VALIDATED</span>
              </div>
              <div className="p-2.5 rounded-lg bg-slate-900/60 border border-slate-800">
                <span className="text-slate-500 block text-[10px] uppercase font-sans">Evaluation</span>
                <span className="text-purple-300 font-semibold">LIMITED 1-YR PROTOTYPE</span>
              </div>
              <div className="p-2.5 rounded-lg bg-slate-900/60 border border-slate-800">
                <span className="text-slate-500 block text-[10px] uppercase font-sans">Operational</span>
                <span className="text-rose-400 font-semibold">NO (DEMO ONLY)</span>
              </div>
            </div>

            {/* Disclaimer Callout */}
            <div className="p-3.5 rounded-lg bg-amber-950/30 border border-amber-500/40 text-xs text-amber-200/90 flex items-start space-x-2.5">
              <AlertTriangle className="w-4 h-4 text-amber-400 flex-shrink-0 mt-0.5" />
              <span>
                <strong>Demonstration Boundary: </strong>
                {decision.scientific_warning} These thresholds are demonstration values and require agronomic validation before operational use.
              </span>
            </div>
          </div>
        ) : null}
      </div>

      {/* SECTION 7: ADVISORY ENGINE (PHASE 5A) */}
      <div className="glass-panel rounded-2xl p-6 border border-slate-800 space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800 pb-4">
          <div>
            <div className="inline-flex items-center space-x-1.5 px-2.5 py-0.5 rounded-md bg-sky-950/80 border border-sky-800 text-sky-300 text-[10px] font-semibold uppercase tracking-wider mb-1">
              <span>Advisory Rule Framework (Phase 5A)</span>
            </div>
            <h2 className="text-lg font-bold text-white flex items-center space-x-2">
              <BookOpen className="w-5 h-5 text-sky-400" />
              <span>Advisory Engine</span>
            </h2>
            <p className="text-xs text-slate-400">
              Pure decision-to-advisory translation layer. Enforces strict scientific traceability: NO RULE = NO ADVICE.
            </p>
          </div>

          <div className="flex items-center space-x-3">
            <span className="text-xs text-slate-400 font-medium">Crop:</span>
            <select
              value={selectedCrop}
              onChange={(e) => setSelectedCrop(e.target.value)}
              className="bg-slate-900 border border-slate-700 rounded-lg px-3 py-1.5 text-xs text-slate-200 focus:outline-none focus:border-sky-500 capitalize"
            >
              {cropOptions.map((c) => (
                <option key={c.id} value={c.id}>
                  {c.name}
                </option>
              ))}
            </select>
          </div>
        </div>

        {advisoryLoading ? (
          <div className="p-8 text-center text-slate-400 text-xs">Querying advisory rule registry...</div>
        ) : advisory ? (
          <div className="space-y-6">
            {/* Visual Grid: Prototype Decision, Selected Crop, Advisory Status */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {/* Prototype Decision Card */}
              <div className="p-5 rounded-xl bg-slate-900/60 border border-slate-800 flex flex-col justify-between">
                <div>
                  <div className="text-[10px] uppercase tracking-wider font-semibold text-slate-400">
                    Prototype Decision
                  </div>
                  <div className="text-2xl font-extrabold font-mono text-emerald-400 mt-1">
                    {advisory.decision || decision?.decision || 'WAIT'}
                  </div>
                </div>
                <div className="text-[11px] text-slate-400 mt-3 space-y-0.5">
                  <div>Decision Status: <span className="text-amber-400 font-semibold">{advisory.decision_status}</span></div>
                  <div>Probability: <span className="text-sky-300 font-mono font-semibold">{advisory.probability !== null && advisory.probability !== undefined ? `${(advisory.probability * 100).toFixed(1)}%` : '--'}</span></div>
                </div>
              </div>

              {/* Selected Crop Card */}
              <div className="p-5 rounded-xl bg-slate-900/60 border border-slate-800 flex flex-col justify-between">
                <div>
                  <div className="text-[10px] uppercase tracking-wider font-semibold text-slate-400">
                    Crop
                  </div>
                  <div className="text-2xl font-extrabold font-mono text-white mt-1 capitalize">
                    {advisory.crop_id || selectedCrop}
                  </div>
                </div>
                <div className="text-[11px] text-slate-400 mt-3 space-y-0.5">
                  <div>Language: <span className="text-slate-200 font-semibold uppercase">{advisory.language}</span></div>
                  <div>Block: <span className="text-slate-200 font-semibold">{advisory.block_id || selectedBlock}</span></div>
                </div>
              </div>

              {/* Advisory Status Card */}
              <div
                className={`p-5 rounded-xl border flex flex-col justify-between ${
                  advisory.advisory_status === 'RULE_MATCHED'
                    ? 'bg-emerald-950/40 border-emerald-500/50 text-emerald-200'
                    : 'bg-rose-950/40 border-rose-500/50 text-rose-200'
                }`}
              >
                <div>
                  <div className="text-[10px] uppercase tracking-wider font-semibold opacity-75">
                    Advisory Status
                  </div>
                  <div className="text-2xl font-extrabold font-mono mt-1">
                    {advisory.advisory_status === 'NO_VALIDATED_RULE' ? 'NO VALIDATED RULE' : advisory.advisory_status}
                  </div>
                </div>
                <div className="text-[11px] mt-3 space-y-0.5 opacity-80">
                  <div>Validation Status: <span className="font-semibold">{advisory.validation_status}</span></div>
                  <div>Operational: <span className="font-semibold">{advisory.is_operational ? 'YES' : 'NO'}</span></div>
                </div>
              </div>
            </div>

            {/* Why No Advisory? Explanation Panel */}
            <div className="p-4 rounded-xl bg-slate-950/60 border border-slate-800 space-y-3">
              <div className="text-xs font-bold text-white uppercase tracking-wider flex items-center space-x-2">
                <HelpCircle className="w-4 h-4 text-sky-400" />
                <span>Why no advisory?</span>
              </div>
              <div className="text-xs text-slate-200 leading-relaxed font-sans">
                {advisory.advisory_status === 'NO_VALIDATED_RULE'
                  ? 'No validated crop-specific agronomic rule is currently configured for this decision.'
                  : advisory.advisory_text || 'Rule matched from registry.'}
              </div>
              <div className="text-[11px] text-slate-400 bg-slate-900/60 p-3 rounded-lg border border-slate-800 leading-relaxed">
                <span className="font-semibold text-slate-300">Scientific Boundary: </span>
                {advisory.scientific_warning}
              </div>
            </div>

            {/* System Status Table */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs font-mono">
              <div className="p-2.5 rounded-lg bg-slate-900/60 border border-slate-800">
                <span className="text-slate-500 block text-[10px] uppercase font-sans">Decision Status</span>
                <span className="text-amber-400 font-semibold">{advisory.decision_status}</span>
              </div>
              <div className="p-2.5 rounded-lg bg-slate-900/60 border border-slate-800">
                <span className="text-slate-500 block text-[10px] uppercase font-sans">Rule ID</span>
                <span className="text-slate-300 font-semibold">{advisory.rule_id || 'NONE (NO RULE)'}</span>
              </div>
              <div className="p-2.5 rounded-lg bg-slate-900/60 border border-slate-800">
                <span className="text-slate-500 block text-[10px] uppercase font-sans">Source Traceability</span>
                <span className="text-purple-300 font-semibold">{advisory.source?.source_name || 'UNCONFIGURED'}</span>
              </div>
              <div className="p-2.5 rounded-lg bg-slate-900/60 border border-slate-800">
                <span className="text-slate-500 block text-[10px] uppercase font-sans">Operational</span>
                <span className="text-rose-400 font-semibold">NO</span>
              </div>
            </div>

            {/* Safety Notice Callout */}
            <div className="p-3.5 rounded-lg bg-sky-950/30 border border-sky-500/40 text-xs text-sky-200/90 flex items-start space-x-2.5">
              <ShieldAlert className="w-4 h-4 text-sky-400 flex-shrink-0 mt-0.5" />
              <span>
                <strong>Zero Unsupported Advice Guarantee: </strong>
                Under Meghvani Phase 5A safety policy, prototype risk models never produce generic farming advice. Crop sowing guidance requires source attribution (ICAR, CRIDA, KVK, or SAU) and explicit VALIDATED status before operational dissemination.
              </span>
            </div>
          </div>
        ) : null}
      </div>
    </div>
  );
};
