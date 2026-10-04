import React, { useState } from 'react';
import { MapPin, ShieldCheck, AlertTriangle, AlertOctagon, Info, Layers } from 'lucide-react';
import { Block } from '../types';

interface BlockRiskInfo {
  blockId: string;
  blockName: string;
  district: string;
  lat: number;
  lon: number;
  falseOnsetRisk: number; // e.g. 0.18
  breakRisk: number;
  heavyRainRisk: number;
  decision: 'SOW_NOW' | 'SOW_PART_NOW' | 'WAIT';
  confidence: string;
  dataCoverage: string;
}

interface BlockRiskMapProps {
  selectedBlockId: string;
  onSelectBlock: (blockId: string) => void;
  blocks?: Block[];
}

export const BlockRiskMap: React.FC<BlockRiskMapProps> = ({
  selectedBlockId,
  onSelectBlock,
}) => {
  const [activeLayer, setActiveLayer] = useState<'falseOnset' | 'break' | 'heavyRain' | 'confidence'>('falseOnset');

  // Ground truth blocks with prototype IMD gridded coordinates
  const blockData: BlockRiskInfo[] = [
    {
      blockId: 'BLK001',
      blockName: 'Nagpur Rural',
      district: 'Nagpur District, Vidarbha',
      lat: 21.1458,
      lon: 79.0882,
      falseOnsetRisk: 0.18,
      breakRisk: 0.22,
      heavyRainRisk: 0.12,
      decision: 'SOW_NOW',
      confidence: 'HIGH',
      dataCoverage: '100% IMD Gridded (2019–2024)',
    },
    {
      blockId: 'BLK002',
      blockName: 'Wardha East',
      district: 'Wardha District, Vidarbha',
      lat: 20.7453,
      lon: 78.6022,
      falseOnsetRisk: 0.35,
      breakRisk: 0.40,
      heavyRainRisk: 0.25,
      decision: 'SOW_PART_NOW',
      confidence: 'MEDIUM',
      dataCoverage: '100% IMD Gridded (2019–2024)',
    },
    {
      blockId: 'BLK003',
      blockName: 'Amravati Central',
      district: 'Amravati District, Vidarbha',
      lat: 20.9374,
      lon: 77.7796,
      falseOnsetRisk: 0.64,
      breakRisk: 0.58,
      heavyRainRisk: 0.45,
      decision: 'WAIT',
      confidence: 'HIGH',
      dataCoverage: '100% IMD Gridded (2019–2024)',
    },
  ];

  const getRiskColor = (prob: number) => {
    if (prob < 0.30) return { bg: 'bg-emerald-500', border: 'border-emerald-600', text: 'text-emerald-800', light: 'bg-emerald-50' };
    if (prob < 0.60) return { bg: 'bg-amber-500', border: 'border-amber-600', text: 'text-amber-800', light: 'bg-amber-50' };
    return { bg: 'bg-rose-500', border: 'border-rose-600', text: 'text-rose-800', light: 'bg-rose-50' };
  };

  const getDecisionBadge = (decision: string) => {
    if (decision === 'SOW_NOW') return 'bg-emerald-100 text-emerald-800 border-emerald-300';
    if (decision === 'SOW_PART_NOW') return 'bg-amber-100 text-amber-800 border-amber-300';
    return 'bg-rose-100 text-rose-800 border-rose-300';
  };

  return (
    <div className="agri-card p-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-stone-200">
        <div>
          <div className="flex items-center space-x-2">
            <span className="text-xl">🗺️</span>
            <h3 className="text-base font-bold text-stone-900 tracking-tight">Block Risk Map & Spatial Outlook</h3>
          </div>
          <p className="text-xs text-stone-600 mt-0.5">
            Maharashtra / Vidarbha prototype zone: IMD 0.25° representative centroid telemetry.
          </p>
        </div>

        {/* Map Layer Selector */}
        <div className="flex items-center space-x-1 p-1 bg-stone-100 rounded-xl border border-stone-200 self-start sm:self-auto text-xs font-semibold">
          <button
            onClick={() => setActiveLayer('falseOnset')}
            className={`px-2.5 py-1.5 rounded-lg transition-all ${
              activeLayer === 'falseOnset' ? 'bg-white text-forest-900 shadow-xs border border-stone-200' : 'text-stone-700 hover:text-stone-900'
            }`}
          >
            False Onset
          </button>
          <button
            onClick={() => setActiveLayer('break')}
            className={`px-2.5 py-1.5 rounded-lg transition-all ${
              activeLayer === 'break' ? 'bg-white text-forest-900 shadow-xs border border-stone-200' : 'text-stone-700 hover:text-stone-900'
            }`}
          >
            Dry Break
          </button>
          <button
            onClick={() => setActiveLayer('heavyRain')}
            className={`px-2.5 py-1.5 rounded-lg transition-all ${
              activeLayer === 'heavyRain' ? 'bg-white text-forest-900 shadow-xs border border-stone-200' : 'text-stone-700 hover:text-stone-900'
            }`}
          >
            Heavy Rain
          </button>
        </div>
      </div>

      {/* Grid of Blocks */}
      <div className="mt-5 grid grid-cols-1 md:grid-cols-3 gap-4">
        {blockData.map((b) => {
          const isSelected = selectedBlockId === b.blockId;
          const prob =
            activeLayer === 'falseOnset'
              ? b.falseOnsetRisk
              : activeLayer === 'break'
              ? b.breakRisk
              : b.heavyRainRisk;
          const colors = getRiskColor(prob);

          return (
            <div
              key={b.blockId}
              onClick={() => onSelectBlock(b.blockId)}
              className={`p-4 rounded-xl border cursor-pointer transition-all ${
                isSelected
                  ? 'bg-forest-50/60 border-forest-600 ring-2 ring-forest-500 shadow-sm'
                  : 'bg-stone-50 border-stone-200 hover:bg-white hover:border-forest-300'
              }`}
            >
              <div className="flex items-start justify-between">
                <div>
                  <div className="flex items-center space-x-1.5">
                    <MapPin className="w-4 h-4 text-forest-700" />
                    <span className="font-bold text-sm text-stone-900">{b.blockName}</span>
                  </div>
                  <p className="text-[11px] text-stone-600 mt-0.5">{b.district}</p>
                </div>
                <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full border ${getDecisionBadge(b.decision)}`}>
                  {b.decision.replace('_', ' ')}
                </span>
              </div>

              {/* Metric bar */}
              <div className="mt-4 space-y-1.5">
                <div className="flex items-center justify-between text-xs font-semibold">
                  <span className="text-stone-700">
                    {activeLayer === 'falseOnset'
                      ? 'False Onset Risk'
                      : activeLayer === 'break'
                      ? 'Monsoon Break Risk'
                      : 'Heavy Rain Risk'}
                  </span>
                  <span className={colors.text}>{(prob * 100).toFixed(0)}%</span>
                </div>
                <div className="w-full h-2 rounded-full bg-stone-200 overflow-hidden">
                  <div
                    className={`h-full rounded-full transition-all duration-300 ${colors.bg}`}
                    style={{ width: `${Math.min(prob * 100, 100)}%` }}
                  />
                </div>
              </div>

              {/* Coordinates & Metadata */}
              <div className="mt-3 pt-2.5 border-t border-stone-200/80 flex items-center justify-between text-[11px] text-stone-600">
                <span>{b.lat.toFixed(2)}°N, {b.lon.toFixed(2)}°E</span>
                <span className="text-forest-700 font-semibold">{isSelected ? '✓ Selected' : 'Click to View'}</span>
              </div>
            </div>
          );
        })}
      </div>

      {/* Spatial Notice */}
      <div className="mt-4 p-3 rounded-xl bg-stone-100/70 border border-stone-200/70 flex items-center justify-between text-[11px] text-stone-600">
        <div className="flex items-center space-x-2">
          <Info className="w-4 h-4 text-stone-500 shrink-0" />
          <span>
            <strong>Representative Centroid Mapping:</strong> Blocks snapped to IMD 0.25° grid centroid cells. Polygon boundaries pending block geojson integration.
          </span>
        </div>
        <span className="font-semibold text-stone-700 shrink-0 ml-2">Maharashtra / Vidarbha Zone</span>
      </div>
    </div>
  );
};
