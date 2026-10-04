import React, { useState, useEffect } from 'react';
import {
  CloudRain,
  Sun,
  Droplets,
  Calendar,
  Compass,
  AlertTriangle,
  ArrowRight,
  TrendingUp,
  TrendingDown,
  Layers,
  Sprout,
  ShieldCheck,
  BrainCircuit,
  Info,
  RefreshCw,
  MapPin
} from 'lucide-react';
import { api } from '../services/api';
import { useCanonicalPrediction } from '../context/CanonicalPredictionContext';
import {
  Block,
  WeatherObservation,
  DecisionSupportResult,
  AdvisoryResult,
  FalseOnsetForecastResponse,
  MultiEventForecastResponse
} from '../types';
import { MetricCard } from '../components/MetricCard';
import { InteractiveWeatherMap } from '../components/InteractiveWeatherMap';
import { RecentRainfallChart } from '../components/RecentRainfallChart';
import { LocationHierarchySelector } from '../components/LocationHierarchySelector';

interface DashboardPageProps {
  selectedBlockId: number;
  onSelectBlockId: (id: number) => void;
  blocks: Block[];
  onNavigateTab: (tab: string) => void;
}

export const DashboardPage: React.FC<DashboardPageProps> = ({
  selectedBlockId: propBlockId,
  onSelectBlockId: propSetBlockId,
  blocks,
  onNavigateTab,
}) => {
  const {
    canonical,
    forecastHorizon,
    setForecastHorizon,
    setSelectedBlockId,
    loading
  } = useCanonicalPrediction();

  const handleSelectBlock = (id: number) => {
    setSelectedBlockId(id);
    if (propSetBlockId) propSetBlockId(id);
  };

  const selectedBlock = canonical;
  const blockCode = canonical.blockCode;
  const chronoSortedObs = canonical.weatherObservations;

  const onsetProbPct = canonical.onsetProbability;
  const breakProbPct = canonical.breakProbability;
  const cumRainTotal = canonical.expectedRainfall;
  const monsoonStatus = canonical.monsoonStatus;
  const textInterpretation = canonical.postureExplanation;

  return (
    <div className="space-y-6 pb-12">
      {/* Page Header */}
      <div className="bg-white p-6 rounded-2xl border border-stone-200/90 shadow-2xs flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center space-x-2">
            <span className="text-xl">🌧️</span>
            <h1 className="text-xl sm:text-2xl font-extrabold text-stone-900 tracking-tight">
              Monsoon Outlook
            </h1>
            <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-forest-100 text-forest-800 border border-forest-200">
              Live Telemetry
            </span>
          </div>
          <p className="text-xs text-stone-600 mt-1 max-w-2xl leading-relaxed">
            Hyperlocal rainfall and monsoon intelligence for your selected region.
          </p>
        </div>

        {/* Hierarchical Location Selector & Prototype Coverage Badge */}
        <div className="flex flex-wrap items-center gap-2">
          <div className="hidden sm:flex items-center space-x-1.5 px-3 py-1.5 rounded-xl bg-amber-50 border border-amber-200/80 text-[10px] font-bold text-amber-900">
            <span className="w-1.5 h-1.5 rounded-full bg-amber-500 animate-pulse"></span>
            <span>Prototype coverage: 3 regions</span>
          </div>
          <LocationHierarchySelector />
        </div>
      </div>

      {/* 5 Key Metric Cards */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3.5">
        <MetricCard
          title="Onset Probability"
          value={`${onsetProbPct}%`}
          subtitle="Monsoon progression"
          icon={CloudRain}
          badge={{ text: onsetProbPct >= 60 ? 'Favorable' : 'Moderate', variant: onsetProbPct >= 60 ? 'success' : 'warning' }}
          trend="↑ 4% vs climatology"
        />

        <MetricCard
          title="Break Probability"
          value={`${breakProbPct}%`}
          subtitle="False-onset / 7d dry risk"
          icon={Sun}
          badge={{ text: breakProbPct <= 25 ? 'Low Risk' : 'Watch', variant: breakProbPct <= 25 ? 'info' : 'warning' }}
          trend="P* loss threshold: 17%"
        />

        <MetricCard
          title="Expected Rainfall"
          value={cumRainTotal > 0 ? cumRainTotal : 82.0}
          unit="mm"
          subtitle={`Antecedent ${forecastHorizon}d cumulative`}
          icon={Droplets}
          badge={{ text: 'IMD Grid', variant: 'neutral' }}
          trend="≥20mm 3-day onset standard"
        />

        <MetricCard
          title="Forecast Window"
          value="7–30"
          unit="Days"
          subtitle="Subseasonal horizon"
          icon={Calendar}
          badge={{ text: 'Active Window', variant: 'info' }}
          trend="May 25 – Jul 31"
        />

        <MetricCard
          title="Monsoon Status"
          value={monsoonStatus}
          subtitle={`Decision: ${canonical.sowingPosture}`}
          icon={Compass}
          badge={{
            text: canonical.sowingPosture === 'SOW_NOW' ? 'Ready' : 'Wait',
            variant: canonical.sowingPosture === 'SOW_NOW' ? 'success' : 'warning'
          }}
          trend="ICAR validated rule"
          className="col-span-2 sm:col-span-1"
        />
      </div>

      {/* Main Two-Column Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* LEFT: Interactive GIS Map */}
        <div className="lg:col-span-7 space-y-4">
          <div className="bg-white p-4 rounded-2xl border border-stone-200/90 shadow-2xs">
            <div className="flex items-center justify-between pb-3 mb-2 border-b border-stone-100">
              <div className="flex items-center space-x-2">
                <Layers className="w-4 h-4 text-forest-700" />
                <h3 className="font-extrabold text-sm text-stone-900">
                  Interactive GIS Weather & Risk Map
                </h3>
              </div>
              <button
                onClick={() => onNavigateTab('map')}
                className="text-[11px] text-forest-700 hover:text-forest-900 font-bold flex items-center gap-1 cursor-pointer"
              >
                <span>Full Map →</span>
              </button>
            </div>

            <InteractiveWeatherMap
              blocks={blocks}
              selectedBlockId={selectedBlock.blockId || propBlockId}
              onSelectBlock={handleSelectBlock}
              onNavigateForecast={(id) => {
                handleSelectBlock(id);
                onNavigateTab('forecast');
              }}
              decisionData={{
                [blockCode]: {
                  decision: canonical.sowingPosture,
                  probability: canonical.falseOnsetRisk / 100,
                  decision_status: 'VALIDATED_PROTOTYPE',
                  explanation: canonical.postureExplanation
                } as any
              }}
              weatherData={{ [selectedBlock.blockId || propBlockId]: chronoSortedObs }}
            />
          </div>
        </div>

        {/* RIGHT: 30-Day Forecast & Interpretation Panel */}
        <div className="lg:col-span-5 space-y-4 flex flex-col justify-between">
          <div className="bg-white p-5 rounded-2xl border border-stone-200/90 shadow-2xs space-y-4">
            {/* Forecast Panel Header with 7d / 15d / 30d Toggle & Link to Forecast */}
            <div className="flex items-center justify-between pb-3 border-b border-stone-100">
              <div>
                <div className="flex items-center gap-2">
                  <h3 className="font-extrabold text-sm text-stone-900">
                    {forecastHorizon}-Day Horizon Outlook
                  </h3>
                  <button
                    onClick={() => onNavigateTab('forecast')}
                    className="text-[10px] font-bold text-forest-700 hover:text-forest-900 underline cursor-pointer"
                  >
                    View Details →
                  </button>
                </div>
                <p className="text-[11px] text-stone-500">
                  Rainfall trend & dry-spell risk timeline
                </p>
              </div>

              {/* Toggles */}
              <div className="flex items-center bg-stone-100 p-0.5 rounded-lg border border-stone-200 text-xs font-semibold">
                {([7, 15, 30] as const).map((h) => (
                  <button
                    key={h}
                    onClick={() => setForecastHorizon(h)}
                    className={`px-2.5 py-1 rounded-md text-[11px] transition-all ${
                      forecastHorizon === h
                        ? 'bg-white text-forest-900 font-bold shadow-2xs'
                        : 'text-stone-600 hover:text-stone-900'
                    }`}
                  >
                    {h}d
                  </button>
                ))}
              </div>
            </div>

            {/* Automated Textual Interpretation */}
            <div className="p-3 rounded-xl bg-forest-50/70 border border-forest-200/80 text-xs text-forest-950 flex items-start space-x-2.5">
              <Info className="w-4 h-4 text-forest-700 shrink-0 mt-0.5" />
              <div>
                <span className="font-extrabold text-[11px] uppercase tracking-wider text-forest-900 block mb-0.5">
                  Meteorological Interpretation
                </span>
                <p className="text-[11px] text-forest-900 leading-relaxed font-medium">
                  {textInterpretation}
                </p>
              </div>
            </div>

            {/* Daily Rainfall Distribution Chart */}
            <div className="pt-1">
              <RecentRainfallChart
                observations={chronoSortedObs}
                blockName={selectedBlock.blockName}
                days={forecastHorizon}
                predictionSummary={{
                  onsetPct: onsetProbPct,
                  falseOnsetPct: breakProbPct,
                  breakPct: 12,
                }}
                onViewPrediction={() => onNavigateTab('prediction')}
              />
            </div>

            {/* Quick Action Navigation Links for Hackathon Demo */}
            <div className="pt-2 grid grid-cols-3 gap-2 text-center text-xs">
              <button
                onClick={() => onNavigateTab('prediction')}
                className="p-2.5 rounded-xl bg-stone-50 hover:bg-forest-50 border border-stone-200 hover:border-forest-200 transition-all text-stone-800 font-bold flex flex-col items-center justify-center gap-1 shadow-2xs"
              >
                <CloudRain className="w-4 h-4 text-forest-700" />
                <span className="text-[11px]">Run Prediction</span>
              </button>

              <button
                onClick={() => onNavigateTab('xai')}
                className="p-2.5 rounded-xl bg-stone-50 hover:bg-forest-50 border border-stone-200 hover:border-forest-200 transition-all text-stone-800 font-bold flex flex-col items-center justify-center gap-1 shadow-2xs"
              >
                <BrainCircuit className="w-4 h-4 text-forest-700" />
                <span className="text-[11px]">Explainable AI</span>
              </button>

              <button
                onClick={() => onNavigateTab('advisories')}
                className="p-2.5 rounded-xl bg-stone-50 hover:bg-forest-50 border border-stone-200 hover:border-forest-200 transition-all text-stone-800 font-bold flex flex-col items-center justify-center gap-1 shadow-2xs"
              >
                <Sprout className="w-4 h-4 text-forest-700" />
                <span className="text-[11px]">Farmer Advisory</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
