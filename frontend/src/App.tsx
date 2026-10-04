import React, { useState, useEffect } from 'react';
import { Sidebar } from './components/Sidebar';
import { TopHeader } from './components/TopHeader';
import { Footer } from './components/Footer';

// Primary Redesigned Pages
import { DashboardPage } from './pages/DashboardPage';
import { MonsoonPredictionPage } from './pages/MonsoonPredictionPage';
import { LiveMapPage } from './pages/LiveMapPage';
import { ForecastPage } from './pages/ForecastPage';
import { ExplainableAIPage } from './pages/ExplainableAIPage';
import { AdvisoriesPage } from './pages/AdvisoriesPage';
import { DataModelPage } from './pages/DataModelPage';
import { ArchitecturePage } from './pages/ArchitecturePage';

// Retained Operational & Verification Pages
import { SIHDemoPage } from './pages/SIHDemoPage';
import { AlertCenterPage } from './pages/AlertCenterPage';
import { FarmerRegistrationSim } from './pages/FarmerRegistrationSim';
import { ObservationFeedbackPage } from './pages/ObservationFeedbackPage';
import { OfficerDashboard } from './pages/OfficerDashboard';
import { SystemStatusPage } from './pages/SystemStatusPage';
import { HistoricalAnalysis } from './pages/HistoricalAnalysis';
import { ScientificValidationPage } from './pages/ScientificValidationPage';

import { api } from './services/api';
import { Block } from './types';

export function App() {
  const [currentTab, setCurrentTab] = useState<string>('dashboard');
  const [mobileSidebarOpen, setMobileSidebarOpen] = useState<boolean>(false);
  const [selectedBlockId, setSelectedBlockId] = useState<number>(1);
  const [blocks, setBlocks] = useState<Block[]>([
    {
      id: 1,
      name: 'Nagpur Rural (Nagpur)',
      district: 'Nagpur',
      state: 'Maharashtra',
      latitude: 21.1458,
      longitude: 79.0882,
      active: true,
    },
    {
      id: 2,
      name: 'Wardha East (Wardha)',
      district: 'Wardha',
      state: 'Maharashtra',
      latitude: 20.7453,
      longitude: 78.6022,
      active: true,
    },
    {
      id: 3,
      name: 'Amravati Central (Amravati)',
      district: 'Amravati',
      state: 'Maharashtra',
      latitude: 20.9374,
      longitude: 77.7796,
      active: true,
    },
  ]);

  useEffect(() => {
    const loadBlocks = async () => {
      try {
        const data = await api.getBlocks();
        if (data && data.length > 0) {
          setBlocks(data);
        }
      } catch (err) {
        console.warn('Using canonical blocks fallback:', err);
      }
    };
    loadBlocks();
  }, []);

  // Listen for navigation events from interactive components (e.g., map detailed forecast button)
  useEffect(() => {
    const handleNavigation = (e: Event) => {
      const customEvent = e as CustomEvent<{ tab?: string; blockId?: number }>;
      if (customEvent.detail?.blockId) {
        setSelectedBlockId(customEvent.detail.blockId);
      }
      if (customEvent.detail?.tab) {
        setCurrentTab(customEvent.detail.tab);
      }
    };
    window.addEventListener('meghvani:navigate', handleNavigation);
    return () => window.removeEventListener('meghvani:navigate', handleNavigation);
  }, []);

  return (
    <div className="min-h-screen bg-[#F6F8FB] text-stone-900 font-sans flex">
      {/* Professional Left Sidebar */}
      <Sidebar
        currentTab={currentTab}
        onSelectTab={setCurrentTab}
        isOpen={mobileSidebarOpen}
        onCloseMobile={() => setMobileSidebarOpen(false)}
      />

      {/* Main Content Area (Offset by Sidebar on Desktop) */}
      <div className="flex-1 flex flex-col min-w-0 lg:pl-64">
        {/* Top Header with Journey & Location Selectors */}
        <TopHeader
          currentTab={currentTab}
          onSelectTab={setCurrentTab}
          blocks={blocks}
          selectedBlockId={selectedBlockId}
          onSelectBlockId={setSelectedBlockId}
          onOpenMobileMenu={() => setMobileSidebarOpen(true)}
        />

        {/* Dynamic Page Views */}
        <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6">
          {(currentTab === 'dashboard' || currentTab === 'landing') && (
            <DashboardPage
              blocks={blocks}
              selectedBlockId={selectedBlockId}
              onSelectBlockId={setSelectedBlockId}
              onNavigateTab={setCurrentTab}
            />
          )}

          {currentTab === 'prediction' && (
            <MonsoonPredictionPage
              blocks={blocks}
              selectedBlockId={selectedBlockId}
              onSelectBlockId={setSelectedBlockId}
              onNavigateTab={setCurrentTab}
            />
          )}

          {currentTab === 'map' && (
            <LiveMapPage
              blocks={blocks}
              selectedBlockId={selectedBlockId}
              onSelectBlockId={setSelectedBlockId}
              onNavigateTab={setCurrentTab}
            />
          )}

          {currentTab === 'forecast' && (
            <ForecastPage
              blocks={blocks}
              selectedBlockId={selectedBlockId}
              onSelectBlockId={setSelectedBlockId}
              onNavigateTab={setCurrentTab}
            />
          )}

          {currentTab === 'xai' && (
            <ExplainableAIPage
              blocks={blocks}
              selectedBlockId={selectedBlockId}
              onSelectBlockId={setSelectedBlockId}
              onNavigateTab={setCurrentTab}
            />
          )}

          {currentTab === 'advisories' && (
            <AdvisoriesPage
              blocks={blocks}
              selectedBlockId={selectedBlockId}
              onSelectBlockId={setSelectedBlockId}
              onNavigateTab={setCurrentTab}
            />
          )}

          {currentTab === 'model' && <DataModelPage />}
          {currentTab === 'architecture' && <ArchitecturePage />}

          {/* Preserved Secondary & Verification Pages */}
          {currentTab === 'demo' && <SIHDemoPage />}
          {currentTab === 'alerts' && <AlertCenterPage />}
          {currentTab === 'farmers' && <FarmerRegistrationSim />}
          {currentTab === 'observations' && <ObservationFeedbackPage />}
          {currentTab === 'officer' && <OfficerDashboard />}
          {currentTab === 'status' && <SystemStatusPage />}
          {currentTab === 'historical' && <HistoricalAnalysis />}
          {currentTab === 'validation' && <ScientificValidationPage />}
        </main>

        {/* Global Footer */}
        <Footer />
      </div>
    </div>
  );
}

export default App;
