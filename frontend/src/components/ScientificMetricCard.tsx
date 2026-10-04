import React from 'react';
import { LucideIcon, Info } from 'lucide-react';

interface ScientificMetricCardProps {
  title: string;
  metricType: 'DISCRIMINATION' | 'PROBABILISTIC_QUALITY' | 'CALIBRATION_ERROR' | 'BENCHMARK';
  value: string | number;
  referenceValue?: string | number;
  referenceLabel?: string;
  interpretation?: string;
  isNegativeSkill?: boolean;
  statusBadge?: string;
}

export const ScientificMetricCard: React.FC<ScientificMetricCardProps> = ({
  title,
  metricType,
  value,
  referenceValue,
  referenceLabel,
  interpretation,
  isNegativeSkill = false,
  statusBadge,
}) => {
  const typeConfig = {
    DISCRIMINATION: {
      label: 'DISCRIMINATION METRIC',
      badge: 'bg-purple-100 text-purple-800 border-purple-200',
    },
    PROBABILISTIC_QUALITY: {
      label: 'PROBABILISTIC QUALITY',
      badge: 'bg-sky-100 text-sky-800 border-sky-200',
    },
    CALIBRATION_ERROR: {
      label: 'CALIBRATION ERROR (ECE)',
      badge: 'bg-amber-100 text-amber-800 border-amber-200',
    },
    BENCHMARK: {
      label: 'CLIMATOLOGICAL REFERENCE',
      badge: 'bg-stone-100 text-stone-700 border-stone-200',
    },
  };

  const current = typeConfig[metricType];

  return (
    <div className="agri-card p-5 border-stone-200">
      <div className="flex items-center justify-between">
        <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full border ${current.badge}`}>
          {current.label}
        </span>
        {statusBadge && (
          <span className="text-[10px] font-semibold text-stone-500 uppercase tracking-wider">
            {statusBadge}
          </span>
        )}
      </div>

      <div className="mt-3">
        <p className="text-xs font-semibold uppercase tracking-wider text-stone-500">{title}</p>
        <div className="mt-1 flex items-baseline space-x-2">
          <span
            className={`text-2xl sm:text-3xl font-extrabold tracking-tight ${
              isNegativeSkill ? 'text-rose-600' : 'text-stone-900'
            }`}
          >
            {value}
          </span>
          {referenceValue !== undefined && (
            <span className="text-xs text-stone-500">
              vs {referenceLabel || 'Ref'}: <strong>{referenceValue}</strong>
            </span>
          )}
        </div>
      </div>

      {interpretation && (
        <div className="mt-3 pt-2.5 border-t border-stone-100 flex items-start space-x-1.5 text-[11px] text-stone-600">
          <Info className="w-3.5 h-3.5 text-stone-400 shrink-0 mt-0.5" />
          <p className="leading-snug">{interpretation}</p>
        </div>
      )}
    </div>
  );
};
