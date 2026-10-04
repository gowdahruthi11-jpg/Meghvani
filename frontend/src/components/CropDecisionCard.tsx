import React from 'react';
import { Sprout, CheckCircle2, AlertTriangle, AlertOctagon, HelpCircle, BookOpen } from 'lucide-react';

export interface CropDecisionData {
  cropId: 'soybean' | 'cotton' | 'pigeonpea' | string;
  cropName: string;
  marathiName?: string;
  hindiName?: string;
  decision: 'SOW_NOW' | 'SOW_PART_NOW' | 'WAIT' | 'INSUFFICIENT_DATA';
  forecastCondition?: string;
  agronomicReason?: string;
  sourceStatus: 'VALIDATED' | 'REVIEW_REQUIRED' | 'UNVALIDATED' | 'NO_RULE';
  institutionalSource?: string;
  actionMessage?: string;
}

interface CropDecisionCardProps {
  data: CropDecisionData;
  isSelected?: boolean;
  onSelect?: () => void;
}

export const CropDecisionCard: React.FC<CropDecisionCardProps> = ({
  data,
  isSelected = false,
  onSelect,
}) => {
  const getCropEmoji = (id: string) => {
    switch (id.toLowerCase()) {
      case 'soybean':
        return '🌱';
      case 'cotton':
        return '🌿';
      case 'pigeonpea':
      case 'tur':
        return '🌾';
      default:
        return '🌱';
    }
  };

  const decisionConfig = {
    SOW_NOW: {
      label: 'SOW NOW',
      color: 'bg-emerald-100 text-emerald-800 border-emerald-300',
      borderAccent: 'border-t-4 border-t-emerald-600',
      icon: CheckCircle2,
      badgeText: 'Favorable Sowing Window',
    },
    SOW_PART_NOW: {
      label: 'SOW PART NOW',
      color: 'bg-amber-100 text-amber-800 border-amber-300',
      borderAccent: 'border-t-4 border-t-amber-500',
      icon: AlertTriangle,
      badgeText: 'Staggered / Caution',
    },
    WAIT: {
      label: 'WAIT / HOLD SOWING',
      color: 'bg-rose-100 text-rose-800 border-rose-300',
      borderAccent: 'border-t-4 border-t-rose-500',
      icon: AlertOctagon,
      badgeText: 'High Hazard / Dry Spell',
    },
    INSUFFICIENT_DATA: {
      label: 'UNAVAILABLE',
      color: 'bg-stone-100 text-stone-700 border-stone-300',
      borderAccent: 'border-t-4 border-t-stone-400',
      icon: HelpCircle,
      badgeText: 'No Validated Rule',
    },
  };

  const current = decisionConfig[data.decision] || decisionConfig.INSUFFICIENT_DATA;
  const Icon = current.icon;

  const sourceStatusBadges = {
    VALIDATED: 'bg-emerald-50 text-emerald-700 border-emerald-200',
    REVIEW_REQUIRED: 'bg-amber-50 text-amber-700 border-amber-200',
    UNVALIDATED: 'bg-rose-50 text-rose-700 border-rose-200',
    NO_RULE: 'bg-stone-100 text-stone-500 border-stone-200',
  };

  return (
    <div
      onClick={onSelect}
      className={`agri-card p-5 ${current.borderAccent} ${
        isSelected ? 'ring-2 ring-forest-600 shadow-md' : ''
      } ${onSelect ? 'cursor-pointer hover:border-forest-300' : ''}`}
    >
      {/* Top Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-2.5">
          <span className="text-2xl" role="img" aria-label={data.cropName}>
            {getCropEmoji(data.cropId)}
          </span>
          <div>
            <h4 className="text-sm font-bold text-stone-900 leading-tight">{data.cropName}</h4>
            <span className="text-[11px] text-stone-600">
              {data.marathiName ? `${data.marathiName} • ` : ''}Kharif Rainfed
            </span>
          </div>
        </div>

        <span
          className={`text-[10px] font-bold px-2 py-0.5 rounded-full border ${
            sourceStatusBadges[data.sourceStatus] || sourceStatusBadges.NO_RULE
          }`}
        >
          {data.sourceStatus === 'VALIDATED' ? 'Institutional Source Verified' : data.sourceStatus}
        </span>
      </div>

      {/* Prominent Decision Badge */}
      <div className="my-4 p-3 rounded-xl bg-stone-50 border border-stone-200/80 flex items-center justify-between">
        <div>
          <span className="text-[10px] font-semibold uppercase tracking-wider text-stone-600 block">
            Advisory Decision
          </span>
          <span className="text-base sm:text-lg font-black text-stone-900 tracking-tight">
            {current.label}
          </span>
        </div>
        <div className={`px-2.5 py-1 rounded-lg border text-xs font-bold flex items-center space-x-1.5 ${current.color}`}>
          <Icon className="w-3.5 h-3.5" />
          <span>{current.badgeText}</span>
        </div>
      </div>

      {/* Agronomic Guidance */}
      <div className="space-y-2 text-xs">
        <div>
          <span className="font-semibold text-stone-700 block">Agro-Meteorological Condition:</span>
          <p className="text-stone-600 mt-0.5 leading-relaxed">
            {data.forecastCondition || 'Rainfall criteria evaluated against localized threshold.'}
          </p>
        </div>

        {data.actionMessage && (
          <div className="p-2.5 rounded-lg bg-forest-50/70 border border-forest-100 text-forest-900">
            <span className="font-semibold block text-[11px] uppercase tracking-wider text-forest-800">
              Farmer Action:
            </span>
            <p className="mt-0.5 text-xs text-forest-950 font-medium leading-relaxed">
              {data.actionMessage}
            </p>
          </div>
        )}

        {data.institutionalSource && (
          <div className="pt-2 border-t border-stone-100 flex items-center space-x-1.5 text-[11px] text-stone-600">
            <BookOpen className="w-3.5 h-3.5 text-forest-700 shrink-0" />
            <span className="truncate">Source: {data.institutionalSource}</span>
          </div>
        )}
      </div>
    </div>
  );
};
