import React, { useState, useEffect } from 'react';
import {
  Database,
  Layers,
  Calendar,
  AlertTriangle,
  CheckCircle2,
  ShieldAlert,
  Clock,
  Filter,
  RefreshCw,
  TrendingUp,
  Info,
  Sliders
} from 'lucide-react';
import { api } from '../services/api';
import { PredictionDatasetSummary, PredictionRecord } from '../types';

export const PredictionDatasetPage: React.FC = () => {
  const [summary, setSummary] = useState<PredictionDatasetSummary | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [recordsLoading, setRecordsLoading] = useState<boolean>(false);
  const [selectedBlock, setSelectedBlock] = useState<string>('BLK001');
  const [records, setRecords] = useState<PredictionRecord[]>([]);
  const [totalRecords, setTotalRecords] = useState<number>(0);
  const [selectedHorizon, setSelectedHorizon] = useState<number>(7);
  const [qualityFilter, setQualityFilter] = useState<string>('ALL');

  const blockOptions = [
    { id: 'BLK001', name: 'Nagpur Rural (BLK001)' },
    { id: 'BLK002', name: 'Wardha East (BLK002)' },
    { id: 'BLK003', name: 'Amravati Central (BLK003)' },
  ];

  const fetchSummary = async () => {
    try {
      const data = await api.getPredictionSummary();
      setSummary(data);
    } catch (err) {
      console.error('Failed to load prediction summary:', err);
    }
  };

  const fetchBlockRecords = async (blockId: string, qFilter: string) => {
    setRecordsLoading(true);
    try {
      const filterParam = qFilter === 'ALL' ? undefined : qFilter;
      const res = await api.getPredictionRecords(blockId, 50, 0, filterParam);
      setRecords(res.records || []);
      setTotalRecords(res.total_records || 0);
    } catch (err) {
      console.error('Failed to load block prediction records:', err);
    } finally {
      setRecordsLoading(false);
    }
  };

  useEffect(() => {
    const load = async () => {
      setLoading(true);
      await fetchSummary();
      await fetchBlockRecords(selectedBlock, qualityFilter);
      setLoading(false);
    };
    load();
  }, []);

  useEffect(() => {
    fetchBlockRecords(selectedBlock, qualityFilter);
  }, [selectedBlock, qualityFilter]);

  return (
    <div className="space-y-8 pb-16">
      {/* Header Banner */}
      <div className="relative overflow-hidden rounded-2xl bg-gradient-to-br from-slate-900 via-slate-800 to-indigo-950 p-6 sm:p-8 border border-slate-700/60 shadow-xl">
        <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div className="space-y-3">
            <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-indigo-500/10 border border-indigo-400/30 text-indigo-300 text-xs font-semibold">
              <Database className="w-3.5 h-3.5" />
              <span>PHASE 3A: PREDICTIVE DATASET & TARGET ENGINEERING</span>
            </div>
            <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
              Supervised Prediction Dataset
            </h1>
            <p className="text-sm text-slate-300 max-w-2xl leading-relaxed">
              Backward-looking predictors paired with strictly causal future event horizons.
              Engineered for baseline classification models in Phase 3B.
            </p>
          </div>

          {/* Model Status Badge */}
          <div className="flex flex-col items-start md:items-end justify-center bg-slate-950/60 backdrop-blur-md px-5 py-4 rounded-xl border border-amber-500/30 space-y-1">
            <div className="flex items-center space-x-2 text-amber-400 font-semibold text-sm">
              <AlertTriangle className="w-4 h-4" />
              <span>Model Status</span>
            </div>
            <div className="text-xs font-mono uppercase tracking-wider text-slate-300">
              Prediction model not trained yet
            </div>
            <p className="text-[11px] text-slate-400 text-left md:text-right">
              No fake probabilities or mock forecasts displayed.
            </p>
          </div>
        </div>
      </div>

      {/* Strict Leakage Guarantee Card */}
      <div className="rounded-xl bg-slate-900/90 border border-emerald-500/30 p-5 shadow-lg flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div className="flex items-start space-x-3.5">
          <div className="p-2.5 rounded-lg bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 mt-0.5">
            <ShieldAlert className="w-5 h-5" />
          </div>
          <div className="space-y-1">
            <div className="flex items-center space-x-2">
              <h2 className="text-sm font-bold text-emerald-300">Data Leakage Audit: Strict Separation Enforced</h2>
              <span className="px-2 py-0.5 text-[10px] font-bold rounded-full bg-emerald-500/20 text-emerald-300 uppercase">
                {summary?.leakage_status || 'VERIFIED'}
              </span>
            </div>
            <p className="text-xs text-slate-400 leading-normal max-w-3xl">
              For prediction date <code className="text-emerald-400">T</code>, all features are computed exclusively from observations <code className="text-emerald-400">&le; T</code>.
              Target horizons strictly evaluate dates <code className="text-emerald-400">&gt; T</code> up to <code className="text-emerald-400">T + N</code> (current day <code className="text-emerald-400">T</code> is strictly excluded).
            </p>
          </div>
        </div>
        <div className="flex items-center space-x-2 text-xs text-slate-300 bg-slate-950 px-3 py-2 rounded-lg border border-slate-800">
          <CheckCircle2 className="w-4 h-4 text-emerald-400" />
          <span>Zero Future Leakage</span>
        </div>
      </div>

      {/* Dataset Overview Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="rounded-xl bg-slate-900/80 border border-slate-800 p-4 space-y-1">
          <div className="flex items-center justify-between text-slate-400">
            <span className="text-xs font-medium uppercase tracking-wider">Prediction Rows</span>
            <Layers className="w-4 h-4 text-sky-400" />
          </div>
          <div className="text-2xl font-bold text-white">
            {loading ? '...' : (summary?.rows ?? 0).toLocaleString()}
          </div>
          <div className="text-[11px] text-slate-400">
            Across {summary?.block_count || 0} blocks
          </div>
        </div>

        <div className="rounded-xl bg-slate-900/80 border border-slate-800 p-4 space-y-1">
          <div className="flex items-center justify-between text-slate-400">
            <span className="text-xs font-medium uppercase tracking-wider">Historical Years</span>
            <Calendar className="w-4 h-4 text-indigo-400" />
          </div>
          <div className="text-2xl font-bold text-white">
            {loading ? '...' : (summary?.years?.join(', ') || 'N/A')}
          </div>
          <div className="text-[11px] text-amber-400/90 flex items-center space-x-1">
            <Info className="w-3 h-3 flex-shrink-0" />
            <span>Single-year demo data</span>
          </div>
        </div>

        <div className="rounded-xl bg-slate-900/80 border border-slate-800 p-4 space-y-1">
          <div className="flex items-center justify-between text-slate-400">
            <span className="text-xs font-medium uppercase tracking-wider">Prediction Horizons</span>
            <Clock className="w-4 h-4 text-teal-400" />
          </div>
          <div className="text-2xl font-bold text-white">
            {loading ? '...' : `${summary?.horizons?.length || 4} Windows`}
          </div>
          <div className="text-[11px] text-slate-400">
            {summary?.horizons ? summary.horizons.map(h => `${h}d`).join(', ') : '7d, 14d, 21d, 30d'}
          </div>
        </div>

        <div className="rounded-xl bg-slate-900/80 border border-slate-800 p-4 space-y-1">
          <div className="flex items-center justify-between text-slate-400">
            <span className="text-xs font-medium uppercase tracking-wider">Quality Flags</span>
            <AlertTriangle className="w-4 h-4 text-amber-400" />
          </div>
          <div className="text-2xl font-bold text-white">
            {loading ? '...' : `${summary?.quality_statistics?.insufficient_history_rows || 0} History Limit`}
          </div>
          <div className="text-[11px] text-slate-400">
            {summary?.quality_statistics?.missing_features ? Object.keys(summary.quality_statistics.missing_features).length : 0} missing features
          </div>
        </div>
      </div>

      {/* Target Distribution Breakdown */}
      <div className="rounded-xl bg-slate-900 border border-slate-800 p-6 space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h2 className="text-lg font-bold text-white flex items-center space-x-2">
              <TrendingUp className="w-5 h-5 text-sky-400" />
              <span>Future Target Distributions</span>
            </h2>
            <p className="text-xs text-slate-400 mt-1">
              Binary label balance across prediction horizons (1 = event occurs strictly in (T+1 &rarr; T+N)).
            </p>
          </div>

          {/* Horizon Selector */}
          <div className="flex items-center space-x-1 bg-slate-950 p-1 rounded-lg border border-slate-800">
            {(summary?.horizons || [7, 14, 21, 30]).map((h) => (
              <button
                key={h}
                onClick={() => setSelectedHorizon(h)}
                className={`px-3 py-1.5 text-xs font-semibold rounded-md transition-colors ${
                  selectedHorizon === h
                    ? 'bg-sky-500 text-white shadow'
                    : 'text-slate-400 hover:text-white'
                }`}
              >
                {h}-Day Horizon
              </button>
            ))}
          </div>
        </div>

        {/* Target Cards for Selected Horizon */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
          {[
            { key: 'onset', label: 'Onset Trigger', desc: 'Primary onset within horizon' },
            { key: 'false_onset', label: 'False Onset', desc: 'Onset followed by dry spell' },
            { key: 'break', label: 'Break Episode Start', desc: 'Qualifying break begins (start date)' },
            { key: 'heavy_rain', label: 'Heavy Rain Risk', desc: '&ge; 64.5mm rainfall event' },
            { key: 'revival', label: 'Revival Event', desc: 'Post-break rainfall resurgence' },
          ].map((target) => {
            const colName = `target_${target.key}_${selectedHorizon}d`;
            const stats = summary?.target_distributions?.[colName];
            const pos = stats?.positive_count ?? 0;
            const neg = stats?.negative_count ?? 0;
            const rate = stats?.positive_rate_pct ?? 0;

            return (
              <div
                key={target.key}
                className="rounded-lg bg-slate-950 border border-slate-800/80 p-4 space-y-2.5 hover:border-slate-700 transition-colors"
              >
                <div className="space-y-0.5">
                  <div className="text-xs font-bold text-white">{target.label}</div>
                  <div className="text-[10px] text-slate-400">{target.desc}</div>
                </div>

                <div className="pt-1 flex items-baseline justify-between">
                  <span className="text-xl font-bold text-sky-400">{pos}</span>
                  <span className="text-xs font-medium text-slate-400">/ {pos + neg} rows</span>
                </div>

                {/* Progress Bar */}
                <div className="w-full bg-slate-800 rounded-full h-1.5 overflow-hidden">
                  <div
                    className="bg-sky-500 h-1.5 rounded-full transition-all duration-300"
                    style={{ width: `${Math.min(100, rate)}%` }}
                  />
                </div>

                <div className="flex justify-between items-center text-[10px] text-slate-400">
                  <span>Class rate:</span>
                  <span className="font-semibold text-slate-200">{rate}% pos</span>
                </div>
              </div>
            );
          })}
        </div>

        <div className="text-[11px] text-slate-400 italic bg-slate-950/60 p-3 rounded-lg border border-slate-800/60">
          <strong>Note on Break Episodes:</strong> In accordance with meteorological practice, <code className="text-sky-300">target_break_Nd</code> records whether a qualifying break episode <em>starts</em> within the horizon, rather than treating every consecutive dry day as a separate independent event.
        </div>
      </div>

      {/* Block Inspection & Feature Browser */}
      <div className="rounded-xl bg-slate-900 border border-slate-800 p-6 space-y-6">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <h2 className="text-lg font-bold text-white flex items-center space-x-2">
              <Sliders className="w-5 h-5 text-indigo-400" />
              <span>Block Predictor & Target Browser</span>
            </h2>
            <p className="text-xs text-slate-400 mt-1">
              Inspect engineered rows for a block. Observe strict causal feature values vs future targets.
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-3">
            {/* Block selector */}
            <div className="flex items-center space-x-2">
              <span className="text-xs text-slate-400">Block:</span>
              <select
                value={selectedBlock}
                onChange={(e) => setSelectedBlock(e.target.value)}
                className="bg-slate-950 border border-slate-700 text-xs text-white rounded-lg px-3 py-1.5 focus:outline-none focus:border-sky-500"
              >
                {blockOptions.map((b) => (
                  <option key={b.id} value={b.id}>
                    {b.name}
                  </option>
                ))}
              </select>
            </div>

            {/* Quality filter */}
            <div className="flex items-center space-x-2">
              <span className="text-xs text-slate-400">Quality:</span>
              <select
                value={qualityFilter}
                onChange={(e) => setQualityFilter(e.target.value)}
                className="bg-slate-950 border border-slate-700 text-xs text-white rounded-lg px-3 py-1.5 focus:outline-none focus:border-sky-500"
              >
                <option value="ALL">All Records</option>
                <option value="GOOD">GOOD</option>
                <option value="INSUFFICIENT_HISTORY">INSUFFICIENT_HISTORY</option>
              </select>
            </div>

            <button
              onClick={() => fetchBlockRecords(selectedBlock, qualityFilter)}
              className="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 transition-colors"
              title="Refresh"
            >
              <RefreshCw className={`w-4 h-4 ${recordsLoading ? 'animate-spin' : ''}`} />
            </button>
          </div>
        </div>

        {/* Data Table */}
        <div className="overflow-x-auto rounded-lg border border-slate-800">
          <table className="w-full text-left text-xs text-slate-300">
            <thead className="bg-slate-950/80 text-[11px] uppercase tracking-wider text-slate-400 border-b border-slate-800">
              <tr>
                <th className="px-3 py-2.5">Date (T)</th>
                <th className="px-3 py-2.5">Rain (mm)</th>
                <th className="px-3 py-2.5">Rain 7d</th>
                <th className="px-3 py-2.5">Rain 30d</th>
                <th className="px-3 py-2.5">Dry/Wet Days</th>
                <th className="px-3 py-2.5">Change 7d</th>
                <th className="px-3 py-2.5">Monsoon?</th>
                <th className="px-3 py-2.5 text-center text-sky-400 bg-sky-950/20 border-l border-r border-slate-800">
                  Target Onset (7d)
                </th>
                <th className="px-3 py-2.5 text-center text-amber-400 bg-amber-950/20 border-r border-slate-800">
                  Target Break (7d)
                </th>
                <th className="px-3 py-2.5 text-center text-rose-400 bg-rose-950/20 border-r border-slate-800">
                  Target Heavy (7d)
                </th>
                <th className="px-3 py-2.5">Quality Flag</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 font-mono text-[11px]">
              {recordsLoading ? (
                <tr>
                  <td colSpan={11} className="px-4 py-8 text-center text-slate-400 font-sans">
                    Loading prediction records...
                  </td>
                </tr>
              ) : records.length === 0 ? (
                <tr>
                  <td colSpan={11} className="px-4 py-8 text-center text-slate-400 font-sans">
                    No records found matching filters.
                  </td>
                </tr>
              ) : (
                records.map((r, idx) => (
                  <tr key={idx} className="hover:bg-slate-800/40 transition-colors">
                    <td className="px-3 py-2 font-semibold text-white">{r.prediction_date}</td>
                    <td className="px-3 py-2">{r.rainfall_mm.toFixed(1)}</td>
                    <td className="px-3 py-2">{r.rainfall_7d.toFixed(1)}</td>
                    <td className="px-3 py-2">{r.rainfall_30d.toFixed(1)}</td>
                    <td className="px-3 py-2">
                      <span className="text-amber-400">{r.dry_spell_days}d dry</span> /{' '}
                      <span className="text-emerald-400">{r.wet_spell_days}d wet</span>
                    </td>
                    <td className="px-3 py-2">
                      {r.rainfall_change_7d !== null && r.rainfall_change_7d !== undefined
                        ? (r.rainfall_change_7d >= 0 ? `+${r.rainfall_change_7d.toFixed(1)}` : r.rainfall_change_7d.toFixed(1))
                        : '-'}
                    </td>
                    <td className="px-3 py-2">
                      {r.monsoon_month_flag === 1 ? (
                        <span className="px-1.5 py-0.5 rounded bg-emerald-500/20 text-emerald-300 text-[10px]">YES</span>
                      ) : (
                        <span className="px-1.5 py-0.5 rounded bg-slate-800 text-slate-400 text-[10px]">NO</span>
                      )}
                    </td>
                    {/* Future Targets */}
                    <td className="px-3 py-2 text-center bg-sky-950/10 border-l border-r border-slate-800">
                      {r.target_onset_7d === 1 ? (
                        <span className="px-2 py-0.5 rounded bg-sky-500 text-slate-950 font-bold text-[10px]">1</span>
                      ) : (
                        <span className="text-slate-600">0</span>
                      )}
                    </td>
                    <td className="px-3 py-2 text-center bg-amber-950/10 border-r border-slate-800">
                      {r.target_break_7d === 1 ? (
                        <span className="px-2 py-0.5 rounded bg-amber-400 text-slate-950 font-bold text-[10px]">1</span>
                      ) : (
                        <span className="text-slate-600">0</span>
                      )}
                    </td>
                    <td className="px-3 py-2 text-center bg-rose-950/10 border-r border-slate-800">
                      {r.target_heavy_rain_7d === 1 ? (
                        <span className="px-2 py-0.5 rounded bg-rose-500 text-white font-bold text-[10px]">1</span>
                      ) : (
                        <span className="text-slate-600">0</span>
                      )}
                    </td>
                    <td className="px-3 py-2">
                      <span
                        className={`px-2 py-0.5 rounded text-[10px] font-semibold ${
                          r.data_quality_flag === 'GOOD'
                            ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                            : 'bg-amber-500/10 text-amber-400 border border-amber-500/20'
                        }`}
                      >
                        {r.data_quality_flag}
                      </span>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        <div className="flex items-center justify-between text-xs text-slate-400">
          <span>Showing up to {records.length} records of {totalRecords} total for {selectedBlock}</span>
          <span className="italic">All targets strictly predict events occurring on dates &gt; T.</span>
        </div>
      </div>
    </div>
  );
};
