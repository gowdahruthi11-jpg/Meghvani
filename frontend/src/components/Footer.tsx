import React from 'react';
import { AlertTriangle, ShieldCheck, Heart } from 'lucide-react';

export const Footer: React.FC = () => {
  return (
    <footer className="border-t border-slate-800 bg-slate-950/70 py-8 px-4 sm:px-6 lg:px-8 text-xs text-slate-400 mt-auto">
      <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-4">
        <div>
          <p className="font-semibold text-slate-300">
            Meghvani — Smart India Hackathon 2026 Agriculture Prototype
          </p>
          <p className="text-slate-500 mt-1">
            Block-scale monsoon onset, false-onset, break spell, and crop advisory engine.
          </p>
        </div>

        <div className="flex items-center space-x-2 px-3 py-1.5 rounded-lg bg-amber-500/10 border border-amber-500/20 text-amber-300 text-[11px]">
          <AlertTriangle className="w-3.5 h-3.5 shrink-0" />
          <span>
            <strong>Phase 1 Transparency:</strong> Weather telemetry and telecommunications are simulated for architectural validation.
          </span>
        </div>
      </div>
    </footer>
  );
};
