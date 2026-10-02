import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import {
  Farmer,
  Block,
  Village,
  Crop,
  FarmerObservation,
  AlertLog,
  ForecastOutput
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
  PhoneCall,
  MessageSquare
} from 'lucide-react';

export const OfficerDashboard: React.FC = () => {
  const [farmers, setFarmers] = useState<Farmer[]>([]);
  const [blocks, setBlocks] = useState<Block[]>([]);
  const [villages, setVillages] = useState<Village[]>([]);
  const [crops, setCrops] = useState<Crop[]>([]);
  const [observations, setObservations] = useState<FarmerObservation[]>([]);
  const [alerts, setAlerts] = useState<AlertLog[]>([]);
  const [forecastContract, setForecastContract] = useState<ForecastOutput | null>(null);

  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Alert simulation state
  const [selectedBlockId, setSelectedBlockId] = useState<number>(1);
  const [selectedRiskLevel, setSelectedRiskLevel] = useState<string>('NORMAL');
  const [selectedAlertType, setSelectedAlertType] = useState<string>('ONSET');
  const [dispatchStatus, setDispatchStatus] = useState<string | null>(null);
  const [dispatching, setDispatching] = useState<boolean>(false);

  const loadData = async () => {
    try {
      setError(null);
      const [f, b, v, c, obs, alt, fc] = await Promise.all([
        api.getFarmers(),
        api.getBlocks(),
        api.getVillages(),
        api.getCrops(),
        api.getObservations(),
        api.getAlerts(),
        api.getForecast(1).catch(() => null),
      ]);
      setFarmers(f);
      setBlocks(b);
      setVillages(v);
      setCrops(c);
      setObservations(obs);
      setAlerts(alt);
      setForecastContract(fc);
    } catch (err: any) {
      setError(err.message || 'Failed to load officer dashboard data');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleRefresh = () => {
    setRefreshing(true);
    loadData();
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
      });
      setDispatchStatus(
        `Dispatched alert to ${res.total_farmers_targeted} farmer(s) in selected block! (${res.dispatches.length} channel logs created)`
      );
      // Reload alerts audit trail
      const updatedAlerts = await api.getAlerts();
      setAlerts(updatedAlerts);
    } catch (err: any) {
      setDispatchStatus(`Error: ${err.message}`);
    } finally {
      setDispatching(false);
    }
  };

  // Crop distribution aggregation
  const cropCounts = crops.map((crop) => {
    const count = farmers.filter((f) => f.crop_id === crop.id).length;
    return { name: crop.name, count };
  });

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="flex items-center space-x-2 text-sky-400">
          <RefreshCw className="w-5 h-5 animate-spin" />
          <span className="text-sm">Loading officer telemetry...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8 pb-12">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold text-white tracking-tight flex items-center space-x-2">
            <ShieldCheck className="w-6 h-6 text-emerald-400" />
            <span>Agricultural Officer Command Center</span>
          </h2>
          <p className="text-slate-400 text-sm mt-1">
            Block-scale farmer targeting, crop distribution, crowd feedback, and communication status.
          </p>
        </div>

        <button
          onClick={handleRefresh}
          disabled={refreshing}
          className="inline-flex items-center space-x-1.5 px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold border border-slate-700 transition-all disabled:opacity-50 self-start sm:self-auto"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${refreshing ? 'animate-spin' : ''}`} />
          <span>Refresh Data</span>
        </button>
      </div>

      {error && (
        <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-sm">
          {error}
        </div>
      )}

      {/* Metric Cards Grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="p-5 rounded-2xl glass-panel border border-slate-800 space-y-1">
          <div className="flex items-center justify-between text-slate-400 text-xs font-medium">
            <span>Registered Farmers</span>
            <Users className="w-4 h-4 text-sky-400" />
          </div>
          <p className="text-2xl font-extrabold text-white tracking-tight">{farmers.length}</p>
          <p className="text-[11px] text-teal-400 font-medium">Consented & Active</p>
        </div>

        <div className="p-5 rounded-2xl glass-panel border border-slate-800 space-y-1">
          <div className="flex items-center justify-between text-slate-400 text-xs font-medium">
            <span>Active Blocks</span>
            <Layers className="w-4 h-4 text-indigo-400" />
          </div>
          <p className="text-2xl font-extrabold text-white tracking-tight">{blocks.length}</p>
          <p className="text-[11px] text-slate-400">Primary Prediction Units</p>
        </div>

        <div className="p-5 rounded-2xl glass-panel border border-slate-800 space-y-1">
          <div className="flex items-center justify-between text-slate-400 text-xs font-medium">
            <span>Mapped Villages</span>
            <MapPin className="w-4 h-4 text-emerald-400" />
          </div>
          <p className="text-2xl font-extrabold text-white tracking-tight">{villages.length}</p>
          <p className="text-[11px] text-slate-400">PIN-Code Linked</p>
        </div>

        <div className="p-5 rounded-2xl glass-panel border border-slate-800 space-y-1">
          <div className="flex items-center justify-between text-slate-400 text-xs font-medium">
            <span>Alerts Dispatched</span>
            <Bell className="w-4 h-4 text-amber-400" />
          </div>
          <p className="text-2xl font-extrabold text-white tracking-tight">{alerts.length}</p>
          <p className="text-[11px] text-slate-400">Audit Trail Entries</p>
        </div>
      </div>

      {/* Two Column Layout: Crop Distribution & Alert Simulator */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Crop Distribution */}
        <div className="lg:col-span-6 p-6 rounded-2xl glass-panel border border-slate-800 space-y-4">
          <h3 className="text-sm font-bold text-white flex items-center space-x-2">
            <Sprout className="w-4 h-4 text-emerald-400" />
            <span>Crop Sowing Distribution (Registered Farmers)</span>
          </h3>
          <div className="grid grid-cols-2 gap-3 pt-1">
            {cropCounts.map((c) => (
              <div
                key={c.name}
                className="p-3 rounded-xl bg-slate-900/60 border border-slate-800/80 flex items-center justify-between"
              >
                <span className="text-xs text-slate-300 font-medium">{c.name}</span>
                <span className="text-xs font-bold text-sky-400 bg-sky-500/10 px-2 py-0.5 rounded-md">
                  {c.count} farmers
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* Severity-Based Alert Simulator */}
        <div className="lg:col-span-6 p-6 rounded-2xl glass-panel border border-slate-800 space-y-4">
          <h3 className="text-sm font-bold text-white flex items-center space-x-2">
            <Send className="w-4 h-4 text-sky-400" />
            <span>Simulate Severity-Based Alert Dispatch</span>
          </h3>
          <form onSubmit={handleSimulateAlert} className="space-y-3 text-xs">
            <div className="grid grid-cols-3 gap-2">
              <div>
                <label className="text-slate-400 block mb-1">Target Block</label>
                <select
                  value={selectedBlockId}
                  onChange={(e) => setSelectedBlockId(Number(e.target.value))}
                  className="w-full bg-slate-900 border border-slate-700 rounded-lg p-2 text-white"
                >
                  {blocks.map((b) => (
                    <option key={b.id} value={b.id}>
                      {b.name}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="text-slate-400 block mb-1">Alert Event</label>
                <select
                  value={selectedAlertType}
                  onChange={(e) => setSelectedAlertType(e.target.value)}
                  className="w-full bg-slate-900 border border-slate-700 rounded-lg p-2 text-white"
                >
                  <option value="ONSET">Onset Window</option>
                  <option value="FALSE_ONSET">False Onset Risk</option>
                  <option value="BREAK">Dry Spell / Break</option>
                  <option value="HEAVY_RAIN">Heavy Rainfall</option>
                </select>
              </div>

              <div>
                <label className="text-slate-400 block mb-1">Severity Risk</label>
                <select
                  value={selectedRiskLevel}
                  onChange={(e) => setSelectedRiskLevel(e.target.value)}
                  className="w-full bg-slate-900 border border-slate-700 rounded-lg p-2 text-white"
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
              className="w-full py-2.5 rounded-xl bg-sky-600 hover:bg-sky-500 text-white font-semibold transition-all disabled:opacity-50"
            >
              {dispatching ? 'Dispatching...' : 'Broadcast Simulated Alert'}
            </button>

            {dispatchStatus && (
              <p className="text-[11px] text-teal-300 bg-teal-500/10 p-2 rounded-lg border border-teal-500/20">
                {dispatchStatus}
              </p>
            )}
          </form>
        </div>
      </div>

      {/* Forecast Engine Contract Placeholder */}
      <div className="p-6 rounded-2xl glass-panel border border-slate-800 space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-800 pb-3">
          <div>
            <h3 className="text-sm font-bold text-white flex items-center space-x-2">
              <Layers className="w-4 h-4 text-sky-400" />
              <span>Block Forecast Engine Contract (Phase 4 ML Slot)</span>
            </h3>
            <p className="text-xs text-slate-400 mt-0.5">
              Standardized probabilistic schema defined for subsequent scikit-learn / LightGBM calibration.
            </p>
          </div>
          <span className="self-start sm:self-auto px-2.5 py-1 rounded-full bg-amber-500/10 border border-amber-500/30 text-amber-300 font-semibold text-[11px]">
            Forecast engine not connected yet (Phase 1 Foundation)
          </span>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-5 gap-3 text-xs">
          <div className="p-3 rounded-xl bg-slate-900/50 border border-slate-800">
            <span className="text-slate-500 block">P(Onset)</span>
            <span className="font-mono text-slate-400">Phase 4 Contract</span>
          </div>
          <div className="p-3 rounded-xl bg-slate-900/50 border border-slate-800">
            <span className="text-slate-500 block">P(False Onset)</span>
            <span className="font-mono text-slate-400">Phase 4 Contract</span>
          </div>
          <div className="p-3 rounded-xl bg-slate-900/50 border border-slate-800">
            <span className="text-slate-500 block">P(Break Spell)</span>
            <span className="font-mono text-slate-400">Phase 4 Contract</span>
          </div>
          <div className="p-3 rounded-xl bg-slate-900/50 border border-slate-800">
            <span className="text-slate-500 block">P(Revival)</span>
            <span className="font-mono text-slate-400">Phase 4 Contract</span>
          </div>
          <div className="p-3 rounded-xl bg-slate-900/50 border border-slate-800">
            <span className="text-slate-500 block">P(Heavy Rain)</span>
            <span className="font-mono text-slate-400">Phase 4 Contract</span>
          </div>
        </div>
      </div>

      {/* Two Column Layout: Farmer Observations & Alert Audit Trail */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Crowd Ground-Truth Observations */}
        <div className="lg:col-span-6 p-6 rounded-2xl glass-panel border border-slate-800 space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-bold text-white flex items-center space-x-2">
              <Eye className="w-4 h-4 text-teal-400" />
              <span>Recent Farmer Crowd Observations</span>
            </h3>
            <span className="text-[10px] text-slate-500">Validation Mode</span>
          </div>

          <div className="overflow-x-auto text-xs">
            <table className="w-full text-left">
              <thead>
                <tr className="border-b border-slate-800 text-slate-400">
                  <th className="pb-2">Date</th>
                  <th className="pb-2">Block</th>
                  <th className="pb-2">Type</th>
                  <th className="pb-2">Reading</th>
                  <th className="pb-2">Source</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {observations.slice(0, 6).map((o) => (
                  <tr key={o.id} className="text-slate-300">
                    <td className="py-2">{o.observation_date}</td>
                    <td className="py-2">Block #{o.block_id}</td>
                    <td className="py-2">
                      <span
                        className={`px-1.5 py-0.5 rounded text-[10px] font-semibold ${
                          o.observation_type === 'HEAVY_RAIN'
                            ? 'bg-rose-500/20 text-rose-300'
                            : o.observation_type === 'RAIN'
                            ? 'bg-sky-500/20 text-sky-300'
                            : 'bg-amber-500/20 text-amber-300'
                        }`}
                      >
                        {o.observation_type}
                      </span>
                    </td>
                    <td className="py-2">{o.value ? `${o.value} mm` : '—'}</td>
                    <td className="py-2 text-slate-500">{o.source}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <p className="text-[11px] text-slate-500">
            Note: Crowd observations do NOT automatically retrain models. They are stored for calibration research.
          </p>
        </div>

        {/* Alert Logs Trail */}
        <div className="lg:col-span-6 p-6 rounded-2xl glass-panel border border-slate-800 space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-bold text-white flex items-center space-x-2">
              <Bell className="w-4 h-4 text-amber-400" />
              <span>Recent Alert Dispatch Audit Trail</span>
            </h3>
            <span className="text-[10px] text-teal-400">Mock Providers</span>
          </div>

          <div className="overflow-x-auto text-xs">
            <table className="w-full text-left">
              <thead>
                <tr className="border-b border-slate-800 text-slate-400">
                  <th className="pb-2">Channel</th>
                  <th className="pb-2">Event</th>
                  <th className="pb-2">Risk</th>
                  <th className="pb-2">Status</th>
                  <th className="pb-2">Attempt</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {alerts.slice(0, 6).map((a) => (
                  <tr key={a.id} className="text-slate-300">
                    <td className="py-2 font-mono text-slate-400">{a.channel}</td>
                    <td className="py-2">{a.alert_type}</td>
                    <td className="py-2">
                      <span
                        className={`px-1.5 py-0.5 rounded text-[10px] font-semibold ${
                          a.risk_level === 'HIGH_RISK'
                            ? 'bg-rose-500/20 text-rose-300'
                            : a.risk_level === 'IMPORTANT'
                            ? 'bg-amber-500/20 text-amber-300'
                            : 'bg-slate-800 text-slate-300'
                        }`}
                      >
                        {a.risk_level}
                      </span>
                    </td>
                    <td className="py-2">
                      <span
                        className={`px-1.5 py-0.5 rounded text-[10px] font-mono ${
                          a.status === 'SIMULATED'
                            ? 'bg-teal-500/10 text-teal-300'
                            : a.status === 'NO_ANSWER'
                            ? 'bg-rose-500/20 text-rose-300'
                            : 'bg-slate-800 text-slate-400'
                        }`}
                      >
                        {a.status}
                      </span>
                    </td>
                    <td className="py-2">#{a.attempt_number}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      {/* Registered Farmers Table with Privacy Masking */}
      <div className="p-6 rounded-2xl glass-panel border border-slate-800 space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="text-sm font-bold text-white flex items-center space-x-2">
            <Users className="w-4 h-4 text-sky-400" />
            <span>Registered Farmers Directory (Privacy-Preserved View)</span>
          </h3>
          <span className="text-[10px] text-teal-400 bg-teal-500/10 border border-teal-500/20 px-2 py-0.5 rounded-full">
            Phone Numbers Masked • Zero Aadhaar
          </span>
        </div>

        <div className="overflow-x-auto text-xs">
          <table className="w-full text-left">
            <thead>
              <tr className="border-b border-slate-800 text-slate-400">
                <th className="pb-2">ID</th>
                <th className="pb-2">Masked Phone</th>
                <th className="pb-2">Language</th>
                <th className="pb-2">PIN</th>
                <th className="pb-2">Block ID</th>
                <th className="pb-2">Channel Pref</th>
                <th className="pb-2">Consent Verified</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {farmers.map((f) => (
                <tr key={f.id} className="text-slate-300">
                  <td className="py-2.5 font-mono text-slate-500">#{f.id}</td>
                  <td className="py-2.5 font-mono text-sky-400">{f.phone_number_masked}</td>
                  <td className="py-2.5">{f.preferred_language}</td>
                  <td className="py-2.5 font-mono">{f.pin_code}</td>
                  <td className="py-2.5">Block #{f.block_id}</td>
                  <td className="py-2.5">{f.communication_preference}</td>
                  <td className="py-2.5 text-emerald-400 font-medium">✓ Explicit Consent</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
