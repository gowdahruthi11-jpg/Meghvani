import React, { useState, useEffect } from 'react';
import {
  BrainCircuit,
  Sliders,
  Sparkles,
  Info,
  CheckCircle2,
  ArrowDown,
  Layers,
  HelpCircle,
  ShieldCheck,
  TrendingDown,
  BarChart3,
  RefreshCw
} from 'lucide-react';
import { api } from '../services/api';
import { BaselineModelMetadata, FeatureContribution, Block } from '../types';
import { useCanonicalPrediction } from '../context/CanonicalPredictionContext';
import { LocationHierarchySelector } from '../components/LocationHierarchySelector';

interface ExplainableAIPageProps {
  blocks: Block[];
  selectedBlockId: number;
  onSelectBlockId: (id: number) => void;
  onNavigateTab: (tab: string) => void;
}

const FEATURE_LABEL_MAP: Record<string, { label: string; desc: string; domain: string }> = {
  day_of_year: {
    label: 'Seasonal Progression (Day of Year)',
    desc: 'Temporal climatological position within the summer monsoon season',
    domain: 'Climatology'
  },
  dry_spell_days: {
    label: 'Ongoing Dry Spell Duration',
    desc: 'Consecutive antecedent days with daily precipitation < 2.5 mm',
    domain: 'Persistence'
  },
  rainfall_14d: {
    label: '14-Day Cumulative Rainfall',
    desc: 'Deep soil moisture recharge index over the preceding two weeks',
    domain: 'Soil Moisture'
  },
  days_since_last_onset: {
    label: 'Lockout Since Last Onset',
    desc: 'Days elapsed since the preceding validated monsoon onset event',
    domain: 'Event Tracking'
  },
  rainfall_7d: {
    label: '7-Day Cumulative Rainfall',
    desc: 'Seedbed layer moisture accumulation over past week',
    domain: 'Rainfall'
  },
  days_since_last_break: {
    label: 'Recency of Break Episode',
    desc: 'Temporal distance from the latest active monsoon hiatus',
    domain: 'Event Tracking'
  },
  rainfall_change_7d: {
    label: '7-Day Rainfall Velocity',
    desc: 'Directional acceleration of atmospheric moisture flux',
    domain: 'Dynamics'
  },
  rainfall_change_3d: {
    label: '3-Day Rainfall Momentum',
    desc: 'Immediate change in rainfall intensity over past 72 hours',
    domain: 'Dynamics'
  },
  rainfall_3d: {
    label: '3-Day Short-Term Precipitation',
    desc: 'Immediate surface runoff and germination moisture availability',
    domain: 'Rainfall'
  },
  rainfall_ratio_3d_7d: {
    label: 'Moisture Persistence Ratio',
    desc: 'Ratio of immediate 3d rain to 7d cumulative total',
    domain: 'Dynamics'
  },
};

export const ExplainableAIPage: React.FC<ExplainableAIPageProps> = ({
  blocks: propBlocks,
  selectedBlockId: propBlockId,
  onSelectBlockId: propSetBlockId,
  onNavigateTab,
}) => {
  const {
    canonical,
    selectedBlock,
    setSelectedBlockId,
    blocks,
  } = useCanonicalPrediction();

  const handleSelectBlock = (id: number) => {
    setSelectedBlockId(id);
    if (propSetBlockId) propSetBlockId(id);
  };

  const [metadata, setMetadata] = useState<BaselineModelMetadata | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [filterDomain, setFilterDomain] = useState<string>('ALL');

  useEffect(() => {
    const load = async () => {
      setLoading(true);
      try {
        const data = await api.getBaselineSummary();
        setMetadata(data);
      } catch (err) {
        console.error('Failed to load baseline model metadata:', err);
      } finally {
        setLoading(false);
      }
    };
    load();
  }, []);

  const rawFeatures: FeatureContribution[] = metadata?.feature_contributions || [];

  // Calculate total absolute sum for normalized relative percentage shares
  const totalAbsCoeff = rawFeatures.reduce((acc, f) => acc + (f.absolute_coefficient || 0), 0) || 1;

  const enrichedFeatures = rawFeatures.map((f) => {
    const meta = FEATURE_LABEL_MAP[f.feature_name] || {
      label: f.feature_name.replace(/_/g, ' '),
      desc: 'Standardized atmospheric feature',
      domain: 'Atmospheric'
    };
    const sharePct = Math.round((f.absolute_coefficient / totalAbsCoeff) * 100);
    return {
      ...f,
      label: meta.label,
      desc: meta.desc,
      domain: meta.domain,
      sharePct,
    };
  });

  const displayedFeatures =
    filterDomain === 'ALL'
      ? enrichedFeatures
      : enrichedFeatures.filter((f) => f.domain === filterDomain);

  // Top 2 dominant features for automated natural language synthesis
  const top1 = enrichedFeatures[0]?.label || 'Seasonal Progression';
  const top2 = enrichedFeatures[1]?.label || 'Ongoing Dry Spell Duration';

  return (
    <div className="space-y-6 pb-12">
      {/* Header */}
      <div className="bg-white p-6 rounded-2xl border border-stone-200/90 shadow-2xs">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div className="flex items-center space-x-2.5">
            <div className="w-10 h-10 rounded-xl bg-forest-50 border border-forest-200 flex items-center justify-center text-forest-800">
              <BrainCircuit className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <h1 className="text-xl sm:text-2xl font-extrabold text-stone-900 tracking-tight">
                  Why did the model make this prediction?
                </h1>
                <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-forest-100 text-forest-800 border border-forest-200 uppercase tracking-wider">
                  Explainable AI (XAI)
                </span>
              </div>
              <p className="text-xs text-stone-600 mt-0.5">
                Standardized linear model weights and feature contributions for statistical transparency.
              </p>
            </div>
          </div>

          <div className="flex items-center space-x-2">
            <div className="hidden sm:flex items-center space-x-1.5 px-2.5 py-1 rounded-xl bg-amber-50 border border-amber-200/80 text-[10px] font-bold text-amber-900">
              <span className="w-1.5 h-1.5 rounded-full bg-amber-500 animate-pulse"></span>
              <span>Prototype coverage: 3 regions</span>
            </div>
            <LocationHierarchySelector />
          </div>
        </div>
      </div>

      {/* 4-Stage Explainability Flow Banner */}
      <div className="bg-white p-5 rounded-2xl border border-stone-200/90 shadow-2xs">
        <span className="text-[11px] font-extrabold uppercase tracking-wider text-stone-400 block mb-3">
          Explainability Pipeline Architecture
        </span>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-3 text-xs">
          {/* Step 1 */}
          <div className="p-3.5 rounded-xl bg-stone-50 border border-stone-200 flex flex-col justify-between">
            <div>
              <span className="text-[10px] font-black uppercase text-stone-400 block">Step 1</span>
              <span className="font-extrabold text-stone-900 text-sm block mt-0.5">Prediction Target</span>
              <p className="text-[11px] text-stone-500 mt-1">
                Explanation for: False Onset Risk — {canonical.falseOnsetRisk}% ({selectedBlock.name})
              </p>
            </div>
            <div className="mt-2 text-forest-700 font-bold text-[10px]">● Supervised Logistic</div>
          </div>

          {/* Step 2 */}
          <div className="p-3.5 rounded-xl bg-stone-50 border border-stone-200 flex flex-col justify-between">
            <div>
              <span className="text-[10px] font-black uppercase text-stone-400 block">Step 2</span>
              <span className="font-extrabold text-stone-900 text-sm block mt-0.5">Feature Weights</span>
              <p className="text-[11px] text-stone-500 mt-1">
                Linear coefficients fitted on StandardScaler features
              </p>
            </div>
            <div className="mt-2 text-forest-700 font-bold text-[10px]">● Standardized Z-Score</div>
          </div>

          {/* Step 3 */}
          <div className="p-3.5 rounded-xl bg-stone-50 border border-stone-200 flex flex-col justify-between">
            <div>
              <span className="text-[10px] font-black uppercase text-stone-400 block">Step 3</span>
              <span className="font-extrabold text-stone-900 text-sm block mt-0.5">Contribution Share</span>
              <p className="text-[11px] text-stone-500 mt-1">
                Relative normalized attribution to final probability
              </p>
            </div>
            <div className="mt-2 text-forest-700 font-bold text-[10px]">● 27% Top Driver</div>
          </div>

          {/* Step 4 */}
          <div className="p-3.5 rounded-xl bg-forest-50 border border-forest-200 flex flex-col justify-between">
            <div>
              <span className="text-[10px] font-black uppercase text-forest-600 block">Step 4</span>
              <span className="font-extrabold text-forest-950 text-sm block mt-0.5">Plain Synthesis</span>
              <p className="text-[11px] text-forest-800 mt-1">
                Natural language interpretation for farmers and officers
              </p>
            </div>
            <div className="mt-2 text-forest-800 font-bold text-[10px]">● Actionable Translation</div>
          </div>
        </div>
      </div>

      {/* Human-Readable Explanation Highlight Box */}
      <div className="p-5 rounded-2xl bg-gradient-to-r from-forest-900 to-forest-800 text-white shadow-md space-y-2">
        <div className="flex items-center space-x-2">
          <Sparkles className="w-5 h-5 text-amber-300" />
          <h3 className="font-extrabold text-base text-white">
            Human-Readable Model Synthesis · {selectedBlock.name}
          </h3>
        </div>
        <p className="text-sm text-forest-100 leading-relaxed font-sans">
          "{canonical.postureExplanation} {top1} and {top2} are currently the primary statistical drivers for the {canonical.falseOnsetRisk}% false-onset risk score. Current sowing posture: {canonical.sowingPosture.replace(/_/g, ' ')}."
        </p>
        <span className="text-[11px] text-forest-300 block pt-1">
          Automated translation grounded in standardized model coefficients.
        </span>
      </div>

      {/* Feature Importance Section */}
      <div className="bg-white p-6 rounded-2xl border border-stone-200/90 shadow-2xs space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-stone-100">
          <div>
            <h3 className="font-extrabold text-sm text-stone-900">
              Ranked Feature Importance & Attribution
            </h3>
            <p className="text-xs text-stone-500">
              Values represent fitted standardized linear model weights (coefficients) from actual model training.
            </p>
          </div>

          {/* Domain Filter Pills */}
          <div className="flex items-center space-x-1 bg-stone-100 p-1 rounded-xl border border-stone-200 text-xs font-semibold">
            {['ALL', 'Climatology', 'Soil Moisture', 'Rainfall', 'Dynamics'].map((dom) => (
              <button
                key={dom}
                onClick={() => setFilterDomain(dom)}
                className={`px-2.5 py-1 rounded-lg text-[11px] transition-all ${
                  filterDomain === dom
                    ? 'bg-white text-forest-900 font-bold shadow-2xs'
                    : 'text-stone-600 hover:text-stone-900'
                }`}
              >
                {dom}
              </button>
            ))}
          </div>
        </div>

        {/* Feature Bars */}
        <div className="space-y-3 pt-2">
          {displayedFeatures.map((f, idx) => (
            <div
              key={f.feature_name}
              className="p-3 rounded-xl bg-stone-50 hover:bg-stone-100/80 border border-stone-200/80 transition-all text-xs"
            >
              <div className="flex items-center justify-between mb-1.5">
                <div className="flex items-center space-x-2">
                  <span className="w-5 h-5 rounded-md bg-stone-200 text-stone-700 font-bold text-[10px] flex items-center justify-center shrink-0">
                    #{idx + 1}
                  </span>
                  <span className="font-extrabold text-stone-900">{f.label}</span>
                  <span className="text-[10px] font-bold text-stone-500 bg-stone-200/60 px-1.5 py-0.5 rounded">
                    {f.domain}
                  </span>
                </div>

                <div className="flex items-center space-x-2 font-mono">
                  <span className="text-stone-500 text-[11px]">Weight: {f.coefficient > 0 ? `+${f.coefficient}` : f.coefficient}</span>
                  <span className="font-extrabold text-forest-900 bg-forest-100 px-2 py-0.5 rounded text-[11px]">
                    {f.sharePct}%
                  </span>
                </div>
              </div>

              {/* Progress Bar */}
              <div className="w-full bg-stone-200 h-2.5 rounded-full overflow-hidden">
                <div
                  style={{ width: `${Math.min(100, Math.max(5, f.sharePct * 3.5))}%` }}
                  className={`h-full rounded-full transition-all duration-500 ${
                    f.coefficient < 0
                      ? 'bg-gradient-to-r from-emerald-600 to-emerald-500'
                      : 'bg-gradient-to-r from-amber-600 to-amber-500'
                  }`}
                />
              </div>

              <p className="text-[10px] text-stone-500 mt-1 leading-snug">
                {f.desc} • {f.interpretation}
              </p>
            </div>
          ))}
        </div>

        {/* Scientific Transparency Notice */}
        <div className="mt-4 p-3 rounded-xl bg-stone-100 border border-stone-200 text-[11px] text-stone-600 flex items-start space-x-2">
          <Info className="w-4 h-4 text-stone-500 shrink-0 mt-0.5" />
          <span>
            <strong>Scientific Disclosure:</strong> These values represent fitted standardized linear model weights from the Phase 3B/8A multi-year logistic regression model. They indicate statistical correlation and relative importance within the feature vector, not physical causality.
          </span>
        </div>
      </div>
    </div>
  );
};
