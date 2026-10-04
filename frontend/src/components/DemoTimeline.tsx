import React from 'react';
import {
  CloudRain,
  BarChart3,
  AlertTriangle,
  Sprout,
  Smartphone,
  Send,
  UserCheck,
  CheckCircle2,
  Shield,
  ArrowRight
} from 'lucide-react';

export interface TimelineStep {
  id: string;
  number: number;
  title: string;
  subtitle: string;
  icon: any;
  status: 'COMPLETED' | 'ACTIVE' | 'PENDING';
  dataSummary?: string;
}

interface DemoTimelineProps {
  currentStepId: string;
  onSelectStep: (stepId: string) => void;
}

export const DemoTimeline: React.FC<DemoTimelineProps> = ({
  currentStepId,
  onSelectStep,
}) => {
  const steps: TimelineStep[] = [
    {
      id: 'weather',
      number: 1,
      title: 'Weather Ingestion',
      subtitle: 'IMD 0.25° Gridded Rainfall',
      icon: CloudRain,
      status: 'COMPLETED',
      dataSummary: '6,576 Station Days',
    },
    {
      id: 'forecast',
      number: 2,
      title: 'Model Forecast',
      subtitle: 'Platt Calibrated Sigmoid',
      icon: BarChart3,
      status: 'COMPLETED',
      dataSummary: '7D False Onset: 18%',
    },
    {
      id: 'risk',
      number: 3,
      title: 'Risk Evaluation',
      subtitle: 'Decision Thresholds',
      icon: AlertTriangle,
      status: 'COMPLETED',
      dataSummary: '< 30% Low Hazard',
    },
    {
      id: 'decision',
      number: 4,
      title: 'Farm Decision',
      subtitle: 'Validated Sowing Advice',
      icon: Sprout,
      status: 'ACTIVE',
      dataSummary: 'SOW NOW (Soybean)',
    },
    {
      id: 'message',
      number: 5,
      title: 'Farmer Message',
      subtitle: 'Multilingual Regional',
      icon: Smartphone,
      status: 'COMPLETED',
      dataSummary: 'Marathi / Hindi / English',
    },
    {
      id: 'delivery',
      number: 6,
      title: 'Simulated Delivery',
      subtitle: 'SMS / WhatsApp / IVR',
      icon: Send,
      status: 'COMPLETED',
      dataSummary: 'Voice Retry + SMS Fallback',
    },
    {
      id: 'observation',
      number: 7,
      title: 'Farmer Observation',
      subtitle: 'Ground Truth Feedback',
      icon: UserCheck,
      status: 'COMPLETED',
      dataSummary: 'Rain Gauge / Sowing Date',
    },
    {
      id: 'validation',
      number: 8,
      title: 'Scientific Audit',
      subtitle: 'Rolling-Origin Integrity',
      icon: CheckCircle2,
      status: 'COMPLETED',
      dataSummary: 'ECE 1.87% | Brier 0.037',
    },
    {
      id: 'officer',
      number: 9,
      title: 'Officer Center',
      subtitle: 'Block & District View',
      icon: Shield,
      status: 'COMPLETED',
      dataSummary: 'Vidarbha Command Console',
    },
  ];

  return (
    <div className="agri-card p-6">
      {/* Top Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-stone-200">
        <div>
          <div className="flex items-center space-x-2">
            <span className="text-xl">🌾</span>
            <h3 className="text-base font-bold text-stone-900 tracking-tight">
              Meghvani End-to-End Decision & Delivery Pipeline
            </h3>
          </div>
          <p className="text-xs text-stone-600 mt-0.5">
            Click any stage along the 9-point agricultural intelligence cycle to inspect live contracts.
          </p>
        </div>

        <div className="flex items-center space-x-2 shrink-0">
          <span className="text-[10px] font-bold px-2.5 py-1 rounded-full bg-forest-100 text-forest-800 border border-forest-300">
            HISTORICAL REPLAY
          </span>
          <span className="text-[10px] font-bold px-2.5 py-1 rounded-full bg-amber-100 text-amber-800 border border-amber-300">
            SIMULATION ONLY
          </span>
          <span className="text-[10px] font-bold px-2.5 py-1 rounded-full bg-rose-100 text-rose-800 border border-rose-300">
            NOT OPERATIONAL
          </span>
        </div>
      </div>

      {/* Timeline Steps (Responsive horizontal flow) */}
      <div className="mt-5 overflow-x-auto pb-3">
        <div className="flex items-center space-x-2 min-w-max">
          {steps.map((st, idx) => {
            const isSelected = currentStepId === st.id;
            const Icon = st.icon;

            return (
              <React.Fragment key={st.id}>
                <div
                  onClick={() => onSelectStep(st.id)}
                  className={`p-3.5 rounded-xl border cursor-pointer transition-all w-48 text-left ${
                    isSelected
                      ? 'bg-forest-50 border-forest-600 ring-2 ring-forest-500 shadow-sm'
                      : 'bg-stone-50 border-stone-200 hover:bg-white hover:border-forest-300'
                  }`}
                >
                  <div className="flex items-center justify-between mb-2">
                    <span
                      className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold ${
                        isSelected
                          ? 'bg-forest-700 text-white'
                          : 'bg-stone-200 text-stone-700'
                      }`}
                    >
                      {st.number}
                    </span>
                    <Icon
                      className={`w-4 h-4 ${
                        isSelected ? 'text-forest-700' : 'text-stone-500'
                      }`}
                    />
                  </div>

                  <p className="text-xs font-bold text-stone-900 leading-tight">
                    {st.title}
                  </p>
                  <p className="text-[11px] text-stone-600 mt-0.5 truncate">
                    {st.subtitle}
                  </p>

                  {st.dataSummary && (
                    <div className="mt-2.5 pt-2 border-t border-stone-200/80">
                      <span className="text-[10px] font-semibold text-forest-800 bg-forest-100/70 px-1.5 py-0.5 rounded block truncate">
                        {st.dataSummary}
                      </span>
                    </div>
                  )}
                </div>

                {idx < steps.length - 1 && (
                  <ArrowRight className="w-4 h-4 text-stone-400 shrink-0" />
                )}
              </React.Fragment>
            );
          })}
        </div>
      </div>
    </div>
  );
};
