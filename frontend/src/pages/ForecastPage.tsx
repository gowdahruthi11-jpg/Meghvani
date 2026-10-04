import React from 'react';
import {
  ArrowLeft,
  Calendar,
  CloudRain,
  Sun,
  Droplets,
  ShieldCheck,
  AlertTriangle,
  RefreshCw,
  MapPin,
  Clock,
  Compass,
  ArrowRight,
  TrendingDown,
  Layers,
  Sparkles,
  Info
} from 'lucide-react';
import { useCanonicalPrediction } from '../context/CanonicalPredictionContext';
import { LocationHierarchySelector } from '../components/LocationHierarchySelector';
import { Block } from '../types';

interface ForecastPageProps {
  blocks: Block[];
  selectedBlockId: number;
  onSelectBlockId: (id: number) => void;
  onNavigateTab: (tab: string) => void;
}

export const ForecastPage: React.FC<ForecastPageProps> = ({
  blocks,
  selectedBlockId,
  onSelectBlockId,
  onNavigateTab,
}) => {
  const {
    canonical,
    forecastHorizon,
    setForecastHorizon,
    setSelectedBlockId,
    loading,
    error,
    refresh
  } = useCanonicalPrediction();

  const handleSelectBlock = (id: number) => {
    setSelectedBlockId(id);
    if (onSelectBlockId) onSelectBlockId(id);
  };

  // Horizon-sliced weather observations (oldest to newest)
  const allObs = canonical.weatherObservations;
  const slicedObs = allObs.slice(-forecastHorizon);

  // Rainy vs Dry days count in active horizon
  const rainyDays = slicedObs.filter((o) => (o.rainfall_mm || 0) >= 2.5).length;
  const dryDays = slicedObs.length - rainyDays;

  // Window date boundaries
  const today = new Date();
  const formatShortDate = (d: Date) =>
    d.toLocaleDateString('en-IN', { day: '2-digit', month: 'short' });

  const windowEndDate = new Date(today);
  windowEndDate.setDate(today.getDate() + forecastHorizon);

  const windowStr = `${formatShortDate(today)} → ${formatShortDate(windowEndDate)}`;

  return (
    <div className="space-y-6 pb-12">
      {/* ===================================================================== */}
      {/* 1. HEADER WITH BREADCRUMB, TITLE, & SUBHEADING                        */}
      {/* ===================================================================== */}
      <div className="bg-white p-6 rounded-2xl border border-stone-200/90 shadow-2xs flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="space-y-1.5">
          <div className="flex items-center gap-3">
            <button
              onClick={() => onNavigateTab('map')}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-stone-100 hover:bg-stone-200 text-stone-700 font-bold text-xs transition-colors shadow-2xs cursor-pointer"
            >
              <ArrowLeft className="w-3.5 h-3.5" />
              <span>Back to Map</span>
            </button>
            <span className="text-stone-300">|</span>
            <span className="text-xs font-extrabold uppercase tracking-wider text-forest-700">
              {canonical.blockName} • {canonical.district} • {canonical.state}
            </span>
          </div>

          <h1 className="text-2xl sm:text-3xl font-black text-stone-900 tracking-tight flex items-center gap-2">
            <span>🌧️</span>
            <span>{forecastHorizon}-Day Monsoon Outlook</span>
          </h1>
          <p className="text-xs text-stone-600 font-medium">
            Rainfall trend, onset probability and dry-spell risk across the forecast horizon.
          </p>
        </div>

        {/* Global Region Switcher Dropdown */}
        <div className="flex items-center gap-2 self-start md:self-auto">
          <span className="text-xs font-bold text-stone-500 hidden sm:inline">Hierarchy:</span>
          <LocationHierarchySelector />
        </div>
      </div>

      {/* Loading Banner */}
      {loading && (
        <div className="p-4 rounded-2xl bg-blue-50 border border-blue-200 text-blue-900 text-xs flex items-center justify-between">
          <div className="flex items-center gap-2">
            <RefreshCw className="w-4 h-4 animate-spin text-blue-700" />
            <span>Running calibrated monsoon prediction across {forecastHorizon}-day horizon...</span>
          </div>
        </div>
      )}

      {/* Error Banner with Retry */}
      {error && !loading && (
        <div className="p-4 rounded-2xl bg-rose-50 border border-rose-200 text-rose-900 text-xs flex items-center justify-between">
          <div className="flex items-center gap-2">
            <AlertTriangle className="w-4 h-4 text-rose-600" />
            <span>{error}</span>
          </div>
          <button
            onClick={() => refresh()}
            className="px-3 py-1 bg-white border border-rose-300 rounded-lg font-bold text-rose-700 hover:bg-rose-100 transition-colors cursor-pointer"
          >
            Retry
          </button>
        </div>
      )}

      {/* ===================================================================== */}
      {/* 2. HORIZON SELECTOR (7D, 15D, 30D)                                    */}
      {/* ===================================================================== */}
      <div className="bg-white p-4 rounded-2xl border border-stone-200/90 shadow-2xs flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div className="flex items-center gap-2">
          <Calendar className="w-4 h-4 text-forest-700" />
          <span className="text-xs font-extrabold uppercase tracking-wider text-stone-700">
            Forecast Horizon:
          </span>
          <span className="text-xs font-medium text-stone-500">
            Window: {windowStr}
          </span>
        </div>

        <div className="flex items-center gap-2">
          {([7, 15, 30] as const).map((h) => (
            <button
              key={h}
              onClick={() => setForecastHorizon(h)}
              className={`px-4 py-2 rounded-xl text-xs font-bold transition-all cursor-pointer ${
                forecastHorizon === h
                  ? 'bg-forest-800 text-white shadow-xs ring-2 ring-forest-600/30'
                  : 'bg-stone-100 text-stone-700 hover:bg-stone-200'
              }`}
            >
              {h}D Horizon
            </button>
          ))}
        </div>
      </div>

      {/* ===================================================================== */}
      {/* 3. 5 SUMMARY CARDS                                                    */}
      {/* ===================================================================== */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3.5">
        {/* Expected Rainfall */}
        <div className="p-4 rounded-2xl bg-white border border-stone-200/90 shadow-2xs space-y-1">
          <div className="flex items-center justify-between text-stone-400">
            <span className="text-[10px] font-extrabold uppercase tracking-wider">Expected Rainfall</span>
            <Droplets className="w-4 h-4 text-sky-600" />
          </div>
          <div className="text-2xl font-black text-stone-900">
            {canonical.expectedRainfall} <span className="text-xs font-normal text-stone-500">mm</span>
          </div>
          <div className="text-[11px] text-stone-500">Antecedent {forecastHorizon}d cumulative</div>
          <div className="text-[10px] text-emerald-700 font-bold mt-1">IMD Gridded Obs</div>
        </div>

        {/* Onset Probability */}
        <div className="p-4 rounded-2xl bg-white border border-stone-200/90 shadow-2xs space-y-1">
          <div className="flex items-center justify-between text-stone-400">
            <span className="text-[10px] font-extrabold uppercase tracking-wider">Onset Probability</span>
            <CloudRain className="w-4 h-4 text-forest-700" />
          </div>
          <div className="text-2xl font-black text-forest-900">
            {canonical.onsetProbability}%
          </div>
          <div className="text-[11px] text-stone-500">P(Onset in {forecastHorizon}d)</div>
          <div className="text-[10px] text-forest-700 font-bold mt-1">
            {canonical.onsetProbability >= 65 ? '● Favorable Surge' : '● Moisture Building'}
          </div>
        </div>

        {/* Break Risk */}
        <div className="p-4 rounded-2xl bg-white border border-stone-200/90 shadow-2xs space-y-1">
          <div className="flex items-center justify-between text-stone-400">
            <span className="text-[10px] font-extrabold uppercase tracking-wider">Break Risk</span>
            <Sun className="w-4 h-4 text-amber-600" />
          </div>
          <div className="text-2xl font-black text-amber-900">
            {canonical.breakProbability}%
          </div>
          <div className="text-[11px] text-stone-500">&ge;5 consecutive dry days</div>
          <div className="text-[10px] text-amber-700 font-bold mt-1">
            {canonical.breakProbability <= 25 ? '● Low Break Risk' : '● Monitor Hiatus'}
          </div>
        </div>

        {/* Dry Spell Risk */}
        <div className="p-4 rounded-2xl bg-white border border-stone-200/90 shadow-2xs space-y-1">
          <div className="flex items-center justify-between text-stone-400">
            <span className="text-[10px] font-extrabold uppercase tracking-wider">Dry Spell Risk</span>
            <Clock className="w-4 h-4 text-orange-600" />
          </div>
          <div className="text-2xl font-black text-stone-900">
            {canonical.currentDryStreak} <span className="text-xs font-normal text-stone-500">Days</span>
          </div>
          <div className="text-[11px] text-stone-500">Current dry streak &lt;2.5mm</div>
          <div className="text-[10px] text-stone-600 font-bold mt-1">Max recent: {canonical.maxRecentDryStreak}d</div>
        </div>

        {/* Confidence */}
        <div className="p-4 rounded-2xl bg-white border border-stone-200/90 shadow-2xs space-y-1">
          <div className="flex items-center justify-between text-stone-400">
            <span className="text-[10px] font-extrabold uppercase tracking-wider">Confidence</span>
            <ShieldCheck className="w-4 h-4 text-emerald-600" />
          </div>
          <div className="text-2xl font-black text-emerald-800">
            {canonical.confidenceLevel}
          </div>
          <div className="text-[11px] text-stone-500">{canonical.confidenceScorePct}% Score</div>
          <div className="text-[10px] text-emerald-700 font-bold mt-1">Brier Score: {canonical.brierScore}</div>
        </div>
      </div>

      {/* ===================================================================== */}
      {/* 4. RAINFALL OBSERVATIONS & PROJECTED HORIZON CHART                    */}
      {/* ===================================================================== */}
      <div className="bg-white p-6 rounded-2xl border border-stone-200/90 shadow-2xs space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-stone-100 pb-4">
          <div>
            <h2 className="text-base font-extrabold text-stone-900 flex items-center gap-2">
              <Droplets className="w-4 h-4 text-sky-600" />
              <span>Daily Rainfall Telemetry (Antecedent & Horizon Trend)</span>
            </h2>
            <p className="text-xs text-stone-500 mt-0.5">
              Daily gridded IMD precipitation observations (mm) for {canonical.blockName} across {forecastHorizon}-day window.
            </p>
          </div>

          <div className="flex items-center gap-3 text-xs">
            <span className="flex items-center gap-1.5 font-bold text-sky-800">
              <span className="w-3 h-3 rounded-xs bg-sky-500 inline-block"></span>
              <span>Observed Rain</span>
            </span>
            <span className="flex items-center gap-1.5 font-bold text-stone-500">
              <span className="w-3 h-3 rounded-xs bg-stone-300 inline-block"></span>
              <span>Baseline Threshold (&ge;2.5mm)</span>
            </span>
          </div>
        </div>

        {/* Bar Chart Visualization */}
        {slicedObs.length > 0 ? (
          <div className="pt-4">
            <div className="h-48 flex items-end gap-1 sm:gap-2 border-b border-stone-200 pb-2 px-1">
              {slicedObs.map((obs, idx) => {
                const rain = obs.rainfall_mm || 0;
                const maxRain = Math.max(...slicedObs.map((o) => o.rainfall_mm || 0), 25);
                const heightPct = Math.min(100, Math.max(8, Math.round((rain / maxRain) * 100)));
                const isRainy = rain >= 2.5;

                return (
                  <div key={idx} className="flex-1 flex flex-col items-center h-full justify-end group relative">
                    {/* Tooltip on hover */}
                    <div className="absolute -top-9 bg-stone-900 text-white text-[10px] px-2 py-0.5 rounded shadow-md opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none whitespace-nowrap z-10 font-bold">
                      {obs.observation_date}: {rain} mm
                    </div>

                    <div
                      style={{ height: `${heightPct}%` }}
                      className={`w-full max-w-[28px] rounded-t-sm transition-all duration-300 ${
                        rain > 20
                          ? 'bg-forest-700 group-hover:bg-forest-800'
                          : isRainy
                          ? 'bg-sky-500 group-hover:bg-sky-600'
                          : 'bg-stone-200 group-hover:bg-stone-300'
                      }`}
                    />
                    <span className="text-[9px] text-stone-400 mt-1 truncate max-w-[36px] font-mono">
                      {obs.observation_date.slice(5)}
                    </span>
                  </div>
                );
              })}
            </div>

            <div className="flex justify-between items-center text-[11px] text-stone-500 mt-3 pt-2">
              <div>
                Rainy Days (&ge;2.5mm): <strong className="text-stone-800">{rainyDays}</strong> / {slicedObs.length} Days
              </div>
              <div>
                Dry Days (&lt;2.5mm): <strong className="text-amber-800">{dryDays}</strong> Days
              </div>
              <div>
                Cumulative Total: <strong className="text-forest-900">{canonical.expectedRainfall} mm</strong>
              </div>
            </div>
          </div>
        ) : (
          <div className="p-8 text-center bg-stone-50 rounded-xl border border-stone-200 space-y-2">
            <Info className="w-6 h-6 text-stone-400 mx-auto" />
            <h4 className="text-sm font-bold text-stone-800">Forecast Data Pending for {canonical.blockName}</h4>
            <p className="text-xs text-stone-500 max-w-md mx-auto">
              Daily observational rainfall telemetry is being ingested from IMD gridded series.
            </p>
            <button
              onClick={() => refresh()}
              className="mt-2 px-3 py-1.5 bg-forest-800 text-white rounded-lg text-xs font-bold cursor-pointer"
            >
              Refresh Telemetry
            </button>
          </div>
        )}
      </div>

      {/* ===================================================================== */}
      {/* 5. MONSOON PROBABILITY TIMELINE / HORIZON WINDOW                      */}
      {/* ===================================================================== */}
      <div className="p-6 rounded-3xl bg-gradient-to-br from-forest-950 via-forest-900 to-stone-900 text-white shadow-lg space-y-5">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-forest-800/80 pb-4">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <span className="text-[10px] font-extrabold uppercase px-2 py-0.5 rounded bg-forest-700/80 text-forest-200">
                Calibrated Event Probabilities
              </span>
              <span className="text-xs text-forest-300">
                Window: <strong>{windowStr}</strong>
              </span>
            </div>
            <h3 className="text-lg font-black text-white">
              {forecastHorizon}-Day Calibrated Agrometeorological Event Profile
            </h3>
          </div>

          <div className="flex items-center gap-2">
            <span className="text-xs bg-forest-800/80 text-emerald-300 font-bold px-3 py-1 rounded-xl border border-forest-700">
              Confidence: {canonical.confidenceLevel} ({canonical.confidenceScorePct}%)
            </span>
          </div>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 text-xs">
          {/* Onset */}
          <div className="p-4 rounded-2xl bg-forest-900/60 border border-forest-800 space-y-2">
            <div className="flex justify-between items-center text-forest-200 font-bold">
              <span>{forecastHorizon}-Day Onset Probability</span>
              <span className="text-xl font-black text-amber-300">{canonical.onsetProbability}%</span>
            </div>
            <div className="w-full bg-forest-950 h-2 rounded-full overflow-hidden">
              <div
                style={{ width: `${canonical.onsetProbability}%` }}
                className="bg-emerald-400 h-full rounded-full transition-all"
              />
            </div>
            <div className="text-[10px] text-forest-300">
              Forecast Window: {windowStr}
            </div>
          </div>

          {/* Break */}
          <div className="p-4 rounded-2xl bg-forest-900/60 border border-forest-800 space-y-2">
            <div className="flex justify-between items-center text-forest-200 font-bold">
              <span>{forecastHorizon}-Day Break Probability</span>
              <span className="text-xl font-black text-amber-400">{canonical.breakProbability}%</span>
            </div>
            <div className="w-full bg-forest-950 h-2 rounded-full overflow-hidden">
              <div
                style={{ width: `${canonical.breakProbability}%` }}
                className="bg-amber-400 h-full rounded-full transition-all"
              />
            </div>
            <div className="text-[10px] text-forest-300">
              Dry spell &ge;5 consecutive days (&lt;2.5mm)
            </div>
          </div>

          {/* Heavy Rain */}
          <div className="p-4 rounded-2xl bg-forest-900/60 border border-forest-800 space-y-2">
            <div className="flex justify-between items-center text-forest-200 font-bold">
              <span>Heavy Rain Episode</span>
              <span className="text-xl font-black text-sky-300">{canonical.heavyRainProbability}%</span>
            </div>
            <div className="w-full bg-forest-950 h-2 rounded-full overflow-hidden">
              <div
                style={{ width: `${canonical.heavyRainProbability}%` }}
                className="bg-sky-400 h-full rounded-full transition-all"
              />
            </div>
            <div className="text-[10px] text-forest-300">
              Extreme rainfall &ge;64.5 mm/day threshold
            </div>
          </div>
        </div>

        {/* Explain Link */}
        <div className="pt-2 flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs border-t border-forest-800/60">
          <span className="text-forest-300">
            Inspect the causal feature importances driving this {canonical.blockName} forecast:
          </span>
          <button
            onClick={() => onNavigateTab('xai')}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-amber-400 hover:bg-amber-300 text-forest-950 font-bold transition-all shadow-xs cursor-pointer self-start sm:self-auto"
          >
            <span>Explain Why Model Made This Prediction →</span>
          </button>
        </div>
      </div>

      {/* ===================================================================== */}
      {/* 6. DRY SPELL ANALYSIS & KEY PERIODS                                   */}
      {/* ===================================================================== */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Dry Spell Analysis */}
        <div className="bg-white p-6 rounded-2xl border border-stone-200/90 shadow-2xs space-y-4">
          <div className="border-b border-stone-100 pb-3">
            <h3 className="text-sm font-extrabold text-stone-900 flex items-center gap-2">
              <Sun className="w-4 h-4 text-amber-600" />
              <span>Dry Spell & Hiatus Risk Assessment</span>
            </h3>
            <p className="text-xs text-stone-500 mt-0.5">
              Empirical moisture deficit indicators derived from consecutive dry streak telemetry.
            </p>
          </div>

          <div className="space-y-3 text-xs">
            <div className="p-3 rounded-xl bg-stone-50 border border-stone-200 flex items-center justify-between">
              <span className="font-semibold text-stone-600">Current Consecutive Dry Days (&lt;2.5mm):</span>
              <span className="font-black text-stone-900 text-sm">{canonical.currentDryStreak} Days</span>
            </div>

            <div className="p-3 rounded-xl bg-stone-50 border border-stone-200 flex items-center justify-between">
              <span className="font-semibold text-stone-600">Maximum Recent Dry Spell:</span>
              <span className="font-black text-stone-900 text-sm">{canonical.maxRecentDryStreak} Days</span>
            </div>

            <div className="p-3 rounded-xl bg-stone-50 border border-stone-200 flex items-center justify-between">
              <span className="font-semibold text-stone-600">Model Dry-Break Risk:</span>
              <span className="font-black text-amber-800 text-sm">{canonical.breakProbability}%</span>
            </div>

            <div className="p-3 rounded-xl bg-stone-50 border border-stone-200 flex items-center justify-between">
              <span className="font-semibold text-stone-600">7-Day Antecedent Rainfall:</span>
              <span className="font-black text-stone-900 text-sm">{canonical.cumRain7d} mm</span>
            </div>

            <div className="p-3 rounded-xl bg-stone-50 border border-stone-200 flex items-center justify-between">
              <span className="font-semibold text-stone-600">15-Day Antecedent Rainfall:</span>
              <span className="font-black text-stone-900 text-sm">{canonical.cumRain15d} mm</span>
            </div>
          </div>
        </div>

        {/* Key Event Periods */}
        <div className="bg-white p-6 rounded-2xl border border-stone-200/90 shadow-2xs space-y-4">
          <div className="border-b border-stone-100 pb-3">
            <h3 className="text-sm font-extrabold text-stone-900 flex items-center gap-2">
              <Calendar className="w-4 h-4 text-forest-700" />
              <span>Projected Agrometeorological Windows</span>
            </h3>
            <p className="text-xs text-stone-500 mt-0.5">
              Event-window estimation and seasonal moisture accumulation benchmarks.
            </p>
          </div>

          <div className="space-y-3 text-xs">
            <div className="p-3.5 rounded-xl bg-emerald-50/70 border border-emerald-200 space-y-1">
              <div className="flex justify-between items-center text-emerald-900 font-bold">
                <span>Active Window ({windowStr})</span>
                <span className="text-[10px] uppercase px-2 py-0.5 rounded bg-emerald-200 text-emerald-950 font-extrabold">
                  {canonical.monsoonStatus}
                </span>
              </div>
              <p className="text-stone-600 text-[11px] leading-relaxed">
                {canonical.postureExplanation}
              </p>
            </div>

            <div className="p-3.5 rounded-xl bg-stone-50 border border-stone-200 space-y-1">
              <div className="flex justify-between items-center text-stone-800 font-bold">
                <span>Sowing Posture Recommendation</span>
                <span className={`text-[10px] uppercase px-2 py-0.5 rounded font-extrabold ${
                  canonical.sowingPosture === 'SOW_NOW'
                    ? 'bg-emerald-100 text-emerald-900'
                    : canonical.sowingPosture === 'WAIT'
                    ? 'bg-rose-100 text-rose-900'
                    : 'bg-amber-100 text-amber-900'
                }`}>
                  {canonical.sowingPosture}
                </span>
              </div>
              <p className="text-stone-500 text-[11px]">
                {canonical.sowingPosture === 'SOW_NOW'
                  ? 'Favorable seedbed moisture. Proceed with kharif sowing under validated ICAR guidelines.'
                  : canonical.sowingPosture === 'WAIT'
                  ? 'High break spell risk or depleted moisture. Delay full sowing to prevent seed mortality.'
                  : 'Stagger sowing across parcel plots to hedge against germination moisture variation.'}
              </p>
            </div>

            <div className="p-3 rounded-xl bg-stone-50 border border-stone-200 text-[11px] text-stone-500 flex items-center justify-between">
              <span>Data Source Provenance:</span>
              <strong className="text-stone-700">{canonical.dataSource}</strong>
            </div>
          </div>
        </div>
      </div>

      {/* ===================================================================== */}
      {/* 7. DATA SOURCE TRANSPARENCY BANNER                                    */}
      {/* ===================================================================== */}
      <div className="p-4 rounded-2xl bg-stone-100 border border-stone-200 text-stone-600 text-xs flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div className="flex items-center gap-2">
          <ShieldCheck className="w-4 h-4 text-forest-700 shrink-0" />
          <span>
            <strong>{canonical.dataStatus}</strong> · {canonical.modelArchitecture}
          </span>
        </div>
        <div className="flex items-center gap-3 text-[11px] text-stone-500">
          <span>Updated: {canonical.predictionTimestamp}</span>
          <button
            onClick={() => refresh()}
            className="hover:text-stone-900 font-bold flex items-center gap-1 cursor-pointer"
          >
            <RefreshCw className="w-3 h-3" />
            <span>Refresh</span>
          </button>
        </div>
      </div>
    </div>
  );
};
