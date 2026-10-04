import React, { useState, useRef, useEffect, useMemo } from 'react';
import {
  MapPin,
  ChevronDown,
  ChevronRight,
  ShieldCheck,
  Check,
  X,
  Compass,
  Layers,
  Sparkles,
  Info
} from 'lucide-react';
import { useCanonicalPrediction } from '../context/CanonicalPredictionContext';
import { Block, Village } from '../types';

interface LocationHierarchySelectorProps {
  className?: string;
  variant?: 'compact' | 'expanded';
}

export const LocationHierarchySelector: React.FC<LocationHierarchySelectorProps> = ({
  className = '',
  variant = 'compact'
}) => {
  const {
    selectedState,
    districts,
    selectedDistrict,
    selectedBlockId,
    selectedBlock,
    blocks,
    villages,
    selectedVillageId,
    selectedVillage,
    setSelectedBlockId,
    setSelectedVillageId,
    selectLocationHierarchy,
  } = useCanonicalPrediction();

  const [isOpen, setIsOpen] = useState(false);
  const [activeDistrictTab, setActiveDistrictTab] = useState<string>(selectedDistrict);
  const containerRef = useRef<HTMLDivElement>(null);

  // Sync active district tab with selected block when opened
  useEffect(() => {
    setActiveDistrictTab(selectedBlock.district);
  }, [selectedBlock.district, isOpen]);

  // Click outside listener
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };
    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside);
    }
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [isOpen]);

  // Blocks filtered by active district tab
  const districtBlocks = useMemo(() => {
    return blocks.filter((b) => b.district === activeDistrictTab);
  }, [blocks, activeDistrictTab]);

  // Villages filtered by currently selected block
  const blockVillages = useMemo(() => {
    return villages.filter((v) => v.block_id === selectedBlock.id);
  }, [villages, selectedBlock.id]);

  const cleanBlockName = (name: string) => {
    return name.replace(/\s*\([^)]*\)/, '');
  };

  return (
    <div className={`relative inline-block ${className}`} ref={containerRef}>
      {/* Trigger Button */}
      <button
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center space-x-1.5 bg-stone-50 hover:bg-stone-100/90 border border-stone-200/90 hover:border-forest-600/40 rounded-xl px-3 py-1.5 text-xs shadow-2xs transition-all cursor-pointer group"
        title="Open Hierarchical Location Selector (State → District → Block → Village)"
      >
        <MapPin className="w-3.5 h-3.5 text-forest-700 shrink-0 group-hover:scale-110 transition-transform" />
        
        <div className="flex items-center space-x-1 font-semibold text-stone-700 text-left">
          <span className="hidden sm:inline text-stone-500">{selectedState}</span>
          <span className="hidden sm:inline text-stone-400">›</span>
          <span className="hidden md:inline text-stone-600">{selectedBlock.district}</span>
          <span className="hidden md:inline text-stone-400">›</span>
          <span className="font-extrabold text-stone-900">{cleanBlockName(selectedBlock.name)}</span>
          {selectedVillage && (
            <>
              <span className="text-stone-400">›</span>
              <span className="text-forest-800 font-bold hidden lg:inline">{selectedVillage.name}</span>
            </>
          )}
        </div>

        <ChevronDown className={`w-3.5 h-3.5 text-stone-400 transition-transform duration-200 ${isOpen ? 'rotate-180' : ''}`} />
      </button>

      {/* Hierarchical Dropdown Card */}
      {isOpen && (
        <div className="absolute right-0 top-full mt-2 w-[340px] sm:w-[480px] bg-white rounded-2xl border border-stone-200/95 shadow-xl z-50 overflow-hidden animate-in fade-in zoom-in-95 duration-150">
          {/* Header */}
          <div className="p-3.5 bg-gradient-to-r from-stone-50 via-white to-stone-50 border-b border-stone-100 flex items-center justify-between">
            <div>
              <div className="flex items-center space-x-2">
                <span className="text-[10px] font-extrabold uppercase tracking-wider text-forest-800 bg-forest-50 border border-forest-200/80 px-2 py-0.5 rounded-full">
                  Location Hierarchy
                </span>
                <span className="text-[10px] font-bold text-amber-800 bg-amber-50 border border-amber-200 px-2 py-0.5 rounded-full">
                  Prototype Coverage: 3 Regions
                </span>
              </div>
              <h3 className="text-sm font-extrabold text-stone-900 mt-1">
                State › District › Block / Taluka › Village
              </h3>
            </div>
            <button
              onClick={() => setIsOpen(false)}
              className="p-1 rounded-lg text-stone-400 hover:text-stone-600 hover:bg-stone-100"
            >
              <X className="w-4 h-4" />
            </button>
          </div>

          <div className="p-4 space-y-4 max-h-[75vh] overflow-y-auto text-xs">
            {/* Tier 1: State */}
            <div>
              <div className="flex items-center justify-between text-[11px] font-bold text-stone-500 uppercase tracking-wider mb-1.5">
                <span>1. State</span>
                <span className="text-[10px] font-semibold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200">
                  Active Province
                </span>
              </div>
              <div className="p-2.5 rounded-xl bg-stone-50 border border-stone-200 font-extrabold text-stone-900 flex items-center justify-between">
                <span>{selectedState}</span>
                <span className="text-[10px] text-stone-500 font-normal">Western Peninsular Region</span>
              </div>
            </div>

            {/* Tier 2: District */}
            <div>
              <div className="flex items-center justify-between text-[11px] font-bold text-stone-500 uppercase tracking-wider mb-1.5">
                <span>2. Select District</span>
                <span className="text-[10px] font-normal text-stone-400">{districts.length} available</span>
              </div>
              <div className="grid grid-cols-3 gap-2">
                {districts.map((dist) => {
                  const isSelected = activeDistrictTab === dist;
                  const isCurrentlyActiveBlockDistrict = selectedBlock.district === dist;
                  return (
                    <button
                      key={dist}
                      type="button"
                      onClick={() => setActiveDistrictTab(dist)}
                      className={`p-2 rounded-xl text-left font-bold transition-all border cursor-pointer ${
                        isSelected
                          ? 'bg-forest-800 text-white border-forest-900 shadow-xs'
                          : 'bg-stone-50 text-stone-700 border-stone-200 hover:bg-stone-100'
                      }`}
                    >
                      <div className="text-[11px] flex items-center justify-between">
                        <span>{dist}</span>
                        {isCurrentlyActiveBlockDistrict && (
                          <span className={`w-1.5 h-1.5 rounded-full ${isSelected ? 'bg-amber-300' : 'bg-forest-600'}`} />
                        )}
                      </div>
                    </button>
                  );
                })}
              </div>
            </div>

            {/* Tier 3: Block / Taluka */}
            <div>
              <div className="flex items-center justify-between text-[11px] font-bold text-stone-500 uppercase tracking-wider mb-1.5">
                <span>3. Operational Forecast Block ({activeDistrictTab})</span>
                <span className="text-[10px] text-forest-700 font-semibold">Primary Prediction Unit</span>
              </div>
              <div className="space-y-1.5">
                {districtBlocks.map((b) => {
                  const isSelected = selectedBlock.id === b.id;
                  const code = b.id === 1 ? 'BLK001' : b.id === 2 ? 'BLK002' : 'BLK003';
                  return (
                    <button
                      key={b.id}
                      type="button"
                      onClick={() => {
                        selectLocationHierarchy(b.district, b.id, null);
                        setIsOpen(false);
                      }}
                      className={`w-full p-2.5 rounded-xl border text-left transition-all flex items-center justify-between cursor-pointer ${
                        isSelected
                          ? 'bg-forest-50 border-forest-300 ring-2 ring-forest-600/20'
                          : 'bg-white border-stone-200 hover:bg-stone-50'
                      }`}
                    >
                      <div>
                        <div className="flex items-center space-x-2">
                          <span className={`font-black text-xs ${isSelected ? 'text-forest-950' : 'text-stone-900'}`}>
                            {b.name}
                          </span>
                          <span className="text-[10px] font-mono px-1.5 py-0.2 rounded bg-stone-100 text-stone-600 border border-stone-200">
                            {code}
                          </span>
                        </div>
                        <span className="text-[10px] text-stone-500 block mt-0.5">
                          Centroid: {b.latitude.toFixed(2)}°N, {b.longitude.toFixed(2)}°E · IMD 0.25° Grid
                        </span>
                      </div>

                      <div className="flex items-center space-x-2">
                        {isSelected ? (
                          <span className="inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-extrabold bg-forest-800 text-white shadow-2xs">
                            <Check className="w-3 h-3 mr-0.5" />
                            Active
                          </span>
                        ) : (
                          <span className="text-[10px] text-stone-400 font-bold hover:text-stone-600">
                            Select →
                          </span>
                        )}
                      </div>
                    </button>
                  );
                })}
              </div>
            </div>

            {/* Tier 4: Village Local Context */}
            {blockVillages.length > 0 && (
              <div>
                <div className="flex items-center justify-between text-[11px] font-bold text-stone-500 uppercase tracking-wider mb-1.5">
                  <span>4. Village Local Context (Optional)</span>
                  <span className="text-[10px] text-stone-400">{blockVillages.length} registered in {cleanBlockName(selectedBlock.name)}</span>
                </div>
                <div className="flex flex-wrap gap-1.5">
                  <button
                    type="button"
                    onClick={() => {
                      setSelectedVillageId(null);
                      setIsOpen(false);
                    }}
                    className={`px-2.5 py-1 rounded-lg text-[11px] font-bold border transition-all ${
                      selectedVillageId === null
                        ? 'bg-forest-800 text-white border-forest-900 shadow-2xs'
                        : 'bg-stone-50 text-stone-700 border-stone-200 hover:bg-stone-100'
                    }`}
                  >
                    Entire Block / All Villages
                  </button>
                  {blockVillages.map((v) => {
                    const isSelected = selectedVillageId === v.id;
                    return (
                      <button
                        key={v.id}
                        type="button"
                        onClick={() => {
                          setSelectedVillageId(v.id);
                          setIsOpen(false);
                        }}
                        className={`px-2.5 py-1 rounded-lg text-[11px] font-bold border transition-all ${
                          isSelected
                            ? 'bg-forest-800 text-white border-forest-900 shadow-2xs'
                            : 'bg-stone-50 text-stone-700 border-stone-200 hover:bg-stone-100'
                        }`}
                      >
                        {v.name} <span className="text-[9px] opacity-75 font-mono">({v.pin_code})</span>
                      </button>
                    );
                  })}
                </div>
              </div>
            )}
          </div>

          {/* Footer with Scientific Transparency Note */}
          <div className="p-3 bg-stone-50 border-t border-stone-100 text-[11px] text-stone-500 space-y-1">
            <div className="flex items-center space-x-1.5 text-stone-700 font-bold">
              <ShieldCheck className="w-3.5 h-3.5 text-forest-700 shrink-0" />
              <span>Hierarchical Scalability Guarantee:</span>
            </div>
            <p className="text-[10px] leading-relaxed text-stone-500">
              Adding new administrative units to the backend database immediately surfaces them in this selector. Model predictions remain validated for Vidarbha prototype nodes.
            </p>
          </div>
        </div>
      )}
    </div>
  );
};
