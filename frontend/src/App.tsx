import React, { useState } from 'react';
import { Navbar } from './components/Navbar';
import { Footer } from './components/Footer';
import { LandingPage } from './pages/LandingPage';
import { FarmerRegistrationSim } from './pages/FarmerRegistrationSim';
import { OfficerDashboard } from './pages/OfficerDashboard';
import { SystemStatusPage } from './pages/SystemStatusPage';

export function App() {
  const [currentTab, setCurrentTab] = useState<string>('landing');

  return (
    <div className="min-h-screen flex flex-col bg-slate-950 text-slate-100 selection:bg-sky-500 selection:text-white">
      {/* Top Navigation */}
      <Navbar currentTab={currentTab} setCurrentTab={setCurrentTab} />

      {/* Main Container */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 pt-8">
        {currentTab === 'landing' && <LandingPage setCurrentTab={setCurrentTab} />}
        {currentTab === 'register' && <FarmerRegistrationSim />}
        {currentTab === 'dashboard' && <OfficerDashboard />}
        {currentTab === 'status' && <SystemStatusPage />}
      </main>

      {/* Bottom Footer */}
      <Footer />
    </div>
  );
}

export default App;
