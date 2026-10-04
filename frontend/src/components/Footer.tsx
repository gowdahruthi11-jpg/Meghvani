import React from 'react';
import { AlertCircle, ShieldCheck } from 'lucide-react';

export const Footer: React.FC = () => {
  return (
    <footer className="border-t border-stone-200/90 bg-stone-100/60 py-8 px-4 sm:px-6 lg:px-8 text-xs text-stone-500 mt-auto">
      <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-4">
        <div>
          <div className="flex items-center space-x-2">
            <span className="text-base" role="img" aria-label="wheat">🌾</span>
            <span className="font-bold text-stone-800 text-sm">MEGHVANI</span>
            <span className="text-stone-400">•</span>
            <span className="font-medium text-stone-600">Hyperlocal Monsoon Intelligence</span>
          </div>
          <p className="text-stone-500 mt-1 max-w-xl text-[11px] leading-relaxed">
            Helping farmers make better sowing decisions with localized rainfall outlooks.
            Prototype decision support engineered for Smart India Hackathon 2026.
          </p>
        </div>

        <div className="flex flex-col sm:flex-row items-start sm:items-center gap-2">
          <div className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-white border border-stone-200 text-stone-700 text-[11px] shadow-2xs">
            <ShieldCheck className="w-3.5 h-3.5 text-forest-700 shrink-0" />
            <span>Vidarbha Prototype: Nagpur Rural, Wardha East, Amravati Central</span>
          </div>

          <div className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-amber-50 border border-amber-200 text-amber-800 text-[11px]">
            <AlertCircle className="w-3.5 h-3.5 shrink-0" />
            <span>Research Benchmark • Not Operational</span>
          </div>
        </div>
      </div>
    </footer>
  );
};
