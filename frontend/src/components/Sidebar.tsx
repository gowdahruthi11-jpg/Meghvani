import React from 'react';
import {
  LayoutDashboard,
  CloudRain,
  Map,
  BarChart3,
  BrainCircuit,
  Sprout,
  Database,
  Play,
  Bell,
  Users,
  MessageSquare,
  ShieldCheck,
  CheckCircle2,
  Activity,
  Layers,
  HelpCircle,
  ExternalLink
} from 'lucide-react';

interface SidebarProps {
  currentTab: string;
  onSelectTab: (tab: string) => void;
  isOpen: boolean;
  onCloseMobile: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({
  currentTab,
  onSelectTab,
  isOpen,
  onCloseMobile,
}) => {
  const primaryNav = [
    { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard, badge: null },
    { id: 'prediction', label: 'Monsoon Prediction', icon: CloudRain, badge: 'ML' },
    { id: 'map', label: 'Live Map', icon: Map, badge: 'GIS' },
    { id: 'forecast', label: 'Forecast', icon: BarChart3, badge: '30d' },
    { id: 'xai', label: 'Explainable AI', icon: BrainCircuit, badge: 'XAI' },
    { id: 'advisories', label: 'Advisories', icon: Sprout, badge: 'ICAR' },
    { id: 'model', label: 'Data & Model', icon: Database, badge: null },
    { id: 'architecture', label: 'System Architecture', icon: Layers, badge: 'SYS' },
  ];

  const secondaryNav = [
    { id: 'demo', label: 'SIH Demo Replay', icon: Play },
    { id: 'alerts', label: 'Alert Center', icon: Bell },
    { id: 'farmers', label: 'Farmer Directory', icon: Users },
    { id: 'observations', label: 'Ground Observations', icon: MessageSquare },
    { id: 'officer', label: 'Officer Dashboard', icon: ShieldCheck },
  ];

  const handleNav = (id: string) => {
    onSelectTab(id);
    onCloseMobile();
  };

  const now = new Date();
  const timeStr = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

  return (
    <>
      {/* Mobile Overlay */}
      {isOpen && (
        <div
          onClick={onCloseMobile}
          className="fixed inset-0 z-40 bg-stone-900/40 backdrop-blur-xs lg:hidden"
        />
      )}

      {/* Sidebar Container */}
      <aside
        className={`fixed top-0 bottom-0 left-0 z-50 w-64 bg-white border-r border-stone-200/90 flex flex-col justify-between transition-transform duration-200 ease-in-out lg:translate-x-0 ${
          isOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        {/* Brand Header */}
        <div className="p-4 border-b border-stone-100 flex items-center justify-between">
          <div
            onClick={() => handleNav('dashboard')}
            className="flex items-center space-x-2.5 cursor-pointer group"
          >
            <div className="w-9 h-9 rounded-xl bg-forest-800 text-white flex items-center justify-center font-bold text-lg shadow-xs group-hover:bg-forest-900 transition-colors">
              🌧️
            </div>
            <div>
              <div className="flex items-center space-x-1.5">
                <span className="font-extrabold text-base tracking-tight text-stone-900">
                  MEGHVANI
                </span>
                <span className="text-[9px] font-black uppercase px-1.5 py-0.5 rounded bg-amber-100 text-amber-900 border border-amber-300">
                  SIH
                </span>
              </div>
              <p className="text-[10px] text-stone-500 font-semibold tracking-wide">
                Hyperlocal Monsoon Intelligence
              </p>
            </div>
          </div>
        </div>

        {/* Scrollable Navigation */}
        <div className="flex-1 overflow-y-auto px-3 py-4 space-y-6">
          {/* Main Navigation */}
          <div>
            <span className="px-3 text-[10px] font-extrabold uppercase tracking-wider text-stone-400">
              Intelligence
            </span>
            <div className="mt-2 space-y-1">
              {primaryNav.map((item) => {
                const Icon = item.icon;
                const isActive = currentTab === item.id;
                return (
                  <button
                    key={item.id}
                    onClick={() => handleNav(item.id)}
                    className={`w-full flex items-center justify-between px-3 py-2 rounded-xl text-xs font-semibold transition-all ${
                      isActive
                        ? 'bg-forest-50 text-forest-900 font-extrabold border border-forest-200/80 shadow-2xs'
                        : 'text-stone-600 hover:text-stone-900 hover:bg-stone-50'
                    }`}
                  >
                    <div className="flex items-center space-x-2.5 truncate">
                      <Icon
                        className={`w-4 h-4 shrink-0 ${
                          isActive ? 'text-forest-700' : 'text-stone-400'
                        }`}
                      />
                      <span className="truncate">{item.label}</span>
                    </div>
                    {item.badge && (
                      <span
                        className={`text-[9px] font-extrabold px-1.5 py-0.5 rounded uppercase tracking-wider ${
                          isActive
                            ? 'bg-forest-200/60 text-forest-900'
                            : 'bg-stone-100 text-stone-500'
                        }`}
                      >
                        {item.badge}
                      </span>
                    )}
                  </button>
                );
              })}
            </div>
          </div>

          {/* Secondary Operations */}
          <div>
            <span className="px-3 text-[10px] font-extrabold uppercase tracking-wider text-stone-400">
              Operations & Simulation
            </span>
            <div className="mt-2 space-y-1">
              {secondaryNav.map((item) => {
                const Icon = item.icon;
                const isActive = currentTab === item.id;
                return (
                  <button
                    key={item.id}
                    onClick={() => handleNav(item.id)}
                    className={`w-full flex items-center space-x-2.5 px-3 py-2 rounded-xl text-xs font-semibold transition-all ${
                      isActive
                        ? 'bg-stone-100 text-stone-900 font-bold border border-stone-200'
                        : 'text-stone-600 hover:text-stone-900 hover:bg-stone-50'
                    }`}
                  >
                    <Icon
                      className={`w-4 h-4 shrink-0 ${
                        isActive ? 'text-forest-700' : 'text-stone-400'
                      }`}
                    />
                    <span className="truncate">{item.label}</span>
                  </button>
                );
              })}
            </div>
          </div>
        </div>

        {/* Sidebar Footer: System Status */}
        <div className="p-3 border-t border-stone-100 bg-stone-50/70 text-xs">
          <div className="p-2.5 rounded-xl bg-white border border-stone-200/80 shadow-2xs space-y-1.5">
            <div className="flex items-center justify-between text-[11px] font-bold text-stone-800">
              <span className="flex items-center space-x-1.5">
                <span className="relative flex h-2 w-2">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                  <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
                </span>
                <span>System Operational</span>
              </span>
              <span className="text-[10px] text-stone-400 font-mono">{timeStr}</span>
            </div>

            <div className="space-y-0.5 text-[10px] text-stone-500">
              <div className="flex items-center justify-between">
                <span>Data Pipeline:</span>
                <span className="font-semibold text-emerald-700">● Active (IMD/ERA5)</span>
              </div>
              <div className="flex items-center justify-between">
                <span>Predictor Engine:</span>
                <span className="font-semibold text-stone-700">● Calibrated (Phase 8B)</span>
              </div>
            </div>
          </div>
        </div>
      </aside>
    </>
  );
};
