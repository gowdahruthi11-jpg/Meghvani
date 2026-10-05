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
  Info,
  Radio,
  Zap,
  UserCheck,
  ChevronRight,
  Cpu,
  MapPin,
  Clock,
  Check,
  Volume2
} from 'lucide-react';
import { api } from '../services/api';
import {
  AlertLogAudit,
  AlertPreviewResponse,
  AlertSimulationResult,
  CommunicationGatewayStatus,
  CommunicationSummary,
  CommunicationTransaction
} from '../types';

export const AlertCenterPage: React.FC = () => {
  const [activeSubTab, setActiveSubTab] = useState<'timeline' | 'dashboard' | 'sandbox'>('timeline');

  // Gateway & Timeline State
  const [gatewayStatus, setGatewayStatus] = useState<CommunicationGatewayStatus | null>(null);
  const [commSummary, setCommSummary] = useState<CommunicationSummary | null>(null);
  const [timeline, setTimeline] = useState<CommunicationTransaction[]>([]);
  const [loadingTimeline, setLoadingTimeline] = useState<boolean>(true);
  const [selectedTransaction, setSelectedTransaction] = useState<CommunicationTransaction | null>(null);

  // Quick SMS Test Form State
  const [testPhone, setTestPhone] = useState<string>('+919876543210');
  const [testBody, setTestBody] = useState<string>('MEGH');
  const [isSendingTest, setIsSendingTest] = useState<boolean>(false);
  const [testFeedback, setTestFeedback] = useState<string | null>(null);

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

  // Fetch Gateway & Timeline
  const fetchCommunicationData = async () => {
    try {
      const [statusRes, summaryRes, timelineRes] = await Promise.all([
        api.getCommunicationStatus(),
        api.getCommunicationSummary(),
        api.getCommunicationTimeline(60)
      ]);
      setGatewayStatus(statusRes);
      setCommSummary(summaryRes);
      setTimeline(timelineRes);
    } catch (err) {
      console.error('Failed to fetch communication data:', err);
    } finally {
      setLoadingTimeline(false);
    }
  };

  // Fetch Officer Audit Alerts
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
    fetchCommunicationData();
    fetchAlerts();

    // Auto-poll communication timeline every 3.5 seconds for live SMS updates
    const interval = setInterval(() => {
      fetchCommunicationData();
    }, 3500);

    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    fetchAlerts();
  }, [statusFilter, channelFilter, severityFilter]);

  // Derived dashboard metrics
  const totalAlerts = alerts.length;
  const successfulCount = alerts.filter(a => a.status === 'SIMULATED_SENT').length;
  const fallbackCount = alerts.filter(a => a.status === 'FALLBACK_USED').length;
  const consentBlockedCount = alerts.filter(a => a.status === 'BLOCKED_NO_CONSENT').length;
  const noRuleBlockedCount = alerts.filter(a => a.status === 'BLOCKED_NO_VALIDATED_RULE').length;

  const handleSendTestSMS = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!testPhone || !testBody) return;
    setIsSendingTest(true);
    setTestFeedback(null);
    try {
      const res = await api.testIncomingSMS({
        from_phone: testPhone,
        body: testBody
      });
      setTestFeedback(`Processed: Step -> ${res.step_after || 'DONE'}. Reply sent!`);
      // Update body to sensible next step
      if (testBody.toUpperCase() === 'MEGH') setTestBody('1');
      else if (testBody === '1') setTestBody('441501');
      else if (testBody === '441501') setTestBody('1');
      else if (testBody === '1') setTestBody('YES');
      else if (testBody.toUpperCase() === 'YES') setTestBody('STATUS');
      fetchCommunicationData();
    } catch (err: any) {
      setTestFeedback(`Error: ${err.message || 'Failed to dispatch test SMS'}`);
    } finally {
      setIsSendingTest(false);
    }
  };

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
      fetchAlerts();
      fetchCommunicationData();
    } catch (err: any) {
      setErrorMessage(err.message || 'Failed to simulate alert dispatch');
    } finally {
      setSimulating(false);
    }
  };

  const getStatusBadge = (status: string) => {
    const s = status.toUpperCase();
    if (s.includes('SENT') || s === 'RECEIVED' || s === 'SUCCESS') {
      return (
        <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-semibold bg-emerald-950/80 text-emerald-400 border border-emerald-800">
          <CheckCircle className="w-3 h-3 mr-1" />
          {status}
        </span>
      );
    }
    if (s.includes('PROCESSED') || s.includes('PENDING') || s.includes('FALLBACK')) {
      return (
        <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-semibold bg-amber-950/80 text-amber-300 border border-amber-800">
          <RefreshCw className="w-3 h-3 mr-1 animate-spin" />
          {status}
        </span>
      );
    }
    if (s.includes('DUPLICATE')) {
      return (
        <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-semibold bg-blue-950/80 text-blue-400 border border-blue-800">
          {status}
        </span>
      );
    }
    return (
      <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-semibold bg-rose-950/80 text-rose-400 border border-rose-800">
        <XCircle className="w-3 h-3 mr-1" />
        {status}
      </span>
    );
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
                  <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-emerald-950 text-emerald-400 border border-emerald-800">
                    REAL SMS ENABLED
                  </span>
                </div>
                <p className="text-xs text-slate-400">
                  Live Conversational Registration, Multi-Event ML Advisories & Multi-Channel Alert Routing
                </p>
              </div>
            </div>
          </div>

          {/* Gateway Status Badge */}
          <div className="flex items-center space-x-3">
            <div className={`rounded-xl px-4 py-2 border shadow-lg ${
              gatewayStatus?.is_live
                ? 'bg-emerald-950/70 border-emerald-500/50 text-emerald-300'
                : 'bg-slate-950/80 border-amber-500/40 text-amber-400'
            }`}>
              <div className="text-[10px] font-black uppercase tracking-wider flex items-center space-x-1.5">
                <span className={`w-2 h-2 rounded-full animate-ping ${gatewayStatus?.is_live ? 'bg-emerald-400' : 'bg-amber-400'}`} />
                <span>{gatewayStatus?.gateway_label || 'SMS GATEWAY: ● MOCK (SIMULATION)'}</span>
              </div>
              <div className="text-[11px] text-slate-300 font-mono mt-0.5">
                {gatewayStatus?.is_live
                  ? `Twilio: ${gatewayStatus.twilio_phone_number_masked || 'Active'}`
                  : 'Mode: SIMULATION (Mock Provider)'}
              </div>
            </div>

            <button
              onClick={() => {
                fetchCommunicationData();
                fetchAlerts();
              }}
              className="p-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white border border-slate-700 transition"
              title="Refresh timeline"
            >
              <RefreshCw className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Tab Switcher */}
        <div className="flex space-x-2 mt-6 pt-6 border-t border-slate-800/80 overflow-x-auto">
          <button
            onClick={() => setActiveSubTab('timeline')}
            className={`px-4 py-2 rounded-lg text-sm font-semibold transition-all whitespace-nowrap flex items-center space-x-2 ${
              activeSubTab === 'timeline'
                ? 'bg-emerald-600 text-white shadow-lg shadow-emerald-600/30'
                : 'bg-slate-800/60 text-slate-400 hover:text-slate-200'
            }`}
          >
            <Radio className="w-4 h-4" />
            <span>Live Communication Timeline</span>
          </button>
          <button
            onClick={() => setActiveSubTab('dashboard')}
            className={`px-4 py-2 rounded-lg text-sm font-semibold transition-all whitespace-nowrap flex items-center space-x-2 ${
              activeSubTab === 'dashboard'
                ? 'bg-sky-500 text-white shadow-lg shadow-sky-500/25'
                : 'bg-slate-800/60 text-slate-400 hover:text-slate-200'
            }`}
          >
            <ShieldCheck className="w-4 h-4" />
            <span>Officer Alert Audit Dashboard</span>
          </button>
          <button
            onClick={() => setActiveSubTab('sandbox')}
            className={`px-4 py-2 rounded-lg text-sm font-semibold transition-all whitespace-nowrap flex items-center space-x-2 ${
              activeSubTab === 'sandbox'
                ? 'bg-sky-500 text-white shadow-lg shadow-sky-500/25'
                : 'bg-slate-800/60 text-slate-400 hover:text-slate-200'
            }`}
          >
            <Zap className="w-4 h-4" />
            <span>Farmer Simulation & Sandbox</span>
          </button>

          <button
            onClick={() => window.dispatchEvent(new CustomEvent('meghvani:navigate', { detail: { tab: 'farmers' } }))}
            className="ml-auto px-4 py-2 rounded-lg text-sm font-bold transition-all whitespace-nowrap flex items-center space-x-2 bg-forest-800 hover:bg-forest-900 text-white border border-forest-600 shadow-md"
            title="Open realistic mobile phone SMS interface"
          >
            <Smartphone className="w-4 h-4 text-emerald-400" />
            <span>Farmer Mobile Phone (SMS) ↗</span>
          </button>
        </div>
      </div>

      {/* ========================================================================= */}
      {/* 0. LIVE COMMUNICATION TIMELINE TAB (PRIMARY SIH DEMO)                      */}
      {/* ========================================================================= */}
      {activeSubTab === 'timeline' && (
        <div className="space-y-6">
          {/* Top 4 Summary Cards */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
            <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl shadow-md">
              <div className="flex items-center justify-between">
                <span className="text-xs text-sky-400 font-semibold uppercase tracking-wider">SMS Received</span>
                <MessageSquare className="w-4 h-4 text-sky-400" />
              </div>
              <div className="text-3xl font-black text-white mt-1">
                {commSummary?.sms_received ?? 0}
              </div>
              <div className="text-[11px] text-slate-400 mt-1">Inbound farmer webhooks</div>
            </div>

            <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl shadow-md">
              <div className="flex items-center justify-between">
                <span className="text-xs text-emerald-400 font-semibold uppercase tracking-wider">SMS Sent</span>
                <Send className="w-4 h-4 text-emerald-400" />
              </div>
              <div className="text-3xl font-black text-emerald-300 mt-1">
                {commSummary?.sms_sent ?? 0}
              </div>
              <div className="text-[11px] text-slate-400 mt-1">Dispatched replies & alerts</div>
            </div>

            <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl shadow-md">
              <div className="flex items-center justify-between">
                <span className="text-xs text-purple-400 font-semibold uppercase tracking-wider">Active Farmers</span>
                <UserCheck className="w-4 h-4 text-purple-400" />
              </div>
              <div className="text-3xl font-black text-purple-300 mt-1">
                {commSummary?.active_farmers ?? 0}
              </div>
              <div className="text-[11px] text-slate-400 mt-1">Registered & consented</div>
            </div>

            <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl shadow-md">
              <div className="flex items-center justify-between">
                <span className="text-xs text-amber-400 font-semibold uppercase tracking-wider">Latest Advisory</span>
                <Zap className="w-4 h-4 text-amber-400" />
              </div>
              <div className="text-xs text-slate-200 mt-1 font-medium truncate" title={commSummary?.latest_advisory.snippet}>
                {commSummary?.latest_advisory.snippet || 'Standing by...'}
              </div>
              <div className="text-[10px] text-amber-500/80 mt-1">
                {commSummary?.latest_advisory.timestamp
                  ? new Date(commSummary.latest_advisory.timestamp).toLocaleTimeString()
                  : 'Multi-event pipeline'}
              </div>
            </div>
          </div>

          {/* Quick Interactive SMS Simulator Bar */}
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 shadow-md">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
              <div className="space-y-1">
                <div className="text-xs font-bold text-white uppercase tracking-wider flex items-center space-x-2">
                  <Smartphone className="w-4 h-4 text-emerald-400" />
                  <span>Real SMS Simulator / Webhook Test Console</span>
                </div>
                <p className="text-[11px] text-slate-400">
                  Simulate incoming farmer text or test conversational flow (MEGH $\to$ PIN $\to$ Village $\to$ Crop $\to$ Consent $\to$ STATUS).
                </p>
              </div>

              <form onSubmit={handleSendTestSMS} className="flex flex-wrap items-center gap-2">
                <input
                  type="text"
                  value={testPhone}
                  onChange={(e) => setTestPhone(e.target.value)}
                  placeholder="+919876543210"
                  className="bg-slate-950 border border-slate-700 text-xs text-white rounded-lg px-3 py-1.5 font-mono focus:border-emerald-500 outline-none w-36"
                />
                <input
                  type="text"
                  value={testBody}
                  onChange={(e) => setTestBody(e.target.value)}
                  placeholder="e.g. MEGH, 1, 441501, STATUS"
                  className="bg-slate-950 border border-slate-700 text-xs text-white rounded-lg px-3 py-1.5 focus:border-emerald-500 outline-none w-48"
                />
                <button
                  type="submit"
                  disabled={isSendingTest}
                  className="bg-emerald-600 hover:bg-emerald-500 text-white font-semibold text-xs px-4 py-1.5 rounded-lg flex items-center space-x-1.5 transition disabled:opacity-50"
                >
                  <Send className="w-3.5 h-3.5" />
                  <span>{isSendingTest ? 'Sending...' : 'Send SMS'}</span>
                </button>
              </form>
            </div>
            {testFeedback && (
              <div className="mt-2 text-xs font-mono text-emerald-400 bg-emerald-950/40 px-3 py-1 rounded border border-emerald-900/50">
                {testFeedback}
              </div>
            )}
          </div>

          {/* Main Chronological Timeline */}
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-4">
            <div className="flex items-center justify-between border-b border-slate-800 pb-4">
              <div>
                <h3 className="font-bold text-white text-base flex items-center space-x-2">
                  <Radio className="w-5 h-5 text-emerald-400 animate-pulse" />
                  <span>Live Communication Timeline</span>
                </h3>
                <p className="text-xs text-slate-400">
                  Real-time transaction log for inbound webhooks and outbound replies. Click any entry to inspect the full architecture pipeline.
                </p>
              </div>
              <div className="text-xs text-slate-400 font-mono">
                Auto-refresh: <span className="text-emerald-400 font-bold">ACTIVE (3.5s)</span>
              </div>
            </div>

            {loadingTimeline && timeline.length === 0 ? (
              <div className="py-12 text-center text-slate-500 text-sm">Loading live transactions...</div>
            ) : timeline.length === 0 ? (
              <div className="py-12 text-center text-slate-500 text-sm">
                No transactions recorded yet. Send SMS with body &quot;MEGH&quot; to begin!
              </div>
            ) : (
              <div className="space-y-3.5">
                {timeline.map((tx) => {
                  const isInbound = tx.direction === 'INBOUND';
                  const isRegistrationSuccess = tx.event_type === 'NEW_FARMER_REGISTERED';
                  const isAdvisory = tx.event_type === 'ADVISORY' || tx.step_after === 'STATUS';
                  const isVoice = tx.channel === 'VOICE' || tx.event_type === 'AI_VOICE_ALERT';

                  // Prominent AI VOICE ALERT Card
                  if (isVoice) {
                    const isPlayed = tx.status === 'PLAYED' || tx.status === 'COMPLETED';
                    const isReady = tx.status === 'READY';
                    return (
                      <div
                        key={tx.id}
                        onClick={() => setSelectedTransaction(tx)}
                        className="cursor-pointer bg-gradient-to-r from-purple-950/80 via-slate-900 to-slate-950 border-2 border-purple-500/70 rounded-xl p-4 shadow-lg hover:border-purple-400 transition"
                      >
                        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-2.5 border-b border-purple-900/50">
                          <div className="flex flex-wrap items-center gap-2">
                            <span className="px-2.5 py-0.5 rounded text-[11px] font-black tracking-wider uppercase bg-purple-900/90 text-purple-200 border border-purple-600 flex items-center space-x-1.5 shadow-sm">
                              <PhoneCall className="w-3 h-3 text-purple-300" />
                              <span>AI VOICE ALERT — DEMO</span>
                            </span>
                            <span className="font-mono text-xs font-bold text-white">
                              {tx.masked_phone}
                            </span>
                            <span className="text-[10px] text-slate-400 font-mono">
                              {tx.timestamp ? new Date(tx.timestamp).toLocaleTimeString() : ''}
                            </span>
                          </div>

                          <div className="flex items-center space-x-2">
                            <span className="text-[10px] font-mono uppercase px-2 py-0.5 rounded bg-purple-950 text-purple-300 border border-purple-800">
                              {tx.provider || 'Sarvam AI (Bulbul v3)'}
                            </span>
                            <span className="text-[10px] font-bold uppercase px-2 py-0.5 rounded bg-red-950 text-red-300 border border-red-800">
                              HIGH_RISK
                            </span>
                            {isPlayed ? (
                              <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-semibold bg-emerald-950/80 text-emerald-400 border border-emerald-800">
                                <CheckCircle className="w-3 h-3 mr-1" />
                                Voice Alert Played
                              </span>
                            ) : isReady ? (
                              <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-semibold bg-purple-950/80 text-purple-300 border border-purple-700">
                                <Volume2 className="w-3 h-3 mr-1" />
                                Voice Alert Ready
                              </span>
                            ) : (
                              getStatusBadge(tx.status)
                            )}
                          </div>
                        </div>

                        <div className="mt-2.5 flex items-start justify-between gap-4">
                          <div className="space-y-1.5">
                            <div className="flex items-center space-x-2">
                              <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-purple-900/50 text-purple-300 border border-purple-800">
                                Language: {tx.language ? tx.language.toUpperCase() : 'MR'}
                              </span>
                              <span className="text-xs text-purple-300 font-medium flex items-center space-x-1">
                                <Volume2 className="w-3.5 h-3.5 text-purple-400" />
                                <span>Bulbul v3 TTS Audio Advisory</span>
                              </span>
                            </div>
                            <p className="text-xs text-slate-200 font-mono whitespace-pre-wrap leading-relaxed bg-slate-950/80 p-3 rounded-lg border border-purple-950">
                              &quot;{tx.full_message}&quot;
                            </p>
                            <div className="text-[11px] text-slate-400 flex flex-wrap items-center gap-2 pt-1">
                              <span>Farmer: <strong className="text-white">{tx.masked_phone}</strong></span>
                              <span>•</span>
                              <span>Village: <strong className="text-white">{tx.village || 'Kalmeshwar'}</strong> ({tx.block || 'Nagpur Rural'})</span>
                              <span>•</span>
                              <span>Crop: <strong className="text-white">{tx.crop || 'Soybean'}</strong></span>
                              <span>•</span>
                              <span className="text-purple-300 font-semibold">Routing: HIGH_RISK → VOICE + SMS</span>
                            </div>
                          </div>

                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              setSelectedTransaction(tx);
                            }}
                            className="shrink-0 text-xs bg-purple-900/70 hover:bg-purple-800 text-purple-200 px-3 py-1.5 rounded-lg font-semibold border border-purple-700 transition flex items-center space-x-1 mt-1"
                          >
                            <span>Inspect Voice Trace</span>
                            <ChevronRight className="w-3.5 h-3.5" />
                          </button>
                        </div>
                      </div>
                    );
                  }

                  // Prominent NEW FARMER REGISTERED Card
                  if (isRegistrationSuccess) {
                    return (
                      <div
                        key={tx.id}
                        onClick={() => setSelectedTransaction(tx)}
                        className="cursor-pointer bg-gradient-to-r from-emerald-950/80 via-emerald-900/40 to-slate-900 border-2 border-emerald-500/80 rounded-xl p-4 shadow-lg hover:border-emerald-400 transition"
                      >
                        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                          <div className="flex items-center space-x-3">
                            <div className="w-10 h-10 rounded-xl bg-emerald-500/20 text-emerald-400 flex items-center justify-center border border-emerald-500/40">
                              <UserCheck className="w-6 h-6" />
                            </div>
                            <div>
                              <div className="flex items-center space-x-2">
                                <span className="text-xs font-black uppercase tracking-wider text-emerald-300">
                                  NEW FARMER REGISTERED
                                </span>
                                <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-emerald-900/60 text-emerald-200 border border-emerald-700">
                                  {tx.masked_phone}
                                </span>
                                <span className="text-[10px] text-slate-400 font-mono">
                                  {tx.timestamp ? new Date(tx.timestamp).toLocaleTimeString() : ''}
                                </span>
                              </div>
                              <div className="text-xs text-slate-200 mt-1">
                                Village: <strong className="text-white">{tx.village || 'Registered'}</strong> | Block: <strong className="text-white">{tx.block || 'Nagpur Rural'}</strong> | Crop: <strong className="text-white">{tx.crop || 'Soybean'}</strong> | Language: <strong className="text-white">{tx.language || 'Hindi'}</strong> | Consent: <strong className="text-emerald-400">YES</strong>
                              </div>
                            </div>
                          </div>

                          <div className="flex items-center space-x-2">
                            <span className="text-xs font-semibold text-emerald-400 bg-emerald-950 px-2.5 py-1 rounded border border-emerald-800">
                              Registration Complete
                            </span>
                            <button className="text-xs bg-slate-800 hover:bg-slate-700 text-sky-300 px-3 py-1 rounded border border-slate-700 flex items-center space-x-1">
                              <span>Inspect</span>
                              <ChevronRight className="w-3 h-3" />
                            </button>
                          </div>
                        </div>
                      </div>
                    );
                  }

                  return (
                    <div
                      key={tx.id}
                      onClick={() => setSelectedTransaction(tx)}
                      className={`cursor-pointer rounded-xl p-4 border transition-all hover:border-sky-500/60 ${
                        isInbound
                          ? 'bg-slate-950/70 border-slate-800 hover:bg-slate-900/80'
                          : 'bg-slate-900/90 border-slate-700/80 hover:bg-slate-800/80'
                      }`}
                    >
                      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-2 border-b border-slate-800/60">
                        <div className="flex items-center space-x-2.5">
                          <span
                            className={`px-2.5 py-0.5 rounded text-[11px] font-black tracking-wider uppercase ${
                              isInbound
                                ? 'bg-sky-950 text-sky-300 border border-sky-800'
                                : 'bg-emerald-950 text-emerald-300 border border-emerald-800'
                            }`}
                          >
                            {isInbound ? '[INBOUND]' : '[OUTBOUND]'}
                          </span>
                          <span className="font-mono text-xs font-bold text-white">
                            {tx.masked_phone}
                          </span>
                          <span className="text-[10px] text-slate-500 font-mono">
                            {tx.timestamp ? new Date(tx.timestamp).toLocaleTimeString() : ''}
                          </span>
                        </div>

                        <div className="flex items-center space-x-2">
                          <span className="text-[10px] font-mono uppercase px-2 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-700">
                            {tx.provider || 'MOCK'}
                          </span>
                          {tx.step_after && (
                            <span className="text-[10px] font-bold uppercase px-2 py-0.5 rounded bg-purple-950 text-purple-300 border border-purple-800">
                              STEP: {tx.step_after}
                            </span>
                          )}
                          {getStatusBadge(tx.status)}
                        </div>
                      </div>

                      <div className="mt-2.5 flex items-start justify-between gap-4">
                        <div className="space-y-1">
                          <p className="text-xs text-slate-200 font-mono whitespace-pre-wrap leading-relaxed">
                            {tx.full_message}
                          </p>
                          {tx.village && (
                            <div className="text-[11px] text-slate-400 flex items-center space-x-2 pt-1">
                              <span>Farmer: {tx.masked_phone}</span>
                              <span>•</span>
                              <span>{tx.village} ({tx.block})</span>
                              {tx.crop && <span>• Crop: {tx.crop}</span>}
                            </div>
                          )}
                        </div>

                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            setSelectedTransaction(tx);
                          }}
                          className="shrink-0 text-[11px] bg-slate-800 hover:bg-slate-700 text-sky-400 px-2.5 py-1 rounded font-semibold border border-slate-700 transition"
                        >
                          Drill Down
                        </button>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>

          {/* ========================================================================= */}
          {/* DEMO TRANSACTION VIEW MODAL / DRAWER                                     */}
          {/* Communication -> Farmer -> Location -> Model -> Prediction -> XAI -> Advisory -> SMS */}
          {/* ========================================================================= */}
          {selectedTransaction && (
            <div className="fixed inset-0 z-50 bg-black/75 backdrop-blur-sm flex items-center justify-center p-4 overflow-y-auto">
              <div className="bg-slate-900 border border-slate-700 rounded-2xl max-w-3xl w-full p-6 space-y-6 shadow-2xl relative my-8">
                {selectedTransaction.channel === 'VOICE' || selectedTransaction.event_type === 'AI_VOICE_ALERT' ? (
                  <>
                    <div className="flex items-center justify-between border-b border-purple-900/60 pb-4">
                      <div className="flex items-center space-x-3">
                        <div className="w-10 h-10 rounded-xl bg-purple-500/20 text-purple-400 flex items-center justify-center border border-purple-500/30">
                          <PhoneCall className="w-6 h-6 animate-pulse" />
                        </div>
                        <div>
                          <div className="flex items-center space-x-2">
                            <h3 className="font-bold text-white text-base">Meghvani AI Voice Alert Architecture</h3>
                            <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-purple-950 text-purple-300 border border-purple-700">
                              DEMO SIMULATION
                            </span>
                          </div>
                          <p className="text-xs text-slate-400">
                            Full trace: Communication $\to$ Farmer $\to$ Location $\to$ Prediction $\to$ Risk $\to$ XAI $\to$ Advisory $\to$ Voice Gen $\to$ Playback
                          </p>
                        </div>
                      </div>
                      <button
                        onClick={() => setSelectedTransaction(null)}
                        className="text-slate-400 hover:text-white p-1 rounded-lg hover:bg-slate-800"
                      >
                        ✕
                      </button>
                    </div>

                    {/* 9-Step Voice Pipeline Flow */}
                    <div className="space-y-3.5 max-h-[65vh] overflow-y-auto pr-1">
                      {/* 1. Communication Routing */}
                      <div className="bg-slate-950 p-3.5 rounded-xl border border-slate-800 flex items-start space-x-3">
                        <div className="w-7 h-7 rounded-lg bg-purple-500/20 text-purple-300 flex items-center justify-center text-xs font-bold shrink-0">
                          1
                        </div>
                        <div className="flex-1 text-xs space-y-1">
                          <div className="font-bold text-white flex items-center justify-between">
                            <span>Communication Hierarchy & Escalation Routing</span>
                            <span className="font-mono text-purple-400 font-bold">HIGH_RISK → VOICE + SMS</span>
                          </div>
                          <div className="text-slate-400">
                            Policy: <strong className="text-slate-200">NORMAL $\to$ SMS</strong> | <strong className="text-slate-200">IMPORTANT $\to$ SMS/WhatsApp</strong> | <strong className="text-purple-300 font-bold">HIGH_RISK $\to$ VOICE + SMS</strong>
                          </div>
                        </div>
                      </div>

                      {/* 2. Farmer Identification */}
                      <div className="bg-slate-950 p-3.5 rounded-xl border border-slate-800 flex items-start space-x-3">
                        <div className="w-7 h-7 rounded-lg bg-sky-500/20 text-sky-400 flex items-center justify-center text-xs font-bold shrink-0">
                          2
                        </div>
                        <div className="flex-1 text-xs space-y-1">
                          <div className="font-bold text-white flex items-center justify-between">
                            <span>Farmer Profile & Multilingual Preferences</span>
                            <span className="font-mono text-sky-300 font-bold">{selectedTransaction.masked_phone}</span>
                          </div>
                          <div className="text-slate-400">
                            Preferred Language: <strong className="text-white uppercase">{selectedTransaction.language || 'mr'}</strong> | Registered Crop: <strong className="text-white">{selectedTransaction.crop || 'Soybean'}</strong> | Consent: <strong className="text-emerald-400">Active (YES)</strong>
                          </div>
                        </div>
                      </div>

                      {/* 3. Location Hierarchy */}
                      <div className="bg-slate-950 p-3.5 rounded-xl border border-slate-800 flex items-start space-x-3">
                        <div className="w-7 h-7 rounded-lg bg-emerald-500/20 text-emerald-400 flex items-center justify-center text-xs font-bold shrink-0">
                          3
                        </div>
                        <div className="flex-1 text-xs space-y-1">
                          <div className="font-bold text-white">Hyperlocal Geography & Spatial Mapping</div>
                          <div className="text-slate-400">
                            Village: <strong className="text-white">{selectedTransaction.village || 'Kalmeshwar'}</strong> | Block: <strong className="text-white">{selectedTransaction.block || 'Nagpur Rural (BLK001)'}</strong> | State: <strong>Maharashtra</strong>
                          </div>
                        </div>
                      </div>

                      {/* 4. Hyperlocal Prediction */}
                      <div className="bg-slate-950 p-3.5 rounded-xl border border-slate-800 flex items-start space-x-3">
                        <div className="w-7 h-7 rounded-lg bg-amber-500/20 text-amber-400 flex items-center justify-center text-xs font-bold shrink-0">
                          4
                        </div>
                        <div className="flex-1 text-xs space-y-1">
                          <div className="font-bold text-white flex items-center justify-between">
                            <span>Hyperlocal ML Prediction (Reused Model Pipeline)</span>
                            <span className="text-amber-400 font-bold font-mono">
                              {selectedTransaction.xai_context?.probability_pct ?? 82}% Prob
                            </span>
                          </div>
                          <div className="text-slate-400">
                            Forecast: <strong className="text-white">Heavy Rainfall & Soil Saturation Surge</strong> | Target Horizon: <strong>24-48 Hours</strong>
                          </div>
                        </div>
                      </div>

                      {/* 5. Risk Assessment */}
                      <div className="bg-slate-950 p-3.5 rounded-xl border border-slate-800 flex items-start space-x-3">
                        <div className="w-7 h-7 rounded-lg bg-red-500/20 text-red-400 flex items-center justify-center text-xs font-bold shrink-0">
                          5
                        </div>
                        <div className="flex-1 text-xs space-y-1">
                          <div className="font-bold text-white flex items-center justify-between">
                            <span>Risk Engine Assessment</span>
                            <span className="text-xs font-bold px-2 py-0.5 rounded bg-red-950 text-red-300 border border-red-800">
                              HIGH_RISK
                            </span>
                          </div>
                          <div className="text-slate-400">
                            Classification: <strong className="text-red-400">HIGH_RISK (Severity Threshold $\ge 75\%$)</strong>. Triggers automated escalation to AI Voice Call.
                          </div>
                        </div>
                      </div>

                      {/* 6. Explainable AI (XAI) */}
                      <div className="bg-slate-950 p-3.5 rounded-xl border border-slate-800 flex items-start space-x-3">
                        <div className="w-7 h-7 rounded-lg bg-indigo-500/20 text-indigo-400 flex items-center justify-center text-xs font-bold shrink-0">
                          6
                        </div>
                        <div className="flex-1 text-xs space-y-1">
                          <div className="font-bold text-white">Farmer-Friendly Agricultural XAI Explanation</div>
                          <div className="text-slate-300 italic bg-slate-900 p-2.5 rounded border border-slate-800">
                            &quot;Rainfall conditions are intensifying rapidly, but recent dry spell creates severe runoff risk and false onset vulnerability.&quot;
                          </div>
                        </div>
                      </div>

                      {/* 7. Advisory Engine */}
                      <div className="bg-slate-950 p-3.5 rounded-xl border border-slate-800 flex items-start space-x-3">
                        <div className="w-7 h-7 rounded-lg bg-teal-500/20 text-teal-400 flex items-center justify-center text-xs font-bold shrink-0">
                          7
                        </div>
                        <div className="flex-1 text-xs space-y-1.5">
                          <div className="font-bold text-white flex items-center justify-between">
                            <span>Advisory Engine (Localized Script)</span>
                            <span className="font-bold text-teal-300 uppercase">
                              {selectedTransaction.language || 'mr'}
                            </span>
                          </div>
                          <div className="bg-slate-900 p-2.5 rounded-lg border border-slate-800 font-mono text-slate-200">
                            {selectedTransaction.full_message}
                          </div>
                        </div>
                      </div>

                      {/* 8. Sarvam AI Voice Generation */}
                      <div className="bg-slate-950 p-3.5 rounded-xl border border-slate-800 flex items-start space-x-3">
                        <div className="w-7 h-7 rounded-lg bg-purple-500/20 text-purple-400 flex items-center justify-center text-xs font-bold shrink-0">
                          8
                        </div>
                        <div className="flex-1 text-xs space-y-1">
                          <div className="font-bold text-white flex items-center justify-between">
                            <span>Sarvam AI Bulbul v3 TTS Service</span>
                            <span className="font-mono text-purple-300">{selectedTransaction.provider || 'Sarvam AI (Bulbul v3)'}</span>
                          </div>
                          <div className="text-slate-400">
                            Synthesis: <strong className="text-white">Bulbul v3 Neural Voice</strong> | In-Memory Audio Caching: <strong className="text-emerald-400">ENABLED</strong> (Prevents redundant API calls on replay)
                          </div>
                        </div>
                      </div>

                      {/* 9. Delivery & Playback Simulation */}
                      <div className="bg-slate-950 p-3.5 rounded-xl border border-slate-800 flex items-start space-x-3">
                        <div className="w-7 h-7 rounded-lg bg-emerald-500/20 text-emerald-400 flex items-center justify-center text-xs font-bold shrink-0">
                          9
                        </div>
                        <div className="flex-1 text-xs space-y-1">
                          <div className="font-bold text-white flex items-center justify-between">
                            <span>Farmer Mobile Delivery & Call Simulation</span>
                            <span className="font-bold text-emerald-400">
                              {selectedTransaction.status === 'PLAYED' ? 'Voice Alert Played' : 'Voice Alert Ready'}
                            </span>
                          </div>
                          <div className="text-slate-400">
                            Simulation Mode: <strong className="text-slate-200">In-App Mobile Call (Honest Demo)</strong>. Phone rings $\to$ Answer $\to$ Waveform streaming $\to$ Replay/End call.
                          </div>
                        </div>
                      </div>
                    </div>
                  </>
                ) : (
                  <>
                    <div className="flex items-center justify-between border-b border-slate-800 pb-4">
                      <div className="flex items-center space-x-3">
                        <div className="w-10 h-10 rounded-xl bg-emerald-500/20 text-emerald-400 flex items-center justify-center border border-emerald-500/30">
                          <Cpu className="w-6 h-6" />
                        </div>
                        <div>
                          <h3 className="font-bold text-white text-base">Meghvani End-to-End Transaction Architecture</h3>
                          <p className="text-xs text-slate-400">
                            Full trace: Webhook $\to$ Farmer $\to$ Location $\to$ Multi-Event ML $\to$ XAI $\to$ Advisory $\to$ SMS
                          </p>
                        </div>
                      </div>
                      <button
                        onClick={() => setSelectedTransaction(null)}
                        className="text-slate-400 hover:text-white p-1 rounded-lg hover:bg-slate-800"
                      >
                        ✕
                      </button>
                    </div>

                    {/* Standard SMS Pipeline Flow Visualization */}
                    <div className="space-y-4">
                      {/* Step 1: Communication Gateway */}
                      <div className="bg-slate-950 p-3.5 rounded-xl border border-slate-800 flex items-start space-x-3">
                        <div className="w-7 h-7 rounded-lg bg-sky-500/20 text-sky-400 flex items-center justify-center text-xs font-bold shrink-0">
                          1
                        </div>
                        <div className="flex-1 text-xs space-y-1">
                          <div className="font-bold text-white flex items-center justify-between">
                            <span>Communication Gateway ({selectedTransaction.direction})</span>
                            <span className="font-mono text-sky-400">{selectedTransaction.provider}</span>
                          </div>
                          <div className="text-slate-400">
                            Status: <strong className="text-emerald-400">{selectedTransaction.status}</strong> | Timestamp: {selectedTransaction.timestamp ? new Date(selectedTransaction.timestamp).toLocaleString() : 'N/A'}
                          </div>
                        </div>
                      </div>

                      {/* Step 2: Farmer Profile */}
                      <div className="bg-slate-950 p-3.5 rounded-xl border border-slate-800 flex items-start space-x-3">
                        <div className="w-7 h-7 rounded-lg bg-purple-500/20 text-purple-400 flex items-center justify-center text-xs font-bold shrink-0">
                          2
                        </div>
                        <div className="flex-1 text-xs space-y-1">
                          <div className="font-bold text-white flex items-center justify-between">
                            <span>Farmer Identification & Privacy Masking</span>
                            <span className="font-mono text-purple-300 font-bold">{selectedTransaction.masked_phone}</span>
                          </div>
                          <div className="text-slate-400">
                            Preferred Language: <strong className="text-white">{selectedTransaction.language || 'Hindi'}</strong> | Consent: <strong className="text-emerald-400">Active (YES)</strong> | Channel: <strong>SMS</strong>
                          </div>
                        </div>
                      </div>

                      {/* Step 3: Location Hierarchy */}
                      <div className="bg-slate-950 p-3.5 rounded-xl border border-slate-800 flex items-start space-x-3">
                        <div className="w-7 h-7 rounded-lg bg-emerald-500/20 text-emerald-400 flex items-center justify-center text-xs font-bold shrink-0">
                          3
                        </div>
                        <div className="flex-1 text-xs space-y-1">
                          <div className="font-bold text-white">Hyperlocal Geography & Spatial Mapping</div>
                          <div className="text-slate-400">
                            Village: <strong className="text-white">{selectedTransaction.village || 'Kalmeshwar'}</strong> | Block: <strong className="text-white">{selectedTransaction.block || 'Nagpur Rural (BLK001)'}</strong> | State: <strong>Maharashtra</strong>
                          </div>
                        </div>
                      </div>

                      {/* Step 4: ML Prediction & Multi-Event Pipeline */}
                      <div className="bg-slate-950 p-3.5 rounded-xl border border-slate-800 flex items-start space-x-3">
                        <div className="w-7 h-7 rounded-lg bg-amber-500/20 text-amber-400 flex items-center justify-center text-xs font-bold shrink-0">
                          4
                        </div>
                        <div className="flex-1 text-xs space-y-1">
                          <div className="font-bold text-white flex items-center justify-between">
                            <span>Multi-Event Probabilistic Model (Phase 3B Baseline)</span>
                            <span className="text-amber-400 font-bold">
                              {selectedTransaction.xai_context?.risk_tier || 'Low Risk'}
                            </span>
                          </div>
                          <div className="text-slate-400">
                            Target Risk: <strong>False Onset (7-Day Horizon)</strong> | Calibrated Probability: <strong className="text-white font-mono">{selectedTransaction.xai_context?.probability_pct ?? 18}%</strong>
                          </div>
                        </div>
                      </div>

                      {/* Step 5: Explainable AI (XAI) Attribution */}
                      <div className="bg-slate-950 p-3.5 rounded-xl border border-slate-800 flex items-start space-x-3">
                        <div className="w-7 h-7 rounded-lg bg-indigo-500/20 text-indigo-400 flex items-center justify-center text-xs font-bold shrink-0">
                          5
                        </div>
                        <div className="flex-1 text-xs space-y-1.5">
                          <div className="font-bold text-white">Explainable AI (Signed Feature Contributions)</div>
                          <div className="grid grid-cols-1 sm:grid-cols-3 gap-2">
                            {selectedTransaction.xai_context?.top_drivers?.map((td, i) => (
                              <div key={i} className="bg-slate-900 p-2 rounded border border-slate-800 text-[11px]">
                                <div className="text-slate-300 font-medium truncate">{td.label}</div>
                                <div className="flex items-center justify-between text-slate-400 mt-0.5">
                                  <span>Share: {td.share_pct}%</span>
                                  <span className={td.direction === 'REDUCING' ? 'text-emerald-400 font-bold' : 'text-amber-400 font-bold'}>
                                    {td.direction}
                                  </span>
                                </div>
                              </div>
                            )) || (
                              <div className="text-slate-400 text-xs col-span-3">
                                Features evaluated against historical climatology & antecedent 7-day rainfall.
                              </div>
                            )}
                          </div>
                        </div>
                      </div>

                      {/* Step 6: Advisory & Outbound SMS Dispatch */}
                      <div className="bg-slate-950 p-3.5 rounded-xl border border-slate-800 flex items-start space-x-3">
                        <div className="w-7 h-7 rounded-lg bg-emerald-500/20 text-emerald-400 flex items-center justify-center text-xs font-bold shrink-0">
                          6
                        </div>
                        <div className="flex-1 text-xs space-y-1.5">
                          <div className="font-bold text-white flex items-center justify-between">
                            <span>Advisory Decision Rule & Real SMS Dispatch</span>
                            <span className="font-bold text-emerald-400">
                              {selectedTransaction.xai_context?.decision || 'SOW_NOW'}
                            </span>
                          </div>
                          <div className="bg-slate-900 p-3 rounded-lg border border-slate-800 font-mono text-slate-200 whitespace-pre-wrap">
                            {selectedTransaction.full_message}
                          </div>
                        </div>
                      </div>
                    </div>
                  </>
                )}

                <div className="flex justify-end pt-2 border-t border-slate-800">
                  <button
                    onClick={() => setSelectedTransaction(null)}
                    className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-white font-semibold text-xs rounded-lg transition"
                  >
                    Close Trace View
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* ========================================================================= */}
      {/* 1. OFFICER AUDIT DASHBOARD TAB                                            */}
      {/* ========================================================================= */}
      {activeSubTab === 'dashboard' && (
        <div className="space-y-6">
          {/* Summary Metric Cards */}
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-4">
            <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl">
              <div className="text-xs text-slate-400 font-medium">Alerts Generated</div>
              <div className="text-2xl font-black text-white mt-1">{totalAlerts}</div>
              <div className="text-[10px] text-slate-500 mt-1">Total in audit trail</div>
            </div>

            <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl">
              <div className="text-xs text-emerald-400 font-medium">Dispatched / Sent</div>
              <div className="text-2xl font-black text-emerald-300 mt-1">{successfulCount}</div>
              <div className="text-[10px] text-emerald-500/80 mt-1">Mock / Twilio dispatch</div>
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
          </div>

          {/* Filters & Controls */}
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 flex flex-wrap items-center justify-between gap-4">
            <div className="flex flex-wrap items-center gap-3 text-xs">
              <div className="flex items-center space-x-1.5 text-slate-400">
                <Filter className="w-3.5 h-3.5" />
                <span className="font-semibold">Filter:</span>
              </div>

              <select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
                className="bg-slate-950 border border-slate-700 text-slate-300 rounded px-2.5 py-1.5 outline-none focus:border-sky-500"
              >
                <option value="">All Statuses</option>
                <option value="SIMULATED_SENT">Simulated Sent</option>
                <option value="FALLBACK_USED">Fallback Used</option>
                <option value="BLOCKED_NO_CONSENT">No Consent</option>
                <option value="BLOCKED_NO_VALIDATED_RULE">No Validated Rule</option>
                <option value="DUPLICATE_SUPPRESSED">Duplicate Suppressed</option>
              </select>

              <select
                value={channelFilter}
                onChange={(e) => setChannelFilter(e.target.value)}
                className="bg-slate-950 border border-slate-700 text-slate-300 rounded px-2.5 py-1.5 outline-none focus:border-sky-500"
              >
                <option value="">All Channels</option>
                <option value="SMS">SMS</option>
                <option value="VOICE">Voice</option>
                <option value="WHATSAPP">WhatsApp</option>
              </select>

              <select
                value={severityFilter}
                onChange={(e) => setSeverityFilter(e.target.value)}
                className="bg-slate-950 border border-slate-700 text-slate-300 rounded px-2.5 py-1.5 outline-none focus:border-sky-500"
              >
                <option value="">All Severities</option>
                <option value="INFO">Info</option>
                <option value="IMPORTANT">Important</option>
                <option value="HIGH">High</option>
              </select>
            </div>

            <div className="flex items-center space-x-3">
              <span className="text-xs text-slate-400">
                Privacy Protection: <strong className="text-emerald-400">Strict Masking Active</strong>
              </span>
              <button
                onClick={fetchAlerts}
                className="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white transition-colors"
                title="Refresh logs"
              >
                <RefreshCw className="w-4 h-4" />
              </button>
            </div>
          </div>

          {/* Alert Audit Table */}
          <div className="bg-slate-900 border border-slate-800 rounded-2xl overflow-hidden shadow-xl">
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs text-slate-300">
                <thead className="bg-slate-950/80 text-slate-400 uppercase text-[10px] tracking-wider border-b border-slate-800">
                  <tr>
                    <th className="py-3 px-4">Timestamp</th>
                    <th className="py-3 px-4">Masked Recipient</th>
                    <th className="py-3 px-4">Crop</th>
                    <th className="py-3 px-4">Decision</th>
                    <th className="py-3 px-4">Severity</th>
                    <th className="py-3 px-4">Channel</th>
                    <th className="py-3 px-4">Status</th>
                    <th className="py-3 px-4">Fallback</th>
                    <th className="py-3 px-4 text-right">Action</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60 font-mono">
                  {loadingAlerts ? (
                    <tr>
                      <td colSpan={9} className="text-center py-10 text-slate-500">
                        Loading audit logs...
                      </td>
                    </tr>
                  ) : alerts.length === 0 ? (
                    <tr>
                      <td colSpan={9} className="text-center py-10 text-slate-500">
                        No audit records match the current filter criteria.
                      </td>
                    </tr>
                  ) : (
                    alerts.map((al) => (
                      <tr key={al.id} className="hover:bg-slate-800/40 transition-colors">
                        <td className="py-3 px-4 whitespace-nowrap text-slate-400">
                          {new Date(al.created_at).toLocaleTimeString()}
                        </td>
                        <td className="py-3 px-4 font-bold text-sky-400 whitespace-nowrap">
                          {al.masked_phone || '******'}
                        </td>
                        <td className="py-3 px-4 capitalize font-sans">{al.crop_id || 'Soybean'}</td>
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
                    <span className="font-mono text-emerald-400 font-bold">
                      {selectedAlert.external_dispatch ? 'TRUE (Twilio SMS)' : 'FALSE (Simulated Mock)'}
                    </span>
                  </div>
                </div>

                <div className="space-y-1.5">
                  <span className="text-xs font-semibold text-slate-400 block">Dispatched Message Body</span>
                  <div className="bg-slate-950 p-4 rounded-xl border border-slate-800 text-xs text-slate-200 whitespace-pre-wrap leading-relaxed font-sans">
                    {selectedAlert.message}
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* ========================================================================= */}
      {/* 2. FARMER SIMULATION & SANDBOX TAB                                        */}
      {/* ========================================================================= */}
      {activeSubTab === 'sandbox' && (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
          {/* Controls Column */}
          <div className="lg:col-span-5 space-y-6">
            <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 space-y-5 shadow-xl">
              <div>
                <h3 className="font-bold text-white text-base flex items-center space-x-2">
                  <Zap className="w-5 h-5 text-amber-400" />
                  <span>Resilience Simulation Setup</span>
                </h3>
                <p className="text-xs text-slate-400">
                  Configure farmer scenario, failure injections, and preview automated fallback.
                </p>
              </div>

              {errorMessage && (
                <div className="bg-rose-950/60 border border-rose-800 text-rose-300 text-xs p-3 rounded-lg">
                  {errorMessage}
                </div>
              )}

              <div className="space-y-4 text-xs">
                <div>
                  <label className="text-slate-400 font-semibold block mb-1">Target Farmer Profile</label>
                  <select
                    value={simFarmerId}
                    onChange={(e) => setSimFarmerId(Number(e.target.value))}
                    className="w-full bg-slate-950 border border-slate-700 text-slate-200 rounded-lg p-2.5 outline-none focus:border-sky-500"
                  >
                    <option value={1}>Farmer #1: Ramesh Patil (Kalmeshwar, Soybean, Marathi - Consented)</option>
                    <option value={2}>Farmer #2: Suresh Deshmukh (Mohpa, Cotton, Marathi - Consented)</option>
                    <option value={3}>Farmer #3: Sunita Wankhede (Dhotra, Soybean, Hindi - Consented)</option>
                    <option value={4}>Farmer #4: Non-Consenting Farmer (Consent Block Test)</option>
                  </select>
                </div>

                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="text-slate-400 font-semibold block mb-1">Crop</label>
                    <select
                      value={simCropId}
                      onChange={(e) => setSimCropId(e.target.value)}
                      className="w-full bg-slate-950 border border-slate-700 text-slate-200 rounded-lg p-2.5 outline-none focus:border-sky-500 capitalize"
                    >
                      <option value="soybean">Soybean</option>
                      <option value="cotton">Cotton</option>
                      <option value="pigeonpea">Pigeonpea</option>
                    </select>
                  </div>
                  <div>
                    <label className="text-slate-400 font-semibold block mb-1">Language</label>
                    <select
                      value={simLanguage}
                      onChange={(e) => setSimLanguage(e.target.value)}
                      className="w-full bg-slate-950 border border-slate-700 text-slate-200 rounded-lg p-2.5 outline-none focus:border-sky-500"
                    >
                      <option value="mr">Marathi (mr)</option>
                      <option value="hi">Hindi (hi)</option>
                      <option value="en">English (en)</option>
                    </select>
                  </div>
                </div>

                <div>
                  <label className="text-slate-400 font-semibold block mb-1">
                    Severity Level (Auto-derived from model if unselected)
                  </label>
                  <select
                    value={simSeverity}
                    onChange={(e) => setSimSeverity(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-700 text-slate-200 rounded-lg p-2.5 outline-none focus:border-sky-500"
                  >
                    <option value="">Auto (Use Live Model / Threshold Engine)</option>
                    <option value="INFO">INFO: SMS Only (Low Risk, SOW_NOW)</option>
                    <option value="IMPORTANT">IMPORTANT: SMS + WhatsApp (Moderate Risk, SOW_PART_NOW)</option>
                    <option value="HIGH">HIGH: Voice Call with SMS Fallback (Elevated Risk, WAIT)</option>
                  </select>
                </div>

                <div>
                  <label className="text-slate-400 font-semibold block mb-1">
                    Channel Preference Override
                  </label>
                  <select
                    value={simChannelPref}
                    onChange={(e) => setSimChannelPref(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-700 text-slate-200 rounded-lg p-2.5 outline-none focus:border-sky-500"
                  >
                    <option value="ALL">Follow Severity Matrix</option>
                    <option value="SMS">Force SMS Only</option>
                    <option value="VOICE">Force Voice Only</option>
                    <option value="WHATSAPP">Force WhatsApp Only</option>
                  </select>
                </div>

                <div>
                  <label className="text-amber-400 font-semibold block mb-1 flex items-center space-x-1">
                    <AlertTriangle className="w-3.5 h-3.5" />
                    <span>Fault Injection (Test Resilience Fallback)</span>
                  </label>
                  <select
                    value={simForceFailure}
                    onChange={(e) => setSimForceFailure(e.target.value)}
                    className="w-full bg-slate-950 border border-amber-800/80 text-amber-200 rounded-lg p-2.5 outline-none focus:border-amber-500"
                  >
                    <option value="">Normal Operation (No Fault)</option>
                    <option value="VOICE">Simulate Voice Failure (Unanswered Call $\to$ Fallback to SMS)</option>
                    <option value="WHATSAPP">Simulate WhatsApp Gateway Timeout</option>
                    <option value="ALL">Simulate Total Outage</option>
                  </select>
                </div>
              </div>

              <div className="pt-2 flex items-center space-x-3">
                <button
                  type="button"
                  onClick={handlePreview}
                  disabled={previewing}
                  className="flex-1 py-2.5 rounded-lg font-semibold text-xs bg-slate-800 hover:bg-slate-700 text-sky-400 border border-slate-700 transition-colors disabled:opacity-50 flex items-center justify-center space-x-1.5"
                >
                  <Eye className="w-4 h-4" />
                  <span>{previewing ? 'Evaluating...' : 'Preview Plan'}</span>
                </button>
                <button
                  type="button"
                  onClick={handleSimulate}
                  disabled={simulating}
                  className="flex-1 py-2.5 rounded-lg font-semibold text-xs bg-sky-500 hover:bg-sky-400 text-white shadow-lg shadow-sky-500/25 transition-all disabled:opacity-50 flex items-center justify-center space-x-1.5"
                >
                  <Send className="w-4 h-4" />
                  <span>{simulating ? 'Simulating...' : 'Simulate Dispatch'}</span>
                </button>
              </div>
            </div>
          </div>

          {/* Results Column */}
          <div className="lg:col-span-7 space-y-6">
            {simResult && (
              <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 space-y-5 shadow-xl">
                <div className="flex items-center justify-between pb-3 border-b border-slate-800">
                  <div className="flex items-center space-x-2">
                    <CheckCircle className="w-5 h-5 text-emerald-400" />
                    <h3 className="font-bold text-white text-base">Simulation Dispatch Result</h3>
                  </div>
                  <div>{getStatusBadge(simResult.status)}</div>
                </div>

                <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
                  <div className="bg-slate-950 p-3 rounded-lg border border-slate-800">
                    <span className="text-slate-500 block">Recipient</span>
                    <span className="font-mono text-sky-300 font-bold">{simResult.masked_phone || '******'}</span>
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
                    <span className="text-slate-500 block">Fallback Used</span>
                    <span className={simResult.fallback_used ? 'text-amber-400 font-bold' : 'text-slate-400'}>
                      {simResult.fallback_used ? 'Yes (SMS Fallback)' : 'No'}
                    </span>
                  </div>
                </div>

                <div className="space-y-1.5">
                  <span className="text-xs font-semibold text-slate-400 block">Dispatched Message Body</span>
                  <div className="bg-slate-950 p-4 rounded-xl border border-slate-800 text-xs text-slate-200 whitespace-pre-wrap leading-relaxed font-sans">
                    {simResult.message}
                  </div>
                </div>
              </div>
            )}

            {previewResult && !simResult && (
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
