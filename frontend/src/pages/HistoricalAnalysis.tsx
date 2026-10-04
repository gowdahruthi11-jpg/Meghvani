import React, { useState, useEffect } from 'react';
import {
  CloudRain,
  Flame,
  AlertTriangle,
  RefreshCw,
  Calendar,
  Layers,
  Sparkles,
  BarChart2,
  Filter,
  CheckCircle2,
  Info
} from 'lucide-react';
import { api } from '../services/api';
import { HistoricalSummary, HistoricalRecord } from '../types';

export const HistoricalAnalysis: React.FC = () => {
  const [summary, setSummary] = useState<HistoricalSummary | null>(null);
  const [selectedBlock, setSelectedBlock] = useState<string>('BLK001');
  const [records, setRecords] = useState<HistoricalRecord[]>([]);
  const [filterEvent, setFilterEvent] = useState<string>('ALL');
  const [loading, setLoading] = useState<boolean>(true);
  const [processing, setProcessing] = useState<boolean>(false);
  const [processMessage, setProcessMessage] = useState<string | null>(null);
  const [hoveredRecord, setHoveredRecord] = useState<HistoricalRecord | null>(null);

  const blockOptions = [
    { id: 'BLK001', name: 'Nagpur Rural (BLK001)' },
    { id: 'BLK002', name: 'Wardha East (BLK002)' },
    { id: 'BLK003', name: 'Amravati Central (BLK003)' },
  ];

  const fetchSummary = async () => {
    try {
      const data = await api.getHistoricalSummary();
      setSummary(data);
    } catch (err) {
      console.error('Error fetching historical summary:', err);
    }
  };

  const fetchRecords = async (blockId: string) => {
    setLoading(true);
    try {
      const res = await api.getHistoricalBlockTimeline(blockId, 365);
      setRecords(res.records || []);
    } catch (err) {
      console.error('Error fetching block timeline:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSummary();
    fetchRecords(selectedBlock);
  }, [selectedBlock]);

  const handleReprocess = async () => {
    setProcessing(true);
    setProcessMessage(null);
    try {
      const res = await api.processHistoricalData();
      setProcessMessage(res.message);
      await fetchSummary();
      await fetchRecords(selectedBlock);
    } catch (err: any) {
      setProcessMessage(`Error re-processing: ${err.message}`);
    } finally {
      setProcessing(false);
    }
  };

  // Filter records by event type
  const filteredRecords = records.filter((r) => {
    if (filterEvent === 'ALL') return true;
    if (filterEvent === 'ONSET') return r.onset_trigger === 1;
    if (filterEvent === 'FALSE_ONSET') return r.false_onset === 1;
    if (filterEvent === 'BREAK') return r.break_event === 1;
    if (filterEvent === 'HEAVY_RAIN') return r.heavy_rain_event === 1;
    if (filterEvent === 'REVIVAL') return r.revival_event === 1;
    return true;
  });

  // Calculate timeline max for SVG scaling
  const maxRainfall = Math.max(10, ...records.map((r) => r.rainfall_mm || 0));

  return (
    <div className="space-y-6 pb-12">
      {/* Top Header */}
      <div className="agri-card p-6 bg-white border-stone-200">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div>
            <div className="flex items-center space-x-2">
              <span className="text-2xl">📊</span>
              <h1 className="text-xl sm:text-2xl font-bold text-stone-900 tracking-tight flex items-center gap-2">
                Historical Rainfall & Event Engine
              </h1>
              <span className="px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-emerald-100 text-emerald-800 border border-emerald-300">
                Phase 2
              </span>
            </div>
            <p className="text-xs text-stone-600 mt-1 max-w-2xl leading-relaxed">
              Deterministic agro-meteorological feature engineering, rolling precipitation metrics, and prototype event detection labels.
            </p>
          </div>

          <button
            onClick={handleReprocess}
            disabled={processing}
            className="flex items-center space-x-2 px-3.5 py-2 rounded-xl bg-forest-800 hover:bg-forest-900 text-white text-xs font-bold transition shadow-2xs disabled:opacity-50 self-start sm:self-auto"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${processing ? 'animate-spin' : ''}`} />
            <span>{processing ? 'Processing Engine...' : 'Re-process Dataset'}</span>
          </button>
        </div>

        {/* Scientific & Regulatory Disclaimer Banner */}
        <div className="mt-4 p-3.5 rounded-xl bg-amber-50 border border-amber-200 text-amber-900 text-xs flex items-start space-x-3">
          <Info className="w-5 h-5 text-amber-700 shrink-0 mt-0.5" />
          <div className="space-y-0.5">
            <span className="font-bold text-amber-950 uppercase tracking-wide">
              Prototype Heuristic Thresholds Notice
            </span>
            <p className="text-amber-900 leading-relaxed text-[11px]">
              Historical event definitions (onset triggers, false onsets, break spells, heavy rainfall, and revivals) are
              engineering heuristic thresholds configured for machine learning feature preparation. They are{' '}
              <strong>NOT</strong> official India Meteorological Department (IMD) operational meteorological standards.
            </p>
          </div>
        </div>
      </div>

      {processMessage && (
        <div className="p-3.5 rounded-xl bg-forest-50 border border-forest-200 text-forest-900 text-xs flex items-center space-x-2">
          <CheckCircle2 className="w-4 h-4 text-forest-700 shrink-0" />
          <span>{processMessage}</span>
        </div>
      )}

      {/* Summary KPI Metrics */}
      <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-8 gap-2.5">
        <div className="agri-card p-3 bg-stone-50 border-stone-200">
          <span className="text-[11px] text-stone-600 font-bold uppercase">Blocks</span>
          <p className="text-lg font-black text-stone-900 mt-0.5">{summary?.blocks ?? '-'}</p>
          <span className="text-[10px] text-stone-500">Agro-zones</span>
        </div>

        <div className="agri-card p-3 bg-stone-50 border-stone-200">
          <span className="text-[11px] text-stone-600 font-bold uppercase">Total Days</span>
          <p className="text-lg font-black text-stone-900 mt-0.5">{summary?.records ?? '-'}</p>
          <span className="text-[10px] text-stone-500">Observations</span>
        </div>

        <div className="agri-card p-3 bg-stone-50 border-stone-200">
          <span className="text-[11px] text-emerald-700 font-bold uppercase">Onsets</span>
          <p className="text-lg font-black text-emerald-800 mt-0.5">{summary?.onset_triggers ?? '-'}</p>
          <span className="text-[10px] text-stone-500">&ge;20mm / 3d</span>
        </div>

        <div className="agri-card p-3 bg-stone-50 border-stone-200">
          <span className="text-[11px] text-amber-700 font-bold uppercase">False Onsets</span>
          <p className="text-lg font-black text-amber-800 mt-0.5">{summary?.false_onsets ?? '-'}</p>
          <span className="text-[10px] text-stone-500">&ge;7d dry in 30d</span>
        </div>

        <div className="agri-card p-3 bg-stone-50 border-stone-200">
          <span className="text-[11px] text-rose-700 font-bold uppercase">Break Days</span>
          <p className="text-lg font-black text-rose-800 mt-0.5">{summary?.break_spell_days_count ?? '-'}</p>
          <span className="text-[10px] text-stone-500">Dry intervals</span>
        </div>

        <div className="agri-card p-3 bg-stone-50 border-stone-200">
          <span className="text-[11px] text-rose-700 font-bold uppercase">Break Episodes</span>
          <p className="text-lg font-black text-rose-800 mt-0.5">{summary?.distinct_break_episodes ?? '-'}</p>
          <span className="text-[10px] text-stone-500">Distinct episodes</span>
        </div>

        <div className="agri-card p-3 bg-stone-50 border-stone-200">
          <span className="text-[11px] text-purple-700 font-bold uppercase">Heavy Rain</span>
          <p className="text-lg font-black text-purple-800 mt-0.5">{summary?.heavy_rain_events ?? '-'}</p>
          <span className="text-[10px] text-stone-500">&ge;64.5mm/day</span>
        </div>

        <div className="agri-card p-3 bg-stone-50 border-stone-200">
          <span className="text-[11px] text-teal-700 font-bold uppercase">Revivals</span>
          <p className="text-lg font-black text-teal-800 mt-0.5">{summary?.revival_events ?? '-'}</p>
          <span className="text-[10px] text-stone-500">&ge;15mm post-break</span>
        </div>
      </div>

      {/* Controls Bar */}
      <div className="agri-card p-3.5 bg-white border-stone-200 flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3">
        <div className="flex items-center space-x-2">
          <label className="text-xs font-bold text-stone-700">Select Block:</label>
          <select
            value={selectedBlock}
            onChange={(e) => setSelectedBlock(e.target.value)}
            className="bg-stone-50 border border-stone-300 text-stone-900 text-xs rounded-lg px-3 py-1.5 focus:outline-none focus:border-forest-600 font-semibold"
          >
            {blockOptions.map((opt) => (
              <option key={opt.id} value={opt.id}>
                {opt.name}
              </option>
            ))}
          </select>
        </div>

        <div className="flex items-center space-x-2">
          <Filter className="w-3.5 h-3.5 text-stone-500" />
          <span className="text-xs font-bold text-stone-700">Event Filter:</span>
          <select
            value={filterEvent}
            onChange={(e) => setFilterEvent(e.target.value)}
            className="bg-stone-50 border border-stone-300 text-stone-900 text-xs rounded-lg px-3 py-1.5 focus:outline-none focus:border-forest-600 font-semibold"
          >
            <option value="ALL">All Days</option>
            <option value="ONSET">Primary Onset Triggers Only</option>
            <option value="FALSE_ONSET">False Onsets Only</option>
            <option value="BREAK">Break Days Only</option>
            <option value="HEAVY_RAIN">Heavy Rain Only</option>
            <option value="REVIVAL">Revival Events Only</option>
          </select>
        </div>
      </div>

      {/* Visual Timeline Chart */}
      <div className="agri-card p-5 bg-white border-stone-200 space-y-3">
        <div className="flex items-center justify-between pb-2 border-b border-stone-100">
          <h2 className="text-sm font-bold text-stone-900 flex items-center gap-2">
            <Calendar className="w-4 h-4 text-forest-700" />
            Seasonal Rainfall & Detected Events Timeline ({selectedBlock})
          </h2>
          <span className="text-[11px] text-stone-500 font-mono">
            {records[0]?.date} → {records[records.length - 1]?.date}
          </span>
        </div>

        {/* Hover inspector display */}
        <div className="h-7 flex items-center text-xs">
          {hoveredRecord ? (
            <div className="flex items-center space-x-3 text-stone-800 bg-stone-100 px-3 py-1 rounded-lg border border-stone-200 shadow-2xs">
              <span className="font-bold text-forest-800">{hoveredRecord.date}</span>
              <span>Rain: <strong className="text-stone-900">{hoveredRecord.rainfall_mm} mm</strong></span>
              <span>3D: <strong className="text-stone-900">{hoveredRecord.rainfall_3d} mm</strong></span>
              <span>7D: <strong className="text-stone-900">{hoveredRecord.rainfall_7d} mm</strong></span>
              <span>Dry streak: <strong className="text-amber-800">{hoveredRecord.dry_spell_days}d</strong></span>
              {hoveredRecord.onset_trigger === 1 && (
                <span className="px-1.5 py-0.5 rounded bg-emerald-100 text-emerald-800 text-[10px] font-bold">ONSET</span>
              )}
              {hoveredRecord.false_onset === 1 && (
                <span className="px-1.5 py-0.5 rounded bg-amber-100 text-amber-800 text-[10px] font-bold">FALSE ONSET</span>
              )}
              {hoveredRecord.break_event === 1 && (
                <span className="px-1.5 py-0.5 rounded bg-rose-100 text-rose-800 text-[10px] font-bold">BREAK</span>
              )}
              {hoveredRecord.heavy_rain_event === 1 && (
                <span className="px-1.5 py-0.5 rounded bg-purple-100 text-purple-800 text-[10px] font-bold">HEAVY RAIN</span>
              )}
              {hoveredRecord.revival_event === 1 && (
                <span className="px-1.5 py-0.5 rounded bg-teal-100 text-teal-800 text-[10px] font-bold">REVIVAL</span>
              )}
            </div>
          ) : (
            <span className="text-stone-500 italic text-[11px]">Hover over any bar in the timeline to inspect features and events.</span>
          )}
        </div>

        {/* SVG Bar Chart */}
        <div className="w-full overflow-x-auto bg-stone-50/70 p-3 rounded-xl border border-stone-200">
          <div className="min-w-[700px] h-40 flex items-end gap-[2px] pt-4 pb-2 border-b border-stone-200">
            {records.map((rec) => {
              const heightPct = Math.min(100, Math.max(4, (rec.rainfall_mm / maxRainfall) * 100));
              let barColor = 'bg-stone-300';
              if (rec.heavy_rain_event === 1) barColor = 'bg-purple-600';
              else if (rec.false_onset === 1) barColor = 'bg-amber-500';
              else if (rec.revival_event === 1) barColor = 'bg-teal-600';
              else if (rec.onset_trigger === 1) barColor = 'bg-emerald-600';
              else if (rec.break_event === 1) barColor = 'bg-rose-500';
              else if (rec.rainfall_mm > 0) barColor = 'bg-sky-500';

              return (
                <div
                  key={rec.date}
                  onMouseEnter={() => setHoveredRecord(rec)}
                  onMouseLeave={() => setHoveredRecord(null)}
                  className="flex-1 flex flex-col items-center justify-end h-full cursor-pointer group relative"
                >
                  {(rec.onset_trigger === 1 || rec.false_onset === 1 || rec.break_event === 1 || rec.heavy_rain_event === 1 || rec.revival_event === 1) && (
                    <div
                      className={`w-1.5 h-1.5 rounded-full mb-1 ${
                        rec.heavy_rain_event === 1
                          ? 'bg-purple-600'
                          : rec.false_onset === 1
                          ? 'bg-amber-500'
                          : rec.break_event === 1
                          ? 'bg-rose-500'
                          : rec.revival_event === 1
                          ? 'bg-teal-600'
                          : 'bg-emerald-600'
                      }`}
                    />
                  )}
                  <div
                    style={{ height: `${heightPct}%` }}
                    className={`w-full rounded-t-xs transition-all duration-150 group-hover:brightness-110 ${barColor}`}
                  />
                </div>
              );
            })}
          </div>
        </div>

        {/* Legend */}
        <div className="flex flex-wrap items-center gap-4 text-[11px] text-stone-600 pt-1">
          <div className="flex items-center space-x-1.5">
            <span className="w-2.5 h-2.5 rounded-xs bg-emerald-600 inline-block" />
            <span>Onset Trigger (&ge;20mm/3d)</span>
          </div>
          <div className="flex items-center space-x-1.5">
            <span className="w-2.5 h-2.5 rounded-xs bg-amber-500 inline-block" />
            <span>False Onset (Dry spell in 30d)</span>
          </div>
          <div className="flex items-center space-x-1.5">
            <span className="w-2.5 h-2.5 rounded-xs bg-rose-500 inline-block" />
            <span>Break Spell (&ge;5d dry)</span>
          </div>
          <div className="flex items-center space-x-1.5">
            <span className="w-2.5 h-2.5 rounded-xs bg-purple-600 inline-block" />
            <span>Heavy Rain (&ge;64.5mm)</span>
          </div>
          <div className="flex items-center space-x-1.5">
            <span className="w-2.5 h-2.5 rounded-xs bg-teal-600 inline-block" />
            <span>Revival (Post-break rain)</span>
          </div>
        </div>
      </div>

      {/* Feature & Detection Data Table */}
      <div className="agri-card bg-white border-stone-200 overflow-hidden">
        <div className="px-5 py-3.5 border-b border-stone-200 flex items-center justify-between">
          <h2 className="text-sm font-bold text-stone-900 flex items-center gap-2">
            <Layers className="w-4 h-4 text-forest-700" />
            Historical Features & Event Labels ({filteredRecords.length} records)
          </h2>
          <span className="text-[11px] text-stone-500 font-mono">data/processed/historical_events.csv</span>
        </div>

        <div className="overflow-x-auto max-h-96 overflow-y-auto">
          <table className="w-full text-left text-xs text-stone-700 font-mono">
            <thead className="bg-stone-100 text-stone-700 uppercase tracking-wider border-b border-stone-200 sticky top-0 text-[11px]">
              <tr>
                <th className="py-2.5 px-4 font-sans font-bold">Date</th>
                <th className="py-2.5 px-3">Rain (mm)</th>
                <th className="py-2.5 px-3">3D Sum</th>
                <th className="py-2.5 px-3">7D Sum</th>
                <th className="py-2.5 px-3">14D Sum</th>
                <th className="py-2.5 px-3">Dry Streak</th>
                <th className="py-2.5 px-3">Events Detected</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-stone-100">
              {filteredRecords.map((r) => (
                <tr key={r.date} className="hover:bg-stone-50">
                  <td className="py-2 px-4 font-sans font-medium text-stone-900">{r.date}</td>
                  <td className="py-2 px-3 font-bold text-stone-800">{r.rainfall_mm.toFixed(1)}</td>
                  <td className="py-2 px-3">{r.rainfall_3d.toFixed(1)}</td>
                  <td className="py-2 px-3">{r.rainfall_7d.toFixed(1)}</td>
                  <td className="py-2 px-3">{r.rainfall_14d.toFixed(1)}</td>
                  <td className="py-2 px-3 text-amber-800">{r.dry_spell_days}d</td>
                  <td className="py-2 px-3">
                    <div className="flex flex-wrap gap-1">
                      {r.onset_trigger === 1 && (
                        <span className="px-1.5 py-0.2 rounded text-[10px] bg-emerald-100 text-emerald-800 font-bold font-sans">
                          ONSET
                        </span>
                      )}
                      {r.false_onset === 1 && (
                        <span className="px-1.5 py-0.2 rounded text-[10px] bg-amber-100 text-amber-800 font-bold font-sans">
                          FALSE ONSET
                        </span>
                      )}
                      {r.break_event === 1 && (
                        <span className="px-1.5 py-0.2 rounded text-[10px] bg-rose-100 text-rose-800 font-bold font-sans">
                          BREAK
                        </span>
                      )}
                      {r.heavy_rain_event === 1 && (
                        <span className="px-1.5 py-0.2 rounded text-[10px] bg-purple-100 text-purple-800 font-bold font-sans">
                          HEAVY RAIN
                        </span>
                      )}
                      {r.revival_event === 1 && (
                        <span className="px-1.5 py-0.2 rounded text-[10px] bg-teal-100 text-teal-800 font-bold font-sans">
                          REVIVAL
                        </span>
                      )}
                      {r.onset_trigger === 0 &&
                        r.false_onset === 0 &&
                        r.break_event === 0 &&
                        r.heavy_rain_event === 0 &&
                        r.revival_event === 0 && (
                          <span className="text-stone-400 font-sans italic text-[11px]">—</span>
                        )}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
