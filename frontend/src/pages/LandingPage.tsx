import React from 'react';
import {
  CloudLightning,
  Smartphone,
  ShieldCheck,
  Radio,
  ArrowRight,
  Database,
  Cpu,
  Layers,
  Sparkles,
  CheckCircle2,
  AlertCircle
} from 'lucide-react';

interface LandingPageProps {
  setCurrentTab: (tab: string) => void;
}

export const LandingPage: React.FC<LandingPageProps> = ({ setCurrentTab }) => {
  return (
    <div className="space-y-12 pb-12">
      {/* Hero Section */}
      <section className="relative overflow-hidden rounded-3xl p-8 sm:p-12 glass-panel-elevated border border-slate-800 bg-gradient-to-b from-slate-900 via-slate-900/90 to-slate-950">
        <div className="absolute top-0 right-0 -mt-16 -mr-16 w-96 h-96 bg-sky-500/10 rounded-full blur-3xl pointer-events-none" />
        <div className="absolute bottom-0 left-0 -mb-16 -ml-16 w-96 h-96 bg-teal-500/10 rounded-full blur-3xl pointer-events-none" />

        <div className="relative z-10 max-w-3xl space-y-6">
          <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-sky-500/10 border border-sky-500/20 text-sky-400 text-xs font-semibold uppercase tracking-wider">
            <Sparkles className="w-3.5 h-3.5" />
            <span>Smart India Hackathon 2026 Prototype</span>
          </div>

          <h1 className="text-3xl sm:text-5xl font-extrabold tracking-tight text-white leading-tight">
            Hyperlocal Monsoon Intelligence at{' '}
            <span className="bg-gradient-to-r from-sky-400 via-teal-300 to-emerald-400 bg-clip-text text-transparent">
              Block & Village Scale
            </span>
          </h1>

          <p className="text-slate-300 text-base sm:text-lg leading-relaxed">
            Predict hyperlocal monsoon onset, false-onset dry spells, break intervals, and heavy-rain hazards.
            Convert meteorological probabilities into agronomic sowing advice delivered to smallholders via
            conversational SMS, voice calls, and WhatsApp in regional languages.
          </p>

          <div className="flex flex-wrap gap-4 pt-2">
            <button
              onClick={() => setCurrentTab('register')}
              className="inline-flex items-center space-x-2 px-6 py-3 rounded-xl bg-gradient-to-r from-sky-500 to-teal-500 text-white font-semibold text-sm shadow-lg shadow-sky-500/25 hover:from-sky-400 hover:to-teal-400 transition-all hover:scale-[1.02] active:scale-[0.98]"
            >
              <Smartphone className="w-4 h-4" />
              <span>Simulate Farmer Registration</span>
              <ArrowRight className="w-4 h-4" />
            </button>

            <button
              onClick={() => setCurrentTab('dashboard')}
              className="inline-flex items-center space-x-2 px-6 py-3 rounded-xl bg-slate-800/80 hover:bg-slate-700/80 text-slate-200 border border-slate-700 font-semibold text-sm transition-all"
            >
              <ShieldCheck className="w-4 h-4 text-emerald-400" />
              <span>Officer Command Center</span>
            </button>
          </div>
        </div>
      </section>

      {/* Core Architectural Pillars */}
      <section className="space-y-6">
        <div className="text-center max-w-2xl mx-auto space-y-2">
          <h2 className="text-2xl sm:text-3xl font-bold text-white tracking-tight">
            Phase 1: Production-Ready Foundation
          </h2>
          <p className="text-slate-400 text-sm">
            Modular architecture engineered from scratch with complete separation of data ingestion, 
            probabilistic contracts, communication adapters, and farmer consent.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* Pillar 1 */}
          <div className="p-6 rounded-2xl glass-panel border border-slate-800/80 hover:border-sky-500/30 transition-colors space-y-4">
            <div className="w-12 h-12 rounded-xl bg-sky-500/10 border border-sky-500/20 flex items-center justify-center text-sky-400">
              <Layers className="w-6 h-6" />
            </div>
            <h3 className="text-lg font-bold text-white">Block-Scale Target Unit</h3>
            <p className="text-slate-400 text-sm leading-relaxed">
              Block is established as the primary meteorological prediction unit. Villages map automatically via PIN code without requiring farmers to guess administrative boundaries.
            </p>
            <div className="flex items-center space-x-2 text-xs text-sky-400 font-medium">
              <CheckCircle2 className="w-4 h-4" />
              <span>No hardcoded block boundaries</span>
            </div>
          </div>

          {/* Pillar 2 */}
          <div className="p-6 rounded-2xl glass-panel border border-slate-800/80 hover:border-emerald-500/30 transition-colors space-y-4">
            <div className="w-12 h-12 rounded-xl bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-emerald-400">
              <Smartphone className="w-6 h-6" />
            </div>
            <h3 className="text-lg font-bold text-white">Conversational SMS State Machine</h3>
            <p className="text-slate-400 text-sm leading-relaxed">
              Farmers onboard simply by texting <code className="text-sky-300 bg-slate-800 px-1 py-0.5 rounded">MEGH</code> or giving a missed call. Multilingual conversational state machine validates language, PIN, village, and explicit consent.
            </p>
            <div className="flex items-center space-x-2 text-xs text-emerald-400 font-medium">
              <CheckCircle2 className="w-4 h-4" />
              <span>Zero-cost incoming caller detection</span>
            </div>
          </div>

          {/* Pillar 3 */}
          <div className="p-6 rounded-2xl glass-panel border border-slate-800/80 hover:border-teal-500/30 transition-colors space-y-4">
            <div className="w-12 h-12 rounded-xl bg-teal-500/10 border border-teal-500/20 flex items-center justify-center text-teal-400">
              <Radio className="w-6 h-6" />
            </div>
            <h3 className="text-lg font-bold text-white">Severity Alerting & Voice Fallback</h3>
            <p className="text-slate-400 text-sm leading-relaxed">
              Intelligent multi-channel routing (SMS, WhatsApp, Voice). Automated retry policies trigger SMS fallback when urgent voice alert calls remain unanswered.
            </p>
            <div className="flex items-center space-x-2 text-xs text-teal-400 font-medium">
              <CheckCircle2 className="w-4 h-4" />
              <span>Configurable thresholds in YAML</span>
            </div>
          </div>
        </div>
      </section>

      {/* Engineering Transparency Notice */}
      <section className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800 flex items-start space-x-4">
        <AlertCircle className="w-6 h-6 text-sky-400 shrink-0 mt-0.5" />
        <div className="space-y-1 text-xs sm:text-sm text-slate-300">
          <h4 className="font-semibold text-white">Ethical AI & Data Transparency Standards</h4>
          <p className="text-slate-400">
            Meghvani strictly complies with hackathon integrity guidelines:
            Phase 1 provides the production backend, Pydantic schemas, and database foundation.
            No fake ML predictions are generated; no live telecommunications credentials are committed;
            all demonstration observations are labelled <span className="text-amber-400 font-mono">DEMO DATA</span>.
          </p>
        </div>
      </section>
    </div>
  );
};
