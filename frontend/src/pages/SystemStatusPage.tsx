import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import { SystemHealth } from '../types';
import {
  Activity,
  CheckCircle2,
  AlertTriangle,
  Server,
  Database,
  Radio,
  Cpu,
  Layers,
  RefreshCw,
  ShieldCheck
} from 'lucide-react';
import { AgricultureMetricCard } from '../components/AgricultureMetricCard';

export const SystemStatusPage: React.FC = () => {
  const [health, setHealth] = useState<SystemHealth | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const checkHealth = async () => {
    try {
      setError(null);
      const res = await api.getHealth();
      setHealth(res);
    } catch (err: any) {
      setError(err.message || 'Failed to connect to backend service');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    checkHealth();
  }, []);

  const roadmapPhases = [
    { num: 'PHASE 1', title: 'Production-Ready Foundation', status: 'COMPLETED', desc: 'Architecture, DB schemas, state-machines, mock adapters, test suite, and officer/farmer shells.' },
    { num: 'PHASE 2', title: 'Historical Rainfall & Event Detection', status: 'COMPLETED', desc: 'IMD gridded data pipeline, historical onset/break ground truth labeling.' },
    { num: 'PHASE 3', title: 'Feature Engineering & Baseline Forecasting', status: 'COMPLETED', desc: 'Antecedent precipitation metrics, rolling statistics, chronological splits.' },
    { num: 'PHASE 4', title: 'Probabilistic ML Baseline', status: 'COMPLETED', desc: 'Logistic false onset baseline, evaluation integrity, Brier Score.' },
    { num: 'PHASE 5', title: 'Decision & Agronomic Rule Framework', status: 'COMPLETED', desc: 'Translating forecast probabilities into actionable sowing decisions for Soybean, Cotton, Tur.' },
    { num: 'PHASE 6', title: 'Communication Simulation & Feedback', status: 'COMPLETED', desc: 'Simulated multi-channel dispatch (SMS, WhatsApp, Voice) and farmer observation collection.' },
    { num: 'PHASE 7', title: 'Multi-Year IMD Data Integration', status: 'COMPLETED', desc: 'Ingestion of 2019–2024 IMD 0.25° daily rainfall across BLK001, BLK002, BLK003.' },
    { num: 'PHASE 8A', title: 'Probabilistic Calibration & Rolling Evaluation', status: 'COMPLETED', desc: 'Platt scaling, guarded Isotonic regression, forward-chaining rolling origin.' },
  ];

  return (
    <div className="space-y-8 pb-12">
      {/* Header */}
      <div className="agri-card p-6 bg-white border-stone-200">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <div className="flex items-center space-x-2">
              <Activity className="w-6 h-6 text-forest-700" />
              <h2 className="text-xl sm:text-2xl font-bold text-stone-900 tracking-tight">
                Meghvani Subsystem Health & Architecture Status
              </h2>
            </div>
            <p className="text-xs text-stone-600 mt-1 max-w-2xl leading-relaxed">
              Real-time API health, database telemetry, provider abstraction status, and SIH roadmap milestones.
            </p>
          </div>

          <button
            onClick={checkHealth}
            className="inline-flex items-center space-x-1.5 px-4 py-2 rounded-xl bg-forest-800 hover:bg-forest-900 text-white text-xs font-bold shadow-xs transition-all self-start sm:self-auto"
          >
            <RefreshCw className="w-3.5 h-3.5" />
            <span>Ping API</span>
          </button>
        </div>
      </div>

      {error && (
        <div className="p-4 rounded-xl bg-rose-50 border border-rose-300 text-rose-800 text-xs">
          {error}
        </div>
      )}

      {/* Subsystem Health Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Backend API */}
        <div className="agri-card p-6 bg-white border-stone-200 space-y-3">
          <div className="flex items-center justify-between pb-2 border-b border-stone-100">
            <span className="font-bold text-stone-900 text-sm flex items-center space-x-2">
              <Server className="w-4 h-4 text-forest-700" />
              <span>FastAPI Backend Service</span>
            </span>
            <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-emerald-100 text-emerald-800 border border-emerald-300">
              {health?.status === 'healthy' ? 'ONLINE' : 'CHECKING'}
            </span>
          </div>
          <div className="text-xs space-y-1.5 text-stone-600">
            <p>Version: <span className="text-stone-900 font-mono font-semibold">{health?.version || '1.0.0-phase8a'}</span></p>
            <p>Environment: <span className="text-stone-900 font-mono font-semibold">{health?.environment || 'development'}</span></p>
            <p>API Endpoint: <span className="text-forest-800 font-mono font-bold">/api</span></p>
          </div>
        </div>

        {/* Database */}
        <div className="agri-card p-6 bg-white border-stone-200 space-y-3">
          <div className="flex items-center justify-between pb-2 border-b border-stone-100">
            <span className="font-bold text-stone-900 text-sm flex items-center space-x-2">
              <Database className="w-4 h-4 text-forest-700" />
              <span>Database Layer</span>
            </span>
            <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-emerald-100 text-emerald-800 border border-emerald-300">
              CONNECTED
            </span>
          </div>
          <div className="text-xs space-y-1.5 text-stone-600">
            <p>Driver: <span className="text-stone-900 font-mono font-semibold">SQLite (Local Dev)</span></p>
            <p>Schema: <span className="text-stone-900">PostGIS / PostgreSQL Ready</span></p>
            <p>Tables: <span className="text-forest-800 font-mono font-semibold">Farmers, Blocks, Observations, Alerts</span></p>
          </div>
        </div>

        {/* Communication Providers */}
        <div className="agri-card p-6 bg-white border-stone-200 space-y-3">
          <div className="flex items-center justify-between pb-2 border-b border-stone-100">
            <span className="font-bold text-stone-900 text-sm flex items-center space-x-2">
              <Radio className="w-4 h-4 text-forest-700" />
              <span>Communication Layer</span>
            </span>
            <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-amber-100 text-amber-800 border border-amber-300">
              MOCK SIMULATED
            </span>
          </div>
          <div className="text-xs space-y-1.5 text-stone-600">
            <p>SMS / WhatsApp: <span className="text-stone-900 font-mono font-semibold">Mock Adapter</span></p>
            <p>Voice / IVR: <span className="text-stone-900 font-mono font-semibold">Simulated with Fallback</span></p>
            <p>Live Dispatch: <span className="text-emerald-700 font-mono font-bold">Quarantined (Zero Spend)</span></p>
          </div>
        </div>
      </div>

      {/* Engineering Disclaimers Banner */}
      <div className="p-5 rounded-2xl bg-amber-50 border border-amber-200 text-amber-900 space-y-2 text-xs">
        <h4 className="font-bold flex items-center space-x-2 text-sm text-amber-950">
          <AlertTriangle className="w-4 h-4 shrink-0 text-amber-700" />
          <span>SIH 2026 Integrity Declarations & Operational Boundary</span>
        </h4>
        <ul className="list-disc list-inside space-y-1 text-amber-900 pl-1">
          <li><strong>Research Benchmark:</strong> All forecast metrics and calibration curves are generated for SIH scientific validation (<code>is_operational = false</code>).</li>
          <li><strong>No Real Telecom Dispatch:</strong> Notifications are routed to mock adapters and logged to SQLite audit tables.</li>
          <li><strong>Ground-Truth Data Isolation:</strong> 2019–2024 IMD 0.25° daily gridded rainfall dataset is verified and held separately from farmer crowd feedback.</li>
        </ul>
      </div>

      {/* Master Hackathon Progression Roadmap */}
      <div className="agri-card p-6 bg-white border-stone-200 space-y-4">
        <div className="flex items-center justify-between pb-2 border-b border-stone-100">
          <h3 className="text-sm font-bold text-stone-900 flex items-center space-x-2">
            <Layers className="w-4 h-4 text-forest-700" />
            <span>Meghvani Engineering Milestones Roadmap</span>
          </h3>
          <span className="text-[10px] text-stone-500 font-semibold">Step-by-Step Architecture</span>
        </div>

        <div className="overflow-x-auto text-xs">
          <table className="w-full text-left text-stone-700">
            <thead>
              <tr className="border-b border-stone-200 text-stone-500 text-[11px] uppercase font-bold">
                <th className="pb-2 w-28">Phase</th>
                <th className="pb-2 w-72">Focus Area</th>
                <th className="pb-2 w-44">Status</th>
                <th className="pb-2">Description</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-stone-100">
              {roadmapPhases.map((p) => (
                <tr key={p.num} className="hover:bg-stone-50">
                  <td className="py-2.5 font-mono text-forest-800 font-bold">{p.num}</td>
                  <td className="py-2.5 font-semibold text-stone-900">{p.title}</td>
                  <td className="py-2.5">
                    <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-emerald-100 text-emerald-800 border border-emerald-300">
                      {p.status}
                    </span>
                  </td>
                  <td className="py-2.5 text-stone-600">{p.desc}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
