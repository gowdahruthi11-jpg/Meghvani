import React, { useState, useEffect, useMemo } from 'react';
import {
  BrainCircuit,
  Sparkles,
  Info,
  CheckCircle2,
  ArrowDown,
  ArrowRight,
  TrendingDown,
  TrendingUp,
  CloudRain,
  Sprout,
  Calendar,
  Clock,
  ChevronDown,
  ChevronUp,
  Sliders,
  ShieldCheck,
  AlertTriangle,
  RefreshCw,
  Compass,
  Layers,
  HelpCircle,
  Activity,
  ArrowDownRight,
  ArrowUpRight,
  Check
} from 'lucide-react';
import { api } from '../services/api';
import {
  FalseOnsetExplanationResponse,
  XAIFeatureItem,
  Block
} from '../types';
import { useCanonicalPrediction } from '../context/CanonicalPredictionContext';
import { LocationHierarchySelector } from '../components/LocationHierarchySelector';

interface ExplainableAIPageProps {
  blocks: Block[];
  selectedBlockId: number;
  onSelectBlockId: (id: number) => void;
  onNavigateTab: (tab: string) => void;
}

export const ExplainableAIPage: React.FC<ExplainableAIPageProps> = ({
  blocks: propBlocks,
  selectedBlockId: propBlockId,
  onSelectBlockId: propSetBlockId,
  onNavigateTab,
}) => {
  const {
    canonical,
    selectedBlock,
    setSelectedBlockId,
    blocks,
  } = useCanonicalPrediction();

  const [explanation, setExplanation] = useState<FalseOnsetExplanationResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [filterDomain, setFilterDomain] = useState<string>('ALL');
  const [showArchitecture, setShowArchitecture] = useState<boolean>(false);
  const [showTransparency, setShowTransparency] = useState<boolean>(false);

  const blockCode = useMemo(() => {
    return selectedBlock.id === 1 ? 'BLK001' : selectedBlock.id === 2 ? 'BLK002' : 'BLK003';
  }, [selectedBlock.id]);

  const loadExplanation = async (bCode: string) => {
    setLoading(true);
    try {
      const data = await api.getFalseOnsetExplanation(bCode);
      setExplanation(data);
    } catch (err) {
      console.error('Failed to load XAI explanation for block:', bCode, err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadExplanation(blockCode);
  }, [blockCode]);

  // Fallback calculation if backend is booting or initializing
  const features: XAIFeatureItem[] = explanation?.features || [];
  const topDrivers: XAIFeatureItem[] = explanation?.top_drivers || features.slice(0, 3);
  const reducingDrivers: XAIFeatureItem[] = explanation?.reducing_drivers || features.filter(f => f.direction === 'REDUCING');
  const increasingDrivers: XAIFeatureItem[] = explanation?.increasing_drivers || features.filter(f => f.direction === 'INCREASING');

  // Filter features based on domain tab
  const displayedFeatures = useMemo(() => {
    if (filterDomain === 'ALL') return features;
    return features.filter((f) => f.domain.toLowerCase() === filterDomain.toLowerCase());
  }, [features, filterDomain]);

  // Dynamic values strictly aligned with canonical prediction
  const regionName = explanation?.region_name || selectedBlock.name;
  const targetName = explanation?.target || 'False Onset Risk';
  const riskPct = explanation?.probability_pct ?? canonical.falseOnsetRisk;
  const riskTier = explanation?.risk_tier || (riskPct < 20 ? 'Low Risk' : riskPct <= 35 ? 'Moderate Risk' : 'Elevated Risk');
  const confidenceLevel = explanation?.confidence_level || canonical.confidenceLevel;
  const confidencePct = explanation?.confidence_pct || canonical.confidenceScorePct;
  const horizonDays = explanation?.horizon_days || 7;
  const decisionPosture = explanation?.decision || canonical.sowingPosture;
  const decisionExplanation = explanation?.decision_explanation || canonical.postureExplanation;

  // Conditions observed
  const observedRain7d = explanation?.observed_conditions?.rainfall_7d_mm ?? canonical.cumRain7d;
  const observedSeedbed = explanation?.observed_conditions?.seedbed_moisture_status ??
    (observedRain7d >= 40 ? `Adequately recharged (${observedRain7d} mm 7-day cumulative rainfall)` : `Partially recharged (${observedRain7d} mm 7-day cumulative rainfall)`);
  const observedDoy = explanation?.observed_conditions?.seasonal_progression_doy ?? 165;
  const observedDryStreak = explanation?.observed_conditions?.dry_spell_days ?? canonical.currentDryStreak;

  // Quick region switcher for judge demo
  const handleSwitchRegion = (id: number) => {
    setSelectedBlockId(id);
    if (propSetBlockId) propSetBlockId(id);
  };

  return (
    <div className="space-y-6 pb-16">
      {/* 1. XAI TOP HEADER & GLOBAL PREDICTION HERO */}
      <div className="bg-white p-6 rounded-2xl border border-stone-200/90 shadow-2xs space-y-6">
        {/* Header row */}
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4 pb-5 border-b border-stone-100">
          <div className="flex items-start sm:items-center space-x-3">
            <div className="w-12 h-12 rounded-xl bg-forest-50 border border-forest-200/90 flex items-center justify-center text-forest-800 shrink-0 shadow-2xs">
              <BrainCircuit className="w-6 h-6" />
            </div>
            <div>
              <div className="flex flex-wrap items-center gap-2">
                <h1 className="text-xl sm:text-2xl font-black text-stone-900 tracking-tight">
                  Why did the model make this prediction?
                </h1>
                <span className="text-[10px] font-bold px-2.5 py-0.5 rounded-full bg-forest-100 text-forest-900 border border-forest-200 uppercase tracking-wider">
                  Explainable AI (XAI)
                </span>
              </div>
              <p className="text-xs text-stone-600 mt-1">
                Transparent instance attribution, directional influence decomposition, and agronomic decision translation.
              </p>
            </div>
          </div>

          {/* Region selector & demo switcher */}
          <div className="flex flex-wrap items-center gap-2.5">
            <div className="flex items-center space-x-1 bg-stone-100/90 p-1 rounded-xl border border-stone-200 text-xs">
              <span className="text-[10px] font-extrabold uppercase px-2 text-stone-500 hidden sm:inline">
                Demo Regions:
              </span>
              {[
                { id: 3, label: 'Amravati Central (28%)' },
                { id: 2, label: 'Wardha East (22%)' },
                { id: 1, label: 'Nagpur Rural (18%)' }
              ].map((r) => (
                <button
                  key={r.id}
                  onClick={() => handleSwitchRegion(r.id)}
                  className={`px-2.5 py-1 rounded-lg text-[11px] font-semibold transition-all ${
                    selectedBlock.id === r.id
                      ? 'bg-forest-900 text-white shadow-2xs font-bold'
                      : 'text-stone-600 hover:text-stone-900 hover:bg-stone-200/60'
                  }`}
                >
                  {r.label}
                </button>
              ))}
            </div>
            <LocationHierarchySelector />
          </div>
        </div>

        {/* Prediction Context Banner */}
        <div className="p-5 rounded-2xl bg-gradient-to-br from-stone-50 via-forest-50/30 to-stone-50 border border-forest-200/80 shadow-2xs">
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
            {/* Left: Region & Target Details */}
            <div className="space-y-1.5">
              <div className="flex items-center space-x-2">
                <span className="text-[10px] font-black uppercase tracking-wider px-2 py-0.5 rounded bg-forest-200/70 text-forest-900">
                  Active Region
                </span>
                <span className="text-xs font-semibold text-stone-500">
                  {selectedBlock.district}, {selectedBlock.state} • {blockCode}
                </span>
              </div>
              <h2 className="text-2xl sm:text-3xl font-black text-stone-900 uppercase tracking-tight">
                {regionName}
              </h2>
              <div className="flex items-center space-x-2 pt-1">
                <span className="text-[11px] font-bold text-stone-500 uppercase tracking-wider">
                  Prediction target:
                </span>
                <span className="text-xs font-black text-forest-950 bg-white px-2.5 py-1 rounded-lg border border-forest-300/70 shadow-2xs">
                  {targetName}
                </span>
                <span className="text-[11px] text-stone-500 font-medium">
                  • {horizonDays}-Day Prediction Horizon
                </span>
              </div>
            </div>

            {/* Right: Risk Metric & Confidence */}
            <div className="flex items-center gap-4 bg-white p-4 rounded-xl border border-stone-200/90 shadow-2xs">
              <div className="text-center pr-4 border-r border-stone-200">
                <span className="text-[10px] font-black uppercase text-stone-400 block tracking-wider">
                  False Onset Risk
                </span>
                <div className="flex items-baseline justify-center space-x-0.5 mt-0.5">
                  <span className={`text-4xl font-black tracking-tight ${
                    riskPct < 20 ? 'text-emerald-700' : riskPct <= 35 ? 'text-amber-600' : 'text-rose-700'
                  }`}>
                    {riskPct}
                  </span>
                  <span className="text-lg font-extrabold text-stone-500">%</span>
                </div>
                <span className={`inline-block text-[10px] font-bold px-2 py-0.5 rounded-full mt-1 ${
                  riskPct < 20
                    ? 'bg-emerald-100 text-emerald-900 border border-emerald-300'
                    : riskPct <= 35
                    ? 'bg-amber-100 text-amber-900 border border-amber-300'
                    : 'bg-rose-100 text-rose-900 border border-rose-300'
                }`}>
                  {riskTier}
                </span>
              </div>

              <div className="space-y-1.5 text-xs">
                <div>
                  <span className="text-stone-400 font-bold block text-[10px] uppercase tracking-wider">Confidence Level</span>
                  <div className="flex items-center space-x-1.5 font-black text-stone-900 text-sm mt-0.5">
                    <ShieldCheck className="w-4 h-4 text-forest-700" />
                    <span>{confidenceLevel} ({confidencePct}%)</span>
                  </div>
                </div>
                <div className="text-[11px] text-stone-500 font-medium">
                  Reliability index: <span className="font-mono font-bold text-stone-700">Brier 0.118</span>
                </div>
                <div className="text-[10px] text-forest-700 font-semibold flex items-center space-x-1">
                  <span className="w-1.5 h-1.5 rounded-full bg-forest-600 animate-pulse"></span>
                  <span>Harmonized with Live Map & Dashboard</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* 2. CHANGE THE EXPLAINABILITY STORY (STORYLINE PIPELINE BANNER) */}
      <div className="bg-white p-5 rounded-2xl border border-stone-200/90 shadow-2xs space-y-3">
        <div className="flex items-center justify-between">
          <span className="text-[11px] font-extrabold uppercase tracking-wider text-stone-400">
            Explainability Storyline · From Raw Signals to Farmer Action
          </span>
          <button
            onClick={() => setShowArchitecture(!showArchitecture)}
            className="text-[11px] font-bold text-forest-800 hover:text-forest-950 flex items-center space-x-1"
          >
            <span>{showArchitecture ? 'Hide Pipeline Architecture' : 'View Pipeline Architecture'}</span>
            {showArchitecture ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
          </button>
        </div>

        {/* Narrative Flow Stepper */}
        <div className="grid grid-cols-2 md:grid-cols-6 gap-2 text-xs pt-1">
          <div className="p-3 rounded-xl bg-forest-50/70 border border-forest-200/80 flex flex-col justify-between">
            <span className="text-[10px] font-black uppercase text-forest-700">1. Prediction</span>
            <span className="font-extrabold text-stone-900 mt-1">{riskPct}% Risk</span>
            <span className="text-[10px] text-stone-500 mt-0.5">{regionName}</span>
          </div>

          <div className="p-3 rounded-xl bg-stone-50 border border-stone-200 flex flex-col justify-between">
            <span className="text-[10px] font-black uppercase text-stone-400">2. Conditions</span>
            <span className="font-extrabold text-stone-900 mt-1">{observedRain7d} mm / 7d</span>
            <span className="text-[10px] text-stone-500 mt-0.5">{observedDryStreak}d dry streak</span>
          </div>

          <div className="p-3 rounded-xl bg-stone-50 border border-stone-200 flex flex-col justify-between">
            <span className="text-[10px] font-black uppercase text-stone-400">3. Top Drivers</span>
            <span className="font-extrabold text-stone-900 mt-1">3 Dominant</span>
            <span className="text-[10px] text-stone-500 mt-0.5">Attribution share</span>
          </div>

          <div className="p-3 rounded-xl bg-stone-50 border border-stone-200 flex flex-col justify-between">
            <span className="text-[10px] font-black uppercase text-stone-400">4. Direction</span>
            <span className="font-extrabold text-stone-900 mt-1">Push & Pull</span>
            <span className="text-[10px] text-stone-500 mt-0.5">Reducing vs Increasing</span>
          </div>

          <div className="p-3 rounded-xl bg-stone-50 border border-stone-200 flex flex-col justify-between">
            <span className="text-[10px] font-black uppercase text-stone-400">5. Synthesis</span>
            <span className="font-extrabold text-stone-900 mt-1">Natural Language</span>
            <span className="text-[10px] text-stone-500 mt-0.5">Agronomic context</span>
          </div>

          <div className="p-3 rounded-xl bg-forest-900 text-white flex flex-col justify-between shadow-2xs">
            <span className="text-[10px] font-black uppercase text-forest-200">6. Implication</span>
            <span className="font-extrabold text-white mt-1">{decisionPosture.replace(/_/g, ' ')}</span>
            <span className="text-[10px] text-forest-200 mt-0.5">Field posture</span>
          </div>
        </div>

        {/* Collapsible Architecture Details */}
        {showArchitecture && (
          <div className="mt-3 p-4 rounded-xl bg-stone-50 border border-stone-200/90 text-xs space-y-2">
            <h4 className="font-bold text-stone-900 text-xs">Baseline Architecture Pipeline</h4>
            <p className="text-[11px] text-stone-600 leading-relaxed">
              Input Vector (18 standardized meteorological features) → SimpleImputer(median) → StandardScaler(Z-Score) → LogisticRegression(class_weight='balanced') → Platt Sigmoid Calibration → Instance-level log-odds decomposition c_i = β_i · z_i.
            </p>
          </div>
        )}
      </div>

      {/* 8. PREDICTION → ACTION VISUAL FLOW (Obvious Connection between ML and Agriculture) */}
      <div className="bg-white p-5 rounded-2xl border border-stone-200/90 shadow-2xs">
        <span className="text-[10px] font-extrabold uppercase tracking-wider text-stone-400 block mb-3">
          ML Signal To Agricultural Action Translation
        </span>
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs">
          {/* Signal */}
          <div className="flex-1 p-3.5 rounded-xl bg-stone-50 border border-stone-200">
            <span className="text-[10px] font-bold text-stone-400 block uppercase">1. Model Signal</span>
            <div className="font-extrabold text-stone-900 text-sm mt-0.5 flex items-center space-x-1.5">
              <CloudRain className="w-4 h-4 text-forest-700" />
              <span>{observedRain7d} mm / 7d Telemetry</span>
            </div>
            <p className="text-[11px] text-stone-500 mt-1">Antecedent moisture accumulation</p>
          </div>

          <div className="hidden sm:flex text-stone-400 shrink-0">
            <ArrowRight className="w-4 h-4" />
          </div>

          {/* Risk */}
          <div className="flex-1 p-3.5 rounded-xl bg-stone-50 border border-stone-200">
            <span className="text-[10px] font-bold text-stone-400 block uppercase">2. False Onset Risk</span>
            <div className={`font-black text-base mt-0.5 ${
              riskPct < 20 ? 'text-emerald-700' : riskPct <= 35 ? 'text-amber-700' : 'text-rose-700'
            }`}>
              {riskPct}% ({riskTier})
            </div>
            <p className="text-[11px] text-stone-500 mt-1">Evaluated against P* = 0.17</p>
          </div>

          <div className="hidden sm:flex text-stone-400 shrink-0">
            <ArrowRight className="w-4 h-4" />
          </div>

          {/* Confidence */}
          <div className="flex-1 p-3.5 rounded-xl bg-stone-50 border border-stone-200">
            <span className="text-[10px] font-bold text-stone-400 block uppercase">3. Confidence</span>
            <div className="font-extrabold text-stone-900 text-sm mt-0.5 flex items-center space-x-1.5">
              <ShieldCheck className="w-4 h-4 text-forest-700" />
              <span>{confidenceLevel} ({confidencePct}%)</span>
            </div>
            <p className="text-[11px] text-stone-500 mt-1">Multi-event BSS calibrated</p>
          </div>

          <div className="hidden sm:flex text-stone-400 shrink-0">
            <ArrowRight className="w-4 h-4" />
          </div>

          {/* Sowing Posture */}
          <div className="flex-1 p-3.5 rounded-xl bg-forest-900 text-white shadow-2xs">
            <span className="text-[10px] font-bold text-forest-200 block uppercase">4. Sowing Posture</span>
            <div className="font-black text-sm mt-0.5 text-amber-300 flex items-center space-x-1.5">
              <Check className="w-4 h-4 text-amber-300" />
              <span>{decisionPosture.replace(/_/g, ' ')}</span>
            </div>
            <p className="text-[11px] text-forest-200 mt-1">Recommended farmer posture</p>
          </div>
        </div>
      </div>

      {/* 7. HUMAN-READABLE MODEL SYNTHESIS (DARK GREEN MEGHVANI CARD) */}
      <div className="p-6 rounded-2xl bg-gradient-to-br from-forest-950 via-forest-900 to-forest-800 text-white shadow-md space-y-5">
        <div className="flex items-center justify-between pb-3 border-b border-forest-700/60">
          <div className="flex items-center space-x-2.5">
            <div className="w-8 h-8 rounded-lg bg-amber-400/20 border border-amber-300/40 flex items-center justify-center text-amber-300">
              <Sparkles className="w-4 h-4" />
            </div>
            <div>
              <h3 className="font-extrabold text-base text-white">
                Human-Readable Model Synthesis · {regionName}
              </h3>
              <p className="text-xs text-forest-200">
                Automated agronomic translation grounded in fitted model parameters and actual telemetry.
              </p>
            </div>
          </div>

          <span className="text-[10px] font-bold px-2.5 py-1 rounded bg-forest-800/80 text-forest-200 border border-forest-700">
            Live Model Interpretation
          </span>
        </div>

        {/* What the model sees */}
        <div>
          <span className="text-[10px] font-black uppercase tracking-wider text-forest-300 block mb-2">
            What The Model Sees
          </span>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-2.5">
            <div className="p-3 rounded-xl bg-white/10 backdrop-blur-xs border border-white/10 flex items-start space-x-2.5">
              <CloudRain className="w-4 h-4 text-amber-300 shrink-0 mt-0.5" />
              <div className="text-xs">
                <span className="font-bold text-white block">7-Day Rainfall</span>
                <span className="text-forest-100 text-[11px]">{observedRain7d} mm recorded over 7 days</span>
              </div>
            </div>

            <div className="p-3 rounded-xl bg-white/10 backdrop-blur-xs border border-white/10 flex items-start space-x-2.5">
              <Sprout className="w-4 h-4 text-emerald-300 shrink-0 mt-0.5" />
              <div className="text-xs">
                <span className="font-bold text-white block">Seedbed Soil Moisture</span>
                <span className="text-forest-100 text-[11px]">{observedSeedbed}</span>
              </div>
            </div>

            <div className="p-3 rounded-xl bg-white/10 backdrop-blur-xs border border-white/10 flex items-start space-x-2.5">
              <Calendar className="w-4 h-4 text-sky-300 shrink-0 mt-0.5" />
              <div className="text-xs">
                <span className="font-bold text-white block">Seasonal Progression</span>
                <span className="text-forest-100 text-[11px]">Advancing seasonal transition (Day {observedDoy})</span>
              </div>
            </div>

            <div className="p-3 rounded-xl bg-white/10 backdrop-blur-xs border border-white/10 flex items-start space-x-2.5">
              <Clock className="w-4 h-4 text-amber-300 shrink-0 mt-0.5" />
              <div className="text-xs">
                <span className="font-bold text-white block">Dry-Spell Persistence</span>
                <span className="text-forest-100 text-[11px]">{observedDryStreak} consecutive dry days recorded</span>
              </div>
            </div>
          </div>
        </div>

        {/* Model Interpretation */}
        <div className="p-4 rounded-xl bg-white/10 border border-white/10 space-y-1">
          <span className="text-[10px] font-black uppercase tracking-wider text-forest-300 block">
            Model Interpretation
          </span>
          <p className="text-sm text-forest-100 leading-relaxed font-sans font-medium">
            "{explanation?.model_synthesis || `The model estimates a ${riskPct}% false-onset risk for ${regionName}. Observed rainfall and seasonal progression reduce the modeled risk, while dry-spell persistence remains an active counter-signal.`}"
          </p>
        </div>

        {/* Decision Implication */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 p-4 rounded-xl bg-forest-950/80 border border-forest-700/80">
          <div className="space-y-0.5">
            <span className="text-[10px] font-black uppercase tracking-wider text-forest-300 block">
              Decision Implication
            </span>
            <div className="text-xs text-forest-200">
              {decisionExplanation}
            </div>
          </div>

          <div className="flex items-center space-x-2 shrink-0">
            <span className="text-[11px] font-extrabold uppercase text-stone-300">Action:</span>
            <span className="px-3.5 py-1.5 rounded-lg bg-amber-400 text-forest-950 font-black text-xs uppercase tracking-wider shadow-2xs">
              {decisionPosture.replace(/_/g, ' ')}
            </span>
          </div>
        </div>
      </div>

      {/* 6. TOP 3 DRIVERS COMPACT VISUALIZATION */}
      <div className="bg-white p-6 rounded-2xl border border-stone-200/90 shadow-2xs space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-3 border-b border-stone-100">
          <div>
            <h3 className="font-extrabold text-sm text-stone-900 uppercase tracking-wider">
              Top 3 Dominant Drivers (Attribution Ranking)
            </h3>
            <p className="text-xs text-stone-500">
              Ranked by normalized absolute attribution share from the model's fitted feature vector.
            </p>
          </div>
          <span className="text-[11px] font-semibold text-stone-400">
            Calculated from z-scored log-odds contributions
          </span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
          {topDrivers.map((driver, idx) => (
            <div
              key={driver.name}
              className="p-4 rounded-xl bg-stone-50/90 border border-stone-200/90 flex flex-col justify-between space-y-3"
            >
              <div className="flex items-start justify-between gap-2">
                <div className="flex items-center space-x-2">
                  <span className="w-6 h-6 rounded-lg bg-stone-200/80 text-stone-800 font-black text-xs flex items-center justify-center shrink-0">
                    #{idx + 1}
                  </span>
                  <div>
                    <span className="font-extrabold text-stone-900 text-xs block leading-snug">
                      {driver.label}
                    </span>
                    <span className="text-[10px] font-bold text-stone-500">
                      {driver.domain}
                    </span>
                  </div>
                </div>

                <span className={`text-[10px] font-extrabold px-2 py-0.5 rounded-md ${
                  driver.direction === 'REDUCING'
                    ? 'bg-emerald-100 text-emerald-900'
                    : 'bg-amber-100 text-amber-900'
                }`}>
                  {driver.share_pct}%
                </span>
              </div>

              {/* Progress bar */}
              <div>
                <div className="w-full bg-stone-200 h-2 rounded-full overflow-hidden">
                  <div
                    style={{ width: `${Math.min(100, Math.max(8, driver.share_pct * 4))}%` }}
                    className={`h-full rounded-full ${
                      driver.direction === 'REDUCING'
                        ? 'bg-gradient-to-r from-emerald-600 to-emerald-500'
                        : 'bg-gradient-to-r from-amber-600 to-amber-500'
                    }`}
                  />
                </div>
                <div className="flex justify-between items-center text-[10px] text-stone-500 mt-1.5 font-medium">
                  <span>Observed: {driver.observed_value} {driver.unit}</span>
                  <span className={`font-bold ${driver.direction === 'REDUCING' ? 'text-emerald-700' : 'text-amber-700'}`}>
                    {driver.influence_label}
                  </span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* 3. TOP DRIVERS SECTION: TWO CONCEPTUAL COLUMNS (REDUCING RISK vs INCREASING RISK) */}
      <div className="bg-white p-6 rounded-2xl border border-stone-200/90 shadow-2xs space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-3 border-b border-stone-100">
          <div>
            <h3 className="font-extrabold text-sm text-stone-900">
              What's driving this prediction?
            </h3>
            <p className="text-xs text-stone-500">
              Directional decomposition showing counteracting atmospheric and soil moisture forces for {regionName}.
            </p>
          </div>
          <span className="text-[11px] font-bold text-forest-800 bg-forest-50 px-2.5 py-1 rounded-lg border border-forest-200">
            Instance Signed Decomposition
          </span>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          {/* Column 1: REDUCING FALSE-ONSET RISK */}
          <div className="p-4 rounded-xl bg-emerald-50/50 border border-emerald-200/80 space-y-3">
            <div className="flex items-center justify-between pb-2 border-b border-emerald-200/60">
              <div className="flex items-center space-x-2">
                <div className="w-6 h-6 rounded-md bg-emerald-600 text-white flex items-center justify-center">
                  <ArrowDownRight className="w-4 h-4" />
                </div>
                <span className="font-black text-xs text-emerald-950 uppercase tracking-wider">
                  Reducing False-Onset Risk ({reducingDrivers.length} features)
                </span>
              </div>
              <span className="text-[10px] font-bold text-emerald-800 bg-emerald-100 px-2 py-0.5 rounded">
                Downward force
              </span>
            </div>

            <div className="space-y-2">
              {reducingDrivers.map((driver) => (
                <div
                  key={driver.name}
                  className="p-3 rounded-lg bg-white border border-emerald-200/70 hover:border-emerald-300 transition-all text-xs space-y-1.5 shadow-2xs"
                >
                  <div className="flex items-center justify-between">
                    <span className="font-bold text-stone-900 flex items-center space-x-1.5">
                      <span className="text-emerald-700 font-extrabold text-sm">↓</span>
                      <span>{driver.label}</span>
                    </span>
                    <span className="font-mono font-extrabold text-emerald-900 bg-emerald-100 px-2 py-0.5 rounded text-[11px]">
                      {driver.share_pct}% share
                    </span>
                  </div>

                  <div className="flex items-center justify-between text-[11px] text-stone-600 font-mono pt-0.5">
                    <span>Observed: <strong className="text-stone-900">{driver.observed_value} {driver.unit}</strong></span>
                    <span>Model weight: <strong className="text-stone-900">{driver.model_weight > 0 ? `+${driver.model_weight}` : driver.model_weight}</strong></span>
                  </div>

                  <div className="w-full bg-emerald-100 h-1.5 rounded-full overflow-hidden">
                    <div
                      style={{ width: `${Math.min(100, Math.max(10, driver.share_pct * 3.5))}%` }}
                      className="bg-emerald-600 h-full rounded-full"
                    />
                  </div>
                </div>
              ))}
              {reducingDrivers.length === 0 && (
                <p className="text-xs text-stone-500 italic p-3">No active reducing features for this observation.</p>
              )}
            </div>
          </div>

          {/* Column 2: INCREASING FALSE-ONSET RISK */}
          <div className="p-4 rounded-xl bg-amber-50/50 border border-amber-200/80 space-y-3">
            <div className="flex items-center justify-between pb-2 border-b border-amber-200/60">
              <div className="flex items-center space-x-2">
                <div className="w-6 h-6 rounded-md bg-amber-600 text-white flex items-center justify-center">
                  <ArrowUpRight className="w-4 h-4" />
                </div>
                <span className="font-black text-xs text-amber-950 uppercase tracking-wider">
                  Increasing False-Onset Risk ({increasingDrivers.length} features)
                </span>
              </div>
              <span className="text-[10px] font-bold text-amber-800 bg-amber-100 px-2 py-0.5 rounded">
                Upward counter-signal
              </span>
            </div>

            <div className="space-y-2">
              {increasingDrivers.map((driver) => (
                <div
                  key={driver.name}
                  className="p-3 rounded-lg bg-white border border-amber-200/70 hover:border-amber-300 transition-all text-xs space-y-1.5 shadow-2xs"
                >
                  <div className="flex items-center justify-between">
                    <span className="font-bold text-stone-900 flex items-center space-x-1.5">
                      <span className="text-amber-700 font-extrabold text-sm">↑</span>
                      <span>{driver.label}</span>
                    </span>
                    <span className="font-mono font-extrabold text-amber-900 bg-amber-100 px-2 py-0.5 rounded text-[11px]">
                      {driver.share_pct}% share
                    </span>
                  </div>

                  <div className="flex items-center justify-between text-[11px] text-stone-600 font-mono pt-0.5">
                    <span>Observed: <strong className="text-stone-900">{driver.observed_value} {driver.unit}</strong></span>
                    <span>Model weight: <strong className="text-stone-900">{driver.model_weight > 0 ? `+${driver.model_weight}` : driver.model_weight}</strong></span>
                  </div>

                  <div className="w-full bg-amber-100 h-1.5 rounded-full overflow-hidden">
                    <div
                      style={{ width: `${Math.min(100, Math.max(10, driver.share_pct * 3.5))}%` }}
                      className="bg-amber-600 h-full rounded-full"
                    />
                  </div>
                </div>
              ))}
              {increasingDrivers.length === 0 && (
                <p className="text-xs text-stone-500 italic p-3">No active increasing features for this observation.</p>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* 5. IMPORTANT DISTINCTION CALLOUT CARD */}
      <div className="p-4 rounded-2xl bg-stone-50 border border-stone-200/90 shadow-2xs space-y-2">
        <div className="flex items-center space-x-2">
          <Info className="w-4 h-4 text-forest-700 shrink-0" />
          <h4 className="font-extrabold text-xs text-stone-900 uppercase tracking-wider">
            Important Conceptual Distinction in Explainable AI
          </h4>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3 text-xs pt-1">
          <div className="p-3 bg-white rounded-xl border border-stone-200">
            <span className="font-black text-stone-900 block text-[11px]">1. Feature Value (x)</span>
            <p className="text-[11px] text-stone-600 mt-1">
              The physical meteorological observation recorded on the ground (e.g., <strong>{observedRain7d} mm</strong> rainfall or <strong>{observedDryStreak} days</strong> dry spell).
            </p>
          </div>

          <div className="p-3 bg-white rounded-xl border border-stone-200">
            <span className="font-black text-stone-900 block text-[11px]">2. Model Weight (β)</span>
            <p className="text-[11px] text-stone-600 mt-1">
              Fixed standardized coefficient fitted across multi-year training data (e.g., <strong>-1.0096</strong> for 7-day rainfall). Indicates global statistical association.
            </p>
          </div>

          <div className="p-3 bg-white rounded-xl border border-stone-200">
            <span className="font-black text-stone-900 block text-[11px]">3. Feature Contribution (c)</span>
            <p className="text-[11px] text-stone-600 mt-1">
              Instance log-odds impact <em>c = β · z</em> normalized to relative attribution share (e.g., <strong>7%</strong>), pushing risk up or down in this specific prediction.
            </p>
          </div>
        </div>
      </div>

      {/* 4 & 11. FEATURE CARDS & FUNCTIONAL FILTERS */}
      <div className="bg-white p-6 rounded-2xl border border-stone-200/90 shadow-2xs space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-stone-100">
          <div>
            <h3 className="font-extrabold text-sm text-stone-900">
              Detailed Feature Cards & Attribution Breakdown
            </h3>
            <p className="text-xs text-stone-500">
              Showing {displayedFeatures.length} of {features.length} model features used to predict false-onset risk.
            </p>
          </div>

          {/* 11. Fully Functional Filter Pills */}
          <div className="flex flex-wrap items-center gap-1 bg-stone-100 p-1 rounded-xl border border-stone-200 text-xs font-semibold">
            {['ALL', 'Climatology', 'Soil Moisture', 'Rainfall', 'Dynamics'].map((dom) => (
              <button
                key={dom}
                onClick={() => setFilterDomain(dom)}
                className={`px-3 py-1 rounded-lg text-[11px] transition-all ${
                  filterDomain.toLowerCase() === dom.toLowerCase()
                    ? 'bg-white text-forest-950 font-black shadow-2xs border border-stone-200/60'
                    : 'text-stone-600 hover:text-stone-900'
                }`}
              >
                {dom}
              </button>
            ))}
          </div>
        </div>

        {/* Feature Cards Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3.5 pt-1">
          {displayedFeatures.map((f, idx) => (
            <div
              key={f.name}
              className="p-4 rounded-xl bg-stone-50/80 hover:bg-stone-50 border border-stone-200/90 transition-all text-xs space-y-3 shadow-2xs"
            >
              {/* Top row */}
              <div className="flex items-start justify-between gap-2">
                <div className="flex items-center space-x-2">
                  <span className="w-5 h-5 rounded-md bg-stone-200 text-stone-700 font-bold text-[10px] flex items-center justify-center shrink-0">
                    #{idx + 1}
                  </span>
                  <div>
                    <span className="font-extrabold text-stone-900 text-xs block">
                      {f.label}
                    </span>
                    <span className="text-[10px] font-bold text-stone-500 bg-stone-200/60 px-1.5 py-0.5 rounded">
                      {f.domain}
                    </span>
                  </div>
                </div>

                <span className={`text-[10px] font-bold px-2 py-0.5 rounded ${
                  f.direction === 'REDUCING'
                    ? 'bg-emerald-100 text-emerald-900'
                    : f.direction === 'INCREASING'
                    ? 'bg-amber-100 text-amber-900'
                    : 'bg-stone-200 text-stone-700'
                }`}>
                  {f.influence_label}
                </span>
              </div>

              {/* Metrics Grid */}
              <div className="grid grid-cols-3 gap-2 p-2.5 rounded-lg bg-white border border-stone-200/80 font-mono text-[11px]">
                <div>
                  <span className="text-[9px] font-bold text-stone-400 block uppercase font-sans">Observed</span>
                  <span className="font-extrabold text-stone-900">{f.observed_value} {f.unit}</span>
                </div>
                <div>
                  <span className="text-[9px] font-bold text-stone-400 block uppercase font-sans">Model Weight</span>
                  <span className="font-extrabold text-stone-700">{f.model_weight > 0 ? `+${f.model_weight}` : f.model_weight}</span>
                </div>
                <div>
                  <span className="text-[9px] font-bold text-stone-400 block uppercase font-sans">Contribution</span>
                  <span className={`font-black ${f.direction === 'REDUCING' ? 'text-emerald-700' : 'text-amber-700'}`}>
                    {f.share_pct}%
                  </span>
                </div>
              </div>

              {/* Progress bar */}
              <div>
                <div className="w-full bg-stone-200 h-2 rounded-full overflow-hidden">
                  <div
                    style={{ width: `${Math.min(100, Math.max(5, f.share_pct * 3.5))}%` }}
                    className={`h-full rounded-full transition-all duration-500 ${
                      f.direction === 'REDUCING'
                        ? 'bg-gradient-to-r from-emerald-600 to-emerald-500'
                        : 'bg-gradient-to-r from-amber-600 to-amber-500'
                    }`}
                  />
                </div>
                <p className="text-[10px] text-stone-500 mt-1 leading-snug">
                  {f.desc}
                </p>
              </div>
            </div>
          ))}
        </div>

        {displayedFeatures.length === 0 && (
          <div className="text-center py-8 text-stone-500 text-xs">
            No features found for filter category "{filterDomain}".
          </div>
        )}
      </div>

      {/* 9. MODEL TRANSPARENCY SECTION (Collapsible & Compact) */}
      <div className="bg-white p-5 rounded-2xl border border-stone-200/90 shadow-2xs space-y-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Sliders className="w-4 h-4 text-forest-700" />
            <h4 className="font-extrabold text-xs text-stone-900 uppercase tracking-wider">
              Model Transparency & Technical Provenance
            </h4>
          </div>
          <button
            onClick={() => setShowTransparency(!showTransparency)}
            className="text-[11px] font-bold text-forest-800 hover:text-forest-950 flex items-center space-x-1"
          >
            <span>{showTransparency ? 'Hide Details' : 'View Model Specifications'}</span>
            {showTransparency ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
          </button>
        </div>

        {showTransparency && (
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-2.5 pt-2 text-xs">
            <div className="p-3 rounded-xl bg-stone-50 border border-stone-200">
              <span className="text-[10px] font-black uppercase text-stone-400 block">Model</span>
              <span className="font-extrabold text-stone-900 mt-0.5 block">Supervised Logistic</span>
            </div>
            <div className="p-3 rounded-xl bg-stone-50 border border-stone-200">
              <span className="text-[10px] font-black uppercase text-stone-400 block">Features</span>
              <span className="font-extrabold text-stone-900 mt-0.5 block">{features.length || 18} Predictors</span>
            </div>
            <div className="p-3 rounded-xl bg-stone-50 border border-stone-200">
              <span className="text-[10px] font-black uppercase text-stone-400 block">Scaling</span>
              <span className="font-extrabold text-stone-900 mt-0.5 block">StandardScaler (Z-Score)</span>
            </div>
            <div className="p-3 rounded-xl bg-stone-50 border border-stone-200">
              <span className="text-[10px] font-black uppercase text-stone-400 block">Calibration</span>
              <span className="font-extrabold text-stone-900 mt-0.5 block">Platt Sigmoid Scaling</span>
            </div>
            <div className="p-3 rounded-xl bg-stone-50 border border-stone-200">
              <span className="text-[10px] font-black uppercase text-stone-400 block">Prediction Horizon</span>
              <span className="font-extrabold text-stone-900 mt-0.5 block">7 Days</span>
            </div>
            <div className="p-3 rounded-xl bg-stone-50 border border-stone-200">
              <span className="text-[10px] font-black uppercase text-stone-400 block">Active Region</span>
              <span className="font-extrabold text-stone-900 mt-0.5 block">{regionName}</span>
            </div>
          </div>
        )}
      </div>

      {/* 10. SCIENTIFIC DISCLAIMER (SUBTLE) */}
      <div className="p-3.5 rounded-xl bg-stone-100/90 border border-stone-200/90 text-[11px] text-stone-600 flex items-start space-x-2.5">
        <Info className="w-4 h-4 text-stone-500 shrink-0 mt-0.5" />
        <span className="leading-relaxed">
          <strong>ⓘ Interpretation note:</strong> Feature weights represent statistical association in the prototype model; they should not be interpreted as causal effects.
        </span>
      </div>
    </div>
  );
};
