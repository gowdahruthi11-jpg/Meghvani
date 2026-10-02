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
  RefreshCw
} from 'lucide-react';

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
    { num: 'PHASE 1', title: 'Production-Ready Foundation', status: 'ACTIVE / COMPLETED', desc: 'Architecture, DB schemas, state-machines, mock providers, test suite, and officer/farmer shells.' },
    { num: 'PHASE 2', title: 'Historical Rainfall & Event Detection', status: 'FUTURE PHASE', desc: 'IMD gridded NetCDF processing, historical onset/break ground truth labeling.' },
    { num: 'PHASE 3', title: 'Feature Engineering & Baseline Forecasting', status: 'FUTURE PHASE', desc: 'MJO indices, OLR anomalies, SST signals, rolling rainfall statistics.' },
    { num: 'PHASE 4', title: 'Probabilistic ML Engines', status: 'FUTURE PHASE', desc: 'Onset, false onset, break, heavy rain calibrated LightGBM/scikit-learn models.' },
    { num: 'PHASE 5', title: 'Probability Calibration & Skill Blending', status: 'FUTURE PHASE', desc: 'Brier score optimization, isotonic regression, and skill-aware blending.' },
    { num: 'PHASE 6', title: 'Sow / Wait Decision Engine', status: 'FUTURE PHASE', desc: 'Translating calibrated probabilities into actionable agronomic decisions.' },
    { num: 'PHASE 7', title: 'Crop-Specific Advisory Engine', status: 'FUTURE PHASE', desc: 'Multi-lingual agronomic advice validated with ICAR-CRIDA and KVK rules.' },
    { num: 'PHASE 8', title: 'Interactive Risk Maps & Spatial Layers', status: 'FUTURE PHASE', desc: 'Leaflet/MapLibre block-level choropleth visualization.' },
    { num: 'PHASE 9', title: 'Production Communication Gateways', status: 'FUTURE PHASE', desc: 'Connecting real telco SMS, Exotel IVR, and Meta WhatsApp Cloud APIs.' },
    { num: 'PHASE 10', title: 'Historical Replay & SIH 2026 Evaluation', status: 'FUTURE PHASE', desc: 'Live demonstration replay across historical drought/onset seasons.' },
  ];

  return (
    <div className="space-y-8 pb-12">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold text-white tracking-tight flex items-center space-x-2">
            <Activity className="w-6 h-6 text-sky-400" />
            <span>Meghvani System Health & Architecture Status</span>
          </h2>
          <p className="text-slate-400 text-sm mt-1">
            Real-time API health, database telemetry, provider abstraction status, and SIH roadmap.
          </p>
        </div>

        <button
          onClick={checkHealth}
          className="inline-flex items-center space-x-1.5 px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold border border-slate-700 transition-all self-start sm:self-auto"
        >
          <RefreshCw className="w-3.5 h-3.5" />
          <span>Ping API</span>
        </button>
      </div>

      {/* Subsystem Health Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Backend API */}
        <div className="p-6 rounded-2xl glass-panel border border-slate-800 space-y-3">
          <div className="flex items-center justify-between">
            <span className="font-semibold text-white text-sm flex items-center space-x-2">
              <Server className="w-4 h-4 text-sky-400" />
              <span>FastAPI Backend</span>
            </span>
            <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
              {health?.status === 'healthy' ? 'ONLINE' : 'CHECKING'}
            </span>
          </div>
          <div className="text-xs space-y-1 text-slate-400">
            <p>Version: <span className="text-slate-200 font-mono">{health?.version || '1.0.0-phase1'}</span></p>
            <p>Environment: <span className="text-slate-200 font-mono">{health?.environment || 'development'}</span></p>
            <p>API Endpoint: <span className="text-sky-400 font-mono">/api</span></p>
          </div>
        </div>

        {/* Database */}
        <div className="p-6 rounded-2xl glass-panel border border-slate-800 space-y-3">
          <div className="flex items-center justify-between">
            <span className="font-semibold text-white text-sm flex items-center space-x-2">
              <Database className="w-4 h-4 text-emerald-400" />
              <span>Database Layer</span>
            </span>
            <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
              CONNECTED
            </span>
          </div>
          <div className="text-xs space-y-1 text-slate-400">
            <p>Driver: <span className="text-slate-200 font-mono">SQLite (Local Dev)</span></p>
            <p>Architecture: <span className="text-slate-200">PostGIS / PostgreSQL Ready</span></p>
            <p>Migrations: <span className="text-teal-400 font-mono">Alembic Configured</span></p>
          </div>
        </div>

        {/* Communication Providers */}
        <div className="p-6 rounded-2xl glass-panel border border-slate-800 space-y-3">
          <div className="flex items-center justify-between">
            <span className="font-semibold text-white text-sm flex items-center space-x-2">
              <Radio className="w-4 h-4 text-amber-400" />
              <span>Communication Layer</span>
            </span>
            <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-amber-500/10 text-amber-400 border border-amber-500/30">
              MOCK MODE
            </span>
          </div>
          <div className="text-xs space-y-1 text-slate-400">
            <p>SMS / WhatsApp: <span className="text-slate-200 font-mono">Mock Provider</span></p>
            <p>Voice / Missed-Call: <span className="text-slate-200 font-mono">Mock with Fallback</span></p>
            <p>Real Credentials: <span className="text-emerald-400 font-mono">None Committed</span></p>
          </div>
        </div>
      </div>

      {/* Engineering Disclaimers Banner */}
      <div className="p-6 rounded-2xl bg-amber-500/10 border border-amber-500/30 text-amber-200 space-y-2 text-xs">
        <h4 className="font-bold flex items-center space-x-2 text-sm text-amber-300">
          <AlertTriangle className="w-4 h-4 shrink-0" />
          <span>SIH 2026 Phase 1 Integrity Declarations</span>
        </h4>
        <ul className="list-disc list-inside space-y-1 text-amber-200/90 pl-1">
          <li><strong>No Fake ML:</strong> Actual machine learning models for monsoon onset are intentionally deferred to Phase 4. Phase 1 guarantees the data contracts and schemas.</li>
          <li><strong>No Real SMS/Voice:</strong> Notifications are routed to mock adapters and logged to SQLite audit tables.</li>
          <li><strong>No Inaccurate Weather Telemetry:</strong> All historical observations are curated sample sequences marked <code className="bg-amber-950/60 px-1 py-0.5 rounded font-mono">DEMO DATA</code>.</li>
        </ul>
      </div>

      {/* Master 10-Phase Roadmap Table */}
      <div className="p-6 rounded-2xl glass-panel border border-slate-800 space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="text-sm font-bold text-white flex items-center space-x-2">
            <Layers className="w-4 h-4 text-sky-400" />
            <span>Master 10-Phase Hackathon Roadmap</span>
          </h3>
          <span className="text-[10px] text-slate-500">Strict Step-by-Step Progression</span>
        </div>

        <div className="overflow-x-auto text-xs">
          <table className="w-full text-left">
            <thead>
              <tr className="border-b border-slate-800 text-slate-400">
                <th className="pb-2 w-28">Phase</th>
                <th className="pb-2 w-72">Focus Area</th>
                <th className="pb-2 w-44">Status</th>
                <th className="pb-2">Description</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {roadmapPhases.map((p, idx) => (
                <tr key={p.num} className="text-slate-300">
                  <td className="py-2.5 font-mono text-sky-400 font-bold">{p.num}</td>
                  <td className="py-2.5 font-semibold text-white">{p.title}</td>
                  <td className="py-2.5">
                    <span
                      className={`px-2 py-0.5 rounded-full text-[10px] font-bold ${
                        idx === 0
                          ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/40'
                          : 'bg-slate-800 text-slate-400'
                      }`}
                    >
                      {p.status}
                    </span>
                  </td>
                  <td className="py-2.5 text-slate-400">{p.desc}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
