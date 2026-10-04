import React from 'react';
import { LucideIcon } from 'lucide-react';

interface AgricultureMetricCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon: LucideIcon;
  variant?: 'forest' | 'leaf' | 'rain' | 'amber' | 'rose' | 'stone';
  badge?: {
    text: string;
    type?: 'success' | 'warning' | 'danger' | 'info' | 'neutral';
  };
  onClick?: () => void;
}

export const AgricultureMetricCard: React.FC<AgricultureMetricCardProps> = ({
  title,
  value,
  subtitle,
  icon: Icon,
  variant = 'forest',
  badge,
  onClick,
}) => {
  const variantStyles = {
    forest: {
      iconBg: 'bg-forest-50 text-forest-800 border-forest-200',
      accent: 'border-l-4 border-l-forest-700',
    },
    leaf: {
      iconBg: 'bg-emerald-50 text-emerald-800 border-emerald-200',
      accent: 'border-l-4 border-l-emerald-600',
    },
    rain: {
      iconBg: 'bg-sky-50 text-sky-800 border-sky-200',
      accent: 'border-l-4 border-l-sky-600',
    },
    amber: {
      iconBg: 'bg-amber-50 text-amber-800 border-amber-200',
      accent: 'border-l-4 border-l-amber-500',
    },
    rose: {
      iconBg: 'bg-rose-50 text-rose-800 border-rose-200',
      accent: 'border-l-4 border-l-rose-500',
    },
    stone: {
      iconBg: 'bg-stone-100 text-stone-700 border-stone-200',
      accent: 'border-l-4 border-l-stone-400',
    },
  };

  const badgeStyles = {
    success: 'bg-emerald-100 text-emerald-800 border-emerald-300',
    warning: 'bg-amber-100 text-amber-800 border-amber-300',
    danger: 'bg-rose-100 text-rose-800 border-rose-300',
    info: 'bg-sky-100 text-sky-800 border-sky-300',
    neutral: 'bg-stone-100 text-stone-700 border-stone-300',
  };

  const current = variantStyles[variant];

  return (
    <div
      onClick={onClick}
      className={`agri-card p-5 ${current.accent} ${onClick ? 'cursor-pointer hover:scale-[1.01]' : ''}`}
    >
      <div className="flex items-start justify-between">
        <div>
          <p className="text-xs font-semibold uppercase tracking-wider text-stone-700">{title}</p>
          <div className="mt-2 flex items-baseline space-x-2">
            <span className="text-2xl sm:text-3xl font-bold text-stone-900 tracking-tight">{value}</span>
            {badge && (
              <span
                className={`text-[11px] font-semibold px-2 py-0.5 rounded-full border ${
                  badgeStyles[badge.type || 'neutral']
                }`}
              >
                {badge.text}
              </span>
            )}
          </div>
          {subtitle && <p className="mt-1 text-xs text-stone-600 leading-relaxed">{subtitle}</p>}
        </div>
        <div className={`w-11 h-11 rounded-xl flex items-center justify-center border ${current.iconBg} shrink-0`}>
          <Icon className="w-5 h-5" />
        </div>
      </div>
    </div>
  );
};
