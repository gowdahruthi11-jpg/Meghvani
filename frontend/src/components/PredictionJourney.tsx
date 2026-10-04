import React from 'react';
import { Eye, BarChart2, CloudRain, BrainCircuit, Sprout, ChevronRight } from 'lucide-react';

interface PredictionJourneyProps {
  currentTab: string;
  onSelectTab: (tab: string) => void;
}

export const PredictionJourney: React.FC<PredictionJourneyProps> = ({ currentTab, onSelectTab }) => {
  const steps = [
    { id: 'map', tabTarget: 'map', label: 'OBSERVE', sub: 'Ground & Grid Telemetry', icon: Eye },
    { id: 'forecast', tabTarget: 'forecast', label: 'ANALYZE', sub: '30-Day Horizon Outlook', icon: BarChart2 },
    { id: 'prediction', tabTarget: 'prediction', label: 'PREDICT', sub: 'Onset & Break Probability', icon: CloudRain },
    { id: 'xai', tabTarget: 'xai', label: 'EXPLAIN', sub: 'Feature Contribution (XAI)', icon: BrainCircuit },
    { id: 'advisories', tabTarget: 'advisories', label: 'ADVISE', sub: 'ICAR Agronomic Action', icon: Sprout },
  ];

  return (
    <div className="hidden xl:flex items-center space-x-1 bg-stone-100/80 p-1.5 rounded-xl border border-stone-200/90 text-xs shadow-2xs">
      {steps.map((step, idx) => {
        const Icon = step.icon;
        const isActive = currentTab === step.tabTarget;
        const isPast = steps.findIndex((s) => s.tabTarget === currentTab) > idx;

        return (
          <React.Fragment key={step.id}>
            <button
              onClick={() => onSelectTab(step.tabTarget)}
              className={`flex items-center space-x-1.5 px-2.5 py-1.5 rounded-lg transition-all text-left ${
                isActive
                  ? 'bg-white text-forest-900 shadow-xs border border-stone-200/80 font-bold'
                  : isPast
                  ? 'text-stone-700 hover:text-stone-900 hover:bg-stone-200/60'
                  : 'text-stone-500 hover:text-stone-800 hover:bg-stone-200/50'
              }`}
              title={`Jump to ${step.label}: ${step.sub}`}
            >
              <div
                className={`w-5 h-5 rounded-md flex items-center justify-center shrink-0 ${
                  isActive
                    ? 'bg-forest-800 text-white'
                    : isPast
                    ? 'bg-emerald-100 text-emerald-800'
                    : 'bg-stone-200 text-stone-600'
                }`}
              >
                <Icon className="w-3 h-3" />
              </div>
              <div className="flex flex-col">
                <span className="font-extrabold text-[10px] tracking-wider leading-none">
                  {step.label}
                </span>
                <span className="text-[9px] text-stone-500 font-normal leading-tight hidden 2xl:block truncate max-w-[100px]">
                  {step.sub}
                </span>
              </div>
            </button>
            {idx < steps.length - 1 && (
              <ChevronRight className="w-3 h-3 text-stone-400 shrink-0" />
            )}
          </React.Fragment>
        );
      })}
    </div>
  );
};
