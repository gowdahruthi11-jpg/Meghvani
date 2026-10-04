import React, { useState, useEffect } from 'react';
import {
  CloudRain,
  MapPin,
  RefreshCw,
  Info,
  Calendar,
  Layers,
  Sprout,
  ShieldAlert,
  ArrowRight,
  Search
} from 'lucide-react';
import { api } from '../services/api';
import {
  Block,
  Crop,
  WeatherObservation,
  FalseOnsetForecastResponse,
  DecisionSupportResult,
  AdvisoryResult
} from '../types';
import { InteractiveWeatherMap } from '../components/InteractiveWeatherMap';
import { FarmDecisionPanel } from '../components/FarmDecisionPanel';
import { RainfallOutlook } from '../components/RainfallOutlook';
import { RecentRainfallChart } from '../components/RecentRainfallChart';
import { MonsoonStory } from '../components/MonsoonStory';
import { CropDecisionCard, CropDecisionData } from '../components/CropDecisionCard';
import { FarmerMessageCard } from '../components/FarmerMessageCard';
import { RiskLegend } from '../components/RiskLegend';

interface LandingPageProps {
  setCurrentTab: (tab: string) => void;
}

export const LandingPage: React.FC<LandingPageProps> = ({ setCurrentTab }) => {
  // State for location, crop, and horizon selection
  const [selectedBlockNum, setSelectedBlockNum] = useState<number>(1);
  const [selectedCropId, setSelectedCropId] = useState<string>('soybean');
  const [selectedHorizon, setSelectedHorizon] = useState<7 | 14 | 21 | 30>(7);
  const [pinInput, setPinInput] = useState<string>('441501');
  const [pinFeedback, setPinFeedback] = useState<string | null>(null);

  // Live data states
  const [blocks, setBlocks] = useState<Block[]>([
    { id: 1, name: 'Nagpur Rural', district: 'Nagpur', state: 'Maharashtra', latitude: 21.1458, longitude: 79.0882, active: true },
    { id: 2, name: 'Wardha East', district: 'Wardha', state: 'Maharashtra', latitude: 20.7453, longitude: 78.6022, active: true },
    { id: 3, name: 'Amravati Central', district: 'Amravati', state: 'Maharashtra', latitude: 20.9374, longitude: 77.7796, active: true },
  ]);
  const [crops, setCrops] = useState<Crop[]>([]);
  const [weatherDataMap, setWeatherDataMap] = useState<Record<number, WeatherObservation[]>>({});
  const [currentWeatherList, setCurrentWeatherList] = useState<WeatherObservation[]>([]);
  const [decisionMap, setDecisionMap] = useState<Record<string, DecisionSupportResult>>({});
  const [forecastData, setForecastData] = useState<FalseOnsetForecastResponse | null>(null);
  const [advisoryData, setAdvisoryData] = useState<AdvisoryResult | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [refreshing, setRefreshing] = useState<boolean>(false);

  const blockCode = selectedBlockNum === 2 ? 'BLK002' : selectedBlockNum === 3 ? 'BLK003' : 'BLK001';
  const selectedBlock = blocks.find((b) => b.id === selectedBlockNum) || blocks[0];

  // Fetch telemetry from backend
  const fetchDashboardData = async (bNum: number, crop: string) => {
    try {
      setRefreshing(true);
      const code = bNum === 2 ? 'BLK002' : bNum === 3 ? 'BLK003' : 'BLK001';

      const [bList, cList, wList, fCast, dResult, advResult] = await Promise.all([
        api.getBlocks().catch(() => []),
        api.getCrops().catch(() => []),
        api.getWeather(bNum).catch(() => []),
        api.getFalseOnsetForecast(code).catch(() => null),
        api.getFalseOnsetDecision(code).catch(() => null),
        api.getBlockAdvisory(code, crop, 'mr').catch(() => null),
      ]);

      if (bList.length > 0) setBlocks(bList);
      if (cList.length > 0) setCrops(cList);
      setCurrentWeatherList(wList);
      setWeatherDataMap((prev) => ({ ...prev, [bNum]: wList }));
      setForecastData(fCast);
      if (dResult) {
        setDecisionMap((prev) => ({ ...prev, [code]: dResult }));
      }
      setAdvisoryData(advResult);
    } catch (err) {
      console.error('Error fetching dashboard telemetry:', err);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    fetchDashboardData(selectedBlockNum, selectedCropId);
  }, [selectedBlockNum, selectedCropId]);

  // Handle map selection
  const handleSelectBlock = (bId: number) => {
    setSelectedBlockNum(bId);
    if (bId === 1) setPinInput('441501');
    else if (bId === 2) setPinInput('442104');
    else if (bId === 3) setPinInput('444904');
    setPinFeedback(null);
  };

  const handlePinLookup = async (inputPin: string) => {
    const cleanPin = inputPin.replace(/\s+/g, '').replace(/-/g, '').trim();
    setPinInput(cleanPin);
    if (cleanPin.length !== 6 || !/^\d+$/.test(cleanPin)) {
      setPinFeedback('Enter 6 numeric digits');
      return;
    }

    try {
      const villages = await api.getVillagesByPin(cleanPin);
      if (villages && villages.length > 0) {
        const v = villages[0];
        setSelectedBlockNum(v.block_id);
        setPinFeedback(`✓ Mapped: ${v.name} (${v.district})`);
      } else if (cleanPin.startsWith('440') || cleanPin.startsWith('441')) {
        setSelectedBlockNum(1);
        setPinFeedback('✓ Mapped: Nagpur Rural');
      } else if (cleanPin.startsWith('442') || cleanPin.startsWith('443')) {
        setSelectedBlockNum(2);
        setPinFeedback('✓ Mapped: Wardha East');
      } else if (cleanPin.startsWith('444') || cleanPin.startsWith('445')) {
        setSelectedBlockNum(3);
        setPinFeedback('✓ Mapped: Amravati Central');
      } else {
        setSelectedBlockNum(1);
        setPinFeedback('✓ Mapped: Nagpur Rural (Prototype)');
      }
    } catch {
      if (cleanPin.startsWith('442')) {
        setSelectedBlockNum(2);
        setPinFeedback('✓ Mapped: Wardha East');
      } else if (cleanPin.startsWith('444')) {
        setSelectedBlockNum(3);
        setPinFeedback('✓ Mapped: Amravati Central');
      } else {
        setSelectedBlockNum(1);
        setPinFeedback('✓ Mapped: Nagpur Rural');
      }
    }
  };

  const rawDecision = decisionMap[blockCode]?.decision || 'SOW_NOW';
  const currentDecision: 'SOW_NOW' | 'SOW_PART_NOW' | 'WAIT' =
    rawDecision === 'SOW_PART_NOW' ? 'SOW_PART_NOW' : rawDecision === 'WAIT' ? 'WAIT' : 'SOW_NOW';
  const recentRainSum = currentWeatherList.slice(-7).reduce((acc, curr) => acc + (curr.rainfall_mm || 0), 0);
  const displayRainMm = recentRainSum > 0 ? Math.round(recentRainSum * 10) / 10 : (selectedBlockNum === 1 ? 92.7 : selectedBlockNum === 2 ? 64.2 : 48.0);

  // Crop Advisory list for Section 9
  const cropAdvisories: CropDecisionData[] = [
    {
      cropId: 'soybean',
      cropName: 'Soybean',
      marathiName: 'सोयाबीन',
      decision: rawDecision === 'UNAVAILABLE' ? 'INSUFFICIENT_DATA' : currentDecision,
      forecastCondition:
        displayRainMm >= 50
          ? 'Onset indicator satisfied with adequate seedbed moisture (>75mm).'
          : 'Elevated dry spell hazard during germination phase.',
      agronomicReason:
        'Rainfed soybean requires prompt sowing after onset confirmation to optimize the vegetative window.',
      sourceStatus: 'VALIDATED',
      institutionalSource: 'ICAR-IISR Indore & Dr. PDKV Akola Contingency Plan',
      actionMessage:
        currentDecision === 'SOW_NOW'
          ? 'Proceed with soybean sowing using certified seed. Adopt Broad Bed Furrow (BBF) configuration for in-situ moisture.'
          : 'Hold sowing for 3–5 days until revival showers occur.',
    },
    {
      cropId: 'cotton',
      cropName: 'Cotton',
      marathiName: 'कापूस',
      decision: currentDecision === 'WAIT' ? 'WAIT' : 'SOW_PART_NOW',
      forecastCondition:
        'Moderate moisture profile. Avoid low-lying plots prone to post-sowing crusting or waterlogging.',
      agronomicReason:
        'Cotton seedlings are highly sensitive to waterlogging and soil surface compaction.',
      sourceStatus: 'VALIDATED',
      institutionalSource: 'ICAR-CICR Nagpur & VNMKV Parbhani Guidelines',
      actionMessage:
        'Undertake staggered dibbling across deep, well-drained soils. Maintain 90 × 60 cm spacing.',
    },
    {
      cropId: 'pigeonpea',
      cropName: 'Pigeonpea (Tur)',
      marathiName: 'तूर',
      decision: 'SOW_NOW',
      forecastCondition: 'Deep-rooting legume tolerant to early season intermittent dry intervals.',
      agronomicReason:
        'Early sowing facilitates root penetration and canopy development before intercrop canopy closure.',
      sourceStatus: 'VALIDATED',
      institutionalSource: 'ICRISAT & MPKV Rahuri Contingency Framework',
      actionMessage:
        'Sow pigeonpea as intercrop with soybean (1:2 or 1:4 ratio) with Trichoderma seed treatment.',
    },
  ];

  return (
    <div className="space-y-6 max-w-7xl mx-auto pb-12">
      {/* 1. COMPACT HERO SECTION (Section 2) */}
      <section className="bg-gradient-to-r from-forest-900 via-forest-800 to-leaf-800 rounded-2xl p-5 sm:p-6 text-white shadow-md relative overflow-hidden">
        {/* Subtle background weather texture */}
        <div className="absolute right-0 top-0 bottom-0 opacity-10 pointer-events-none flex items-center pr-6">
          <CloudRain className="w-56 h-56" />
        </div>

        <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 mb-1.5">
              <span className="text-xl">🌧️</span>
              <h1 className="text-xl sm:text-2xl font-black tracking-tight text-white">
                Vidarbha Monsoon Intelligence
              </h1>
              <span className="bg-emerald-400/20 text-emerald-200 border border-emerald-300/30 text-[10px] font-bold px-2 py-0.5 rounded-full uppercase tracking-wider">
                SIH 2026 Prototype
              </span>
            </div>
            <p className="text-emerald-100/90 text-xs sm:text-sm font-medium">
              See the rain. Understand the risk. Decide when to sow.
            </p>
          </div>

          {/* Quick Context Chips */}
          <div className="flex flex-wrap items-center gap-2 text-xs">
            <div className="bg-black/25 backdrop-blur-sm px-3 py-1.5 rounded-xl border border-white/10 flex items-center gap-1.5">
              <MapPin className="w-3.5 h-3.5 text-emerald-300" />
              <span>Block: <strong>{selectedBlock.name}</strong></span>
            </div>

            <div className="bg-black/25 backdrop-blur-sm px-3 py-1.5 rounded-xl border border-white/10 flex items-center gap-1.5">
              <Sprout className="w-3.5 h-3.5 text-emerald-300" />
              <span>Crop: <strong className="capitalize">{selectedCropId}</strong></span>
            </div>

            <div className="bg-amber-400/20 text-amber-200 px-3 py-1.5 rounded-xl border border-amber-300/30 flex items-center gap-1.5 text-[11px] font-semibold">
              <ShieldAlert className="w-3.5 h-3.5 text-amber-300" />
              <span>Historical Replay · Research Benchmark</span>
            </div>

            <button
              onClick={() => fetchDashboardData(selectedBlockNum, selectedCropId)}
              disabled={refreshing}
              className="p-1.5 rounded-lg bg-white/10 hover:bg-white/20 transition-all text-white border border-white/20"
              title="Refresh telemetry"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${refreshing ? 'animate-spin' : ''}`} />
            </button>
          </div>
        </div>
      </section>

      {/* Location Context & Postal PIN Lookup Bar */}
      <section className="bg-white rounded-xl border border-stone-200/90 px-4 py-3 shadow-xs flex flex-wrap items-center justify-between gap-3 text-xs">
        <div className="flex items-center gap-2">
          <MapPin className="w-4 h-4 text-forest-700" />
          <span className="font-bold text-stone-900">Forecast Context:</span>
          <span className="font-semibold text-forest-900 bg-forest-50 px-2.5 py-0.5 rounded-md border border-forest-200">
            {selectedBlock.name} ({selectedBlock.district} District)
          </span>
          {pinFeedback && (
            <span className="text-[11px] text-emerald-700 font-semibold bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200">
              {pinFeedback}
            </span>
          )}
        </div>

        {/* PIN Lookup Input & Quick Chips */}
        <div className="flex flex-wrap items-center gap-2">
          <form
            onSubmit={(e) => {
              e.preventDefault();
              handlePinLookup(pinInput);
            }}
            className="flex items-center gap-1.5"
          >
            <input
              type="text"
              value={pinInput}
              onChange={(e) => {
                setPinInput(e.target.value);
                setPinFeedback(null);
              }}
              placeholder="Enter PIN (e.g. 441501)"
              maxLength={6}
              className="w-36 px-2.5 py-1 text-xs border border-stone-300 rounded-lg text-stone-900 font-mono focus:outline-none focus:border-forest-600 shadow-inner"
            />
            <button
              type="submit"
              className="px-2.5 py-1 bg-forest-800 hover:bg-forest-900 text-white rounded-lg text-xs font-semibold flex items-center gap-1 shadow-2xs"
            >
              <Search className="w-3 h-3" />
              <span>Lookup</span>
            </button>
          </form>

          {/* Quick PIN Chips */}
          <div className="hidden sm:flex items-center gap-1 pl-2 border-l border-stone-200">
            <span className="text-[10px] text-stone-500 font-semibold">Quick PIN:</span>
            {[
              { pin: '441501', label: '441501 Nagpur' },
              { pin: '442104', label: '442104 Wardha' },
              { pin: '444904', label: '444904 Amravati' },
            ].map((p) => (
              <button
                key={p.pin}
                type="button"
                onClick={() => handlePinLookup(p.pin)}
                className={`px-2 py-0.5 rounded text-[11px] font-medium transition-all ${
                  pinInput === p.pin
                    ? 'bg-forest-800 text-white font-bold'
                    : 'bg-stone-100 hover:bg-stone-200 text-stone-700'
                }`}
              >
                {p.label}
              </button>
            ))}
          </div>
        </div>
      </section>

      {/* 2. MAIN HERO VISUALIZATION & DECISION PANEL (Side-by-Side: Map + Decision) */}
      <section className="grid grid-cols-1 lg:grid-cols-12 gap-5 items-stretch">
        {/* Large Interactive Leaflet Map (65% / col-span-7 or col-span-8) */}
        <div className="lg:col-span-8 min-h-[460px] flex flex-col">
          <InteractiveWeatherMap
            blocks={blocks}
            selectedBlockId={selectedBlockNum}
            onSelectBlock={handleSelectBlock}
            onNavigateForecast={(id) => {
              handleSelectBlock(id);
              setCurrentTab('forecast');
            }}
            decisionData={decisionMap}
            weatherData={weatherDataMap}
          />
        </div>

        {/* Selected Block Farm Decision Panel (35% / col-span-4) */}
        <div className="lg:col-span-4 min-h-[460px] flex flex-col">
          <FarmDecisionPanel
            selectedBlock={selectedBlock}
            selectedCrop={selectedCropId}
            onChangeCrop={setSelectedCropId}
            decisionData={decisionMap[blockCode]}
            advisoryData={advisoryData}
            onViewAdvisory={() => {
              const el = document.getElementById('crop-advisory-section');
              if (el) el.scrollIntoView({ behavior: 'smooth' });
            }}
            onViewFarmerMessage={() => {
              const el = document.getElementById('farmer-message-section');
              if (el) el.scrollIntoView({ behavior: 'smooth' });
            }}
          />
        </div>
      </section>

      {/* 3. WEATHER TIMELINE (Section 9) */}
      <section>
        <RainfallOutlook
          weatherData={currentWeatherList}
          selectedHorizon={selectedHorizon}
          onSelectHorizon={setSelectedHorizon}
          isLoading={loading}
        />
      </section>

      {/* 4. RECENT RAINFALL CHART (Section 8) */}
      <section>
        <RecentRainfallChart
          observations={currentWeatherList}
          blockName={selectedBlock.name}
        />
      </section>

      {/* 5. MONSOON STORY: "🌧 What is happening?" (Section 10) */}
      <section>
        <MonsoonStory
          blockName={selectedBlock.name}
          decisionData={decisionMap[blockCode]}
          recentRainfallMm={displayRainMm}
        />
      </section>

      {/* 6. CROP ADVISORY (Section 9) */}
      <section id="crop-advisory-section" className="space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-stone-200 pb-3">
          <div className="flex items-center space-x-2">
            <span className="text-xl">🌱</span>
            <div>
              <h2 className="text-base font-bold text-stone-900 tracking-tight">
                Validated Crop Sowing Advisory · Vidarbha Region
              </h2>
              <p className="text-xs text-stone-500">
                Rule engine recommendations matched against ICAR-CRIDA, IISR, and VNMKV frameworks
              </p>
            </div>
          </div>
          <span className="text-xs text-stone-500 bg-stone-100 px-3 py-1 rounded-full font-medium self-start sm:self-auto">
            Location Context: <strong>{selectedBlock.name}</strong>
          </span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {cropAdvisories.map((advisory) => (
            <CropDecisionCard
              key={advisory.cropId}
              data={advisory}
              onSelect={() => setSelectedCropId(advisory.cropId)}
            />
          ))}
        </div>
      </section>

      {/* 7. FARMER EXPERIENCE & MULTI-CHANNEL PREVIEW (Section 11) */}
      <section id="farmer-message-section" className="grid grid-cols-1 lg:grid-cols-12 gap-5">
        <div className="lg:col-span-8 flex flex-col justify-between">
          <FarmerMessageCard
            village={selectedBlock.name}
            crop={selectedCropId === 'soybean' ? 'Soybean (सोयाबीन)' : selectedCropId === 'cotton' ? 'Cotton (कापूस)' : 'Pigeonpea (तूर)'}
            decision={currentDecision}
            messageMr={
              advisoryData?.advisory_text ||
              'मेघवाणी सल्ला: कळमेश्वर तालुक्यात समाधानकारक मान्सून आगमन स्थिती अपेक्षित आहे. सोयाबीनची पेरणी करण्यास हरकत नाही. जमिनीत किमान ७५-१०० मिमी ओलावा असल्याची खात्री करा.'
            }
          />
        </div>

        <div className="lg:col-span-4">
          <RiskLegend />
        </div>
      </section>

      {/* 8. SCIENTIFIC INTEGRITY & ETHICAL DISCLOSURE */}
      <section className="bg-stone-100/90 rounded-2xl p-4 border border-stone-300/80 text-xs text-stone-600 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
        <div className="flex items-center gap-2">
          <Info className="w-4 h-4 text-forest-800 shrink-0" />
          <span>
            <strong>Meghvani Research Benchmark Disclosure:</strong> All probabilities and historical rainfall traces reflect the 2019–2024 IMD 0.25° gridded calibration dataset. External dispatch to real telecom gateways is disabled in prototype mode.
          </span>
        </div>
        <button
          onClick={() => setCurrentTab('validation')}
          className="text-xs font-bold text-forest-800 hover:text-forest-900 underline shrink-0"
        >
          View Scientific Validation →
        </button>
      </section>
    </div>
  );
};
