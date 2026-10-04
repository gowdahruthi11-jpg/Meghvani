import React, { useState } from 'react';
import {
  Menu,
  Bell,
  MapPin,
  Calendar,
  CloudRain,
  ShieldCheck,
  ChevronDown
} from 'lucide-react';
import { PredictionJourney } from './PredictionJourney';
import { Block } from '../types';

interface TopHeaderProps {
  currentTab: string;
  onSelectTab: (tab: string) => void;
  blocks: Block[];
  selectedBlockId: number;
  onSelectBlockId: (id: number) => void;
  onOpenMobileMenu: () => void;
  alertCount?: number;
}

export const TopHeader: React.FC<TopHeaderProps> = ({
  currentTab,
  onSelectTab,
  blocks,
  selectedBlockId,
  onSelectBlockId,
  onOpenMobileMenu,
  alertCount = 4,
}) => {
  const [district, setDistrict] = useState<string>('Nagpur');

  const selectedBlock = blocks.find((b) => b.id === selectedBlockId) || blocks[0] || {
    id: 1,
    name: 'Nagpur Rural (Nagpur)',
    district: 'Nagpur',
  };

  const now = new Date();
  const dateStr = now.toLocaleDateString('en-IN', {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
  });

  return (
    <header className="sticky top-0 z-30 bg-white/95 backdrop-blur-md border-b border-stone-200/90 shadow-2xs h-16 px-4 sm:px-6 flex items-center justify-between gap-4">
      {/* Left: Mobile Menu Toggle & Title */}
      <div className="flex items-center space-x-3">
        <button
          onClick={onOpenMobileMenu}
          className="p-2 rounded-xl text-stone-600 hover:text-stone-900 hover:bg-stone-100 lg:hidden"
          aria-label="Open navigation menu"
        >
          <Menu className="w-5 h-5" />
        </button>

        <div className="hidden sm:block">
          <div className="flex items-center space-x-2">
            <span className="font-extrabold text-sm sm:text-base text-stone-900 tracking-tight">
              MEGHVANI
            </span>
            <span className="text-[10px] font-bold text-forest-800 bg-forest-50 border border-forest-200 px-2 py-0.5 rounded-full uppercase tracking-wider">
              Hyperlocal Intelligence
            </span>
          </div>
        </div>
      </div>

      {/* Center: Prediction Journey Component */}
      <PredictionJourney currentTab={currentTab} onSelectTab={onSelectTab} />

      {/* Right: Location Selector, Alerts & Date */}
      <div className="flex items-center space-x-2 sm:space-x-3">
        {/* Compact Location Selector */}
        <div className="flex items-center bg-stone-50 border border-stone-200 rounded-xl px-2.5 py-1.5 text-xs shadow-2xs">
          <MapPin className="w-3.5 h-3.5 text-forest-700 mr-1.5 shrink-0" />
          <span className="text-stone-500 font-semibold hidden md:inline mr-1">
            Maharashtra &gt;
          </span>
          <select
            value={selectedBlockId}
            onChange={(e) => onSelectBlockId(Number(e.target.value))}
            className="bg-transparent font-bold text-stone-900 focus:outline-none cursor-pointer text-xs"
          >
            {blocks.map((b) => (
              <option key={b.id} value={b.id}>
                {b.name}
              </option>
            ))}
          </select>
        </div>

        {/* Date Display */}
        <div className="hidden lg:flex items-center text-[11px] font-semibold text-stone-500 bg-stone-50 px-2.5 py-1.5 rounded-xl border border-stone-200">
          <Calendar className="w-3.5 h-3.5 text-stone-400 mr-1.5" />
          <span>{dateStr}</span>
        </div>

        {/* Notification Bell */}
        <button
          onClick={() => onSelectTab('alerts')}
          className="relative p-2 rounded-xl text-stone-600 hover:text-stone-900 hover:bg-stone-100 transition-colors border border-stone-200/80 shadow-2xs"
          title="View Alert Center"
        >
          <Bell className="w-4 h-4 text-stone-700" />
          {alertCount > 0 && (
            <span className="absolute -top-1 -right-1 w-4 h-4 rounded-full bg-amber-500 text-white text-[9px] font-black flex items-center justify-center shadow-xs">
              {alertCount}
            </span>
          )}
        </button>
      </div>
    </header>
  );
};
