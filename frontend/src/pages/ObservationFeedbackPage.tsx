import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import {
  FarmerObservationHistoryItem,
  ObservationSummary,
  Block,
  Farmer
} from '../types';
import {
  CloudRain,
  Sun,
  CloudLightning,
  CheckCircle2,
  AlertTriangle,
  HelpCircle,
  ShieldAlert,
  Database,
  Calendar,
  Send,
  RefreshCw,
  Search,
  Filter,
  Eye,
  X,
  FileSpreadsheet
} from 'lucide-react';

export const ObservationFeedbackPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'officer' | 'farmer'>('officer');
  const [loading, setLoading] = useState<boolean>(true);
  const [blocks, setBlocks] = useState<Block[]>([]);
  const [farmers, setFarmers] = useState<Farmer[]>([]);
  const [summary, setSummary] = useState<ObservationSummary | null>(null);
  const [history, setHistory] = useState<FarmerObservationHistoryItem[]>([]);
  const [selectedObs, setSelectedObs] = useState<FarmerObservationHistoryItem | null>(null);

  // Filters for officer table
  const [filterBlock, setFilterBlock] = useState<string>('all');
  const [filterType, setFilterType] = useState<string>('all');
  const [filterStatus, setFilterStatus] = useState<string>('all');

  // Farmer submission form state
  const [submittingFarmerId, setSubmittingFarmerId] = useState<number>(1);
  const [selectedType, setSelectedType] = useState<'RAIN' | 'DRY' | 'HEAVY_RAIN'>('RAIN');
  const [selectedCrop, setSelectedCrop] = useState<string>('soybean');
  const [obsDate, setObsDate] = useState<string>(new Date().toISOString().split('T')[0]);
  const [obsTime, setObsTime] = useState<string>('18:00');
  const [obsNotes, setObsNotes] = useState<string>('');
  const [submitSuccessMsg, setSubmitSuccessMsg] = useState<string | null>(null);
  const [submitErrorMsg, setSubmitErrorMsg] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);

  const loadData = async () => {
    setLoading(true);
    try {
      const [blocksRes, farmersRes, summaryRes, historyRes] = await Promise.all([
        api.getBlocks(),
        api.getFarmers(),
        api.getObservationSummary(),
        api.getObservationHistory({ limit: 100 })
      ]);
      setBlocks(blocksRes);
      setFarmers(farmersRes);
      setSummary(summaryRes);
      setHistory(historyRes);
      if (farmersRes.length > 0 && !submittingFarmerId) {
        setSubmittingFarmerId(farmersRes[0].id);
      }
    } catch (err: any) {
      console.error('Failed to load observation data:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleFarmerSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    setSubmitSuccessMsg(null);
    setSubmitErrorMsg(null);

    try {
      const res = await api.submitObservation({
        farmer_id: submittingFarmerId,
        observation_type: selectedType,
        observation_date: obsDate,
        observation_time: obsTime,
        crop_id: selectedCrop,
        notes: obsNotes.trim() || undefined
      });

      if (res.status === 'DUPLICATE_OBSERVATION') {
        setSubmitSuccessMsg('Duplicate observation detected: an observation for this date and event type was already recorded. Report suppressed to prevent duplication.');
      } else {
        setSubmitSuccessMsg('Thank you. Your observation has been recorded. Your local ground-truth feedback aids hyper-local weather research.');
      }
      setObsNotes('');
      // Refresh officer data in background
      const [sum, hist] = await Promise.all([
        api.getObservationSummary(),
        api.getObservationHistory({ limit: 100 })
      ]);
      setSummary(sum);
      setHistory(hist);
    } catch (err: any) {
      setSubmitErrorMsg(err.message || 'Failed to record observation.');
    } finally {
      setIsSubmitting(false);
    }
  };

  // Filtered observation list for officer view
  const filteredHistory = history.filter((item) => {
    if (filterBlock !== 'all' && item.block_id !== parseInt(filterBlock, 10)) {
      return false;
    }
    if (filterType !== 'all' && item.observation_type !== filterType) {
      return false;
    }
    if (filterStatus !== 'all' && item.validation_status !== filterStatus) {
      return false;
    }
    return true;
  });

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between pb-6 border-b border-gray-200">
        <div>
          <div className="flex items-center space-x-3">
            <h1 className="text-2xl font-bold text-gray-900">Observation & Validation Feedback Loop</h1>
            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-100 text-emerald-800">
              Phase 6B Verified
            </span>
          </div>
          <p className="mt-1 text-sm text-gray-500">
            Hyper-local crowd ground-truth verification of monsoon events against available reference observations.
          </p>
        </div>

        {/* Global Safety Indicators */}
        <div className="mt-4 md:mt-0 flex flex-wrap gap-2">
          <span className="inline-flex items-center px-3 py-1 rounded-md text-xs font-semibold bg-purple-100 text-purple-800 border border-purple-200">
            <ShieldAlert className="w-3.5 h-3.5 mr-1" />
            No Automated Retraining
          </span>
          <span className="inline-flex items-center px-3 py-1 rounded-md text-xs font-semibold bg-blue-100 text-blue-800 border border-blue-200">
            <Database className="w-3.5 h-3.5 mr-1" />
            Source: FARMER
          </span>
          <span className="inline-flex items-center px-3 py-1 rounded-md text-xs font-semibold bg-amber-100 text-amber-800 border border-amber-200">
            is_operational: false
          </span>
        </div>
      </div>

      {/* Tabs */}
      <div className="mt-6 flex border-b border-gray-200 space-x-8">
        <button
          onClick={() => setActiveTab('officer')}
          className={`pb-4 px-1 text-sm font-medium border-b-2 flex items-center space-x-2 transition-colors ${
            activeTab === 'officer'
              ? 'border-emerald-600 text-emerald-600'
              : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
          }`}
        >
          <FileSpreadsheet className="w-4 h-4" />
          <span>Officer Audit & Validation Analysis</span>
        </button>

        <button
          onClick={() => setActiveTab('farmer')}
          className={`pb-4 px-1 text-sm font-medium border-b-2 flex items-center space-x-2 transition-colors ${
            activeTab === 'farmer'
              ? 'border-emerald-600 text-emerald-600'
              : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
          }`}
        >
          <CloudRain className="w-4 h-4" />
          <span>Farmer Weather Report (Feedback View)</span>
        </button>
      </div>

      {/* Tab 1: Officer Audit & Validation Dashboard */}
      {activeTab === 'officer' && (
        <div className="mt-6 space-y-6">
          {/* KPI Summary Cards */}
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
            <div className="bg-white p-4 rounded-xl border border-gray-200 shadow-sm">
              <p className="text-xs font-medium text-gray-500 uppercase tracking-wider">Total Reports</p>
              <p className="mt-2 text-2xl font-bold text-gray-900">{summary?.total_observations ?? 0}</p>
              <p className="mt-1 text-xs text-gray-400">Crowd submissions</p>
            </div>

            <div className="bg-white p-4 rounded-xl border border-gray-200 shadow-sm">
              <div className="flex items-center justify-between">
                <p className="text-xs font-medium text-gray-500 uppercase tracking-wider">Rain Reports</p>
                <CloudRain className="w-4 h-4 text-blue-500" />
              </div>
              <p className="mt-2 text-2xl font-bold text-blue-600">{summary?.event_distribution?.rain_count ?? 0}</p>
              <p className="mt-1 text-xs text-gray-400">Normal showers</p>
            </div>

            <div className="bg-white p-4 rounded-xl border border-gray-200 shadow-sm">
              <div className="flex items-center justify-between">
                <p className="text-xs font-medium text-gray-500 uppercase tracking-wider">Dry Reports</p>
                <Sun className="w-4 h-4 text-amber-500" />
              </div>
              <p className="mt-2 text-2xl font-bold text-amber-600">{summary?.event_distribution?.dry_count ?? 0}</p>
              <p className="mt-1 text-xs text-gray-400">Sunny / dry spells</p>
            </div>

            <div className="bg-white p-4 rounded-xl border border-gray-200 shadow-sm">
              <div className="flex items-center justify-between">
                <p className="text-xs font-medium text-gray-500 uppercase tracking-wider">Heavy Rain</p>
                <CloudLightning className="w-4 h-4 text-purple-500" />
              </div>
              <p className="mt-2 text-2xl font-bold text-purple-600">{summary?.event_distribution?.heavy_rain_count ?? 0}</p>
              <p className="mt-1 text-xs text-gray-400">&gt;= 64.5mm benchmark</p>
            </div>

            <div className="bg-white p-4 rounded-xl border border-gray-200 shadow-sm">
              <div className="flex items-center justify-between">
                <p className="text-xs font-medium text-gray-500 uppercase tracking-wider">Comparisons</p>
                <Database className="w-4 h-4 text-emerald-500" />
              </div>
              <p className="mt-2 text-2xl font-bold text-gray-900">{summary?.reference_comparisons_count ?? 0}</p>
              <p className="mt-1 text-xs text-gray-400">With co-dated gauge</p>
            </div>

            <div className="bg-white p-4 rounded-xl border border-gray-200 shadow-sm bg-gradient-to-br from-emerald-50 to-white">
              <div className="flex items-center justify-between">
                <p className="text-xs font-medium text-emerald-800 uppercase tracking-wider">Agreement Rate</p>
                <CheckCircle2 className="w-4 h-4 text-emerald-600" />
              </div>
              <p className="mt-2 text-2xl font-bold text-emerald-700">
                {summary?.agreement_rate_pct != null ? `${summary.agreement_rate_pct}%` : 'N/A'}
              </p>
              <p className="mt-1 text-xs text-emerald-600">Reference agreement</p>
            </div>
          </div>

          {/* Analytical Disclaimer Alert */}
          <div className="bg-blue-50 border-l-4 border-blue-500 p-4 rounded-r-lg">
            <div className="flex items-start">
              <HelpCircle className="w-5 h-5 text-blue-500 mt-0.5 mr-3 flex-shrink-0" />
              <div className="text-sm text-blue-700">
                <p className="font-semibold">Analytical Validation Principles (Phase 6B)</p>
                <p className="mt-1">
                  Farmer observations serve as supplementary qualitative verification. Disagreements between farmer reports and weather stations do <strong>not</strong> imply incorrectness or fraudulent reporting due to hyper-local spatial variability and gauge distance.
                  Observations are strictly stored for research and <strong>never automatically retrain forecasting models</strong>.
                </p>
              </div>
            </div>
          </div>

          {/* Filter Bar & Controls */}
          <div className="bg-white p-4 rounded-xl border border-gray-200 shadow-sm flex flex-wrap items-center justify-between gap-4">
            <div className="flex flex-wrap items-center gap-3">
              <span className="text-xs font-medium text-gray-500 flex items-center">
                <Filter className="w-3.5 h-3.5 mr-1" />
                Filter by:
              </span>

              {/* Block Filter */}
              <select
                value={filterBlock}
                onChange={(e) => setFilterBlock(e.target.value)}
                className="text-xs rounded-lg border-gray-300 py-1.5 px-3 focus:ring-emerald-500 focus:border-emerald-500"
              >
                <option value="all">All Blocks</option>
                {blocks.map((b) => (
                  <option key={b.id} value={b.id}>
                    {b.name}
                  </option>
                ))}
              </select>

              {/* Type Filter */}
              <select
                value={filterType}
                onChange={(e) => setFilterType(e.target.value)}
                className="text-xs rounded-lg border-gray-300 py-1.5 px-3 focus:ring-emerald-500 focus:border-emerald-500"
              >
                <option value="all">All Types</option>
                <option value="RAIN">🌧 Rain</option>
                <option value="DRY">☀ Dry</option>
                <option value="HEAVY_RAIN">⛈ Heavy Rain</option>
              </select>

              {/* Status Filter */}
              <select
                value={filterStatus}
                onChange={(e) => setFilterStatus(e.target.value)}
                className="text-xs rounded-lg border-gray-300 py-1.5 px-3 focus:ring-emerald-500 focus:border-emerald-500"
              >
                <option value="all">All Validation Statuses</option>
                <option value="AGREEMENT">Agreement</option>
                <option value="DISAGREEMENT">Disagreement</option>
                <option value="REFERENCE_DATA_UNAVAILABLE">Reference Unavailable</option>
                <option value="PENDING_REVIEW">Pending Review</option>
              </select>
            </div>

            <button
              onClick={loadData}
              disabled={loading}
              className="inline-flex items-center px-3 py-1.5 border border-gray-300 rounded-lg text-xs font-medium text-gray-700 bg-white hover:bg-gray-50"
            >
              <RefreshCw className={`w-3.5 h-3.5 mr-1.5 ${loading ? 'animate-spin' : ''}`} />
              Refresh
            </button>
          </div>

          {/* Observations Table */}
          <div className="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden">
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200 text-sm">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-4 py-3 text-left font-semibold text-gray-600 text-xs">Date & Time</th>
                    <th className="px-4 py-3 text-left font-semibold text-gray-600 text-xs">Village / Block</th>
                    <th className="px-4 py-3 text-left font-semibold text-gray-600 text-xs">Observation</th>
                    <th className="px-4 py-3 text-left font-semibold text-gray-600 text-xs">Crop</th>
                    <th className="px-4 py-3 text-left font-semibold text-gray-600 text-xs">Reference Rainfall</th>
                    <th className="px-4 py-3 text-left font-semibold text-gray-600 text-xs">Validation Status</th>
                    <th className="px-4 py-3 text-right font-semibold text-gray-600 text-xs">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100">
                  {filteredHistory.length === 0 ? (
                    <tr>
                      <td colSpan={7} className="px-4 py-8 text-center text-gray-400">
                        No observations matching the selected filters.
                      </td>
                    </tr>
                  ) : (
                    filteredHistory.map((item) => (
                      <tr key={item.id} className="hover:bg-gray-50 transition-colors">
                        <td className="px-4 py-3 text-gray-900 whitespace-nowrap">
                          <div className="font-medium">{item.observation_date}</div>
                          {item.observation_time && (
                            <div className="text-xs text-gray-400">{item.observation_time}</div>
                          )}
                        </td>

                        <td className="px-4 py-3 whitespace-nowrap">
                          <div className="font-medium text-gray-900">{item.village_name || 'Village #' + item.village_id}</div>
                          <div className="text-xs text-gray-400">{item.block_name || 'Block #' + item.block_id}</div>
                        </td>

                        <td className="px-4 py-3 whitespace-nowrap">
                          {item.observation_type === 'RAIN' && (
                            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold bg-blue-100 text-blue-800">
                              🌧 Rain
                            </span>
                          )}
                          {item.observation_type === 'DRY' && (
                            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold bg-amber-100 text-amber-800">
                              ☀ Dry
                            </span>
                          )}
                          {item.observation_type === 'HEAVY_RAIN' && (
                            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold bg-purple-100 text-purple-800">
                              ⛈ Heavy Rain
                            </span>
                          )}
                        </td>

                        <td className="px-4 py-3 text-gray-700 whitespace-nowrap capitalize">
                          {item.crop_id || 'N/A'}
                        </td>

                        <td className="px-4 py-3 whitespace-nowrap">
                          {item.reference_rainfall_mm != null ? (
                            <span className="font-mono text-xs font-medium text-gray-800">
                              {item.reference_rainfall_mm.toFixed(1)} mm
                            </span>
                          ) : (
                            <span className="text-xs text-gray-400 italic">No reference data</span>
                          )}
                        </td>

                        <td className="px-4 py-3 whitespace-nowrap">
                          {item.validation_status === 'AGREEMENT' && (
                            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-100 text-emerald-800">
                              <CheckCircle2 className="w-3 h-3 mr-1" />
                              Agreement
                            </span>
                          )}
                          {item.validation_status === 'DISAGREEMENT' && (
                            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold bg-amber-100 text-amber-800">
                              <AlertTriangle className="w-3 h-3 mr-1" />
                              Disagreement
                            </span>
                          )}
                          {item.validation_status === 'REFERENCE_DATA_UNAVAILABLE' && (
                            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold bg-gray-100 text-gray-700">
                              Ref Unavailable
                            </span>
                          )}
                          {item.validation_status === 'PENDING_REVIEW' && (
                            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold bg-blue-100 text-blue-700">
                              Pending Review
                            </span>
                          )}
                        </td>

                        <td className="px-4 py-3 text-right whitespace-nowrap">
                          <button
                            onClick={() => setSelectedObs(item)}
                            className="inline-flex items-center text-xs text-emerald-600 hover:text-emerald-800 font-medium"
                          >
                            <Eye className="w-3.5 h-3.5 mr-1" />
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
        </div>
      )}

      {/* Tab 2: Farmer Weather Report (Feedback View) */}
      {activeTab === 'farmer' && (
        <div className="mt-6 max-w-2xl mx-auto space-y-6">
          <div className="bg-white p-6 sm:p-8 rounded-2xl border border-gray-200 shadow-md">
            <div className="text-center pb-6 border-b border-gray-100">
              <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200 mb-2">
                🌾 Farmer Feedback Interface (शेतकरी अहवाल)
              </span>
              <h2 className="text-xl font-bold text-gray-900">How was the weather today?</h2>
              <p className="text-xs text-gray-500 mt-1">
                आज आपल्या शेतात अथवा गावात हवामान कसे होते? कृपया नोंदवा.
              </p>
            </div>

            {submitSuccessMsg && (
              <div className="mt-4 p-4 rounded-xl bg-emerald-50 border border-emerald-200 text-sm text-emerald-800 flex items-start space-x-3">
                <CheckCircle2 className="w-5 h-5 text-emerald-600 flex-shrink-0 mt-0.5" />
                <div>
                  <p className="font-semibold">{submitSuccessMsg}</p>
                  <p className="text-xs mt-1 text-emerald-700">
                    Observation status: RECORDED. No automatic ML retraining triggered.
                  </p>
                </div>
              </div>
            )}

            {submitErrorMsg && (
              <div className="mt-4 p-4 rounded-xl bg-red-50 border border-red-200 text-sm text-red-800 flex items-start space-x-3">
                <AlertTriangle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
                <div>
                  <p className="font-semibold">{submitErrorMsg}</p>
                </div>
              </div>
            )}

            <form onSubmit={handleFarmerSubmit} className="mt-6 space-y-6">
              {/* Event Type Big Buttons */}
              <div>
                <label className="block text-xs font-semibold text-gray-700 uppercase tracking-wider mb-3 text-center">
                  Select Today's Weather Event
                </label>
                <div className="grid grid-cols-3 gap-3">
                  <button
                    type="button"
                    onClick={() => setSelectedType('RAIN')}
                    className={`flex flex-col items-center justify-center p-4 rounded-xl border-2 transition-all ${
                      selectedType === 'RAIN'
                        ? 'border-blue-500 bg-blue-50 text-blue-900 shadow-sm'
                        : 'border-gray-200 bg-white text-gray-700 hover:border-blue-300'
                    }`}
                  >
                    <span className="text-3xl mb-1">🌧</span>
                    <span className="font-bold text-sm">Rain</span>
                    <span className="text-xs text-gray-500">पाऊस</span>
                  </button>

                  <button
                    type="button"
                    onClick={() => setSelectedType('DRY')}
                    className={`flex flex-col items-center justify-center p-4 rounded-xl border-2 transition-all ${
                      selectedType === 'DRY'
                        ? 'border-amber-500 bg-amber-50 text-amber-900 shadow-sm'
                        : 'border-gray-200 bg-white text-gray-700 hover:border-amber-300'
                    }`}
                  >
                    <span className="text-3xl mb-1">☀</span>
                    <span className="font-bold text-sm">Dry</span>
                    <span className="text-xs text-gray-500">कोरडे</span>
                  </button>

                  <button
                    type="button"
                    onClick={() => setSelectedType('HEAVY_RAIN')}
                    className={`flex flex-col items-center justify-center p-4 rounded-xl border-2 transition-all ${
                      selectedType === 'HEAVY_RAIN'
                        ? 'border-purple-500 bg-purple-50 text-purple-900 shadow-sm'
                        : 'border-gray-200 bg-white text-gray-700 hover:border-purple-300'
                    }`}
                  >
                    <span className="text-3xl mb-1">⛈</span>
                    <span className="font-bold text-sm">Heavy Rain</span>
                    <span className="text-xs text-gray-500">मुसळधार पाऊस</span>
                  </button>
                </div>
              </div>

              {/* Farmer and Crop */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-medium text-gray-700 mb-1">
                    Select Farmer (Demo)
                  </label>
                  <select
                    value={submittingFarmerId}
                    onChange={(e) => setSubmittingFarmerId(parseInt(e.target.value, 10))}
                    className="w-full text-xs rounded-lg border-gray-300 py-2 focus:ring-emerald-500 focus:border-emerald-500"
                  >
                    {farmers.map((f) => (
                      <option key={f.id} value={f.id}>
                        Farmer #{f.id} (Preferred: {f.preferred_language})
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-medium text-gray-700 mb-1">
                    Select Crop (पिक)
                  </label>
                  <select
                    value={selectedCrop}
                    onChange={(e) => setSelectedCrop(e.target.value)}
                    className="w-full text-xs rounded-lg border-gray-300 py-2 focus:ring-emerald-500 focus:border-emerald-500"
                  >
                    <option value="soybean">Soybean (सोयाबीन)</option>
                    <option value="cotton">Cotton (कापूस)</option>
                    <option value="pigeonpea">Pigeonpea / Tur (तूर)</option>
                    <option value="maize">Maize (मका)</option>
                  </select>
                </div>
              </div>

              {/* Date & Time */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-medium text-gray-700 mb-1">
                    Observation Date
                  </label>
                  <input
                    type="date"
                    value={obsDate}
                    onChange={(e) => setObsDate(e.target.value)}
                    max={new Date().toISOString().split('T')[0]}
                    className="w-full text-xs rounded-lg border-gray-300 py-2 focus:ring-emerald-500 focus:border-emerald-500"
                  />
                </div>

                <div>
                  <label className="block text-xs font-medium text-gray-700 mb-1">
                    Observation Time (Optional)
                  </label>
                  <input
                    type="time"
                    value={obsTime}
                    onChange={(e) => setObsTime(e.target.value)}
                    className="w-full text-xs rounded-lg border-gray-300 py-2 focus:ring-emerald-500 focus:border-emerald-500"
                  />
                </div>
              </div>

              {/* Short Note */}
              <div>
                <label className="block text-xs font-medium text-gray-700 mb-1">
                  Field Observations / Short Note (काही विशेष निरीक्षण?)
                </label>
                <textarea
                  value={obsNotes}
                  onChange={(e) => setObsNotes(e.target.value)}
                  placeholder="e.g. Heavy showers for 30 minutes in western plots..."
                  maxLength={500}
                  rows={2}
                  className="w-full text-xs rounded-lg border-gray-300 py-2 focus:ring-emerald-500 focus:border-emerald-500"
                />
              </div>

              {/* Submit Button */}
              <button
                type="submit"
                disabled={isSubmitting}
                className="w-full flex items-center justify-center py-2.5 px-4 border border-transparent rounded-xl shadow-sm text-sm font-semibold text-white bg-emerald-600 hover:bg-emerald-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-emerald-500 transition-colors disabled:opacity-50"
              >
                <Send className="w-4 h-4 mr-2" />
                {isSubmitting ? 'Recording Observation...' : 'Submit Weather Report'}
              </button>
            </form>
          </div>
        </div>
      )}

      {/* Observation Inspection Detail Modal */}
      {selectedObs && (
        <div className="fixed inset-0 z-50 overflow-y-auto bg-black bg-opacity-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-lg w-full p-6 shadow-2xl relative">
            <button
              onClick={() => setSelectedObs(null)}
              className="absolute top-4 right-4 text-gray-400 hover:text-gray-600"
            >
              <X className="w-5 h-5" />
            </button>

            <div className="flex items-center space-x-2 pb-4 border-b border-gray-200">
              <FileSpreadsheet className="w-5 h-5 text-emerald-600" />
              <h3 className="text-lg font-bold text-gray-900">
                Observation #{selectedObs.observation_id} Audit
              </h3>
            </div>

            <div className="mt-4 space-y-3 text-xs">
              <div className="grid grid-cols-2 gap-2 bg-gray-50 p-3 rounded-lg">
                <div>
                  <span className="text-gray-500">Farmer ID:</span>
                  <div className="font-semibold text-gray-800">#{selectedObs.farmer_id}</div>
                </div>
                <div>
                  <span className="text-gray-500">Phone (Masked):</span>
                  <div className="font-mono font-semibold text-gray-800">{selectedObs.masked_phone || '******0000'}</div>
                </div>
                <div>
                  <span className="text-gray-500">Village / Block:</span>
                  <div className="font-semibold text-gray-800">
                    {selectedObs.village_name || 'N/A'} ({selectedObs.block_name || 'Block ' + selectedObs.block_id})
                  </div>
                </div>
                <div>
                  <span className="text-gray-500">Crop:</span>
                  <div className="font-semibold text-gray-800 capitalize">{selectedObs.crop_id || 'N/A'}</div>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-2 bg-blue-50 p-3 rounded-lg">
                <div>
                  <span className="text-blue-600 font-medium">Reported Event:</span>
                  <div className="text-sm font-bold text-blue-900">{selectedObs.observation_type}</div>
                </div>
                <div>
                  <span className="text-blue-600 font-medium">Reference Rainfall:</span>
                  <div className="text-sm font-bold text-blue-900">
                    {selectedObs.reference_rainfall_mm != null ? `${selectedObs.reference_rainfall_mm.toFixed(1)} mm` : 'Unavailable'}
                  </div>
                </div>
              </div>

              <div className="bg-gray-50 p-3 rounded-lg space-y-1">
                <span className="text-gray-500 font-medium">Comparison & Validation Notes:</span>
                <p className="text-gray-800 text-xs italic">
                  {selectedObs.comparison_notes || 'Pending comparison analysis.'}
                </p>
              </div>

              {selectedObs.notes && (
                <div className="bg-gray-50 p-3 rounded-lg space-y-1">
                  <span className="text-gray-500 font-medium">Farmer's Qualitative Notes:</span>
                  <p className="text-gray-800 text-xs">{selectedObs.notes}</p>
                </div>
              )}

              <div className="bg-amber-50 border border-amber-200 p-3 rounded-lg text-amber-800 text-xs">
                <strong>System Safety Guarantee:</strong> Farmer observations are collected as supplementary analytical signals. Disagreement does not imply inaccuracy. Observations are <strong>strictly decoupled from automated ML model retraining</strong>.
              </div>
            </div>

            <div className="mt-6 flex justify-end">
              <button
                onClick={() => setSelectedObs(null)}
                className="px-4 py-2 bg-gray-100 hover:bg-gray-200 text-gray-800 text-xs font-semibold rounded-lg transition-colors"
              >
                Close Audit View
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
