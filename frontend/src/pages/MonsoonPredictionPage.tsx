import React, { useState, useEffect } from 'react';
import {
  CloudRain,
  Sparkles,
  RefreshCw,
  AlertCircle,
  Calendar,
  CheckCircle2,
  BrainCircuit,
  ArrowRight,
  TrendingDown,
  Droplets,
  Layers,
  Sprout,
  ShieldCheck,
  Compass
} from 'lucide-react';
import { useCanonicalPrediction } from '../context/CanonicalPredictionContext';
import { Block } from '../types';
import { LocationHierarchySelector } from '../components/LocationHierarchySelector';

interface MonsoonPredictionPageProps {
  blocks: Block[];
  selectedBlockId: number;
  onSelectBlockId: (id: number) => void;
  onNavigateTab: (tab: string) => void;
}

export const MonsoonPredictionPage: React.FC<MonsoonPredictionPageProps> = ({
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
    runPrediction,
  } = useCanonicalPrediction();

  const handleSelectBlock = (id: number) => {
    setSelectedBlockId(id);
    if (onSelectBlockId) onSelectBlockId(id);
  };

  const selectedBlock = canonical;
  const horizon = forecastHorizon;

  const onsetPct = canonical.onsetProbability;
  const breakPct = canonical.breakProbability;
  const heavyRainPct = canonical.heavyRainProbability;
  const falseOnsetPct = canonical.falseOnsetRisk;
  const confidencePct = canonical.confidenceScorePct;
  const decisionPosture = canonical.sowingPosture;
  const hasRun = true;

  return (
    <div className="space-y-6 pb-12">
      {/* Page Header */}
      <div className="bg-white p-6 rounded-2xl border border-stone-200/90 shadow-2xs flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="flex items-center space-x-2.5">
          <div className="w-10 h-10 rounded-xl bg-forest-50 border border-forest-200 flex items-center justify-center text-forest-800 text-lg">
            <CloudRain className="w-5 h-5" />
          </div>
          <div>
            <h1 className="text-xl sm:text-2xl font-extrabold text-stone-900 tracking-tight">
              Hyperlocal Monsoon Prediction
            </h1>
            <p className="text-xs text-stone-600 mt-0.5">
              Supervised machine learning inference for monsoon onset, dry-spell breaks, and soil moisture transitions.
            </p>
          </div>
        </div>

        <div className="flex flex-wrap items-center gap-2">
          <div className="hidden sm:flex items-center space-x-1.5 px-3 py-1.5 rounded-xl bg-amber-50 border border-amber-200/80 text-[10px] font-bold text-amber-900">
            <span className="w-1.5 h-1.5 rounded-full bg-amber-500 animate-pulse"></span>
            <span>Prototype coverage: 3 regions</span>
          </div>
          <LocationHierarchySelector />
        </div>
      </div>

      {/* Control Panel: State, District, Block, Horizon, Run Button */}
      <div className="bg-white p-5 rounded-2xl border border-stone-200/90 shadow-2xs">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3 items-end">
          {/* State */}
          <div>
            <label className="text-[11px] font-bold text-stone-500 uppercase tracking-wider block mb-1">
              State
            </label>
            <div className="p-2.5 rounded-xl bg-stone-50 border border-stone-200 text-xs font-bold text-stone-800">
              Maharashtra
            </div>
          </div>

          {/* District */}
          <div>
            <label className="text-[11px] font-bold text-stone-500 uppercase tracking-wider block mb-1">
              District
            </label>
            <div className="p-2.5 rounded-xl bg-stone-50 border border-stone-200 text-xs font-bold text-stone-800">
              {selectedBlock.district}
            </div>
          </div>

          {/* Block Selection */}
          <div>
            <label className="text-[11px] font-bold text-stone-500 uppercase tracking-wider block mb-1">
              Block / Taluka
            </label>
            <select
              value={selectedBlock.blockId || selectedBlockId}
              onChange={(e) => handleSelectBlock(Number(e.target.value))}
              className="w-full p-2.5 rounded-xl bg-stone-50 border border-stone-300 text-xs font-bold text-stone-900 focus:outline-none focus:border-forest-600"
            >
              {blocks.map((b) => (
                <option key={b.id} value={b.id}>
                  {b.name}
                </option>
              ))}
            </select>
          </div>

          {/* Forecast Horizon */}
          <div>
            <label className="text-[11px] font-bold text-stone-500 uppercase tracking-wider block mb-1">
              Forecast Horizon
            </label>
            <select
              value={horizon}
              onChange={(e) => {
                const val = Number(e.target.value);
                setForecastHorizon(val === 7 ? 7 : val === 30 ? 30 : 15);
              }}
              className="w-full p-2.5 rounded-xl bg-stone-50 border border-stone-300 text-xs font-bold text-stone-900 focus:outline-none focus:border-forest-600 cursor-pointer"
            >
              <option value={7}>7 Days (Primary)</option>
              <option value={15}>15 Days (Subseasonal)</option>
              <option value={30}>30 Days (Monthly Outlook)</option>
            </select>
          </div>

          {/* Run Button */}
          <div>
            <button
              onClick={runPrediction}
              disabled={loading}
              className="w-full py-2.5 px-4 rounded-xl bg-forest-800 hover:bg-forest-900 text-white text-xs font-bold transition-all disabled:opacity-50 flex items-center justify-center space-x-1.5 shadow-xs"
            >
              <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
              <span>{loading ? 'Running Inference...' : 'Run Prediction'}</span>
            </button>
          </div>
        </div>

        {/* Dynamic Multi-Stage Loading Banner */}
        {loading && (
          <div className="mt-4 p-3.5 rounded-xl bg-stone-50 border border-stone-200/90 text-xs text-stone-700 space-y-1.5 animate-pulse">
            <div className="font-bold flex items-center gap-2 text-forest-800">
              <RefreshCw className="w-3.5 h-3.5 animate-spin" />
              <span>Running calibrated monsoon prediction...</span>
            </div>
            <div className="text-[11px] text-stone-500 flex flex-wrap gap-4 pl-5">
              <span>● Loading rainfall telemetry...</span>
              <span>● Evaluating Platt-calibrated event suite...</span>
              <span>● Calculating feature contributions...</span>
            </div>
          </div>
        )}
      </div>

      {/* Main Result Section */}
      {hasRun && (
        <div className="space-y-6">
          {/* Hero Prediction Outlook Banner */}
          <div className="p-6 rounded-3xl bg-gradient-to-br from-forest-900 via-forest-800 to-forest-950 text-white shadow-lg">
            <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-6 pb-6 border-b border-forest-700/60">
              <div>
                <div className="flex items-center gap-2 mb-2">
                  <span className="px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-forest-700 text-forest-100 border border-forest-600 uppercase tracking-wider">
                    Monsoon Outlook · {selectedBlock.blockName}
                  </span>
                  <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-400 text-forest-950">
                    Confidence: {confidencePct}% (Platt Calibrated)
                  </span>
                  <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-purple-400/90 text-purple-950">
                    {horizon}-Day Horizon
                  </span>
                </div>
                <h2 className="text-2xl sm:text-4xl font-extrabold tracking-tight">
                  {breakPct >= 60
                    ? 'Dry Spell Watch · Wait Before Sowing'
                    : onsetPct >= 70
                    ? 'Potential Onset · Favorable Sowing Conditions'
                    : onsetPct >= 45
                    ? 'Staggered Sowing Posture · SOW_PART_NOW'
                    : 'Moisture Building · Await Primary Onset'}
                </h2>
                <p className="text-xs sm:text-sm text-forest-200 mt-2 max-w-3xl leading-relaxed">
                  Calibrated {horizon}-day outlook: P(Onset) = <strong>{onsetPct}%</strong>, P(Break Spell) = <strong>{breakPct}%</strong>, and P(Heavy Rain) = <strong>{heavyRainPct}%</strong>. Posture derived using zero-leakage lag features and Platt-calibrated logistic regression.
                </p>
              </div>

              {/* Onset Probability Display */}
              <div className="p-5 rounded-2xl bg-forest-950/70 border border-forest-700/80 min-w-[220px] text-center">
                <span className="text-[11px] text-forest-300 font-semibold block uppercase tracking-wider">
                  Onset Probability
                </span>
                <div className="text-5xl font-black text-amber-300 mt-1">
                  {onsetPct}%
                </div>
                <span className="text-[11px] text-forest-300 block mt-1">
                  P(Onset in {horizon}d)
                </span>
              </div>
            </div>

            {/* Probability Distribution for All 4 Calibrated Events */}
            <div className="pt-6">
              <span className="text-xs font-bold text-forest-200 uppercase tracking-wider block mb-3">
                Calibrated Agrometeorological Event Suite ({horizon}-Day Forecast)
              </span>

              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 text-xs">
                {/* Onset */}
                <div className="p-3.5 rounded-xl bg-forest-800/50 border border-forest-700/60 space-y-1.5">
                  <div className="flex justify-between items-center text-forest-200 font-semibold">
                    <span>Monsoon Onset</span>
                    <span className="text-base font-extrabold text-white">{onsetPct}%</span>
                  </div>
                  <div className="w-full bg-forest-950/80 h-2.5 rounded-full overflow-hidden">
                    <div
                      style={{ width: `${onsetPct}%` }}
                      className="bg-emerald-400 h-full rounded-full transition-all duration-500"
                    />
                  </div>
                  <span className="text-[10px] text-forest-300 block">&ge;25mm cumulative rain trigger</span>
                </div>

                {/* Break */}
                <div className="p-3.5 rounded-xl bg-forest-800/50 border border-forest-700/60 space-y-1.5">
                  <div className="flex justify-between items-center text-forest-200 font-semibold">
                    <span>Dry Break Spell</span>
                    <span className="text-base font-extrabold text-white">{breakPct}%</span>
                  </div>
                  <div className="w-full bg-forest-950/80 h-2.5 rounded-full overflow-hidden">
                    <div
                      style={{ width: `${breakPct}%` }}
                      className="bg-amber-400 h-full rounded-full transition-all duration-500"
                    />
                  </div>
                  <span className="text-[10px] text-forest-300 block">&ge;5 consecutive dry days (&lt;2.5mm)</span>
                </div>

                {/* Heavy Rain */}
                <div className="p-3.5 rounded-xl bg-forest-800/50 border border-forest-700/60 space-y-1.5">
                  <div className="flex justify-between items-center text-forest-200 font-semibold">
                    <span>Heavy Rain Episode</span>
                    <span className="text-base font-extrabold text-white">{heavyRainPct}%</span>
                  </div>
                  <div className="w-full bg-forest-950/80 h-2.5 rounded-full overflow-hidden">
                    <div
                      style={{ width: `${heavyRainPct}%` }}
                      className="bg-sky-400 h-full rounded-full transition-all duration-500"
                    />
                  </div>
                  <span className="text-[10px] text-forest-300 block">&ge;64.5mm extreme rainfall/day</span>
                </div>

                {/* False Onset */}
                <div className="p-3.5 rounded-xl bg-forest-800/50 border border-forest-700/60 space-y-1.5">
                  <div className="flex justify-between items-center text-forest-200 font-semibold">
                    <span>False Onset Danger</span>
                    <span className="text-base font-extrabold text-white">{falseOnsetPct}%</span>
                  </div>
                  <div className="w-full bg-forest-950/80 h-2.5 rounded-full overflow-hidden">
                    <div
                      style={{ width: `${falseOnsetPct}%` }}
                      className="bg-rose-400 h-full rounded-full transition-all duration-500"
                    />
                  </div>
                  <span className="text-[10px] text-forest-300 block">Early rain followed by dry spell</span>
                </div>
              </div>
            </div>

            {/* Jump Link to Explainable AI */}
            <div className="mt-6 pt-4 border-t border-forest-700/60 flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs">
              <span className="text-forest-300 text-xs">
                Want to inspect the standardized weights and feature importance driving this output?
              </span>
              <button
                onClick={() => onNavigateTab('xai')}
                className="inline-flex items-center space-x-1.5 px-3.5 py-1.5 rounded-xl bg-amber-400 hover:bg-amber-300 text-forest-950 font-bold transition-all shadow-xs self-start sm:self-auto"
              >
                <BrainCircuit className="w-4 h-4" />
                <span>Explain Why Model Made This Prediction →</span>
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
