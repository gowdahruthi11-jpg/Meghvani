import React from 'react';
import { CloudRain, AlertTriangle, Sprout, Eye, Info } from 'lucide-react';
import { DecisionSupportResult } from '../types';

interface MonsoonStoryProps {
  blockName: string;
  decisionData?: DecisionSupportResult | null;
  recentRainfallMm?: number;
}

export const MonsoonStory: React.FC<MonsoonStoryProps> = ({
  blockName,
  decisionData,
  recentRainfallMm = 92.7,
}) => {
  const prob = decisionData?.probability !== null && decisionData?.probability !== undefined
    ? Math.round(decisionData.probability * 100)
    : 18;
  const decision = decisionData?.decision || 'SOW_NOW';

  return (
    <div className="bg-white rounded-2xl border border-stone-200/90 p-5 shadow-sm">
      <div className="flex items-center justify-between pb-3 mb-4 border-b border-stone-200">
        <div className="flex items-center gap-2">
          <span className="text-xl">🌧️</span>
          <div>
            <h3 className="font-bold text-stone-900 text-sm">
              What is happening? · Monsoon Narrative
            </h3>
            <span className="text-xs text-stone-500">
              Natural-language interpretation for {blockName}
            </span>
          </div>
        </div>

        <span className="text-[11px] font-semibold text-forest-800 bg-forest-50 border border-forest-200/80 px-2.5 py-1 rounded-full">
          Prototype Advisory Narrative
        </span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3.5">
        {/* 1. RAINFALL */}
        <div className="p-3.5 rounded-xl bg-sky-50/70 border border-sky-200/70 flex flex-col justify-between">
          <div>
            <div className="flex items-center gap-1.5 text-xs font-bold text-sky-900 mb-1.5 uppercase tracking-wide">
              <CloudRain className="w-4 h-4 text-sky-700" />
              <span>Rainfall Status</span>
            </div>
            <p className="text-xs text-stone-800 font-medium leading-relaxed">
              {recentRainfallMm >= 50
                ? `Recent rainfall has been adequate (${recentRainfallMm} mm cumulative), satisfying the initial seedbed wetting requirement.`
                : `Recent rainfall has been light to moderate (${recentRainfallMm} mm), approaching the minimum onset threshold.`}
            </p>
          </div>
          <span className="text-[10px] text-sky-800 font-semibold mt-2 block">
            Metric: Cumulative 7D Precipitation
          </span>
        </div>

        {/* 2. RISK */}
        <div className="p-3.5 rounded-xl bg-amber-50/70 border border-amber-200/70 flex flex-col justify-between">
          <div>
            <div className="flex items-center gap-1.5 text-xs font-bold text-amber-900 mb-1.5 uppercase tracking-wide">
              <AlertTriangle className="w-4 h-4 text-amber-700" />
              <span>Monsoon Risk</span>
            </div>
            <p className="text-xs text-stone-800 font-medium leading-relaxed">
              {prob < 30
                ? `False-onset risk is currently low (${prob}%), well below the 40% intervention threshold.`
                : prob < 60
                ? `False-onset risk is moderate (${prob}%); seedbed moisture requires staggered sowing caution.`
                : `False-onset hazard is elevated (${prob}%); prolonged dry spell hazard detected.`}
            </p>
          </div>
          <span className="text-[10px] text-amber-800 font-semibold mt-2 block">
            Metric: False-Onset Probability ({prob}%)
          </span>
        </div>

        {/* 3. FARM ACTION */}
        <div className="p-3.5 rounded-xl bg-emerald-50/70 border border-emerald-200/70 flex flex-col justify-between">
          <div>
            <div className="flex items-center gap-1.5 text-xs font-bold text-emerald-900 mb-1.5 uppercase tracking-wide">
              <Sprout className="w-4 h-4 text-emerald-700" />
              <span>Farm Action</span>
            </div>
            <p className="text-xs text-stone-800 font-medium leading-relaxed">
              {decision === 'SOW_NOW'
                ? 'Current prototype conditions support the selected sowing window with Broad Bed Furrow moisture conservation.'
                : decision === 'SOW_PART_NOW'
                ? 'Current conditions suggest partial or staggered sowing across well-drained medium-to-deep soils.'
                : 'Current advisory recommends waiting for sustained revival showers before sowing.'}
            </p>
          </div>
          <span className="text-[10px] text-emerald-800 font-semibold mt-2 block">
            Decision: {decision.replace(/_/g, ' ')}
          </span>
        </div>

        {/* 4. WATCH */}
        <div className="p-3.5 rounded-xl bg-stone-50 border border-stone-200 flex flex-col justify-between">
          <div>
            <div className="flex items-center gap-1.5 text-xs font-bold text-stone-800 mb-1.5 uppercase tracking-wide">
              <Eye className="w-4 h-4 text-stone-700" />
              <span>Field Watch</span>
            </div>
            <p className="text-xs text-stone-700 font-medium leading-relaxed">
              Continue monitoring for a prolonged dry spell over the next 14–21 day vegetative window. Verify soil profile moisture at 15 cm depth.
            </p>
          </div>
          <div className="flex items-center gap-1 text-[10px] text-stone-500 mt-2">
            <Info className="w-3 h-3 text-stone-400" />
            <span>KVK Advisory protocol</span>
          </div>
        </div>
      </div>
    </div>
  );
};
