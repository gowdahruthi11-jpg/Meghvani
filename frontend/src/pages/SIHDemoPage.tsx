import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import { DemoRunResult, DemoStatusResult } from '../types';
import {
  Play,
  RotateCcw,
  CheckCircle2,
  AlertTriangle,
  ShieldAlert,
  Database,
  Users,
  BrainCircuit,
  BookOpen,
  MessageSquare,
  Bell,
  Activity,
  ArrowRight,
  Info,
  Check,
  Smartphone,
  FileSpreadsheet,
  Sprout,
  ShieldCheck
} from 'lucide-react';
import { DemoTimeline } from '../components/DemoTimeline';

export const SIHDemoPage: React.FC = () => {
  const [loading, setLoading] = useState<boolean>(false);
  const [resetting, setResetting] = useState<boolean>(false);
  const [demoStatus, setDemoStatus] = useState<DemoStatusResult | null>(null);
  const [demoResult, setDemoResult] = useState<DemoRunResult | null>(null);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [activeTimelineStep, setActiveTimelineStep] = useState<string>('decision');

  // Scenario configuration
  const [selectedProb, setSelectedProb] = useState<number>(0.20);
  const [selectedLang, setSelectedLang] = useState<string>('mr');
  const [selectedObsType, setSelectedObsType] = useState<string>('RAIN');

  const fetchStatus = async () => {
    try {
      const st = await api.getDemoStatus();
      setDemoStatus(st);
    } catch (err: any) {
      console.error('Failed to fetch demo status:', err);
    }
  };

  useEffect(() => {
    fetchStatus();
  }, []);

  const handleRunDemo = async () => {
    setLoading(true);
    setErrorMsg(null);
    try {
      const res = await api.runDemo({
        probability: selectedProb,
        language: selectedLang,
        observation_type: selectedObsType,
      });
      setDemoResult(res);
      await fetchStatus();
    } catch (err: any) {
      setErrorMsg(err.message || 'Demo execution failed.');
    } finally {
      setLoading(false);
    }
  };

  const handleResetDemo = async () => {
    setResetting(true);
    try {
      await api.resetDemo();
      setDemoResult(null);
      await fetchStatus();
    } catch (err: any) {
      setErrorMsg(err.message || 'Reset failed.');
    } finally {
      setResetting(false);
    }
  };

  return (
    <div className="space-y-8 pb-12">
      {/* 1. Header Banner */}
      <section className="agri-card p-6 sm:p-8 bg-gradient-to-r from-forest-900 via-forest-800 to-leaf-800 text-white relative overflow-hidden shadow-md">
        <div className="relative z-10 flex flex-col lg:flex-row lg:items-center lg:justify-between gap-6">
          <div className="max-w-3xl space-y-3">
            <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-white/10 border border-white/20 text-leaf-200 text-xs font-semibold">
              <span>🌾</span>
              <span>Smart India Hackathon 2026 Presentation Story</span>
            </div>

            <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
              Meghvani End-to-End System Demonstration
            </h1>

            <p className="text-xs sm:text-sm text-leaf-100 leading-relaxed">
              Demonstrates complete workflow connectivity across all 10 architectural stages:
              Farmer Profile &rarr; Forecast Replay &rarr; Prototype Decision &rarr; Validated Agronomic Rule &rarr;
              Vernacular Message &rarr; Mock Alert Dispatch &rarr; Qualitative Feedback &rarr; Observation Validation &rarr; Officer Audit.
            </p>
          </div>

          {/* Safety & Protocol Badges */}
          <div className="flex flex-wrap gap-2 lg:flex-col lg:items-end shrink-0">
            <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold bg-amber-100 text-amber-900 border border-amber-300">
              <ShieldAlert className="w-3.5 h-3.5 mr-1" />
              Historical Replay / Simulation Only
            </span>
            <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold bg-sky-100 text-sky-900 border border-sky-300">
              <Database className="w-3.5 h-3.5 mr-1" />
              is_operational = false
            </span>
            <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold bg-stone-100 text-stone-800 border border-stone-300">
              external_dispatch = false
            </span>
          </div>
        </div>

        {/* System Status Indicators (SIH Evaluation Panel) */}
        <div className="mt-8 pt-6 border-t border-white/15">
          <h2 className="text-[11px] font-bold text-leaf-200 uppercase tracking-wider mb-3">
            Subsystem Status Indicators (SIH Evaluation Matrix)
          </h2>
          <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-7 gap-2.5 text-xs">
            <div className="bg-white/10 backdrop-blur-xs p-2.5 rounded-xl border border-white/15">
              <p className="text-leaf-200 text-[10px] uppercase font-semibold">Forecast</p>
              <p className="mt-0.5 font-bold text-white">{demoStatus?.status_indicators?.forecast || 'DEMO REPLAY'}</p>
            </div>
            <div className="bg-white/10 backdrop-blur-xs p-2.5 rounded-xl border border-white/15">
              <p className="text-leaf-200 text-[10px] uppercase font-semibold">Decision</p>
              <p className="mt-0.5 font-bold text-white">{demoStatus?.status_indicators?.decision || 'PROTOTYPE'}</p>
            </div>
            <div className="bg-white/10 backdrop-blur-xs p-2.5 rounded-xl border border-white/15">
              <p className="text-leaf-200 text-[10px] uppercase font-semibold">Agronomic Rule</p>
              <p className="mt-0.5 font-bold text-white">{demoStatus?.status_indicators?.agronomic_rule || 'SOURCE-REGISTERED'}</p>
            </div>
            <div className="bg-white/10 backdrop-blur-xs p-2.5 rounded-xl border border-white/15">
              <p className="text-leaf-200 text-[10px] uppercase font-semibold">Communication</p>
              <p className="mt-0.5 font-bold text-white">{demoStatus?.status_indicators?.communication || 'SIMULATED'}</p>
            </div>
            <div className="bg-white/10 backdrop-blur-xs p-2.5 rounded-xl border border-white/15">
              <p className="text-leaf-200 text-[10px] uppercase font-semibold">Feedback</p>
              <p className="mt-0.5 font-bold text-white">{demoStatus?.status_indicators?.feedback || 'RECORDED'}</p>
            </div>
            <div className="bg-white/10 backdrop-blur-xs p-2.5 rounded-xl border border-white/15">
              <p className="text-leaf-200 text-[10px] uppercase font-semibold">Validation</p>
              <p className="mt-0.5 font-bold text-white">{demoStatus?.status_indicators?.validation || 'COMPLETED'}</p>
            </div>
            <div className="bg-white/10 backdrop-blur-xs p-2.5 rounded-xl border border-white/15">
              <p className="text-leaf-200 text-[10px] uppercase font-semibold">Operational</p>
              <p className="mt-0.5 font-bold text-rose-200">{demoStatus?.status_indicators?.operational || 'NO'}</p>
            </div>
          </div>
        </div>
      </section>

      {/* 2. Visual Agricultural Story Timeline */}
      <section>
        <DemoTimeline
          currentStepId={activeTimelineStep}
          onSelectStep={setActiveTimelineStep}
        />
      </section>

      {/* 3. Interactive Scenario Controls */}
      <section className="agri-card p-6 bg-white border-stone-200">
        <div className="flex items-center justify-between pb-4 border-b border-stone-200">
          <div>
            <h2 className="text-base font-bold text-stone-900 flex items-center">
              <Activity className="w-4 h-4 mr-2 text-forest-700" />
              Scenario Configuration & Replay Controls
            </h2>
            <p className="text-xs text-stone-500 mt-0.5">
              Configure risk conditions, regional language, and farmer feedback to test cross-subsystem execution.
            </p>
          </div>
          <span className="text-xs font-semibold text-stone-600">Preset Scenarios</span>
        </div>

        <div className="mt-5 grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* Preset Risk Scenario */}
          <div>
            <label className="block text-xs font-bold text-stone-700 uppercase tracking-wide mb-2">
              1. Monsoon Risk Scenario Preset
            </label>
            <div className="space-y-2">
              <button
                type="button"
                onClick={() => setSelectedProb(0.20)}
                className={`w-full text-left px-3.5 py-2.5 rounded-xl border text-xs font-medium transition-all ${
                  selectedProb === 0.20
                    ? 'border-emerald-600 bg-emerald-50 text-emerald-950 font-bold shadow-2xs'
                    : 'border-stone-200 bg-stone-50 text-stone-700 hover:bg-white'
                }`}
              >
                <div className="font-bold flex items-center justify-between">
                  <span>Low Risk Onset (p = 0.20)</span>
                  <span className="badge-sow-now text-[10px] px-1.5 py-0.5 rounded">SOW NOW</span>
                </div>
                <div className="text-[11px] text-stone-600 mt-1">Triggers: Routine Sowing Advice via SMS</div>
              </button>

              <button
                type="button"
                onClick={() => setSelectedProb(0.45)}
                className={`w-full text-left px-3.5 py-2.5 rounded-xl border text-xs font-medium transition-all ${
                  selectedProb === 0.45
                    ? 'border-amber-600 bg-amber-50 text-amber-950 font-bold shadow-2xs'
                    : 'border-stone-200 bg-stone-50 text-stone-700 hover:bg-white'
                }`}
              >
                <div className="font-bold flex items-center justify-between">
                  <span>Moderate Risk (p = 0.45)</span>
                  <span className="badge-sow-part text-[10px] px-1.5 py-0.5 rounded">SOW PART</span>
                </div>
                <div className="text-[11px] text-stone-600 mt-1">Triggers: Staggered planting & WhatsApp</div>
              </button>

              <button
                type="button"
                onClick={() => setSelectedProb(0.70)}
                className={`w-full text-left px-3.5 py-2.5 rounded-xl border text-xs font-medium transition-all ${
                  selectedProb === 0.70
                    ? 'border-rose-600 bg-rose-50 text-rose-950 font-bold shadow-2xs'
                    : 'border-stone-200 bg-stone-50 text-stone-700 hover:bg-white'
                }`}
              >
                <div className="font-bold flex items-center justify-between">
                  <span>High Risk False Onset (p = 0.70)</span>
                  <span className="badge-wait text-[10px] px-1.5 py-0.5 rounded">WAIT</span>
                </div>
                <div className="text-[11px] text-stone-600 mt-1">Triggers: Urgent Voice IVR + SMS fallback</div>
              </button>
            </div>
          </div>

          {/* Regional Language Selection */}
          <div>
            <label className="block text-xs font-bold text-stone-700 uppercase tracking-wide mb-2">
              2. Farmer Advisory Language
            </label>
            <div className="space-y-2">
              <button
                type="button"
                onClick={() => setSelectedLang('mr')}
                className={`w-full text-left px-3.5 py-2.5 rounded-xl border text-xs font-medium transition-all ${
                  selectedLang === 'mr'
                    ? 'border-forest-600 bg-forest-50 text-forest-950 font-bold shadow-2xs'
                    : 'border-stone-200 bg-stone-50 text-stone-700 hover:bg-white'
                }`}
              >
                <div className="font-bold">मराठी (Marathi)</div>
                <div className="text-[11px] text-stone-600 mt-0.5">Primary regional vernacular for Vidarbha</div>
              </button>

              <button
                type="button"
                onClick={() => setSelectedLang('hi')}
                className={`w-full text-left px-3.5 py-2.5 rounded-xl border text-xs font-medium transition-all ${
                  selectedLang === 'hi'
                    ? 'border-forest-600 bg-forest-50 text-forest-950 font-bold shadow-2xs'
                    : 'border-stone-200 bg-stone-50 text-stone-700 hover:bg-white'
                }`}
              >
                <div className="font-bold">हिंदी (Hindi)</div>
                <div className="text-[11px] text-stone-600 mt-0.5">National language translation</div>
              </button>

              <button
                type="button"
                onClick={() => setSelectedLang('en')}
                className={`w-full text-left px-3.5 py-2.5 rounded-xl border text-xs font-medium transition-all ${
                  selectedLang === 'en'
                    ? 'border-forest-600 bg-forest-50 text-forest-950 font-bold shadow-2xs'
                    : 'border-stone-200 bg-stone-50 text-stone-700 hover:bg-white'
                }`}
              >
                <div className="font-bold">English</div>
                <div className="text-[11px] text-stone-600 mt-0.5">Administrative & research standard</div>
              </button>
            </div>
          </div>

          {/* Farmer Observation Selection */}
          <div>
            <label className="block text-xs font-bold text-stone-700 uppercase tracking-wide mb-2">
              3. Farmer Ground-Truth Feedback
            </label>
            <div className="space-y-2">
              <button
                type="button"
                onClick={() => setSelectedObsType('RAIN')}
                className={`w-full text-left px-3.5 py-2.5 rounded-xl border text-xs font-medium transition-all ${
                  selectedObsType === 'RAIN'
                    ? 'border-sky-600 bg-sky-50 text-sky-950 font-bold shadow-2xs'
                    : 'border-stone-200 bg-stone-50 text-stone-700 hover:bg-white'
                }`}
              >
                <div className="font-bold">🌧 Rain Received (पाऊस)</div>
                <div className="text-[11px] text-stone-600 mt-0.5">Compares against observed rainfall &gt; 0 mm</div>
              </button>

              <button
                type="button"
                onClick={() => setSelectedObsType('DRY')}
                className={`w-full text-left px-3.5 py-2.5 rounded-xl border text-xs font-medium transition-all ${
                  selectedObsType === 'DRY'
                    ? 'border-amber-600 bg-amber-50 text-amber-950 font-bold shadow-2xs'
                    : 'border-stone-200 bg-stone-50 text-stone-700 hover:bg-white'
                }`}
              >
                <div className="font-bold">☀️ Dry Spell (कोरडे)</div>
                <div className="text-[11px] text-stone-600 mt-0.5">Compares against dry ceiling (&le; 2.5 mm)</div>
              </button>

              <button
                type="button"
                onClick={() => setSelectedObsType('HEAVY_RAIN')}
                className={`w-full text-left px-3.5 py-2.5 rounded-xl border text-xs font-medium transition-all ${
                  selectedObsType === 'HEAVY_RAIN'
                    ? 'border-rose-600 bg-rose-50 text-rose-950 font-bold shadow-2xs'
                    : 'border-stone-200 bg-stone-50 text-stone-700 hover:bg-white'
                }`}
              >
                <div className="font-bold">⛈ Heavy Rain (मुसळधार पाऊस)</div>
                <div className="text-[11px] text-stone-600 mt-0.5">Compares against benchmark (&ge; 64.5 mm)</div>
              </button>
            </div>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="mt-6 pt-5 border-t border-stone-200 flex flex-wrap items-center justify-between gap-4">
          <div className="flex items-center space-x-3">
            <button
              onClick={handleRunDemo}
              disabled={loading}
              className="inline-flex items-center px-6 py-3 rounded-xl bg-forest-800 hover:bg-forest-900 text-white font-extrabold text-sm shadow-md hover:scale-[1.02] active:scale-[0.98] transition-all disabled:opacity-50"
            >
              <Play className={`w-4 h-4 mr-2 ${loading ? 'animate-spin' : 'fill-white'}`} />
              {loading ? 'Executing 10-Stage Pipeline...' : 'RUN END-TO-END DEMO'}
            </button>

            <button
              onClick={handleResetDemo}
              disabled={resetting}
              className="inline-flex items-center px-4 py-3 rounded-xl bg-stone-100 hover:bg-stone-200 text-stone-700 text-xs font-semibold border border-stone-300 transition-colors disabled:opacity-50"
            >
              <RotateCcw className={`w-3.5 h-3.5 mr-1.5 ${resetting ? 'animate-spin' : ''}`} />
              {resetting ? 'Resetting...' : 'Reset Demo Records'}
            </button>
          </div>

          <p className="text-xs text-stone-500">
            Target Unit: <strong>Nagpur Rural (BLK001) / Kalmeshwar</strong> (Crop: <strong>Soybean</strong>)
          </p>
        </div>

        {errorMsg && (
          <div className="mt-4 p-4 rounded-xl bg-rose-50 border border-rose-300 text-xs text-rose-800 flex items-start space-x-2">
            <AlertTriangle className="w-4 h-4 text-rose-600 shrink-0 mt-0.5" />
            <span>{errorMsg}</span>
          </div>
        )}
      </section>

      {/* 4. Execution Trace Cards */}
      {demoResult && (
        <section className="space-y-4">
          <div className="flex items-center justify-between pb-2 border-b border-stone-200">
            <h2 className="text-base font-bold text-stone-900 flex items-center">
              <CheckCircle2 className="w-5 h-5 text-emerald-600 mr-2" />
              Live Pipeline Execution Audit Trace (Run ID: {demoResult.demo_id})
            </h2>
            <span className="text-xs font-mono text-stone-500">{demoResult.timestamp}</span>
          </div>

          {/* Trace Cards Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 text-xs">
            {/* Stage 1: Farmer Profile */}
            <div className="agri-card p-4 space-y-2 border-stone-200">
              <div className="flex items-center justify-between text-stone-700 font-semibold border-b border-stone-100 pb-2">
                <span className="flex items-center font-bold">
                  <Users className="w-4 h-4 mr-1.5 text-forest-700" />
                  Stage 1: Farmer Profile & Consent
                </span>
                <span className="text-[10px] text-emerald-800 font-bold bg-emerald-100 px-2 py-0.5 rounded">PASSED</span>
              </div>
              <div className="space-y-1 text-stone-700">
                <p><strong>Farmer:</strong> Demo Farmer #{demoResult.stages['1_farmer'].farmer_id}</p>
                <p><strong>Phone (Masked):</strong> {demoResult.stages['1_farmer'].masked_phone}</p>
                <p><strong>Village / Block:</strong> {demoResult.stages['1_farmer'].village} / {demoResult.stages['1_farmer'].block}</p>
                <p><strong>Crop:</strong> {demoResult.stages['1_farmer'].crop}</p>
                <p className="text-forest-700 font-semibold">✓ Explicit Consent Active</p>
              </div>
            </div>

            {/* Stage 2: Forecast Replay */}
            <div className="agri-card p-4 space-y-2 border-stone-200">
              <div className="flex items-center justify-between text-stone-700 font-semibold border-b border-stone-100 pb-2">
                <span className="flex items-center font-bold">
                  <Activity className="w-4 h-4 mr-1.5 text-sky-700" />
                  Stage 2: Forecast Replay
                </span>
                <span className="text-[10px] text-sky-800 font-bold bg-sky-100 px-2 py-0.5 rounded">REPLAY</span>
              </div>
              <div className="space-y-1 text-stone-700">
                <p><strong>Target:</strong> False Onset 7-Day Window</p>
                <p><strong>Probability:</strong> <span className="font-bold text-sky-800">{demoResult.stages['2_forecast'].probability_pct}</span></p>
                <p><strong>Source / Mode:</strong> {demoResult.stages['2_forecast'].source} ({demoResult.stages['2_forecast'].mode})</p>
                <p className="text-stone-500 italic">Non-Operational Benchmark Replay</p>
              </div>
            </div>

            {/* Stage 3: Prototype Decision */}
            <div className="agri-card p-4 space-y-2 border-stone-200">
              <div className="flex items-center justify-between text-stone-700 font-semibold border-b border-stone-100 pb-2">
                <span className="flex items-center font-bold">
                  <BrainCircuit className="w-4 h-4 mr-1.5 text-emerald-700" />
                  Stage 3: Decision Engine
                </span>
                <span className="text-[10px] text-emerald-800 font-bold bg-emerald-100 px-2 py-0.5 rounded">EVALUATED</span>
              </div>
              <div className="space-y-1 text-stone-700">
                <p><strong>Decision:</strong> <span className="font-black text-emerald-800">{demoResult.stages['3_decision'].decision}</span></p>
                <p><strong>Engine Nature:</strong> {demoResult.stages['3_decision'].decision_engine_status}</p>
                <p className="text-[11px] text-stone-600 italic">{demoResult.stages['3_decision'].explanation}</p>
              </div>
            </div>

            {/* Stage 4: Validated Agronomic Rule */}
            <div className="agri-card p-4 space-y-2 border-stone-200">
              <div className="flex items-center justify-between text-stone-700 font-semibold border-b border-stone-100 pb-2">
                <span className="flex items-center font-bold">
                  <BookOpen className="w-4 h-4 mr-1.5 text-teal-700" />
                  Stage 4: Validated Agronomic Rule
                </span>
                <span className="text-[10px] text-teal-800 font-bold bg-teal-100 px-2 py-0.5 rounded">{demoResult.stages['4_advisory'].validation_status}</span>
              </div>
              <div className="space-y-1 text-stone-700">
                <p><strong>Rule ID:</strong> {demoResult.stages['4_advisory'].rule_id}</p>
                <p><strong>Source:</strong> {demoResult.stages['4_advisory'].source_institution}</p>
                <p><strong>Source Requirement:</strong> {demoResult.stages['4_advisory'].source_supported_condition}</p>
                <p><strong>Model Boundary:</strong> {demoResult.stages['4_advisory'].meghvani_prototype_condition}</p>
              </div>
            </div>

            {/* Stage 5: Vernacular Message */}
            <div className="agri-card p-4 space-y-2 border-stone-200">
              <div className="flex items-center justify-between text-stone-700 font-semibold border-b border-stone-100 pb-2">
                <span className="flex items-center font-bold">
                  <MessageSquare className="w-4 h-4 mr-1.5 text-amber-700" />
                  Stage 5: Vernacular Message
                </span>
                <span className="text-[10px] text-amber-800 font-bold bg-amber-100 px-2 py-0.5 rounded">GENERATED</span>
              </div>
              <div className="space-y-1 text-stone-700">
                <p><strong>Language:</strong> {demoResult.stages['5_message'].language_name}</p>
                <p><strong>Channel:</strong> {demoResult.stages['5_message'].channel}</p>
                <div className="bg-stone-50 p-2.5 rounded-lg border border-stone-200 text-[11px] text-stone-900 mt-1 whitespace-pre-line font-sans">
                  {demoResult.stages['5_message'].message_text}
                </div>
              </div>
            </div>

            {/* Stage 6 & 7: Simulated Communication & Log */}
            <div className="agri-card p-4 space-y-2 border-stone-200">
              <div className="flex items-center justify-between text-stone-700 font-semibold border-b border-stone-100 pb-2">
                <span className="flex items-center font-bold">
                  <Bell className="w-4 h-4 mr-1.5 text-indigo-700" />
                  Stage 6 &amp; 7: Simulated Dispatch &amp; Log
                </span>
                <span className="text-[10px] text-indigo-800 font-bold bg-indigo-100 px-2 py-0.5 rounded">{demoResult.stages['6_communication'].status}</span>
              </div>
              <div className="space-y-1 text-stone-700">
                <p><strong>Alert Log ID:</strong> #{demoResult.stages['6_communication'].alert_id}</p>
                <p><strong>Channel Plan:</strong> {demoResult.stages['6_communication'].channel_plan.join(', ')}</p>
                <p><strong>Mock Provider:</strong> {demoResult.stages['6_communication'].provider}</p>
                <p><strong>External Dispatch:</strong> <span className="text-emerald-700 font-bold">FALSE (Zero packets sent)</span></p>
              </div>
            </div>

            {/* Stage 8, 9 & 10: Farmer Observation, Validation & Officer Audit */}
            <div className="agri-card p-4 space-y-2 border-stone-200 md:col-span-2 lg:col-span-3">
              <div className="flex items-center justify-between text-stone-700 font-semibold border-b border-stone-100 pb-2">
                <span className="flex items-center font-bold">
                  <FileSpreadsheet className="w-4 h-4 mr-1.5 text-emerald-700" />
                  Stage 8, 9 &amp; 10: Farmer Observation, Analytical Validation &amp; Officer Audit
                </span>
                <span className="text-[10px] text-emerald-800 font-bold bg-emerald-100 px-2 py-0.5 rounded">
                  {demoResult.stages['7_observation'].validation_status}
                </span>
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 text-stone-700 pt-1">
                <div>
                  <p><strong>Observation ID:</strong> #{demoResult.stages['7_observation'].observation_id}</p>
                  <p><strong>Reported Event:</strong> {demoResult.stages['7_observation'].observation_type}</p>
                  <p><strong>Source:</strong> {demoResult.stages['7_observation'].source}</p>
                </div>
                <div>
                  <p><strong>Reference Rainfall:</strong> {demoResult.stages['7_observation'].reference_rainfall_mm} mm</p>
                  <p><strong>Validation Result:</strong> <span className="font-bold text-emerald-700">{demoResult.stages['7_observation'].validation_status}</span></p>
                  <p><strong>Automated Retraining:</strong> <span className="text-forest-800 font-bold">NO (Strict Invariant)</span></p>
                </div>
                <div>
                  <p><strong>Officer Audit Status:</strong> Verified Complete</p>
                  <p className="text-[11px] text-stone-600 italic">{demoResult.stages['7_observation'].comparison_notes}</p>
                </div>
              </div>
            </div>
          </div>
        </section>
      )}

      {/* 5. Scientific Boundary Notice */}
      <section className="p-4 rounded-xl bg-stone-100 border border-stone-200 text-xs text-stone-600 space-y-1">
        <p className="font-bold text-stone-800 flex items-center">
          <Info className="w-4 h-4 mr-1.5 text-forest-700" />
          SIH 2026 Evaluation Boundary &amp; Scientific Limitations
        </p>
        <p className="leading-relaxed">
          This demonstration proves software architecture integration and cross-module execution across the entire pipeline.
          It does <strong>not</strong> claim verified operational probability calibration or official government warning issuance.
          The underlying ML baseline is evaluated under Phase 8A rolling-origin forward-chaining records.
        </p>
      </section>
    </div>
  );
};
