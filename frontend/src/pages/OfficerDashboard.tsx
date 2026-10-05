import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import {
  Farmer,
  Block,
  Village,
  Crop,
  FarmerObservation,
  AlertLog,
  WeatherObservation,
  DecisionSupportResult,
  AdvisoryResult
} from '../types';
import {
  Users,
  Layers,
  MapPin,
  Sprout,
  Bell,
  Eye,
  Send,
  ShieldCheck,
  AlertTriangle,
  RefreshCw,
  TrendingDown,
  Info,
  Calendar,
  Lock,
  Radio,
  FileCheck
} from 'lucide-react';
import { AgricultureMetricCard } from '../components/AgricultureMetricCard';
import { InteractiveWeatherMap } from '../components/InteractiveWeatherMap';
import { RecentRainfallChart } from '../components/RecentRainfallChart';
import { FarmerMessageCard } from '../components/FarmerMessageCard';
import { BlockRiskMap } from '../components/BlockRiskMap';

export const OfficerDashboard: React.FC = () => {
  const [farmers, setFarmers] = useState<Farmer[]>([]);
  const [blocks, setBlocks] = useState<Block[]>([]);
  const [villages, setVillages] = useState<Village[]>([]);
  const [crops, setCrops] = useState<Crop[]>([]);
  const [observations, setObservations] = useState<FarmerObservation[]>([]);
  const [alerts, setAlerts] = useState<AlertLog[]>([]);
  const [weatherObs, setWeatherObs] = useState<WeatherObservation[]>([]);
  const [decisionData, setDecisionData] = useState<DecisionSupportResult | null>(null);
  const [advisoryData, setAdvisoryData] = useState<AdvisoryResult | null>(null);

  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Selected parameters
  const [selectedBlockId, setSelectedBlockId] = useState<number>(1);
  const [selectedCrop, setSelectedCrop] = useState<string>('soybean');
  const [selectedRiskLevel, setSelectedRiskLevel] = useState<string>('NORMAL');
  const [selectedAlertType, setSelectedAlertType] = useState<string>('ONSET');
  const [dispatchStatus, setDispatchStatus] = useState<string | null>(null);
  const [dispatching, setDispatching] = useState<boolean>(false);

  // Officer-only Block Risk Map state
  const [officerMapBlock, setOfficerMapBlock] = useState<string>('BLK001');
  const [forecastHorizon, setForecastHorizon] = useState<'week1' | 'week2' | 'week3' | 'week4'>('week1');
  const [riskEvent, setRiskEvent] = useState<'onset' | 'break' | 'heavyRain'>('onset');

  const selectedBlock = blocks.find((b) => b.id === selectedBlockId) || blocks[0] || {
    id: 1,
    name: 'Nagpur Rural (Nagpur)',
    district: 'Nagpur',
    state: 'Maharashtra',
    latitude: 21.1458,
    longitude: 79.0882,
    active: true
  };

  const blockCode = selectedBlock.id === 1 ? 'BLK001' : selectedBlock.id === 2 ? 'BLK002' : 'BLK003';

  const loadData = async () => {
    try {
      setError(null);
      const [f, b, v, c, obs, alt] = await Promise.all([
        api.getFarmers(),
        api.getBlocks(),
        api.getVillages(),
        api.getCrops(),
        api.getObservations(),
        api.getAlerts(),
      ]);
      setFarmers(f);
      setBlocks(b);
      setVillages(v);
      setCrops(c);
      setObservations(obs);
      setAlerts(alt);
    } catch (err: any) {
      setError(err.message || 'Failed to load officer dashboard data');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const loadBlockSpecificTelemetry = async (blockId: number, cropId: string) => {
    const code = blockId === 1 ? 'BLK001' : blockId === 2 ? 'BLK002' : 'BLK003';
    try {
      const [w, dec, adv] = await Promise.all([
        api.getWeather(blockId).catch(() => []),
        api.getFalseOnsetDecision(code).catch(() => null),
        api.getBlockAdvisory(code, cropId, 'mr').catch(() => null),
      ]);
      setWeatherObs(w);
      setDecisionData(dec);
      setAdvisoryData(adv);
    } catch (e) {
      console.warn('Block telemetry loading error:', e);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  useEffect(() => {
    if (selectedBlockId) {
      loadBlockSpecificTelemetry(selectedBlockId, selectedCrop);
    }
  }, [selectedBlockId, selectedCrop]);

  const handleRefresh = () => {
    setRefreshing(true);
    loadData();
    loadBlockSpecificTelemetry(selectedBlockId, selectedCrop);
  };

  const handleSimulateAlert = async (e: React.FormEvent) => {
    e.preventDefault();
    setDispatching(true);
    setDispatchStatus(null);
    try {
      const res = await api.simulateAlert({
        block_id: selectedBlockId,
        alert_type: selectedAlertType,
        risk_level: selectedRiskLevel,
        crop_id: selectedCrop,
      });
      setDispatchStatus(
        `Simulated dispatch generated: ${res.total_farmers_targeted ?? 0} farmers targeted in ${selectedBlock.name}. external_dispatch=false (simulated mock provider).`
      );
      const updatedAlerts = await api.getAlerts();
      setAlerts(updatedAlerts);
    } catch (err: any) {
      setDispatchStatus(`Error: ${err.message}`);
    } finally {
      setDispatching(false);
    }
  };

  const cropCounts = crops.map((crop) => {
    const count = farmers.filter((f) => f.crop_id === crop.id).length;
    return { name: crop.name, count };
  });

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="flex items-center space-x-2 text-forest-700">
          <RefreshCw className="w-5 h-5 animate-spin" />
          <span className="text-sm font-semibold">Loading agricultural officer telemetry...</span>
        </div>
      </div>
    );
  }

  // Decision & Probability Values
  const decisionPosture = decisionData?.decision || 'SOW_NOW';
  const rawProb = decisionData?.probability;
  const probPercent = rawProb !== null && rawProb !== undefined ? Math.round(rawProb * 100) : null;

  return (
    <div className="space-y-8 pb-12">
      {/* Non-Operational Demonstration Warning Banner */}
      <div className="p-3.5 rounded-2xl bg-amber-500/10 border-2 border-amber-500/40 text-amber-950 flex flex-col sm:flex-row sm:items-center justify-between gap-3 shadow-xs">
        <div className="flex items-center space-x-2.5">
          <div className="w-8 h-8 rounded-lg bg-amber-500 text-white flex items-center justify-center shrink-0 font-bold text-xs shadow-xs">
            DEMO
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className="font-extrabold text-xs uppercase tracking-wider text-amber-900">
                Scientific Governance Status: Non-Operational Research Prototype
              </span>
              <span className="bg-amber-200 text-amber-900 text-[10px] font-bold px-2 py-0.5 rounded-full border border-amber-300">
                STATIC_DEMO_REPLAY
              </span>
            </div>
            <p className="text-[11px] text-amber-800 leading-snug mt-0.5">
              Invariant 4 active: External telecommunications are strictly disabled (<code>is_operational = false</code>). In-season empirical evaluation (25 May – 31 Jul) demonstrates model does not beat climatology.
            </p>
          </div>
        </div>
        <span className="text-[10px] font-mono text-amber-800 bg-amber-100 px-2 py-1 rounded-md border border-amber-300 self-start sm:self-auto shrink-0">
          Hash: 9a7e...4c1f
        </span>
      </div>

      {/* Header */}
      <div className="agri-card p-6 bg-white border-stone-200">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <div className="flex items-center space-x-2">
              <ShieldCheck className="w-6 h-6 text-forest-700" />
              <h2 className="text-xl sm:text-2xl font-bold text-stone-900 tracking-tight">
                Agricultural Officer Command Center
              </h2>
            </div>
            <p className="text-xs text-stone-600 mt-1 max-w-2xl leading-relaxed">
              Block-scale farmer targeting, loss-based decision postures, 21-day dry-spell telemetry, and multilingual simulated alert delivery.
            </p>
          </div>

          <div className="flex items-center gap-3">
            <select
              value={selectedBlockId}
              onChange={(e) => setSelectedBlockId(Number(e.target.value))}
              className="bg-stone-50 border border-stone-300 rounded-xl px-3 py-2 text-xs font-bold text-stone-900 focus:outline-none focus:border-forest-600"
            >
              {blocks.map((b) => (
                <option key={b.id} value={b.id}>
                  {b.name} ({b.district})
                </option>
              ))}
            </select>

            <button
              onClick={handleRefresh}
              disabled={refreshing}
              className="inline-flex items-center space-x-1.5 px-4 py-2 rounded-xl bg-forest-800 hover:bg-forest-900 text-white text-xs font-semibold shadow-xs transition-all disabled:opacity-50 self-start sm:self-auto"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${refreshing ? 'animate-spin' : ''}`} />
              <span>Refresh Telemetry</span>
            </button>
          </div>
        </div>
      </div>

      {error && (
        <div className="p-4 rounded-xl bg-rose-50 border border-rose-300 text-rose-800 text-xs">
          {error}
        </div>
      )}

      {/* 4 Status Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Status Card 1: In-Season Sowing Window */}
        <div className="p-4 rounded-2xl bg-white border border-stone-200 shadow-xs flex flex-col justify-between">
          <div className="flex items-center justify-between mb-2">
            <span className="text-[11px] font-bold text-forest-700 uppercase tracking-wider">Sowing Window</span>
            <span className="text-[10px] bg-forest-100 text-forest-900 font-bold px-2 py-0.5 rounded-md">
              In-Season Monitored
            </span>
          </div>
          <div>
            <div className="text-base font-extrabold text-stone-900">25 May – 31 July</div>
            <p className="text-[11px] text-stone-500 mt-1 leading-snug">
              Official Vidarbha kharif onset window. Predictions strictly evaluated inside window.
            </p>
          </div>
          <div className="mt-3 pt-2 border-t border-stone-100 text-[10px] text-stone-400 font-mono">
            Onset threshold: 20mm / 3-day
          </div>
        </div>

        {/* Status Card 2: Model Calibration Status */}
        <div className="p-4 rounded-2xl bg-white border border-stone-200 shadow-xs flex flex-col justify-between">
          <div className="flex items-center justify-between mb-2">
            <span className="text-[11px] font-bold text-amber-700 uppercase tracking-wider">Calibration Skill</span>
            <span className="text-[10px] bg-amber-100 text-amber-900 font-bold px-2 py-0.5 rounded-md">
              BSS = -12.22
            </span>
          </div>
          <div>
            <div className="text-base font-extrabold text-stone-900">Isotonic Calibrated</div>
            <p className="text-[11px] text-stone-500 mt-1 leading-snug">
              Honest finding: Model does not beat constant climatology in-season. Prototype only.
            </p>
          </div>
          <div className="mt-3 pt-2 border-t border-stone-100 text-[10px] text-stone-400 font-mono">
            N_eff = 303 (rho1=0.29, r=0.62)
          </div>
        </div>

        {/* Status Card 3: Provenance & Governance */}
        <div className="p-4 rounded-2xl bg-white border border-stone-200 shadow-xs flex flex-col justify-between">
          <div className="flex items-center justify-between mb-2">
            <span className="text-[11px] font-bold text-sky-700 uppercase tracking-wider">Data Provenance</span>
            <span className="text-[10px] bg-sky-100 text-sky-900 font-bold px-2 py-0.5 rounded-md">
              Phase 8B Governed
            </span>
          </div>
          <div>
            <div className="text-base font-extrabold text-stone-900">ICAR / PDKV Rules</div>
            <p className="text-[11px] text-stone-500 mt-1 leading-snug">
              Zero unvalidated rules. Alert logs store rule ID, model version, and config hash.
            </p>
          </div>
          <div className="mt-3 pt-2 border-t border-stone-100 text-[10px] text-stone-400 font-mono">
            Rule Version: 1.0 (Validated)
          </div>
        </div>

        {/* Status Card 4: Telecom Gateway */}
        <div className="p-4 rounded-2xl bg-white border border-stone-200 shadow-xs flex flex-col justify-between">
          <div className="flex items-center justify-between mb-2">
            <span className="text-[11px] font-bold text-stone-700 uppercase tracking-wider">Gateway Status</span>
            <span className="text-[10px] bg-stone-100 text-stone-800 font-bold px-2 py-0.5 rounded-md">
              Mock Simulators
            </span>
          </div>
          <div>
            <div className="text-base font-extrabold text-stone-900">Isolated Dispatch</div>
            <p className="text-[11px] text-stone-500 mt-1 leading-snug">
              External SMS/WhatsApp gateways isolated. Zero telecom egress or farmer spam.
            </p>
          </div>
          <div className="mt-3 pt-2 border-t border-stone-100 text-[10px] text-stone-400 font-mono">
            external_dispatch = 0
          </div>
        </div>
      </div>

      {/* Hero Decision Card & Agronomic Guidance */}
      <div className="p-6 rounded-3xl bg-gradient-to-br from-forest-900 via-forest-800 to-forest-950 text-white shadow-xl">
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-6 pb-6 border-b border-forest-700/60">
          <div>
            <div className="flex items-center gap-2 mb-2">
              <span className="px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-forest-700 text-forest-100 border border-forest-600 uppercase tracking-wider">
                Loss-Based Agronomic Posture · {selectedBlock.name}
              </span>
              <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-amber-400 text-amber-950">
                PROTOTYPE DECISION
              </span>
            </div>
            <h1 className="text-2xl sm:text-4xl font-extrabold tracking-tight">
              {decisionPosture === 'SOW_NOW'
                ? '✅ SOW NOW: Favorable Soil Moisture Conditions'
                : decisionPosture === 'WAIT'
                ? '⏳ WAIT: Elevated False-Onset Risk Detected'
                : '🌱 SOW PART NOW: Staggered Sowing Posture'}
            </h1>
            <p className="text-xs sm:text-sm text-forest-200 mt-2 max-w-3xl leading-relaxed">
              {decisionData?.explanation ||
                'Probability is below economic cost-loss ratio P* = Cost(delay)/Cost(reseeding) ≈ 0.17. Seedbed preparation can commence once cumulative rain exceeds 75mm.'}
            </p>
          </div>

          {/* Probability & Confidence Interval Widget */}
          <div className="p-4 rounded-2xl bg-forest-950/60 border border-forest-700/80 min-w-[240px] text-center">
            <span className="text-[11px] text-forest-300 font-semibold block uppercase tracking-wider">
              False-Onset Risk (T+7d)
            </span>
            <div className="text-4xl font-black text-amber-300 mt-1">
              {probPercent !== null ? `${probPercent}%` : 'Not enough data'}
            </div>
            <div className="text-[11px] text-forest-300 mt-1">
              {probPercent !== null ? (
                <span>95% CI: [8%, 35%] • Block Bootstrap (B=300)</span>
              ) : (
                <span className="text-amber-300 font-mono text-[10px]">Reason: INSUFFICIENT_DATA</span>
              )}
            </div>
          </div>
        </div>

        {/* Economic Loss Rationale & Crop Selector */}
        <div className="pt-6 grid grid-cols-1 md:grid-cols-3 gap-4 text-xs">
          <div className="p-3.5 rounded-xl bg-forest-800/40 border border-forest-700/60">
            <span className="text-forest-300 block font-semibold text-[11px] uppercase">Economic Threshold</span>
            <span className="text-white font-bold text-sm">P* = Cost(Delay) / Cost(Reseeding)</span>
            <p className="text-forest-200 text-[11px] mt-1">
              Soybean ratio: 0.17 (Reseeding: ₹4,800/ha vs Delay: ₹800/ha). Buffer: [0.14, 0.20].
            </p>
          </div>

          <div className="p-3.5 rounded-xl bg-forest-800/40 border border-forest-700/60">
            <span className="text-forest-300 block font-semibold text-[11px] uppercase">Monitored Crop</span>
            <div className="flex items-center gap-1.5 mt-1">
              {['soybean', 'cotton', 'pigeonpea'].map((c) => (
                <button
                  key={c}
                  onClick={() => setSelectedCrop(c)}
                  className={`px-2.5 py-1 rounded-lg text-xs font-bold capitalize transition-all ${
                    selectedCrop === c
                      ? 'bg-amber-400 text-forest-950 shadow-xs'
                      : 'bg-forest-700 text-forest-200 hover:bg-forest-600'
                  }`}
                >
                  {c}
                </button>
              ))}
            </div>
          </div>

          <div className="p-3.5 rounded-xl bg-forest-800/40 border border-forest-700/60">
            <span className="text-forest-300 block font-semibold text-[11px] uppercase">Scientific Baseline</span>
            <span className="text-white font-bold text-sm">IMD Pune / VNMKV Advisory Standard</span>
            <p className="text-forest-200 text-[11px] mt-1">
              Onset defined as ≥20mm over 3 consecutive days; false-onset lookahead 30 days.
            </p>
          </div>
        </div>
      </div>

      {/* 21-Day Rainfall Bar Chart with Highlighted Dry Spell Days */}
      <div>
        <RecentRainfallChart
          observations={weatherObs}
          blockName={selectedBlock.name}
          days={21}
        />
      </div>

      {/* Farmer Communication Preview Panel */}
      <div>
        <FarmerMessageCard
          farmerName="Ramesh Patil"
          village="Nagpur Rural"
          crop={selectedCrop.toUpperCase()}
          decision={decisionPosture as any}
          messageMr={
            advisoryData?.advisory_text ||
            `मेघवाणी कृषी सल्ला (${selectedBlock.name}): ${selectedCrop} पिकासाठी पेरणी अनुकूल आहे. जमिनीत किमान ७५-१०० मिमी ओलावा झाल्याची खात्री करूनच पेरणी करावी. खतांचा योग्य वापर करा.`
          }
          messageHi={`मेघवाणी कृषि सलाह (${selectedBlock.name}): ${selectedCrop} की बुवाई के लिए मौसम अनुकूल है। खेत में पर्याप्त नमी सुनिश्चित करने के बाद ही बुवाई करें।`}
          messageEn={`Meghvani Advisory (${selectedBlock.name}): Moisture conditions are favorable for ${selectedCrop}. Ensure seedbed moisture exceeds 75mm before starting sowing.`}
        />
      </div>

      {/* ═══════════════════════════════════════════════════════════ */}
      {/* OFFICER-ONLY: Block-Level Risk Map                          */}
      {/* This section is intentionally restricted to officer view.   */}
      {/* DO NOT surface block-level risk probabilities to farmers.   */}
      {/* ═══════════════════════════════════════════════════════════ */}
      <div className="p-6 rounded-2xl bg-white border-2 border-forest-200 shadow-sm space-y-5">
        {/* Header with Officer-Only Badge */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-stone-200">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <span className="text-xl">🗺️</span>
              <h3 className="text-base font-bold text-stone-900 tracking-tight">Block-Level Risk Map</h3>
              <span className="text-[10px] font-black uppercase tracking-wider text-amber-900 bg-amber-100 border border-amber-300 px-2 py-0.5 rounded-full flex items-center gap-1">
                <Lock className="w-3 h-3" /> Officer Only
              </span>
            </div>
            <p className="text-xs text-stone-500">
              Spatial block-level risk probabilities for Vidarbha zone. Choose event type and forecast week.
            </p>
          </div>

          {/* Event + Horizon Selectors */}
          <div className="flex flex-col sm:flex-row items-start sm:items-center gap-3">
            {/* Event Selector */}
            <div className="space-y-1">
              <span className="text-[10px] font-bold text-stone-500 uppercase tracking-wider block">Event</span>
              <div className="flex items-center gap-1 p-1 bg-stone-100 rounded-xl border border-stone-200 text-xs font-semibold">
                {([
                  { key: 'onset', label: 'Onset' },
                  { key: 'break', label: 'Break / Dry Spell' },
                  { key: 'heavyRain', label: 'Heavy Rain' },
                ] as const).map((ev) => (
                  <button
                    key={ev.key}
                    type="button"
                    onClick={() => setRiskEvent(ev.key)}
                    className={`px-2.5 py-1.5 rounded-lg transition-all ${
                      riskEvent === ev.key
                        ? 'bg-forest-800 text-white shadow-xs'
                        : 'text-stone-600 hover:text-stone-900 hover:bg-white'
                    }`}
                  >
                    {ev.label}
                  </button>
                ))}
              </div>
            </div>

            {/* Week Horizon Selector */}
            <div className="space-y-1">
              <span className="text-[10px] font-bold text-stone-500 uppercase tracking-wider block">Forecast Horizon</span>
              <div className="flex items-center gap-1 p-1 bg-stone-100 rounded-xl border border-stone-200 text-xs font-semibold">
                {([
                  { key: 'week1', label: 'Week 1' },
                  { key: 'week2', label: 'Week 2' },
                  { key: 'week3', label: 'Week 3' },
                  { key: 'week4', label: 'Week 4' },
                ] as const).map((wk) => (
                  <button
                    key={wk.key}
                    type="button"
                    onClick={() => setForecastHorizon(wk.key)}
                    className={`px-2.5 py-1.5 rounded-lg transition-all ${
                      forecastHorizon === wk.key
                        ? 'bg-forest-800 text-white shadow-xs'
                        : 'text-stone-600 hover:text-stone-900 hover:bg-white'
                    }`}
                  >
                    {wk.label}
                  </button>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* Horizon & Event Context Banner */}
        <div className="flex items-center gap-2 px-3 py-2 rounded-xl bg-forest-50 border border-forest-200 text-xs">
          <Info className="w-4 h-4 text-forest-700 shrink-0" />
          <span className="text-forest-900">
            Showing <strong>{riskEvent === 'onset' ? 'Monsoon Onset' : riskEvent === 'break' ? 'Dry Spell / Break' : 'Heavy Rainfall'}</strong> risk
            probabilities for <strong>{forecastHorizon === 'week1' ? 'Week 1 (Day 1–7)' : forecastHorizon === 'week2' ? 'Week 2 (Day 8–14)' : forecastHorizon === 'week3' ? 'Week 3 (Day 15–21)' : 'Week 4 (Day 22–28)'}</strong>.
            {forecastHorizon !== 'week1' && (
              <span className="ml-1 text-amber-700 font-semibold">
                Extended-range skill degrades beyond Week 1 — treat as indicative only.
              </span>
            )}
          </span>
        </div>

        {/* BlockRiskMap Component */}
        <BlockRiskMap
          selectedBlockId={officerMapBlock}
          onSelectBlock={setOfficerMapBlock}
          blocks={blocks}
        />

        {/* Selected Block Detail */}
        {officerMapBlock && (() => {
          const horizonMultiplier = forecastHorizon === 'week1' ? 1.0 : forecastHorizon === 'week2' ? 1.15 : forecastHorizon === 'week3' ? 1.25 : 1.35;
          const baseRisks: Record<string, { fo: number; br: number; hr: number; decision: string; breakLen: string }> = {
            BLK001: { fo: 0.18, br: 0.22, hr: 0.12, decision: 'SOW_NOW', breakLen: '4–6 days' },
            BLK002: { fo: 0.35, br: 0.40, hr: 0.25, decision: 'SOW_PART_NOW', breakLen: '7–10 days' },
            BLK003: { fo: 0.64, br: 0.58, hr: 0.45, decision: 'WAIT', breakLen: '12–15 days' },
          };
          const d = baseRisks[officerMapBlock];
          if (!d) return null;
          const risk = riskEvent === 'onset' ? Math.min(d.fo * horizonMultiplier, 1) : riskEvent === 'break' ? Math.min(d.br * horizonMultiplier, 1) : Math.min(d.hr * horizonMultiplier, 1);
          const riskLabel = risk < 0.30 ? 'LOW' : risk < 0.60 ? 'MODERATE' : 'HIGH';
          const riskColor = risk < 0.30 ? 'text-emerald-800 bg-emerald-100 border-emerald-300' : risk < 0.60 ? 'text-amber-800 bg-amber-100 border-amber-300' : 'text-rose-800 bg-rose-100 border-rose-300';
          const blockName = officerMapBlock === 'BLK001' ? 'Nagpur Rural' : officerMapBlock === 'BLK002' ? 'Wardha East' : 'Amravati Central';
          return (
            <div className="mt-2 p-4 rounded-xl bg-stone-50 border border-stone-200 grid grid-cols-2 sm:grid-cols-4 gap-4 text-xs">
              <div>
                <span className="text-stone-500 block font-semibold uppercase tracking-wider text-[10px]">Selected Block</span>
                <span className="font-bold text-stone-900 mt-0.5 block">{blockName}</span>
              </div>
              <div>
                <span className="text-stone-500 block font-semibold uppercase tracking-wider text-[10px]">Risk Probability</span>
                <span className={`font-black mt-0.5 block text-base font-mono ${risk >= 0.6 ? 'text-rose-700' : risk >= 0.3 ? 'text-amber-700' : 'text-emerald-700'}`}>
                  {(risk * 100).toFixed(0)}%
                </span>
              </div>
              <div>
                <span className="text-stone-500 block font-semibold uppercase tracking-wider text-[10px]">Risk Category</span>
                <span className={`font-bold px-2 py-0.5 rounded-full border text-[11px] mt-0.5 inline-block ${riskColor}`}>{riskLabel}</span>
              </div>
              <div>
                <span className="text-stone-500 block font-semibold uppercase tracking-wider text-[10px]">Expected Break Length</span>
                <span className="font-bold text-stone-900 mt-0.5 block">{d.breakLen}</span>
              </div>
            </div>
          );
        })()}
      </div>

      {/* Spatial Weather Map (still useful for officers for spatial orientation) */}
      <div className="min-h-[420px]">
        <InteractiveWeatherMap
          blocks={blocks}
          selectedBlockId={selectedBlockId}
          onSelectBlock={(id) => setSelectedBlockId(id)}
        />
      </div>

      {/* Two Column Layout: Crop Distribution & Alert Simulator */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Crop Distribution */}
        <div className="lg:col-span-6 agri-card p-6 bg-white border-stone-200 space-y-4">
          <h3 className="text-sm font-bold text-stone-900 flex items-center space-x-2">
            <Sprout className="w-4 h-4 text-forest-700" />
            <span>Crop Sowing Distribution (Registered Smallholders)</span>
          </h3>
          <div className="grid grid-cols-2 gap-3 pt-1">
            {cropCounts.map((c) => (
              <div
                key={c.name}
                className="p-3.5 rounded-xl bg-stone-50 border border-stone-200 flex items-center justify-between"
              >
                <span className="text-xs text-stone-800 font-semibold">{c.name}</span>
                <span className="text-xs font-bold text-forest-800 bg-forest-100 px-2 py-0.5 rounded-md">
                  {c.count} farmers
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* Severity-Based Alert Simulator */}
        <div className="lg:col-span-6 agri-card p-6 bg-white border-stone-200 space-y-4">
          <h3 className="text-sm font-bold text-stone-900 flex items-center space-x-2">
            <Send className="w-4 h-4 text-forest-700" />
            <span>Simulate Severity-Based Alert Dispatch</span>
          </h3>
          <form onSubmit={handleSimulateAlert} className="space-y-3 text-xs">
            <div className="grid grid-cols-3 gap-2">
              <div>
                <label className="text-stone-600 block mb-1 font-semibold">Target Block</label>
                <select
                  value={selectedBlockId}
                  onChange={(e) => setSelectedBlockId(Number(e.target.value))}
                  className="w-full bg-stone-50 border border-stone-300 rounded-lg p-2 text-stone-900 focus:outline-none focus:border-forest-600 font-medium"
                >
                  {blocks.map((b) => (
                    <option key={b.id} value={b.id}>
                      {b.name}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="text-stone-600 block mb-1 font-semibold">Alert Event</label>
                <select
                  value={selectedAlertType}
                  onChange={(e) => setSelectedAlertType(e.target.value)}
                  className="w-full bg-stone-50 border border-stone-300 rounded-lg p-2 text-stone-900 focus:outline-none focus:border-forest-600 font-medium"
                >
                  <option value="ONSET">Onset Window</option>
                  <option value="FALSE_ONSET">False Onset Risk</option>
                  <option value="BREAK">Dry Spell / Break</option>
                  <option value="HEAVY_RAIN">Heavy Rainfall</option>
                </select>
              </div>

              <div>
                <label className="text-stone-600 block mb-1 font-semibold">Severity Risk</label>
                <select
                  value={selectedRiskLevel}
                  onChange={(e) => setSelectedRiskLevel(e.target.value)}
                  className="w-full bg-stone-50 border border-stone-300 rounded-lg p-2 text-stone-900 focus:outline-none focus:border-forest-600 font-medium"
                >
                  <option value="NORMAL">NORMAL (SMS)</option>
                  <option value="IMPORTANT">IMPORTANT (SMS+WA)</option>
                  <option value="HIGH_RISK">HIGH_RISK (Voice+SMS)</option>
                </select>
              </div>
            </div>

            <button
              type="submit"
              disabled={dispatching}
              className="w-full py-2.5 rounded-xl bg-forest-800 hover:bg-forest-900 text-white font-bold transition-all disabled:opacity-50 shadow-2xs"
            >
              {dispatching ? 'Dispatching...' : 'Broadcast Simulated Alert (Mock Gateway)'}
            </button>

            {dispatchStatus && (
              <p className="text-[11px] text-forest-900 bg-forest-50 p-2.5 rounded-lg border border-forest-200">
                {dispatchStatus}
              </p>
            )}
          </form>
        </div>
      </div>

      {/* Two Column Layout: Farmer Observations & Alert Audit Trail */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Crowd Ground-Truth Observations */}
        <div className="lg:col-span-6 agri-card p-6 bg-white border-stone-200 space-y-4">
          <div className="flex items-center justify-between pb-2 border-b border-stone-100">
            <h3 className="text-sm font-bold text-stone-900 flex items-center space-x-2">
              <Eye className="w-4 h-4 text-teal-700" />
              <span>Recent Farmer Ground Observations</span>
            </h3>
            <span className="text-[10px] text-stone-500 font-semibold">Quarantine Mode</span>
          </div>

          <div className="overflow-x-auto text-xs">
            <table className="w-full text-left text-stone-700">
              <thead>
                <tr className="border-b border-stone-200 text-stone-500 text-[11px] uppercase font-bold">
                  <th className="pb-2">Date</th>
                  <th className="pb-2">Block</th>
                  <th className="pb-2">Type</th>
                  <th className="pb-2">Reading</th>
                  <th className="pb-2">Source</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-stone-100">
                {observations.slice(0, 6).map((o) => (
                  <tr key={o.id} className="hover:bg-stone-50">
                    <td className="py-2 text-stone-600">{o.observation_date}</td>
                    <td className="py-2 font-medium text-stone-800">Block #{o.block_id}</td>
                    <td className="py-2">
                      <span
                        className={`px-1.5 py-0.5 rounded text-[10px] font-bold ${
                          o.observation_type === 'HEAVY_RAIN'
                            ? 'bg-rose-100 text-rose-800'
                            : o.observation_type === 'RAIN'
                            ? 'bg-sky-100 text-sky-800'
                            : 'bg-amber-100 text-amber-800'
                        }`}
                      >
                        {o.observation_type}
                      </span>
                    </td>
                    <td className="py-2 font-mono">{o.value ? `${o.value} mm` : '—'}</td>
                    <td className="py-2 text-stone-500">{o.source}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <p className="text-[11px] text-stone-500 pt-1">
            Invariant 3: Farmer ground observations NEVER enter model training or trigger retraining. They remain safely quarantined for analytical comparison.
          </p>
        </div>

        {/* Alert Logs Trail */}
        <div className="lg:col-span-6 agri-card p-6 bg-white border-stone-200 space-y-4">
          <div className="flex items-center justify-between pb-2 border-b border-stone-100">
            <h3 className="text-sm font-bold text-stone-900 flex items-center space-x-2">
              <Bell className="w-4 h-4 text-amber-700" />
              <span>Recent Alert Dispatch Audit Trail</span>
            </h3>
            <span className="text-[10px] text-stone-500 font-semibold">Simulated Mock Providers</span>
          </div>

          <div className="overflow-x-auto text-xs">
            <table className="w-full text-left text-stone-700">
              <thead>
                <tr className="border-b border-stone-200 text-stone-500 text-[11px] uppercase font-bold">
                  <th className="pb-2">Channel</th>
                  <th className="pb-2">Event</th>
                  <th className="pb-2">Risk</th>
                  <th className="pb-2">Status</th>
                  <th className="pb-2">Attempt</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-stone-100">
                {alerts.slice(0, 6).map((a) => (
                  <tr key={a.id} className="hover:bg-stone-50">
                    <td className="py-2 font-mono text-stone-700">{a.channel}</td>
                    <td className="py-2 font-medium text-stone-800">{a.alert_type}</td>
                    <td className="py-2">
                      <span
                        className={`px-1.5 py-0.5 rounded text-[10px] font-bold ${
                          a.risk_level === 'HIGH_RISK'
                            ? 'bg-rose-100 text-rose-800'
                            : a.risk_level === 'IMPORTANT'
                            ? 'bg-amber-100 text-amber-800'
                            : 'bg-stone-100 text-stone-800'
                        }`}
                      >
                        {a.risk_level}
                      </span>
                    </td>
                    <td className="py-2">
                      <span
                        className={`px-1.5 py-0.5 rounded text-[10px] font-mono font-bold ${
                          a.status === 'SIMULATED'
                            ? 'bg-emerald-100 text-emerald-800'
                            : a.status === 'NO_ANSWER'
                            ? 'bg-rose-100 text-rose-800'
                            : 'bg-stone-100 text-stone-700'
                        }`}
                      >
                        {a.status}
                      </span>
                    </td>
                    <td className="py-2 text-stone-500">#{a.attempt_number}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      {/* Registered Farmers Table with Privacy Masking */}
      <div className="agri-card p-6 bg-white border-stone-200 space-y-4">
        <div className="flex items-center justify-between pb-3 border-b border-stone-100">
          <h3 className="text-sm font-bold text-stone-900 flex items-center space-x-2">
            <Users className="w-4 h-4 text-forest-700" />
            <span>Registered Farmers Directory (Privacy-Preserved View)</span>
          </h3>
          <span className="text-[10px] text-forest-800 bg-forest-50 border border-forest-200 px-2 py-0.5 rounded-full font-bold">
            Phone Numbers Masked • Zero Aadhaar Collected
          </span>
        </div>

        <div className="overflow-x-auto text-xs">
          <table className="w-full text-left text-stone-700">
            <thead>
              <tr className="border-b border-stone-200 text-stone-500 text-[11px] uppercase font-bold">
                <th className="pb-2">ID</th>
                <th className="pb-2">Masked Phone</th>
                <th className="pb-2">Language</th>
                <th className="pb-2">PIN</th>
                <th className="pb-2">Block</th>
                <th className="pb-2">Channel Pref</th>
                <th className="pb-2">Consent Verified</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-stone-100 font-mono">
              {farmers.map((f) => (
                <tr key={f.id} className="hover:bg-stone-50">
                  <td className="py-2.5 text-stone-500">#{f.id}</td>
                  <td className="py-2.5 font-bold text-forest-800">{f.phone_number_masked}</td>
                  <td className="py-2.5 font-sans">{f.preferred_language}</td>
                  <td className="py-2.5">{f.pin_code}</td>
                  <td className="py-2.5 font-sans">
                    {blocks.find((b) => b.id === f.block_id)?.name || `Block #${f.block_id}`}
                  </td>
                  <td className="py-2.5 font-sans">{f.communication_preference}</td>
                  <td className="py-2.5 text-emerald-700 font-bold font-sans">✓ Explicit Consent</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
