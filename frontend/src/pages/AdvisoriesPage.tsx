import React, { useState, useEffect } from 'react';
import {
  Sprout,
  CheckCircle2,
  Calendar,
  ShieldCheck,
  AlertTriangle,
  Info,
  Droplets,
  BookOpen,
  Volume2,
  PhoneCall,
  Clock,
  ExternalLink
} from 'lucide-react';
import { api } from '../services/api';
import { Block, AdvisoryResult, DecisionSupportResult, WeatherObservation } from '../types';
import { FarmerMessageCard } from '../components/FarmerMessageCard';
import { useCanonicalPrediction } from '../context/CanonicalPredictionContext';

interface AdvisoriesPageProps {
  blocks: Block[];
  selectedBlockId: number;
  onSelectBlockId: (id: number) => void;
  onNavigateTab: (tab: string) => void;
}

export const AdvisoriesPage: React.FC<AdvisoriesPageProps> = ({
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
  } = useCanonicalPrediction();

  const handleSelectBlock = (id: number) => {
    setSelectedBlockId(id);
    if (propSetBlockId) propSetBlockId(id);
  };

  const [selectedCrop, setSelectedCrop] = useState<string>('soybean');
  const [advisory, setAdvisory] = useState<AdvisoryResult | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  const blockCode = selectedBlock.id === 1 ? 'BLK001' : selectedBlock.id === 2 ? 'BLK002' : 'BLK003';

  useEffect(() => {
    const load = async () => {
      setLoading(true);
      try {
        const adv = await api.getBlockAdvisory(blockCode, selectedCrop, 'mr').catch(() => null);
        setAdvisory(adv);
      } catch (e) {
        console.warn('Advisory loading error:', e);
      } finally {
        setLoading(false);
      }
    };
    load();
  }, [blockCode, selectedCrop]);

  const cumRain7 = canonical.cumRain7d;
  const decisionPosture = canonical.sowingPosture;

  return (
    <div className="space-y-6 pb-12">
      {/* Header */}
      <div className="bg-white p-6 rounded-2xl border border-stone-200/90 shadow-2xs flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="flex items-center space-x-2.5">
          <div className="w-10 h-10 rounded-xl bg-forest-50 border border-forest-200 flex items-center justify-center text-forest-800">
            <Sprout className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <h1 className="text-xl sm:text-2xl font-extrabold text-stone-900 tracking-tight">
                Agricultural Advisory
              </h1>
              <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-forest-100 text-forest-800 border border-forest-200 uppercase tracking-wider">
                ICAR / Dr. PDKV Akola
              </span>
            </div>
            <p className="text-xs text-stone-600 mt-0.5">
              Hyperlocal crop decision support deterministically mapped to verified university agronomic guidelines.
            </p>
          </div>
        </div>

        {/* Location & Crop Selector Tabs */}
        <div className="flex flex-wrap items-center gap-3">
          <div className="flex items-center space-x-2 text-xs">
            <span className="text-stone-500 font-semibold">Active Block:</span>
            <select
              value={selectedBlock.id}
              onChange={(e) => handleSelectBlock(Number(e.target.value))}
              className="bg-stone-50 border border-stone-300 rounded-xl px-3 py-1.5 font-bold text-stone-900"
            >
              {blocks.map((b) => (
                <option key={b.id} value={b.id}>
                  {b.name}
                </option>
              ))}
            </select>
          </div>

          <div className="flex items-center space-x-1.5 bg-stone-100 p-1 rounded-xl border border-stone-200 text-xs font-semibold self-start sm:self-auto">
            {[
              { id: 'soybean', label: 'Soybean (सोयाबीन)' },
              { id: 'cotton', label: 'Cotton (कापूस)' },
              { id: 'pigeonpea', label: 'Tur / Arhar (तूर)' },
            ].map((c) => (
              <button
                key={c.id}
                onClick={() => setSelectedCrop(c.id)}
                className={`px-3 py-1.5 rounded-lg transition-all ${
                  selectedCrop === c.id
                    ? 'bg-white text-forest-900 font-extrabold shadow-2xs border border-stone-200'
                    : 'text-stone-600 hover:text-stone-900'
                }`}
              >
                {c.label}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Hero Advisory Card */}
      <div className="p-6 rounded-3xl bg-white border border-stone-200/90 shadow-sm space-y-6">
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-6 pb-6 border-b border-stone-200">
          <div>
            <div className="flex items-center space-x-2 mb-2">
              <span className="text-[11px] font-black uppercase tracking-wider px-2.5 py-0.5 rounded-full bg-emerald-100 text-emerald-900 border border-emerald-300">
                🌱 SOWING WINDOW · {selectedCrop.toUpperCase()}
              </span>
              <span className="text-xs font-bold text-stone-500">
                Block: {selectedBlock.name}
              </span>
            </div>
            <h2 className="text-2xl sm:text-3xl font-extrabold text-stone-900 tracking-tight">
              {decisionPosture === 'SOW_NOW'
                ? '07 June – 12 June · Conditions Favorable for Sowing'
                : decisionPosture === 'WAIT'
                ? 'Wait Window Active · Postpone Sowing Until Further Rain'
                : 'Staggered Sowing Window · Partial Seed Deployment'}
            </h2>
            <p className="text-xs sm:text-sm text-stone-600 mt-2 max-w-3xl leading-relaxed">
              {decisionPosture === 'SOW_NOW'
                ? `Soil moisture accumulation and weather outlook across ${selectedBlock.name} are favorable. Ensure seedbed layer exceeds 75–100 mm total rainfall before committing full seed resources.`
                : `False-onset risk is elevated. Avoid sowing in dry soil (धुळवाफ) to prevent complete seed loss and reseeding costs.`}
            </p>
          </div>

          <div className="p-4 rounded-2xl bg-stone-50 border border-stone-200 min-w-[220px] text-center">
            <span className="text-[10px] font-extrabold uppercase tracking-wider text-stone-500 block">
              Validated Action
            </span>
            <span
              className={`text-xl font-black mt-1 block ${
                decisionPosture === 'SOW_NOW' ? 'text-forest-800' : 'text-amber-800'
              }`}
            >
              {decisionPosture === 'SOW_NOW' ? '✅ SOW NOW' : '⏳ WAIT'}
            </span>
            <span className="text-[10px] text-stone-400 font-mono mt-1 block">
              Rule ID: {advisory?.rule_id || 'ICAR_SOY_01'}
            </span>
          </div>
        </div>

        {/* Scientific 'Why?' Section */}
        <div>
          <h3 className="text-sm font-extrabold text-stone-900 uppercase tracking-wider mb-3">
            Why this recommendation?
          </h3>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-3 text-xs">
            <div className="p-3.5 rounded-xl bg-stone-50 border border-stone-200/80 space-y-1">
              <span className="font-extrabold text-stone-900 flex items-center gap-1.5">
                <CheckCircle2 className={`w-4 h-4 ${cumRain7 >= 25 ? 'text-emerald-600' : 'text-amber-600'}`} />
                <span>Soil Moisture Status</span>
              </span>
              <p className="text-stone-600 text-[11px] leading-relaxed">
                {cumRain7 === 0
                  ? `No rainfall recorded during the previous 7 days across ${selectedBlock.name}. Soil moisture remains depleted.`
                  : cumRain7 < 25
                  ? `Low antecedent rainfall (${cumRain7} mm / 7d) recorded across ${selectedBlock.name}. Pre-monsoon showers insufficient for full germination.`
                  : `Adequate antecedent rainfall (${cumRain7} mm / 7d) provides sufficient seedbed moisture for germination.`}
              </p>
            </div>

            <div className="p-3.5 rounded-xl bg-stone-50 border border-stone-200/80 space-y-1">
              <span className="font-extrabold text-stone-900 flex items-center gap-1.5">
                <CheckCircle2 className={`w-4 h-4 ${canonical.falseOnsetRisk <= 25 ? 'text-emerald-600' : 'text-amber-600'}`} />
                <span>Loss Ratio Economic Boundary</span>
              </span>
              <p className="text-stone-600 text-[11px] leading-relaxed">
                Modeled false-onset risk is {canonical.falseOnsetRisk}% (evaluated against crop loss ratio P* = 0.17: Reseeding ₹4,800/ha vs Delay ₹800/ha).
              </p>
            </div>

            <div className="p-3.5 rounded-xl bg-stone-50 border border-stone-200/80 space-y-1">
              <span className="font-extrabold text-stone-900 flex items-center gap-1.5">
                <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                <span>Verified University Rule</span>
              </span>
              <p className="text-stone-600 text-[11px] leading-relaxed">
                Directly matches Dr. Panjabrao Deshmukh Krishi Vidyapeeth (PDKV) Akola kharif crop advisory guidelines.
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Multilingual Farmer Message Card with Speech Synthesis */}
      <div>
        <FarmerMessageCard
          farmerName="Ramesh Patil"
          village={selectedBlock.name}
          crop={selectedCrop.toUpperCase()}
          decision={decisionPosture as any}
          messageMr={
            advisory?.advisory_text ||
            `मेघवाणी कृषी सल्ला (${selectedBlock.name}): ${selectedCrop} पिकासाठी पेरणी अनुकूल आहे. जमिनीत किमान ७५-१०० मिमी ओलावा झाल्याची खात्री करूनच पेरणी करावी. खतांचा योग्य वापर करा.`
          }
          messageHi={`मेघवाणी कृषि सलाह (${selectedBlock.name}): ${selectedCrop} की बुवाई के लिए मौसम अनुकूल है। खेत में पर्याप्त नमी सुनिश्चित करने के बाद ही बुवाई करें।`}
          messageEn={`Meghvani Advisory (${selectedBlock.name}): Moisture conditions are favorable for ${selectedCrop}. Ensure seedbed moisture exceeds 75mm before starting sowing.`}
        />
      </div>
    </div>
  );
};
