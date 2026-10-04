import React, { useState, useEffect } from 'react';
import {
  Database,
  Layers,
  FileCheck,
  ShieldCheck,
  Activity,
  Calendar,
  CheckCircle2,
  AlertTriangle,
  Info,
  Scale,
  BrainCircuit,
  ExternalLink
} from 'lucide-react';
import { api } from '../services/api';
import { BaselineModelMetadata, PredictionDatasetSummary } from '../types';

export const DataModelPage: React.FC = () => {
  const [modelMeta, setModelMeta] = useState<BaselineModelMetadata | null>(null);
  const [datasetSummary, setDatasetSummary] = useState<PredictionDatasetSummary | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    const load = async () => {
      setLoading(true);
      try {
        const [meta, summary] = await Promise.all([
          api.getBaselineSummary().catch(() => null),
          api.getPredictionSummary().catch(() => null),
        ]);
        setModelMeta(meta);
        setDatasetSummary(summary);
      } catch (e) {
        console.warn('Data model page load error:', e);
      } finally {
        setLoading(false);
      }
    };
    load();
  }, []);

  const dataSources = [
    {
      name: 'India Meteorological Department (IMD)',
      type: 'Gridded Observations',
      resolution: '0.25° x 0.25° (approx 27 km)',
      frequency: 'Daily rainfall (1901–present)',
      role: 'Ground-truth onset, break, and cumulative precipitation baseline'
    },
    {
      name: 'ECMWF ERA5 / ERA5-Land',
      type: 'Atmospheric Reanalysis',
      resolution: '0.1° / 0.25°',
      frequency: 'Hourly / Daily aggregated',
      role: 'Temperature, relative humidity, zonal wind, surface pressure'
    },
    {
      name: 'CHIRPS & Satellite Precipitation',
      type: 'Blended Satellite & Gauge',
      resolution: '0.05° spatial resolution',
      frequency: 'Daily (1981–present)',
      role: 'Spatial cross-validation and convective rainfall boundary verification'
    },
    {
      name: 'ICAR-CRIDA & Dr. PDKV Akola',
      type: 'Institutional Agronomy',
      resolution: 'Agro-climatic Zone VII (Vidarbha)',
      frequency: 'Seasonal kharif advisory releases',
      role: 'Deterministic agronomic decision rules (Soybean, Cotton, Pigeonpea)'
    },
  ];

  return (
    <div className="space-y-6 pb-12">
      {/* Header */}
      <div className="bg-white p-6 rounded-2xl border border-stone-200/90 shadow-2xs">
        <div className="flex items-center space-x-2.5">
          <div className="w-10 h-10 rounded-xl bg-forest-50 border border-forest-200 flex items-center justify-center text-forest-800">
            <Database className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <h1 className="text-xl sm:text-2xl font-extrabold text-stone-900 tracking-tight">
                Data Sources & Model Architecture
              </h1>
              <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-forest-100 text-forest-800 border border-forest-200 uppercase tracking-wider">
                Technical Governance
              </span>
            </div>
            <p className="text-xs text-stone-600 mt-0.5">
              Scientific transparency, data provenance, and rolling-origin validation metrics for SIH evaluation.
            </p>
          </div>
        </div>
      </div>

      {/* Section 1: Verified Data Sources */}
      <div className="bg-white p-6 rounded-2xl border border-stone-200/90 shadow-2xs space-y-4">
        <div className="flex items-center justify-between pb-3 border-b border-stone-100">
          <div>
            <h2 className="text-sm font-extrabold text-stone-900 uppercase tracking-wider">
              1. Curated Environmental Data Sources
            </h2>
            <p className="text-xs text-stone-500">
              Only primary public meteorological records and verified institutional agronomy are used.
            </p>
          </div>
          <span className="text-[10px] font-bold text-forest-800 bg-forest-50 border border-forest-200 px-2 py-0.5 rounded-full">
            Zero Fabricated Data
          </span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {dataSources.map((s) => (
            <div
              key={s.name}
              className="p-4 rounded-xl bg-stone-50 border border-stone-200/80 space-y-2 text-xs"
            >
              <div className="flex items-start justify-between gap-2">
                <span className="font-extrabold text-stone-900 text-sm">{s.name}</span>
                <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-stone-200 text-stone-700 shrink-0">
                  {s.type}
                </span>
              </div>
              <div className="space-y-1 text-stone-600">
                <div><strong>Resolution:</strong> {s.resolution}</div>
                <div><strong>Temporal Cadence:</strong> {s.frequency}</div>
                <div><strong>Pipeline Role:</strong> {s.role}</div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Section 2: Model Architecture & Specifications */}
      <div className="bg-white p-6 rounded-2xl border border-stone-200/90 shadow-2xs space-y-4">
        <div className="flex items-center justify-between pb-3 border-b border-stone-100">
          <div>
            <h2 className="text-sm font-extrabold text-stone-900 uppercase tracking-wider">
              2. Baseline Model Specifications (Phase 3B / 8A)
            </h2>
            <p className="text-xs text-stone-500">
              Supervised probabilistic classifier with post-hoc calibration.
            </p>
          </div>
          <span className="text-[10px] font-mono text-stone-500">
            Hash: 9a7e8...4c1f
          </span>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
          <div className="p-3 rounded-xl bg-stone-50 border border-stone-200/80">
            <span className="text-[10px] text-stone-400 font-bold uppercase block">Model Architecture</span>
            <span className="font-extrabold text-stone-900 text-sm mt-0.5 block">
              Logistic + Isotonic
            </span>
          </div>

          <div className="p-3 rounded-xl bg-stone-50 border border-stone-200/80">
            <span className="text-[10px] text-stone-400 font-bold uppercase block">Training Period</span>
            <span className="font-extrabold text-stone-900 text-sm mt-0.5 block">
              2019–2024 (6 Years)
            </span>
          </div>

          <div className="p-3 rounded-xl bg-stone-50 border border-stone-200/80">
            <span className="text-[10px] text-stone-400 font-bold uppercase block">Prediction Horizon</span>
            <span className="font-extrabold text-stone-900 text-sm mt-0.5 block">
              7 to 30 Days
            </span>
          </div>

          <div className="p-3 rounded-xl bg-stone-50 border border-stone-200/80">
            <span className="text-[10px] text-stone-400 font-bold uppercase block">Effective Sample Size</span>
            <span className="font-extrabold text-forest-800 text-sm mt-0.5 block">
              N_eff = 303 (Nominal 1224)
            </span>
          </div>
        </div>

        {/* Feature List */}
        <div className="pt-2">
          <span className="text-xs font-bold text-stone-700 block mb-2">
            Engineered Predictor Features (t ≤ T zero-leakage invariant enforced):
          </span>
          <div className="flex flex-wrap gap-1.5">
            {[
              'rainfall_mm',
              'rainfall_3d',
              'rainfall_7d',
              'rainfall_14d',
              'dry_spell_days',
              'wet_spell_days',
              'rainfall_change_3d',
              'rainfall_change_7d',
              'rainfall_ratio_3d_7d',
              'day_of_year',
              'days_since_last_onset',
              'days_since_last_break'
            ].map((feat) => (
              <span
                key={feat}
                className="px-2.5 py-1 rounded-lg bg-stone-100 text-stone-800 text-[11px] font-mono border border-stone-200"
              >
                {feat}
              </span>
            ))}
          </div>
        </div>
      </div>

      {/* Section 3: Honest Scientific Performance Disclosure */}
      <div className="p-5 rounded-2xl bg-amber-50 border border-amber-200 text-amber-950 text-xs space-y-2 shadow-2xs">
        <div className="flex items-center space-x-2">
          <AlertTriangle className="w-5 h-5 text-amber-700" />
          <h3 className="font-extrabold text-sm text-amber-900">
            Phase 8B In-Season Verification Disclosure
          </h3>
        </div>
        <p className="text-[11px] text-amber-900 leading-relaxed font-medium">
          In strict compliance with Invariant 5 (never fabricate skill), rigorous in-season evaluation across 2019–2024 within the active kharif sowing window (25 May – 31 July) revealed a Brier Skill Score (BSS) of <strong>-12.22</strong> relative to constant climatology baseline (Brier = 0.0096 vs Model = 0.1271). This is primarily driven by extreme in-season class imbalance (1.14% positive event rate). Consequently, the prototype is transparently labeled as a non-operational research demonstration.
        </p>
      </div>
    </div>
  );
};
