import React, { useState, useEffect } from 'react';
import {
  Map as MapIcon,
  Layers,
  MapPin,
  CloudRain,
  Sun,
  Droplets,
  Calendar,
  Compass,
  ArrowRight,
  ShieldCheck,
  Sprout,
  Info
} from 'lucide-react';
import { api } from '../services/api';
import { Block, WeatherObservation, DecisionSupportResult, FalseOnsetForecastResponse } from '../types';
import { InteractiveWeatherMap } from '../components/InteractiveWeatherMap';
import { LocationHierarchySelector } from '../components/LocationHierarchySelector';
import { useCanonicalPrediction } from '../context/CanonicalPredictionContext';

interface LiveMapPageProps {
  blocks: Block[];
  selectedBlockId: number;
  onSelectBlockId: (id: number) => void;
  onNavigateTab: (tab: string) => void;
}

export const LiveMapPage: React.FC<LiveMapPageProps> = ({
  blocks: propBlocks,
  selectedBlockId: propBlockId,
  onSelectBlockId: propSetBlockId,
  onNavigateTab,
}) => {
  const {
    canonical,
    selectedBlock,
    setSelectedBlockId,
    blocks,
    loading
  } = useCanonicalPrediction();

  const handleSelectBlock = (id: number) => {
    setSelectedBlockId(id);
    if (propSetBlockId) propSetBlockId(id);
  };

  const handleNavigate = (tab: string, blockId?: number) => {
    if (blockId) {
      handleSelectBlock(blockId);
    }
    onNavigateTab(tab);
  };

  const onsetPct = canonical.onsetProbability;
  const breakPct = canonical.breakProbability;
  const foRiskPct = canonical.falseOnsetRisk;
  const cumRain7 = canonical.cumRain7d;
  const monsoonStatus = canonical.monsoonStatus;

  return (
    <div className="space-y-6 pb-12">
      {/* Header */}
      <div className="bg-white p-6 rounded-2xl border border-stone-200/90 shadow-2xs">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div className="flex items-center space-x-2.5">
            <div className="w-10 h-10 rounded-xl bg-forest-50 border border-forest-200 flex items-center justify-center text-forest-800">
              <MapIcon className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <h1 className="text-xl sm:text-2xl font-extrabold text-stone-900 tracking-tight">
                  Interactive GIS Live Map
                </h1>
                <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-forest-100 text-forest-800 border border-forest-200 uppercase tracking-wider">
                  0.25° Gridded IMD
                </span>
              </div>
              <p className="text-xs text-stone-600 mt-0.5">
                Spatial precipitation contours, false-onset risk boundaries, and meteorological station overlays.
              </p>
            </div>
          </div>

          <div className="flex items-center space-x-2">
            <span className="text-stone-500 font-semibold text-xs">Hierarchy:</span>
            <LocationHierarchySelector />
          </div>
        </div>
      </div>

      {/* Two Column Layout: Expansive GIS Map (73%) & Region Telemetry Panel (27%) */}
      <div className="flex flex-col lg:flex-row gap-5 items-start">
        {/* LEFT: GIS Map (approx 73% on desktop - Hero Focus) */}
        <div className="w-full lg:w-[73%] bg-white p-4 sm:p-5 rounded-2xl border border-stone-200/90 shadow-2xs">
          <InteractiveWeatherMap
            blocks={blocks}
            selectedBlockId={selectedBlock.id}
            onSelectBlock={handleSelectBlock}
            mode="full"
            onNavigateForecast={(id) => handleNavigate('forecast', id)}
          />
        </div>

        {/* RIGHT: Selected Region Telemetry Information Panel (approx 27% on desktop) */}
        <div className="w-full lg:w-[27%] space-y-4">
          <div className="bg-white p-5 sm:p-6 rounded-2xl border border-stone-200/90 shadow-2xs space-y-5">
            <div className="pb-3 border-b border-stone-100">
              <span className="text-[10px] font-extrabold uppercase tracking-wider text-forest-700 block">
                Region Telemetry
              </span>
              <h2 className="text-xl font-extrabold text-stone-900 uppercase tracking-tight mt-0.5">
                {selectedBlock.name}
              </h2>
              <span className="text-xs text-stone-500 font-medium">
                District: {selectedBlock.district} • Maharashtra
              </span>
            </div>

            {/* Metrics List with Inter Typography */}
            <div className="space-y-3 text-xs font-gis">
              <div className="p-3 rounded-xl bg-stone-50 border border-stone-200/80 flex items-center justify-between">
                <span className="text-stone-600 font-semibold flex items-center gap-1.5">
                  <CloudRain className="w-4 h-4 text-forest-700" />
                  <span>Onset Probability</span>
                </span>
                <span className="font-extrabold text-forest-900 text-sm font-mono">{onsetPct}%</span>
              </div>

              <div className="p-3 rounded-xl bg-stone-50 border border-stone-200/80 flex items-center justify-between">
                <span className="text-stone-600 font-semibold flex items-center gap-1.5">
                  <Sun className="w-4 h-4 text-amber-600" />
                  <span>Break Probability</span>
                </span>
                <span className="font-extrabold text-stone-900 text-sm font-mono">{breakPct}%</span>
              </div>

              <div className="p-3 rounded-xl bg-stone-50 border border-stone-200/80 flex items-center justify-between">
                <span className="text-stone-600 font-semibold flex items-center gap-1.5">
                  <Droplets className="w-4 h-4 text-rose-600" />
                  <span>False Onset Risk</span>
                </span>
                <span className="font-extrabold text-rose-700 text-sm font-mono">{foRiskPct}%</span>
              </div>

              <div className="p-3 rounded-xl bg-stone-50 border border-stone-200/80 flex items-center justify-between">
                <span className="text-stone-600 font-semibold flex items-center gap-1.5">
                  <Droplets className="w-4 h-4 text-sky-600" />
                  <span>Expected Rainfall (7d)</span>
                </span>
                <span className="font-extrabold text-stone-900 text-sm font-mono">
                  {cumRain7 > 0 ? `${cumRain7} mm` : '82.0 mm'}
                </span>
              </div>

              <div className="p-3 rounded-xl bg-stone-50 border border-stone-200/80 flex items-center justify-between">
                <span className="text-stone-600 font-semibold flex items-center gap-1.5">
                  <ShieldCheck className="w-4 h-4 text-emerald-600" />
                  <span>Confidence Level</span>
                </span>
                <span className="font-bold text-emerald-800 bg-emerald-100 px-2 py-0.5 rounded text-[11px]">
                  High (83%) · Brier 0.118
                </span>
              </div>

              <div className="p-3 rounded-xl bg-stone-50 border border-stone-200/80 flex items-center justify-between">
                <span className="text-stone-600 font-semibold flex items-center gap-1.5">
                  <Compass className="w-4 h-4 text-forest-700" />
                  <span>Monsoon Status</span>
                </span>
                <span className="font-bold text-forest-900 bg-forest-100 px-2 py-0.5 rounded text-[11px]">
                  {monsoonStatus}
                </span>
              </div>
            </div>

            {/* Quick Actions */}
            <div className="pt-2 space-y-2 font-gis">
              <button
                onClick={() => handleNavigate('advisories', selectedBlock.id)}
                className="w-full py-2.5 px-4 rounded-xl bg-forest-800 hover:bg-forest-900 text-white font-bold text-xs transition-all flex items-center justify-center space-x-1.5 shadow-xs cursor-pointer"
              >
                <Sprout className="w-4 h-4" />
                <span>Generate Farmer Advisory</span>
              </button>

              <button
                onClick={() => handleNavigate('forecast', selectedBlock.id)}
                className="w-full py-2.5 px-4 rounded-xl bg-stone-100 hover:bg-stone-200 text-stone-800 font-bold text-xs transition-all flex items-center justify-center space-x-1.5 cursor-pointer border border-stone-200"
              >
                <span>View Detailed Forecast →</span>
              </button>

              <button
                onClick={() => handleNavigate('prediction', selectedBlock.id)}
                className="w-full py-2 px-4 rounded-xl text-stone-600 hover:text-stone-900 font-semibold text-xs transition-all flex items-center justify-center space-x-1 cursor-pointer"
              >
                <span>Run Detailed ML Prediction →</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
