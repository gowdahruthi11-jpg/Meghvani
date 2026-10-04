import React from 'react';
import { ShieldCheck, AlertTriangle, AlertOctagon, HelpCircle } from 'lucide-react';

interface RiskLegendProps {
  compact?: boolean;
}

export const RiskLegend: React.FC<RiskLegendProps> = ({ compact = false }) => {
  const items = [
    {
      level: 'Low Risk',
      decision: 'SOW NOW',
      color: 'bg-emerald-500',
      badge: 'badge-sow-now',
      icon: ShieldCheck,
      desc: 'False onset probability < 30%. Moisture & onset criteria met.',
    },
    {
      level: 'Moderate Caution',
      decision: 'SOW PART NOW',
      color: 'bg-amber-500',
      badge: 'badge-sow-part',
      icon: AlertTriangle,
      desc: 'Risk 30%–60%. Staggered planting recommended to spread risk.',
    },
    {
      level: 'High Risk',
      decision: 'WAIT',
      color: 'bg-rose-500',
      badge: 'badge-wait',
      icon: AlertOctagon,
      desc: 'Risk ≥ 60%. Prolonged dry spell or heavy rain hazard expected.',
    },
    {
      level: 'Data Gap',
      decision: 'NO DATA',
      color: 'bg-stone-400',
      badge: 'bg-stone-100 text-stone-600 border border-stone-300',
      icon: HelpCircle,
      desc: 'Insufficient station telemetry or unvalidated rule.',
    },
  ];

  if (compact) {
    return (
      <div className="flex flex-wrap items-center gap-3 text-xs">
        {items.map((it) => (
          <div key={it.level} className="flex items-center space-x-1.5">
            <span className={`w-2.5 h-2.5 rounded-full ${it.color}`} />
            <span className="font-semibold text-stone-700">{it.decision}</span>
            <span className="text-stone-500">({it.level})</span>
          </div>
        ))}
      </div>
    );
  }

  return (
    <div className="agri-card p-4">
      <div className="flex items-center justify-between mb-3 border-b border-stone-200 pb-2">
        <h4 className="text-xs font-bold uppercase tracking-wider text-stone-700">
          Meghvani Prototype Decision Guidelines
        </h4>
        <span className="text-[10px] text-stone-600 font-medium">Vidarbha Agro-Climatic Protocol</span>
      </div>
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
        {items.map((it) => {
          const Icon = it.icon;
          return (
            <div key={it.level} className="flex items-start space-x-3 p-2.5 rounded-xl bg-stone-50 border border-stone-200/80">
              <div className="w-8 h-8 rounded-lg flex items-center justify-center shrink-0 bg-white border border-stone-200 shadow-2xs">
                <Icon className={`w-4 h-4 ${it.level === 'Low Risk' ? 'text-emerald-700' : it.level === 'Moderate Caution' ? 'text-amber-700' : it.level === 'High Risk' ? 'text-rose-700' : 'text-stone-500'}`} />
              </div>
              <div>
                <div className="flex items-center space-x-1.5">
                  <span className={`text-[10px] font-bold px-1.5 py-0.5 rounded ${it.badge}`}>
                    {it.decision}
                  </span>
                  <span className="text-xs font-semibold text-stone-800">{it.level}</span>
                </div>
                <p className="text-[11px] text-stone-600 mt-1 leading-snug">{it.desc}</p>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
