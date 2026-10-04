import React, { useState } from 'react';
import {
  CloudRain,
  Sprout,
  Users,
  FlaskConical,
  Play,
  Shield,
  Bell,
  MessageSquare,
  BarChart2,
  Database,
  BrainCircuit,
  Activity,
  Menu,
  X,
  ChevronDown
} from 'lucide-react';

interface NavbarProps {
  currentTab: string;
  setCurrentTab: (tab: string) => void;
}

export const Navbar: React.FC<NavbarProps> = ({ currentTab, setCurrentTab }) => {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [systemDropdownOpen, setSystemDropdownOpen] = useState(false);

  // Primary Agriculture-Oriented Navigation Items
  const primaryNavItems = [
    { id: 'landing', label: 'Dashboard', icon: Sprout, shortLabel: 'Overview' },
    { id: 'prediction', label: 'Monsoon Outlook', icon: CloudRain, shortLabel: 'Outlook' },
    { id: 'baseline', label: 'Crop Advisory', icon: Sprout, shortLabel: 'Advisory' },
    { id: 'register', label: 'Farmers', icon: Users, shortLabel: 'Farmers' },
    { id: 'validation', label: 'Scientific Validation', icon: FlaskConical, shortLabel: 'Validation' },
    { id: 'demo', label: 'SIH Demo', icon: Play, shortLabel: 'Demo' },
  ];

  // System & Operations Navigation Items (Grouped for Cleanliness)
  const systemNavItems = [
    { id: 'dashboard', label: 'Officer Console', icon: Shield },
    { id: 'alerts', label: 'Alert Center', icon: Bell },
    { id: 'observations', label: 'Farmer Observations', icon: MessageSquare },
    { id: 'historical', label: 'Historical Weather', icon: BarChart2 },
    { id: 'status', label: 'System Health', icon: Activity },
  ];

  const handleNavClick = (tabId: string) => {
    setCurrentTab(tabId);
    setMobileMenuOpen(false);
    setSystemDropdownOpen(false);
  };

  const isSystemTabActive = systemNavItems.some((item) => item.id === currentTab);

  return (
    <header className="sticky top-0 z-50 bg-white/95 backdrop-blur-md border-b border-stone-200/90 shadow-2xs">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Brand Logo & Title */}
          <div
            onClick={() => handleNavClick('landing')}
            className="flex items-center space-x-3 cursor-pointer group shrink-0"
          >
            <div className="w-10 h-10 rounded-xl bg-forest-800 flex items-center justify-center shadow-xs group-hover:bg-forest-900 transition-colors">
              <span className="text-xl" role="img" aria-label="wheat">
                🌾
              </span>
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <span className="font-extrabold text-lg sm:text-xl tracking-tight text-forest-900">
                  MEGHVANI
                </span>
                <span className="text-[10px] font-bold tracking-wider uppercase px-2 py-0.5 rounded-full bg-forest-100 text-forest-800 border border-forest-200">
                  SIH 2026
                </span>
              </div>
              <p className="text-[11px] text-stone-600 font-medium hidden sm:block">
                Hyperlocal Monsoon Intelligence
              </p>
            </div>
          </div>

          {/* Desktop Navigation */}
          <nav className="hidden lg:flex items-center space-x-1">
            {primaryNavItems.map((item) => {
              const Icon = item.icon;
              const isActive = currentTab === item.id;
              return (
                <button
                  key={item.id}
                  onClick={() => handleNavClick(item.id)}
                  className={`flex items-center space-x-1.5 px-3 py-2 rounded-lg text-xs font-semibold transition-all ${
                    isActive
                      ? 'bg-forest-50 text-forest-800 border border-forest-200 shadow-2xs font-bold'
                      : 'text-stone-700 hover:text-stone-900 hover:bg-stone-50'
                  }`}
                >
                  <Icon className={`w-4 h-4 ${isActive ? 'text-forest-700' : 'text-stone-500'}`} />
                  <span>{item.label}</span>
                </button>
              );
            })}

            {/* System Dropdown */}
            <div className="relative">
              <button
                onClick={() => setSystemDropdownOpen(!systemDropdownOpen)}
                className={`flex items-center space-x-1.5 px-3 py-2 rounded-lg text-xs font-semibold transition-all ${
                  isSystemTabActive
                    ? 'bg-forest-50 text-forest-800 border border-forest-200 font-bold'
                    : 'text-stone-700 hover:text-stone-900 hover:bg-stone-50'
                }`}
              >
                <Shield className="w-4 h-4 text-stone-500" />
                <span>System</span>
                <ChevronDown className="w-3.5 h-3.5 text-stone-400" />
              </button>

              {systemDropdownOpen && (
                <div className="absolute right-0 mt-2 w-56 bg-white rounded-xl shadow-lg border border-stone-200 py-1.5 z-50">
                  <div className="px-3 py-1.5 text-[10px] font-bold uppercase tracking-wider text-stone-600 border-b border-stone-100">
                    Operations & Diagnostics
                  </div>
                  {systemNavItems.map((sItem) => {
                    const SIcon = sItem.icon;
                    const isActive = currentTab === sItem.id;
                    return (
                      <button
                        key={sItem.id}
                        onClick={() => handleNavClick(sItem.id)}
                        className={`w-full flex items-center space-x-2.5 px-3 py-2 text-xs text-left transition-colors ${
                          isActive
                            ? 'bg-forest-50 text-forest-800 font-bold'
                            : 'text-stone-700 hover:bg-stone-50 hover:text-stone-900'
                        }`}
                      >
                        <SIcon className="w-4 h-4 text-stone-500" />
                        <span>{sItem.label}</span>
                      </button>
                    );
                  })}
                </div>
              )}
            </div>
          </nav>

          {/* Location / Status Indicator badge */}
          <div className="hidden sm:flex items-center space-x-2 border-l border-stone-200 pl-3">
            <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
            <span className="text-xs font-semibold text-stone-700">📍 Vidarbha, MH</span>
          </div>

          {/* Mobile Menu Toggle Button */}
          <div className="lg:hidden flex items-center">
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="p-2 rounded-lg text-stone-600 hover:text-stone-900 hover:bg-stone-100"
              aria-label="Toggle navigation menu"
            >
              {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Menu Drawer */}
      {mobileMenuOpen && (
        <div className="lg:hidden border-t border-stone-200 bg-white px-4 pt-3 pb-6 space-y-1">
          <div className="text-[10px] font-bold uppercase tracking-wider text-stone-600 px-3 py-1">
            Agricultural Intelligence
          </div>
          {primaryNavItems.map((item) => {
            const Icon = item.icon;
            const isActive = currentTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => handleNavClick(item.id)}
                className={`w-full flex items-center space-x-2.5 px-3 py-2.5 rounded-lg text-xs font-semibold text-left transition-colors ${
                  isActive
                    ? 'bg-forest-50 text-forest-800 border border-forest-200 font-bold'
                    : 'text-stone-700 hover:bg-stone-50'
                }`}
              >
                <Icon className="w-4 h-4 text-forest-700" />
                <span>{item.label}</span>
              </button>
            );
          })}

          <div className="text-[10px] font-bold uppercase tracking-wider text-stone-600 px-3 pt-3 pb-1 border-t border-stone-100">
            Officer & System Operations
          </div>
          {systemNavItems.map((sItem) => {
            const SIcon = sItem.icon;
            const isActive = currentTab === sItem.id;
            return (
              <button
                key={sItem.id}
                onClick={() => handleNavClick(sItem.id)}
                className={`w-full flex items-center space-x-2.5 px-3 py-2 rounded-lg text-xs font-semibold text-left transition-colors ${
                  isActive
                    ? 'bg-forest-50 text-forest-800 font-bold'
                    : 'text-stone-700 hover:bg-stone-50'
                }`}
              >
                <SIcon className="w-4 h-4 text-stone-500" />
                <span>{sItem.label}</span>
              </button>
            );
          })}
        </div>
      )}
    </header>
  );
};
