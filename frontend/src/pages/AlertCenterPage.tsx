import React, { useState, useEffect } from 'react';
import {
  Bell,
  Send,
  AlertTriangle,
  CheckCircle,
  XCircle,
  ShieldCheck,
  RefreshCw,
  PhoneCall,
  MessageSquare,
  Smartphone,
  Eye,
  ArrowRight,
  Filter,
  Lock,
  Layers,
  Sparkles,
  Info
} from 'lucide-react';
import { api } from '../services/api';
import { AlertLogAudit, AlertPreviewResponse, AlertSimulationResult } from '../types';

export const AlertCenterPage: React.FC = () => {
  const [activeSubTab, setActiveSubTab] = useState<'dashboard' | 'sandbox'>('dashboard');
  
  // Dashboard state
  const [alerts, setAlerts] = useState<AlertLogAudit[]>([]);
  const [loadingAlerts, setLoadingAlerts] = useState<boolean>(true);
  const [statusFilter, setStatusFilter] = useState<string>('');
  const [channelFilter, setChannelFilter] = useState<string>('');
  const [severityFilter, setSeverityFilter] = useState<string>('');
  const [selectedAlert, setSelectedAlert] = useState<AlertLogAudit | null>(null);

  // Sandbox simulation state
  const [simFarmerId, setSimFarmerId] = useState<number>(1);
  const [simCropId, setSimCropId] = useState<string>('soybean');
  const [simLanguage, setSimLanguage] = useState<string>('mr');
  const [simSeverity, setSimSeverity] = useState<string>('');
  const [simChannelPref, setSimChannelPref] = useState<string>('ALL');
  const [simForceFailure, setSimForceFailure] = useState<string>('');
  const [simulating, setSimulating] = useState<boolean>(false);
  const [previewing, setPreviewing] = useState<boolean>(false);
  const [previewResult, setPreviewResult] = useState<AlertPreviewResponse | null>(null);
  const [simResult, setSimResult] = useState<AlertSimulationResult | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const fetchAlerts = async () => {
    setLoadingAlerts(true);
    try {
      const data = await api.getAlertHistory({
        status: statusFilter || undefined,
        channel: channelFilter || undefined,
        severity: severityFilter || undefined,
        limit: 100
      });
      setAlerts(data);
    } catch (err: any) {
      console.error('Failed to load alert history:', err);
    } finally {
      setLoadingAlerts(false);
    }
  };

  useEffect(() => {
    fetchAlerts();
  }, [statusFilter, channelFilter, severityFilter]);

  // Derived dashboard metrics
  const totalAlerts = alerts.length;
  const successfulCount = alerts.filter(a => a.status === 'SIMULATED_SENT').length;
  const fallbackCount = alerts.filter(a => a.status === 'FALLBACK_USED').length;
  const failedCount = alerts.filter(a => a.status === 'SIMULATED_FAILED').length;
  const consentBlockedCount = alerts.filter(a => a.status === 'BLOCKED_NO_CONSENT').length;
  const noRuleBlockedCount = alerts.filter(a => a.status === 'BLOCKED_NO_VALIDATED_RULE').length;
  const duplicateCount = alerts.filter(a => a.status === 'DUPLICATE_SUPPRESSED').length;

  const handlePreview = async () => {
    setPreviewing(true);
    setErrorMessage(null);
    setSimResult(null);
    try {
      const data = await api.previewAlert({
        farmer_id: simFarmerId,
        crop_id: simCropId,
        language: simLanguage,
        severity: simSeverity || undefined
      });
      setPreviewResult(data);
    } catch (err: any) {
      setErrorMessage(err.message || 'Failed to generate alert preview');
    } finally {
      setPreviewing(false);
    }
  };

  const handleSimulate = async () => {
    setSimulating(true);
    setErrorMessage(null);
    try {
      const data = await api.simulateAlert({
        farmer_id: simFarmerId,
        crop_id: simCropId,
        language: simLanguage,
        severity: simSeverity || undefined,
        channel_preference: simChannelPref || undefined,
        force_failure_channel: simForceFailure || undefined
      });
      setSimResult(data);
      // Refresh dashboard table in background
      fetchAlerts();
    } catch (err: any) {
      setErrorMessage(err.message || 'Failed to simulate alert dispatch');
    } finally {
      setSimulating(false);
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'SIMULATED_SENT':
        return <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-semibold bg-emerald-950/80 text-emerald-400 border border-emerald-800">SIMULATED SENT</span>;
      case 'FALLBACK_USED':
        return <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-semibold bg-amber-950/80 text-amber-300 border border-amber-800">FALLBACK USED</span>;
      case 'BLOCKED_NO_CONSENT':
        return <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-semibold bg-rose-950/80 text-rose-400 border border-rose-800">NO CONSENT</span>;
      case 'BLOCKED_NO_VALIDATED_RULE':
        return <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-semibold bg-purple-950/80 text-purple-400 border border-purple-800">NO VALIDATED RULE</span>;
      case 'DUPLICATE_SUPPRESSED':
        return <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-semibold bg-blue-950/80 text-blue-400 border border-blue-800">DUPLICATE SUPPRESSED</span>;
      case 'SIMULATED_FAILED':
        return <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-semibold bg-red-950/80 text-red-400 border border-red-800">FAILED</span>;
      default:
        return <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-semibold bg-slate-800 text-slate-300">{status}</span>;
    }
  };

  const getSeverityBadge = (severity?: string) => {
    const s = (severity || 'INFO').toUpperCase();
    if (s === 'HIGH') {
      return <span className="text-red-400 font-bold bg-red-950/50 px-2 py-0.5 rounded border border-red-800/60 text-xs">HIGH</span>;
    } else if (s === 'IMPORTANT') {
      return <span className="text-amber-400 font-bold bg-amber-950/50 px-2 py-0.5 rounded border border-amber-800/60 text-xs">IMPORTANT</span>;
    }
    return <span className="text-sky-400 font-medium bg-sky-950/50 px-2 py-0.5 rounded border border-sky-800/60 text-xs">INFO</span>;
  };

  const getChannelIcon = (channel: string) => {
    const c = channel.toUpperCase();
    if (c === 'VOICE') return <PhoneCall className="w-3.5 h-3.5 text-purple-400 inline mr-1" />;
    if (c === 'WHATSAPP') return <MessageSquare className="w-3.5 h-3.5 text-emerald-400 inline mr-1" />;
    return <Smartphone className="w-3.5 h-3.5 text-sky-400 inline mr-1" />;
  };

  return (
    <div className="space-y-8 pb-16">
      {/* Top Banner & Header */}
      <div className="relative overflow-hidden rounded-2xl bg-gradient-to-r from-slate-900 via-sky-950 to-slate-900 border border-slate-800 p-6 sm:p-8 shadow-xl">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div className="space-y-2">
            <div className="flex items-center space-x-3">
              <div className="w-12 h-12 rounded-xl bg-sky-500/20 border border-sky-500/30 flex items-center justify-center text-sky-400">
                <Bell className="w-6 h-6 animate-pulse" />
              </div>
              <div>
                <div className="flex items-center space-x-2">
                  <h1 className="text-2xl font-black text-white tracking-tight">Alert Center</h1>
                  <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-sky-950 text-sky-400 border border-sky-800">
                    PHASE 6A
                  </span>
                </div>
                <p className="text-xs text-slate-400">
                  Communication Simulation & Multi-Channel Alert Routing with Automated Fallback
                </p>
              </div>
            </div>
          </div>

          <div className="flex items-center space-x-3">
            <div className="bg-slate-950/80 border border-amber-500/30 rounded-xl px-4 py-2 text-right">
              <div className="text-[10px] font-bold uppercase tracking-wider text-amber-400 flex items-center justify-end space-x-1">
                <ShieldCheck className="w-3.5 h-3.5" />
                <span>MOCK SIMULATION ONLY</span>
              </div>
              <div className="text-xs text-slate-400">external_dispatch: false</div>
            </div>
          </div>
        </div>

        {/* Tab Switcher */}
        <div className="flex space-x-2 mt-6 pt-6 border-t border-slate-800/80">
          <button
            onClick={() => setActiveSubTab('dashboard')}
            className={`px-4 py-2 rounded-lg text-sm font-semibold transition-all ${
              activeSubTab === 'dashboard'
                ? 'bg-sky-500 text-white shadow-lg shadow-sky-500/25'
                : 'bg-slate-800/60 text-slate-400 hover:text-slate-200'
            }`}
          >
            Officer Alert Audit Dashboard
          </button>
          <button
            onClick={() => setActiveSubTab('sandbox')}
            className={`px-4 py-2 rounded-lg text-sm font-semibold transition-all ${
              activeSubTab === 'sandbox'
                ? 'bg-sky-500 text-white shadow-lg shadow-sky-500/25'
                : 'bg-slate-800/60 text-slate-400 hover:text-slate-200'
            }`}
          >
            Farmer Simulation & Resilience Sandbox
          </button>
        </div>
      </div>

      {/* ========================================================================= */}
      {/* 1. OFFICER AUDIT DASHBOARD TAB                                            */}
      {/* ========================================================================= */}
      {activeSubTab === 'dashboard' && (
        <div className="space-y-6">
          {/* Summary Metric Cards */}
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-4">
            <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl">
              <div className="text-xs text-slate-400 font-medium">Alerts Generated</div>
              <div className="text-2xl font-black text-white mt-1">{totalAlerts}</div>
              <div className="text-[10px] text-slate-500 mt-1">Total in audit trail</div>
            </div>

            <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl">
              <div className="text-xs text-emerald-400 font-medium">Simulated Sent</div>
              <div className="text-2xl font-black text-emerald-300 mt-1">{successfulCount}</div>
              <div className="text-[10px] text-emerald-500/80 mt-1">Direct mock delivery</div>
            </div>

            <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl">
              <div className="text-xs text-amber-400 font-medium">Fallback Used</div>
              <div className="text-2xl font-black text-amber-300 mt-1">{fallbackCount}</div>
              <div className="text-[10px] text-amber-500/80 mt-1">Voice/WA $\to$ SMS</div>
            </div>

            <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl">
              <div className="text-xs text-rose-400 font-medium">Consent Blocked</div>
              <div className="text-2xl font-black text-rose-300 mt-1">{consentBlockedCount}</div>
              <div className="text-[10px] text-rose-500/80 mt-1">No consent given</div>
            </div>

            <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl">
              <div className="text-xs text-purple-400 font-medium">No Validated Rule</div>
              <div className="text-2xl font-black text-purple-300 mt-1">{noRuleBlockedCount}</div>
              <div className="text-[10px] text-purple-500/80 mt-1">Safety gate enforced</div>
            </div>

            <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl">
              <div className="text-xs text-blue-400 font-medium">Duplicate Suppressed</div>
              <div className="text-2xl font-black text-blue-300 mt-1">{duplicateCount}</div>
              <div className="text-[10px] text-blue-500/80 mt-1">24h Cooldown policy</div>
            </div>
          </div>

          {/* Filter Bar */}
          <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl flex flex-wrap items-center justify-between gap-4">
            <div className="flex flex-wrap items-center gap-3">
              <div className="flex items-center space-x-1.5 text-xs text-slate-400">
                <Filter className="w-3.5 h-3.5" />
                <span>Filters:</span>
              </div>

              <select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
                className="bg-slate-950 border border-slate-800 text-xs rounded-lg px-3 py-1.5 text-slate-200 focus:outline-none focus:border-sky-500"
              >
                <option value="">All Statuses</option>
                <option value="SIMULATED_SENT">SIMULATED_SENT</option>
                <option value="FALLBACK_USED">FALLBACK_USED</option>
                <option value="BLOCKED_NO_CONSENT">BLOCKED_NO_CONSENT</option>
                <option value="BLOCKED_NO_VALIDATED_RULE">BLOCKED_NO_VALIDATED_RULE</option>
                <option value="DUPLICATE_SUPPRESSED">DUPLICATE_SUPPRESSED</option>
                <option value="SIMULATED_FAILED">SIMULATED_FAILED</option>
              </select>

              <select
                value={channelFilter}
                onChange={(e) => setChannelFilter(e.target.value)}
                className="bg-slate-950 border border-slate-800 text-xs rounded-lg px-3 py-1.5 text-slate-200 focus:outline-none focus:border-sky-500"
              >
                <option value="">All Channels</option>
                <option value="SMS">SMS</option>
                <option value="WHATSAPP">WhatsApp</option>
                <option value="VOICE">Voice</option>
              </select>

              <select
                value={severityFilter}
                onChange={(e) => setSeverityFilter(e.target.value)}
                className="bg-slate-950 border border-slate-800 text-xs rounded-lg px-3 py-1.5 text-slate-200 focus:outline-none focus:border-sky-500"
              >
                <option value="">All Severities</option>
                <option value="INFO">INFO</option>
                <option value="IMPORTANT">IMPORTANT</option>
                <option value="HIGH">HIGH</option>
              </select>
            </div>

            <button
              onClick={fetchAlerts}
              className="flex items-center space-x-1.5 px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs rounded-lg font-medium transition-colors"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${loadingAlerts ? 'animate-spin' : ''}`} />
              <span>Refresh Log</span>
            </button>
          </div>

          {/* Alert Audit Table */}
          <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden shadow-lg">
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead className="bg-slate-950 text-slate-400 font-semibold border-b border-slate-800">
                  <tr>
                    <th className="py-3 px-4">Time (UTC)</th>
                    <th className="py-3 px-4">Block</th>
                    <th className="py-3 px-4">Recipient</th>
                    <th className="py-3 px-4">Crop</th>
                    <th className="py-3 px-4">Decision</th>
                    <th className="py-3 px-4">Severity</th>
                    <th className="py-3 px-4">Channel</th>
                    <th className="py-3 px-4">Status</th>
                    <th className="py-3 px-4">Fallback</th>
                    <th className="py-3 px-4 text-right">Action</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60">
                  {alerts.length === 0 ? (
                    <tr>
                      <td colSpan={10} className="py-8 text-center text-slate-500">
                        {loadingAlerts ? 'Loading simulated alert dispatches...' : 'No alert dispatches found for current filter.'}
                      </td>
                    </tr>
                  ) : (
                    alerts.map((al) => (
                      <tr key={al.id} className="hover:bg-slate-800/40 transition-colors">
                        <td className="py-3 px-4 text-slate-400 whitespace-nowrap">
                          {new Date(al.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })}
                        </td>
                        <td className="py-3 px-4 font-mono text-slate-300">BLK{al.block_id?.toString().padStart(3, '0')}</td>
                        <td className="py-3 px-4 text-slate-300">
                          <span className="font-mono text-slate-400">ID #{al.farmer_id}</span>{' '}
                          <span className="text-slate-500 text-[11px]">({al.masked_phone || '******'})</span>
                        </td>
                        <td className="py-3 px-4 capitalize text-slate-300">{al.crop_id || 'Soybean'}</td>
                        <td className="py-3 px-4 font-semibold text-slate-200">{al.decision || 'SOW_NOW'}</td>
                        <td className="py-3 px-4">{getSeverityBadge(al.severity)}</td>
                        <td className="py-3 px-4 whitespace-nowrap">
                          {getChannelIcon(al.channel)}
                          <span className="text-slate-300">{al.channel}</span>
                        </td>
                        <td className="py-3 px-4 whitespace-nowrap">{getStatusBadge(al.status)}</td>
                        <td className="py-3 px-4">
                          {al.fallback_used ? (
                            <span className="text-amber-400 font-medium">Yes ({al.fallback_channel})</span>
                          ) : (
                            <span className="text-slate-600">None</span>
                          )}
                        </td>
                        <td className="py-3 px-4 text-right">
                          <button
                            onClick={() => setSelectedAlert(al)}
                            className="px-2.5 py-1 bg-slate-800 hover:bg-slate-700 text-sky-400 rounded text-[11px] font-semibold transition-colors"
                          >
                            Inspect
                          </button>
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </div>

          {/* Alert Detail Inspection Modal */}
          {selectedAlert && (
            <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4">
              <div className="bg-slate-900 border border-slate-700 rounded-2xl max-w-2xl w-full p-6 space-y-5 shadow-2xl relative">
                <div className="flex items-center justify-between border-b border-slate-800 pb-4">
                  <div className="flex items-center space-x-3">
                    <div className="w-9 h-9 rounded-xl bg-sky-500/20 text-sky-400 flex items-center justify-center">
                      <Eye className="w-5 h-5" />
                    </div>
                    <div>
                      <h3 className="font-bold text-white text-base">Alert Audit Inspection #{selectedAlert.id}</h3>
                      <p className="text-xs text-slate-400">Recorded: {new Date(selectedAlert.created_at).toLocaleString()}</p>
                    </div>
                  </div>
                  <button
                    onClick={() => setSelectedAlert(null)}
                    className="text-slate-400 hover:text-white p-1 rounded-lg hover:bg-slate-800"
                  >
                    ✕
                  </button>
                </div>

                <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 text-xs">
                  <div className="bg-slate-950 p-3 rounded-lg border border-slate-800">
                    <span className="text-slate-500 block">Farmer ID</span>
                    <span className="font-mono text-white font-bold">{selectedAlert.farmer_id}</span>
                  </div>
                  <div className="bg-slate-950 p-3 rounded-lg border border-slate-800">
                    <span className="text-slate-500 block">Masked Phone</span>
                    <span className="font-mono text-sky-300 font-bold">{selectedAlert.masked_phone || '******'}</span>
                  </div>
                  <div className="bg-slate-950 p-3 rounded-lg border border-slate-800">
                    <span className="text-slate-500 block">Target Block</span>
                    <span className="font-mono text-white">BLK{selectedAlert.block_id?.toString().padStart(3, '0')}</span>
                  </div>
                  <div className="bg-slate-950 p-3 rounded-lg border border-slate-800">
                    <span className="text-slate-500 block">Target Crop</span>
                    <span className="capitalize text-white font-medium">{selectedAlert.crop_id || 'Soybean'}</span>
                  </div>
                  <div className="bg-slate-950 p-3 rounded-lg border border-slate-800">
                    <span className="text-slate-500 block">Decision Posture</span>
                    <span className="font-bold text-white">{selectedAlert.decision || 'SOW_NOW'}</span>
                  </div>
                  <div className="bg-slate-950 p-3 rounded-lg border border-slate-800">
                    <span className="text-slate-500 block">Severity Level</span>
                    <div>{getSeverityBadge(selectedAlert.severity)}</div>
                  </div>
                </div>

                <div className="bg-slate-950 p-3 rounded-lg border border-slate-800 space-y-1.5 text-xs">
                  <div className="flex justify-between">
                    <span className="text-slate-500">Delivery Status:</span>
                    <div>{getStatusBadge(selectedAlert.status)}</div>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-500">Provider Message ID:</span>
                    <span className="font-mono text-slate-300">{selectedAlert.provider_message_id || 'N/A'}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-500">Fallback Triggered:</span>
                    <span className={selectedAlert.fallback_used ? 'text-amber-400 font-bold' : 'text-slate-400'}>
                      {selectedAlert.fallback_used ? `Yes (fell back from ${selectedAlert.fallback_channel})` : 'No'}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-500">External Dispatch:</span>
                    <span className="font-mono text-emerald-400 font-bold">FALSE (Simulated Mock)</span>
                  </div>
                  {selectedAlert.reason && (
                    <div className="pt-1.5 border-t border-slate-800 text-slate-400">
                      <span className="text-slate-500">Dispatch Audit Note:</span> {selectedAlert.reason}
                    </div>
                  )}
                </div>

                {/* Message Body Content */}
                <div className="space-y-1.5">
                  <span className="text-xs font-semibold text-slate-400 block">Simulated Message Payload</span>
                  <div className="bg-slate-950 border border-slate-800 p-4 rounded-xl font-sans text-xs text-slate-200 whitespace-pre-wrap leading-relaxed">
                    {selectedAlert.message}
                  </div>
                </div>

                <div className="p-3 bg-amber-950/40 border border-amber-800/60 rounded-xl text-[11px] text-amber-300 flex items-center space-x-2">
                  <AlertTriangle className="w-4 h-4 text-amber-400 shrink-0" />
                  <span>
                    Meghvani prototype audit log. In accordance with ethical AI guidelines, real farmer communication remains unconfigured.
                  </span>
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* ========================================================================= */}
      {/* 2. FARMER SIMULATION & RESILIENCE SANDBOX TAB                             */}
      {/* ========================================================================= */}
      {activeSubTab === 'sandbox' && (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
          {/* Configuration Form */}
          <div className="lg:col-span-5 space-y-6">
            <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 space-y-5 shadow-xl">
              <div className="flex items-center space-x-2.5 pb-4 border-b border-slate-800">
                <Sparkles className="w-5 h-5 text-sky-400" />
                <h3 className="font-bold text-white text-base">Simulation Configuration</h3>
              </div>

              {/* Farmer Selection */}
              <div className="space-y-1.5">
                <label className="text-xs font-semibold text-slate-300">Select Registered Farmer</label>
                <select
                  value={simFarmerId}
                  onChange={(e) => setSimFarmerId(Number(e.target.value))}
                  className="w-full bg-slate-950 border border-slate-800 text-xs rounded-xl p-3 text-slate-200 focus:outline-none focus:border-sky-500"
                >
                  <option value={1}>Farmer #1: Ramesh Patil (Nagpur Rural, Consent: Yes)</option>
                  <option value={2}>Farmer #2: Suresh Deshmukh (Wardha East, Consent: Yes)</option>
                  <option value={3}>Farmer #3: Sunita Wankhede (Amravati, Consent: Yes)</option>
                </select>
              </div>

              {/* Crop Selection */}
              <div className="space-y-1.5">
                <label className="text-xs font-semibold text-slate-300">Select Sown Kharif Crop</label>
                <select
                  value={simCropId}
                  onChange={(e) => setSimCropId(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 text-xs rounded-xl p-3 text-slate-200 focus:outline-none focus:border-sky-500"
                >
                  <option value="soybean">Soybean (ICAR-CRIDA Validated)</option>
                  <option value="cotton">Cotton (ICAR-CICR Validated)</option>
                  <option value="pigeonpea">Pigeonpea / Tur (Dr. PDKV Validated)</option>
                </select>
              </div>

              {/* Language Selection */}
              <div className="space-y-1.5">
                <label className="text-xs font-semibold text-slate-300">Advisory Language</label>
                <div className="grid grid-cols-3 gap-2">
                  {[
                    { id: 'mr', label: 'मराठी (mr)' },
                    { id: 'hi', label: 'हिन्दी (hi)' },
                    { id: 'en', label: 'English (en)' }
                  ].map((l) => (
                    <button
                      key={l.id}
                      type="button"
                      onClick={() => setSimLanguage(l.id)}
                      className={`py-2 px-3 rounded-lg text-xs font-semibold border transition-all ${
                        simLanguage === l.id
                          ? 'bg-sky-500/20 text-sky-300 border-sky-500/40'
                          : 'bg-slate-950 border-slate-800 text-slate-400 hover:text-slate-200'
                      }`}
                    >
                      {l.label}
                    </button>
                  ))}
                </div>
              </div>

              {/* Severity Override */}
              <div className="space-y-1.5">
                <label className="text-xs font-semibold text-slate-300">Alert Severity Policy</label>
                <select
                  value={simSeverity}
                  onChange={(e) => setSimSeverity(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 text-xs rounded-xl p-3 text-slate-200 focus:outline-none focus:border-sky-500"
                >
                  <option value="">Auto (Derived from Model False-Onset Probability)</option>
                  <option value="INFO">INFO (Routes SMS)</option>
                  <option value="IMPORTANT">IMPORTANT (Routes SMS + WhatsApp)</option>
                  <option value="HIGH">HIGH (Routes Voice + SMS)</option>
                </select>
              </div>

              {/* Channel Preference */}
              <div className="space-y-1.5">
                <label className="text-xs font-semibold text-slate-300">Channel Preference</label>
                <select
                  value={simChannelPref}
                  onChange={(e) => setSimChannelPref(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 text-xs rounded-xl p-3 text-slate-200 focus:outline-none focus:border-sky-500"
                >
                  <option value="ALL">Policy Default (Severity Matrix)</option>
                  <option value="SMS">SMS Only</option>
                  <option value="WHATSAPP">WhatsApp Preferred</option>
                  <option value="VOICE">Voice Preferred</option>
                </select>
              </div>

              {/* Resilience Test: Forced Failure */}
              <div className="p-4 bg-slate-950 rounded-xl border border-slate-800 space-y-2">
                <label className="text-xs font-bold text-amber-400 flex items-center space-x-1.5">
                  <AlertTriangle className="w-3.5 h-3.5" />
                  <span>Resilience Simulation (Test Fallback)</span>
                </label>
                <select
                  value={simForceFailure}
                  onChange={(e) => setSimForceFailure(e.target.value)}
                  className="w-full bg-slate-900 border border-slate-700 text-xs rounded-lg p-2.5 text-slate-200 focus:outline-none focus:border-amber-500"
                >
                  <option value="">No Failure (Standard Delivery)</option>
                  <option value="VOICE">Force Voice Failure $\to$ Triggers SMS Fallback</option>
                  <option value="WHATSAPP">Force WhatsApp Failure $\to$ Triggers SMS Fallback</option>
                </select>
                <p className="text-[10px] text-slate-500">
                  Simulates telecom gateway outage to demonstrate automatic SMS fallback without dropping advisory alerts.
                </p>
              </div>

              {/* Action Buttons */}
              <div className="flex space-x-3 pt-2">
                <button
                  onClick={handlePreview}
                  disabled={previewing || simulating}
                  className="flex-1 py-3 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-xl text-xs font-bold transition-all flex items-center justify-center space-x-2"
                >
                  <Eye className="w-4 h-4" />
                  <span>{previewing ? 'Previewing...' : 'Preview Plan'}</span>
                </button>

                <button
                  onClick={handleSimulate}
                  disabled={simulating || previewing}
                  className="flex-1 py-3 bg-gradient-to-r from-sky-500 to-teal-500 hover:from-sky-400 hover:to-teal-400 text-white rounded-xl text-xs font-bold transition-all shadow-lg shadow-sky-500/25 flex items-center justify-center space-x-2"
                >
                  <Send className="w-4 h-4" />
                  <span>{simulating ? 'Simulating...' : 'Simulate Dispatch'}</span>
                </button>
              </div>

              {errorMessage && (
                <div className="p-3 bg-rose-950/40 border border-rose-800 text-rose-300 text-xs rounded-xl flex items-center space-x-2">
                  <XCircle className="w-4 h-4 text-rose-400 shrink-0" />
                  <span>{errorMessage}</span>
                </div>
              )}
            </div>
          </div>

          {/* Live Pipeline Trace & Result Visualization */}
          <div className="lg:col-span-7 space-y-6">
            {/* End-to-End Pipeline Trace Architecture */}
            <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl">
              <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-4 flex items-center space-x-2">
                <Layers className="w-4 h-4 text-sky-400" />
                <span>End-to-End Pipeline Execution Trace</span>
              </h4>

              <div className="grid grid-cols-2 sm:grid-cols-6 gap-2 text-center text-xs">
                <div className="bg-slate-950 p-2.5 rounded-lg border border-slate-800/80">
                  <div className="text-[10px] text-slate-500 uppercase font-semibold">1. Forecast</div>
                  <div className="text-sky-400 font-bold mt-1">P(False Onset)</div>
                </div>

                <div className="bg-slate-950 p-2.5 rounded-lg border border-slate-800/80">
                  <div className="text-[10px] text-slate-500 uppercase font-semibold">2. Decision</div>
                  <div className="text-emerald-400 font-bold mt-1">SOW_NOW / WAIT</div>
                </div>

                <div className="bg-slate-950 p-2.5 rounded-lg border border-slate-800/80">
                  <div className="text-[10px] text-slate-500 uppercase font-semibold">3. Agronomy</div>
                  <div className="text-purple-400 font-bold mt-1">VALIDATED Rule</div>
                </div>

                <div className="bg-slate-950 p-2.5 rounded-lg border border-slate-800/80">
                  <div className="text-[10px] text-slate-500 uppercase font-semibold">4. Message</div>
                  <div className="text-amber-400 font-bold mt-1">Multi-Lingual</div>
                </div>

                <div className="bg-slate-950 p-2.5 rounded-lg border border-slate-800/80">
                  <div className="text-[10px] text-slate-500 uppercase font-semibold">5. Routing</div>
                  <div className="text-teal-400 font-bold mt-1">Severity Plan</div>
                </div>

                <div className="bg-slate-950 p-2.5 rounded-lg border border-slate-800/80">
                  <div className="text-[10px] text-slate-500 uppercase font-semibold">6. Delivery</div>
                  <div className="text-blue-400 font-bold mt-1">Mock Dispatch</div>
                </div>
              </div>
            </div>

            {/* Simulation Result Output */}
            {simResult && (
              <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 space-y-5 shadow-xl animate-in fade-in duration-300">
                <div className="flex items-center justify-between pb-3 border-b border-slate-800">
                  <div className="flex items-center space-x-2">
                    <CheckCircle className="w-5 h-5 text-emerald-400" />
                    <h3 className="font-bold text-white text-base">Simulation Dispatch Result</h3>
                  </div>
                  <div>{getStatusBadge(simResult.status)}</div>
                </div>

                {/* Key Execution Metrics */}
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
                  <div className="bg-slate-950 p-3 rounded-lg border border-slate-800">
                    <span className="text-slate-500 block">Recipient</span>
                    <span className="font-mono text-sky-400 font-bold">{simResult.masked_phone}</span>
                  </div>
                  <div className="bg-slate-950 p-3 rounded-lg border border-slate-800">
                    <span className="text-slate-500 block">Decision</span>
                    <span className="font-bold text-white">{simResult.decision}</span>
                  </div>
                  <div className="bg-slate-950 p-3 rounded-lg border border-slate-800">
                    <span className="text-slate-500 block">Severity</span>
                    <div>{getSeverityBadge(simResult.severity)}</div>
                  </div>
                  <div className="bg-slate-950 p-3 rounded-lg border border-slate-800">
                    <span className="text-slate-500 block">External Dispatch</span>
                    <span className="font-mono text-emerald-400 font-bold">FALSE (Simulated)</span>
                  </div>
                </div>

                {/* Provider Execution Sequence (Shows Failure & Fallback Trace) */}
                <div className="space-y-2">
                  <span className="text-xs font-bold text-slate-300 block">Provider Dispatch Execution Trace</span>
                  <div className="space-y-2">
                    {simResult.dispatches?.map((d, idx) => (
                      <div
                        key={idx}
                        className={`p-3 rounded-xl border text-xs flex items-center justify-between ${
                          d.success
                            ? 'bg-slate-950 border-emerald-900/60'
                            : 'bg-red-950/30 border-red-800/60'
                        }`}
                      >
                        <div className="flex items-center space-x-2">
                          {d.success ? (
                            <CheckCircle className="w-4 h-4 text-emerald-400" />
                          ) : (
                            <XCircle className="w-4 h-4 text-red-400" />
                          )}
                          <div>
                            <span className="font-bold text-white mr-2">{d.channel}</span>
                            <span className="font-mono text-slate-400 text-[11px]">{d.provider_message_id}</span>
                            {d.error && <p className="text-[11px] text-red-400 mt-0.5">{d.error}</p>}
                          </div>
                        </div>

                        <div>
                          {d.success ? (
                            <span className="text-emerald-400 font-bold">SIMULATED_SENT</span>
                          ) : (
                            <span className="text-red-400 font-bold">SIMULATED_FAILED</span>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Message Payload Display */}
                <div className="space-y-1.5">
                  <span className="text-xs font-semibold text-slate-300 block">Delivered Farmer Payload</span>
                  <div className="bg-slate-950 p-4 rounded-xl border border-slate-800 text-xs text-slate-200 whitespace-pre-wrap font-sans leading-relaxed">
                    {simResult.message}
                  </div>
                </div>

                {simResult.source_institution && (
                  <div className="text-[11px] text-slate-500 border-t border-slate-800 pt-3">
                    <span className="font-semibold text-slate-400">Institutional Sourced Guidance:</span> {simResult.source_institution}
                  </div>
                )}
              </div>
            )}

            {/* Preview Output */}
            {!simResult && previewResult && (
              <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 space-y-4 shadow-xl">
                <div className="flex items-center justify-between pb-3 border-b border-slate-800">
                  <h3 className="font-bold text-white text-base flex items-center space-x-2">
                    <Eye className="w-5 h-5 text-sky-400" />
                    <span>Pre-Dispatch Plan Preview</span>
                  </h3>
                  <div>{getStatusBadge(previewResult.alert_status)}</div>
                </div>

                <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
                  <div className="bg-slate-950 p-3 rounded-lg border border-slate-800">
                    <span className="text-slate-500 block">Target Farmer</span>
                    <span className="font-mono text-sky-300 font-bold">{previewResult.masked_phone}</span>
                  </div>
                  <div className="bg-slate-950 p-3 rounded-lg border border-slate-800">
                    <span className="text-slate-500 block">Decision</span>
                    <span className="font-bold text-white">{previewResult.decision}</span>
                  </div>
                  <div className="bg-slate-950 p-3 rounded-lg border border-slate-800">
                    <span className="text-slate-500 block">Severity Plan</span>
                    <div>{getSeverityBadge(previewResult.severity)}</div>
                  </div>
                  <div className="bg-slate-950 p-3 rounded-lg border border-slate-800">
                    <span className="text-slate-500 block">Channel Sequence</span>
                    <span className="font-semibold text-white">{previewResult.channel_plan?.join(' + ')}</span>
                  </div>
                </div>

                <div className="space-y-1.5">
                  <span className="text-xs font-semibold text-slate-400 block">Message Preview</span>
                  <div className="bg-slate-950 p-4 rounded-xl border border-slate-800 text-xs text-slate-200 whitespace-pre-wrap leading-relaxed font-sans">
                    {previewResult.message_preview}
                  </div>
                </div>
              </div>
            )}

            {!simResult && !previewResult && (
              <div className="bg-slate-900/50 border border-dashed border-slate-800 rounded-2xl p-12 text-center text-slate-500 space-y-3">
                <Smartphone className="w-10 h-10 mx-auto text-slate-600" />
                <p className="text-xs">
                  Configure simulation parameters and click <strong>Preview Plan</strong> or <strong>Simulate Dispatch</strong> to trigger the mock delivery workflow.
                </p>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};
export default AlertCenterPage;
