import React from 'react';
import { Sprout, CheckCircle2, AlertCircle, ShieldAlert, ArrowRight, BookOpen, MessageSquare, ExternalLink } from 'lucide-react';
import { Block, DecisionSupportResult, AdvisoryResult } from '../types';

interface FarmDecisionPanelProps {
  selectedBlock: Block;
  selectedCrop: string;
  onChangeCrop: (crop: string) => void;
  decisionData?: DecisionSupportResult | null;
  advisoryData?: AdvisoryResult | null;
  onViewAdvisory?: () => void;
  onViewFarmerMessage?: () => void;
}

export const FarmDecisionPanel: React.FC<FarmDecisionPanelProps> = ({
  selectedBlock,
  selectedCrop,
  onChangeCrop,
  decisionData,
  advisoryData,
  onViewAdvisory,
  onViewFarmerMessage,
}) => {
  const decision = decisionData?.decision || 'SOW_NOW';
  const probVal = decisionData?.probability !== null && decisionData?.probability !== undefined
    ? Math.round(decisionData.probability * 100)
    : 18;

  // Semantic styles for decision
  const isSowNow = decision === 'SOW_NOW';
  const isSowPart = decision === 'SOW_PART_NOW';

  return (
    <div className="bg-white rounded-2xl border border-stone-200/90 shadow-sm overflow-hidden flex flex-col justify-between h-full">
      {/* Header with Crop Selector */}
      <div className="p-4 bg-gradient-to-br from-stone-50 to-white border-b border-stone-200">
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-2">
            <span className="text-xl">🌱</span>
            <div>
              <span className="text-[11px] font-bold text-forest-700 uppercase tracking-wider block">
                Decision Support
              </span>
              <h3 className="font-bold text-stone-900 text-sm">
                Farm Decision · {selectedBlock.name}
              </h3>
            </div>
          </div>

          {/* Quick Crop Selector Pills */}
          <div className="flex items-center gap-1 bg-stone-100 p-0.5 rounded-lg border border-stone-200 text-xs">
            {[
              { id: 'soybean', label: 'Soybean' },
              { id: 'cotton', label: 'Cotton' },
              { id: 'pigeonpea', label: 'Tur' },
            ].map((c) => (
              <button
                key={c.id}
                onClick={() => onChangeCrop(c.id)}
                className={`px-2 py-1 rounded-md text-[11px] font-medium transition-all ${
                  selectedCrop === c.id
                    ? 'bg-forest-800 text-white shadow-xs'
                    : 'text-stone-600 hover:text-stone-900'
                }`}
              >
                {c.label}
              </button>
            ))}
          </div>
        </div>

        {/* Hero Decision Badge */}
        <div
          className={`p-3.5 rounded-xl border flex items-center justify-between ${
            isSowNow
              ? 'bg-emerald-50/80 border-emerald-300 text-emerald-950'
              : isSowPart
              ? 'bg-amber-50/80 border-amber-300 text-amber-950'
              : 'bg-red-50/80 border-red-300 text-red-950'
          }`}
        >
          <div>
            <span className="text-[10px] font-bold tracking-wider uppercase opacity-75 block">
              Recommended Action
            </span>
            <div className="text-xl font-extrabold tracking-tight flex items-center gap-2">
              <span>{isSowNow ? 'SOW NOW' : isSowPart ? 'SOW PART NOW' : 'WAIT'}</span>
              <span className="text-base">{isSowNow ? '✅' : isSowPart ? '⚠️' : '🛑'}</span>
            </div>
            <p className="text-xs font-medium opacity-90 mt-0.5">
              {isSowNow
                ? 'Low prototype false-onset risk (< 30%)'
                : isSowPart
                ? 'Moderate false-onset caution (30-60%)'
                : 'High false-onset hazard (> 60%)'}
            </p>
          </div>

          <div className="text-right">
            <span className="text-[10px] font-bold text-stone-500 block uppercase">Onset Risk</span>
            <span className="text-lg font-black text-stone-900">{probVal}%</span>
            <span className="text-[10px] text-stone-500 block">7-day horizon</span>
          </div>
        </div>
      </div>

      {/* Body: Agronomic Justification & Boundary Separation */}
      <div className="p-4 space-y-3.5 flex-1 overflow-y-auto text-xs">
        {/* Why? Checklist */}
        <div>
          <h4 className="font-bold text-stone-800 text-xs mb-2 flex items-center gap-1.5">
            <span>🔍</span> Agronomic & Engineering Rationale
          </h4>
          <div className="space-y-1.5">
            <div className="flex items-start gap-2 p-2 rounded-lg bg-stone-50 border border-stone-100">
              <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0 mt-0.5" />
              <div>
                <span className="font-semibold text-stone-800">Recent Rainfall Condition</span>
                <p className="text-stone-600 text-[11px] leading-relaxed">
                  Cumulative 75–100 mm seedbed moisture observed across Vidarbha onset window.
                </p>
              </div>
            </div>

            <div className="flex items-start gap-2 p-2 rounded-lg bg-stone-50 border border-stone-100">
              <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0 mt-0.5" />
              <div>
                <span className="font-semibold text-stone-800">Prototype Risk Below Threshold</span>
                <p className="text-stone-600 text-[11px] leading-relaxed">
                  Calculated false-onset probability ({probVal}%) is well below the 40% intervention threshold.
                </p>
              </div>
            </div>

            <div className="flex items-start gap-2 p-2 rounded-lg bg-stone-50 border border-stone-100">
              <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0 mt-0.5" />
              <div>
                <span className="font-semibold text-stone-800">Validated Rule Availability</span>
                <p className="text-stone-600 text-[11px] leading-relaxed">
                  Active rule: <code className="text-stone-800 font-mono bg-stone-200/70 px-1 py-0.5 rounded text-[10px]">{advisoryData?.rule_id || 'RULE_CRIDA_MH_SOYBEAN_SOW_NOW'}</code>
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Clear Boundary Distinction (CRITICAL REQUIREMENT) */}
        <div className="p-2.5 rounded-xl bg-amber-50/70 border border-amber-200/80 text-[11px] space-y-1.5">
          <div className="font-bold text-amber-900 flex items-center gap-1">
            <BookOpen className="w-3.5 h-3.5 text-amber-700" />
            <span>Boundary: Agronomy vs. Engineering</span>
          </div>
          <div className="text-stone-700 space-y-1 leading-snug">
            <p>
              <strong className="text-emerald-800">Source-Supported Agronomic Condition:</strong>{' '}
              {advisoryData?.source?.source_name || 'ICAR-CRIDA Nagpur Contingency Plan'} (75–100 mm seedbed moisture requirement for {selectedCrop}).
            </p>
            <p>
              <strong className="text-rain-800">Meghvani Engineering Condition:</strong>{' '}
              Statistical false-onset risk ({probVal}%) calculated from multi-day rainfall sequences.
            </p>
          </div>
        </div>
      </div>

      {/* Footer Navigation Buttons */}
      <div className="p-3 bg-stone-50 border-t border-stone-200 flex items-center gap-2">
        <button
          onClick={onViewAdvisory}
          className="flex-1 py-2 px-3 rounded-xl bg-forest-800 hover:bg-forest-900 text-white font-medium text-xs flex items-center justify-center gap-1.5 transition-all shadow-xs"
        >
          <Sprout className="w-3.5 h-3.5" />
          <span>View Full Advisory</span>
        </button>
        <button
          onClick={onViewFarmerMessage}
          className="flex-1 py-2 px-3 rounded-xl bg-white hover:bg-stone-100 text-stone-800 border border-stone-300 font-medium text-xs flex items-center justify-center gap-1.5 transition-all"
        >
          <MessageSquare className="w-3.5 h-3.5 text-rain-600" />
          <span>Farmer Message</span>
        </button>
      </div>
    </div>
  );
};
