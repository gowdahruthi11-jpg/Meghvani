import React from 'react';
import { LucideIcon } from 'lucide-react';

interface MetricCardProps {
  title: string;
  value: string | number;
  unit?: string;
  subtitle?: string;
  icon: LucideIcon;
  badge?: {
    text: string;
    variant: 'success' | 'warning' | 'danger' | 'info' | 'neutral';
  };
  trend?: string;
  confidence?: string;
  className?: string;
}

export const MetricCard: React.FC<MetricCardProps> = ({
  title,
  value,
  unit,
  subtitle,
  icon: Icon,
  badge,
  trend,
  confidence,
  className = '',
}) => {
  const badgeClasses = {
    success: 'bg-emerald-50 text-emerald-800 border-emerald-200',
    warning: 'bg-amber-50 text-amber-800 border-amber-200',
    danger: 'bg-rose-50 text-rose-800 border-rose-200',
    info: 'bg-sky-50 text-sky-800 border-sky-200',
    neutral: 'bg-stone-100 text-stone-700 border-stone-200',
  };

  return (
    <div
      className={`p-4 rounded-2xl bg-white border border-stone-200/90 shadow-2xs hover:shadow-xs transition-all flex flex-col justify-between ${className}`}
    >
      <div className="flex items-start justify-between gap-2">
        <div className="flex items-center space-x-2">
          <div className="w-8 h-8 rounded-xl bg-stone-100 text-stone-700 flex items-center justify-center shrink-0">
            <Icon className="w-4 h-4 text-stone-700" />
          </div>
          <div>
            <span className="text-[11px] font-bold text-stone-500 uppercase tracking-wider block">
              {title}
            </span>
          </div>
        </div>

        {badge && (
          <span
            className={`text-[10px] font-bold px-2 py-0.5 rounded-full border shrink-0 ${
              badgeClasses[badge.variant] || badgeClasses.neutral
            }`}
          >
            {badge.text}
          </span>
        )}
      </div>

      <div className="mt-3">
        <div className="flex items-baseline space-x-1.5">
          <span className="text-2xl sm:text-3xl font-extrabold text-stone-900 tracking-tight">
            {value}
          </span>
          {unit && <span className="text-xs font-semibold text-stone-500">{unit}</span>}
        </div>

        {subtitle && (
          <p className="text-[11px] text-stone-600 font-medium mt-1 leading-snug truncate">
            {subtitle}
          </p>
        )}
      </div>

      {(trend || confidence) && (
        <div className="mt-3 pt-2 border-t border-stone-100 flex items-center justify-between text-[10px] text-stone-500 font-medium">
          {trend && <span>{trend}</span>}
          {confidence && <span className="font-semibold text-stone-600">{confidence}</span>}
        </div>
      )}
    </div>
  );
};
