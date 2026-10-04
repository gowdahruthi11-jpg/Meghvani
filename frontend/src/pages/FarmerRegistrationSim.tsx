import React, { useState, useEffect, useRef } from 'react';
import { api } from '../services/api';
import {
  Smartphone,
  Send,
  PhoneCall,
  RotateCcw,
  CheckCircle,
  ShieldAlert,
  ArrowRight,
  Info,
  Check
} from 'lucide-react';

interface ChatMessage {
  id: string;
  sender: 'system' | 'farmer';
  text: string;
  timestamp: string;
  isCallNotification?: boolean;
}

export const FarmerRegistrationSim: React.FC = () => {
  const [phone, setPhone] = useState('+919876500001');
  const [inputMessage, setInputMessage] = useState('');
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [currentStep, setCurrentStep] = useState<string>('START');
  const [isCompleted, setIsCompleted] = useState<boolean>(false);
  const [registeredFarmerId, setRegisteredFarmerId] = useState<number | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const chatEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const addMessage = (sender: 'system' | 'farmer', text: string, isCall = false) => {
    const newMsg: ChatMessage = {
      id: Math.random().toString(36).substring(7),
      sender,
      text,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      isCallNotification: isCall,
    };
    setMessages((prev) => [...prev, newMsg]);
  };

  const handleStart = async (customPhone?: string) => {
    const targetPhone = (customPhone || phone).trim();
    if (!targetPhone) return;

    handleReset();
    addMessage('farmer', 'MEGH');
    setLoading(true);

    try {
      const res = await api.startRegistration(targetPhone);
      addMessage('system', res.reply_message);
      setCurrentStep(res.current_step);
      setIsCompleted(res.is_completed);
      if (res.registered_farmer_id) setRegisteredFarmerId(res.registered_farmer_id);
    } catch (err: any) {
      setError(err.message || 'Failed to start registration');
    } finally {
      setLoading(false);
    }
  };

  const handleMissedCall = async () => {
    const targetPhone = phone.trim();
    if (!targetPhone) return;

    handleReset();
    setLoading(true);

    try {
      addMessage('farmer', `[Missed Call placed to Meghvani Onboarding Number]`, true);
      const res = await api.simulateMissedCall(targetPhone);
      addMessage('system', res.reply_message);
      setCurrentStep(res.current_step);
      setIsCompleted(res.is_completed);
      if (res.registered_farmer_id) setRegisteredFarmerId(res.registered_farmer_id);
    } catch (err: any) {
      setError(err.message || 'Failed to simulate missed call');
    } finally {
      setLoading(false);
    }
  };

  const handleSendMessage = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    const msg = inputMessage.trim();
    if (!msg || loading) return;

    setInputMessage('');
    setError(null);
    addMessage('farmer', msg);
    setLoading(true);

    try {
      const res = await api.sendRegistrationMessage(phone, msg);
      addMessage('system', res.reply_message);
      setCurrentStep(res.current_step);
      setIsCompleted(res.is_completed);
      if (res.registered_farmer_id) setRegisteredFarmerId(res.registered_farmer_id);
    } catch (err: any) {
      setError(err.message || 'Error processing message');
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setMessages([]);
    setCurrentStep('START');
    setIsCompleted(false);
    setRegisteredFarmerId(null);
    setInputMessage('');
    setError(null);
  };

  const handleQuickReply = async (replyText: string) => {
    if (loading) return;
    setInputMessage('');
    setError(null);
    addMessage('farmer', replyText);
    setLoading(true);

    try {
      const res = await api.sendRegistrationMessage(phone, replyText);
      addMessage('system', res.reply_message);
      setCurrentStep(res.current_step);
      setIsCompleted(res.is_completed);
      if (res.registered_farmer_id) setRegisteredFarmerId(res.registered_farmer_id);
    } catch (err: any) {
      setError(err.message || 'Error processing message');
    } finally {
      setLoading(false);
    }
  };

  const stepsList = [
    { key: 'LANGUAGE', label: '1. Language Select' },
    { key: 'PIN', label: '2. PIN Code' },
    { key: 'VILLAGE', label: '3. Village Select' },
    { key: 'CROP', label: '4. Crop Select' },
    { key: 'CONSENT', label: '5. Explicit Consent' },
    { key: 'COMPLETED', label: '6. Activated' },
  ];

  return (
    <div className="space-y-6 pb-12">
      {/* Header */}
      <div className="agri-card p-6 bg-white border-stone-200">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <div className="flex items-center space-x-2">
              <span className="text-2xl">📱</span>
              <h2 className="text-xl sm:text-2xl font-bold text-stone-900 tracking-tight">
                Farmer Registration & Onboarding Simulator
              </h2>
            </div>
            <p className="text-xs text-stone-600 mt-1 max-w-2xl leading-relaxed">
              Zero-smartphone conversational SMS and missed-call onboarding state machine.
              Simulates automated farmer registration in Marathi, Hindi, and English.
            </p>
          </div>
          <span className="text-[10px] font-bold px-3 py-1 rounded-full bg-forest-100 text-forest-800 border border-forest-300 uppercase tracking-wider self-start sm:self-auto">
            Interactive State Machine
          </span>
        </div>
      </div>

      {/* Main Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
        {/* Left Column: Phone Controls & State Machine Monitor */}
        <div className="lg:col-span-5 space-y-6">
          {/* Phone Config Card */}
          <div className="agri-card p-6 bg-white border-stone-200 space-y-4">
            <div className="flex items-center justify-between pb-3 border-b border-stone-100">
              <h3 className="font-bold text-stone-900 text-sm">
                Farmer Mobile Identification
              </h3>
              <span className="text-[10px] text-forest-800 bg-forest-50 border border-forest-200 px-2 py-0.5 rounded-full font-bold">
                Privacy Protected
              </span>
            </div>

            <div>
              <label className="text-xs font-semibold text-stone-700 block mb-1">
                Simulated Incoming Mobile Number
              </label>
              <input
                type="text"
                value={phone}
                onChange={(e) => setPhone(e.target.value)}
                placeholder="+919876543210"
                className="w-full px-3.5 py-2 bg-stone-50 border border-stone-300 rounded-xl text-sm text-stone-900 focus:outline-none focus:border-forest-600 font-mono shadow-inner"
              />
              <p className="text-[11px] text-stone-500 mt-1.5">
                Note: In production telecom flows, incoming mobile CLI is detected automatically by the telecom gateway.
              </p>
            </div>

            <div className="flex flex-wrap gap-2 pt-1">
              <button
                type="button"
                onClick={() => handleStart()}
                disabled={loading}
                className="flex-1 inline-flex items-center justify-center space-x-1.5 px-3 py-2.5 rounded-xl bg-forest-800 hover:bg-forest-900 text-white font-bold text-xs shadow-xs transition-all disabled:opacity-50"
              >
                <Send className="w-3.5 h-3.5" />
                <span>Text "MEGH"</span>
              </button>

              <button
                type="button"
                onClick={handleMissedCall}
                disabled={loading}
                className="flex-1 inline-flex items-center justify-center space-x-1.5 px-3 py-2.5 rounded-xl bg-teal-700 hover:bg-teal-800 text-white font-bold text-xs shadow-xs transition-all disabled:opacity-50"
              >
                <PhoneCall className="w-3.5 h-3.5" />
                <span>Give Missed Call</span>
              </button>

              <button
                type="button"
                onClick={handleReset}
                className="p-2.5 rounded-xl bg-stone-100 hover:bg-stone-200 text-stone-700 border border-stone-300 transition-colors"
                title="Reset simulation"
              >
                <RotateCcw className="w-4 h-4" />
              </button>
            </div>
          </div>

          {/* State Machine Visualizer */}
          <div className="agri-card p-6 bg-white border-stone-200 space-y-4">
            <h3 className="font-bold text-stone-900 text-sm">State Machine Progress</h3>
            <div className="space-y-2">
              {stepsList.map((st, idx) => {
                const isCurrent = currentStep === st.key;
                const isPast =
                  isCompleted ||
                  (idx < stepsList.findIndex((s) => s.key === currentStep) &&
                    currentStep !== 'START');

                return (
                  <div
                    key={st.key}
                    className={`flex items-center justify-between p-2.5 rounded-xl text-xs transition-all ${
                      isCurrent
                        ? 'bg-forest-50 border border-forest-300 text-forest-900 font-bold shadow-2xs'
                        : isPast
                        ? 'bg-emerald-50/60 border border-emerald-200 text-emerald-800 font-semibold'
                        : 'bg-stone-50 border border-stone-200 text-stone-400'
                    }`}
                  >
                    <span>{st.label}</span>
                    {isPast ? (
                      <CheckCircle className="w-4 h-4 text-emerald-600" />
                    ) : isCurrent ? (
                      <span className="w-2 h-2 rounded-full bg-forest-600 animate-pulse" />
                    ) : (
                      <span className="w-2 h-2 rounded-full bg-stone-300" />
                    )}
                  </div>
                );
              })}
            </div>

            {isCompleted && registeredFarmerId && (
              <div className="p-3.5 rounded-xl bg-emerald-50 border border-emerald-200 text-emerald-900 text-xs flex items-center space-x-2">
                <CheckCircle className="w-4 h-4 shrink-0 text-emerald-700" />
                <span>
                  Farmer Record <strong>#{registeredFarmerId}</strong> successfully activated in database!
                </span>
              </div>
            )}
          </div>

          {/* Simple Farmer-Oriented Outlook Card (Section 16) */}
          <div className="agri-card p-5 bg-white border-stone-200 space-y-3">
            <div className="flex items-center justify-between border-b border-stone-200 pb-2">
              <div className="flex items-center gap-1.5">
                <span className="text-base">🌱</span>
                <h4 className="font-bold text-stone-900 text-xs uppercase tracking-wider">
                  Your Farm Outlook
                </h4>
              </div>
              <span className="text-[11px] font-semibold text-forest-800 bg-forest-50 px-2 py-0.5 rounded-full border border-forest-200">
                📍 Nagpur Rural
              </span>
            </div>

            <div className="grid grid-cols-2 gap-2 text-xs">
              <div className="bg-stone-50 p-2 rounded-lg border border-stone-200">
                <span className="text-[10px] text-stone-500 block font-medium">Selected Crop</span>
                <span className="font-bold text-stone-900">Soybean (सोयाबीन)</span>
              </div>
              <div className="bg-sky-50 p-2 rounded-lg border border-sky-200">
                <span className="text-[10px] text-sky-700 block font-medium">🌧️ Rain Outlook</span>
                <span className="font-bold text-sky-900">Moderate rain expected</span>
              </div>
              <div className="bg-emerald-50 p-2 rounded-lg border border-emerald-200">
                <span className="text-[10px] text-emerald-700 block font-medium">⚠️ False-Onset Risk</span>
                <span className="font-bold text-emerald-900">Low (18%)</span>
              </div>
              <div className="bg-emerald-100/70 p-2 rounded-lg border border-emerald-300">
                <span className="text-[10px] text-emerald-800 block font-medium">🌱 Sowing Action</span>
                <span className="font-extrabold text-emerald-900">SOW NOW</span>
              </div>
            </div>

            <div className="bg-stone-50 p-2.5 rounded-lg border border-stone-200 text-xs text-stone-700">
              <span className="font-semibold block text-stone-900 mb-0.5">Why?</span>
              <p className="leading-snug text-[11px]">
                Recent rainfall conditions support the current prototype sowing window with adequate seedbed moisture.
              </p>
            </div>
          </div>

          {/* Prototype PIN Code Reference Card */}
          <div className="agri-card p-5 bg-white border-stone-200 space-y-2.5">
            <div className="flex items-center justify-between border-b border-stone-200 pb-2">
              <div className="flex items-center gap-1.5">
                <span className="text-sm">📍</span>
                <h4 className="font-bold text-stone-900 text-xs">Supported PIN Code Telemetry</h4>
              </div>
              <span className="text-[10px] bg-emerald-100 text-emerald-800 font-bold px-2 py-0.5 rounded-full">
                Auto-Mapped
              </span>
            </div>
            <p className="text-[11px] text-stone-600 leading-snug">
              The onboarding pipeline maps 6-digit postal PIN codes to meteorological forecasting blocks automatically:
            </p>
            <div className="space-y-1.5 text-[11px]">
              <div className="flex items-center justify-between p-2 rounded-lg bg-stone-50 border border-stone-200">
                <span className="font-mono font-bold text-forest-800">441501 / 440xxx</span>
                <span className="text-stone-700">Nagpur Rural (Kalmeshwar, Mohpa)</span>
              </div>
              <div className="flex items-center justify-between p-2 rounded-lg bg-stone-50 border border-stone-200">
                <span className="font-mono font-bold text-forest-800">442104 / 442301</span>
                <span className="text-stone-700">Wardha East (Seloo, Hinganghat)</span>
              </div>
              <div className="flex items-center justify-between p-2 rounded-lg bg-stone-50 border border-stone-200">
                <span className="font-mono font-bold text-forest-800">444904 / 444905</span>
                <span className="text-stone-700">Amravati Central (Chandur, Morshi)</span>
              </div>
            </div>
          </div>
        </div>

        {/* Right Column: Clean Light Mobile Phone Chat Mockup */}
        <div className="lg:col-span-7 flex justify-center">
          <div className="w-full max-w-md bg-stone-800 rounded-[2.5rem] border-4 border-stone-700 p-3 shadow-xl relative overflow-hidden">
            {/* Phone Speaker Notch */}
            <div className="absolute top-4 left-1/2 -translate-x-1/2 w-28 h-4 bg-stone-700 rounded-full z-20 flex items-center justify-center">
              <div className="w-2.5 h-2.5 rounded-full bg-stone-900 mr-2" />
              <div className="w-8 h-1 rounded-full bg-stone-900" />
            </div>

            {/* Phone Screen */}
            <div className="bg-[#FAF9F5] rounded-[2rem] pt-8 pb-3 px-4 h-[550px] flex flex-col justify-between border border-stone-300">
              {/* Header */}
              <div className="border-b border-stone-200 pb-2.5 flex items-center justify-between">
                <div>
                  <h4 className="font-bold text-stone-900 text-xs">🌾 Meghvani SMS Gateway</h4>
                  <p className="text-[10px] text-forest-700 font-semibold">Short Code: 56161 (Mock Telemetry)</p>
                </div>
                <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
              </div>

              {/* Message History */}
              <div className="flex-1 overflow-y-auto py-3 space-y-3 pr-1 text-xs">
                {messages.length === 0 ? (
                  <div className="h-full flex flex-col items-center justify-center text-center text-stone-400 px-4 space-y-2">
                    <Smartphone className="w-8 h-8 text-stone-300" />
                    <p className="text-xs text-stone-500">
                      Click <strong>Text "MEGH"</strong> or <strong>Give Missed Call</strong> on the left to start conversational onboarding.
                    </p>
                  </div>
                ) : (
                  messages.map((m) => {
                    const isSystem = m.sender === 'system';
                    return (
                      <div
                        key={m.id}
                        className={`flex flex-col ${isSystem ? 'items-start' : 'items-end'}`}
                      >
                        <div
                          className={`max-w-[85%] rounded-2xl px-3.5 py-2.5 whitespace-pre-line leading-relaxed ${
                            m.isCallNotification
                              ? 'bg-amber-100 text-amber-900 border border-amber-300 italic text-[11px]'
                              : isSystem
                              ? 'bg-white text-stone-900 border border-stone-200 shadow-2xs rounded-tl-xs'
                              : 'bg-forest-800 text-white rounded-tr-xs shadow-xs'
                          }`}
                        >
                          {m.text}
                        </div>
                        <span className="text-[10px] text-stone-400 mt-0.5 px-1">{m.timestamp}</span>
                      </div>
                    );
                  })
                )}
                {loading && (
                  <div className="flex items-center space-x-1 text-forest-700 text-xs pl-2">
                    <span className="animate-bounce">●</span>
                    <span className="animate-bounce delay-100">●</span>
                    <span className="animate-bounce delay-200">●</span>
                  </div>
                )}
                <div ref={chatEndRef} />
              </div>

              {/* Step-specific Quick Action Helper Chips */}
              {currentStep === 'PIN' && (
                <div className="py-1.5 px-1 flex flex-wrap items-center gap-1 border-t border-stone-200 bg-stone-50/70 rounded-lg mb-1">
                  <span className="text-[10px] text-stone-500 font-bold uppercase tracking-wider pl-1">
                    Select PIN:
                  </span>
                  <button
                    type="button"
                    onClick={() => handleQuickReply('441501')}
                    className="px-2 py-0.5 rounded-md bg-forest-100 hover:bg-forest-200 text-forest-900 border border-forest-300 text-[10px] font-semibold transition-all"
                  >
                    📍 441501 (Nagpur)
                  </button>
                  <button
                    type="button"
                    onClick={() => handleQuickReply('442104')}
                    className="px-2 py-0.5 rounded-md bg-forest-100 hover:bg-forest-200 text-forest-900 border border-forest-300 text-[10px] font-semibold transition-all"
                  >
                    📍 442104 (Wardha)
                  </button>
                  <button
                    type="button"
                    onClick={() => handleQuickReply('444904')}
                    className="px-2 py-0.5 rounded-md bg-forest-100 hover:bg-forest-200 text-forest-900 border border-forest-300 text-[10px] font-semibold transition-all"
                  >
                    📍 444904 (Amravati)
                  </button>
                  <button
                    type="button"
                    onClick={() => handleQuickReply('440001')}
                    className="px-2 py-0.5 rounded-md bg-stone-100 hover:bg-stone-200 text-stone-800 border border-stone-300 text-[10px] font-semibold transition-all"
                  >
                    📍 440001 (Nagpur Urban)
                  </button>
                </div>
              )}

              {currentStep === 'LANGUAGE' && (
                <div className="py-1.5 px-1 flex flex-wrap items-center gap-1 border-t border-stone-200 bg-stone-50/70 rounded-lg mb-1">
                  <span className="text-[10px] text-stone-500 font-bold uppercase tracking-wider pl-1">
                    Language:
                  </span>
                  <button
                    type="button"
                    onClick={() => handleQuickReply('1')}
                    className="px-2 py-0.5 rounded-md bg-stone-100 hover:bg-forest-100 text-stone-800 text-[10px] font-semibold border border-stone-200"
                  >
                    1: Hindi
                  </button>
                  <button
                    type="button"
                    onClick={() => handleQuickReply('2')}
                    className="px-2 py-0.5 rounded-md bg-forest-100 hover:bg-forest-200 text-forest-900 text-[10px] font-bold border border-forest-300"
                  >
                    2: Marathi
                  </button>
                  <button
                    type="button"
                    onClick={() => handleQuickReply('3')}
                    className="px-2 py-0.5 rounded-md bg-stone-100 hover:bg-forest-100 text-stone-800 text-[10px] font-semibold border border-stone-200"
                  >
                    3: Kannada
                  </button>
                  <button
                    type="button"
                    onClick={() => handleQuickReply('4')}
                    className="px-2 py-0.5 rounded-md bg-stone-100 hover:bg-forest-100 text-stone-800 text-[10px] font-semibold border border-stone-200"
                  >
                    4: English
                  </button>
                </div>
              )}

              {currentStep === 'VILLAGE' && (
                <div className="py-1.5 px-1 flex flex-wrap items-center gap-1.5 border-t border-stone-200 bg-stone-50/70 rounded-lg mb-1">
                  <span className="text-[10px] text-stone-500 font-bold uppercase tracking-wider pl-1">
                    Select Village:
                  </span>
                  <button
                    type="button"
                    onClick={() => handleQuickReply('1')}
                    className="px-3 py-0.5 rounded-md bg-forest-100 hover:bg-forest-200 text-forest-900 border border-forest-300 text-[10px] font-bold"
                  >
                    Option 1
                  </button>
                  <button
                    type="button"
                    onClick={() => handleQuickReply('2')}
                    className="px-3 py-0.5 rounded-md bg-forest-100 hover:bg-forest-200 text-forest-900 border border-forest-300 text-[10px] font-bold"
                  >
                    Option 2
                  </button>
                </div>
              )}

              {currentStep === 'CROP' && (
                <div className="py-1.5 px-1 flex flex-wrap items-center gap-1 border-t border-stone-200 bg-stone-50/70 rounded-lg mb-1">
                  <span className="text-[10px] text-stone-500 font-bold uppercase tracking-wider pl-1">
                    Select Crop:
                  </span>
                  <button
                    type="button"
                    onClick={() => handleQuickReply('1')}
                    className="px-2 py-0.5 rounded-md bg-forest-100 hover:bg-forest-200 text-forest-900 border border-forest-300 text-[10px] font-semibold"
                  >
                    1: Soybean
                  </button>
                  <button
                    type="button"
                    onClick={() => handleQuickReply('2')}
                    className="px-2 py-0.5 rounded-md bg-forest-100 hover:bg-forest-200 text-forest-900 border border-forest-300 text-[10px] font-semibold"
                  >
                    2: Cotton
                  </button>
                  <button
                    type="button"
                    onClick={() => handleQuickReply('3')}
                    className="px-2 py-0.5 rounded-md bg-forest-100 hover:bg-forest-200 text-forest-900 border border-forest-300 text-[10px] font-semibold"
                  >
                    3: Tur
                  </button>
                </div>
              )}

              {currentStep === 'CONSENT' && (
                <div className="py-1.5 px-1 flex flex-wrap items-center gap-2 border-t border-stone-200 bg-stone-50/70 rounded-lg mb-1">
                  <span className="text-[10px] text-stone-500 font-bold uppercase tracking-wider pl-1">
                    Consent:
                  </span>
                  <button
                    type="button"
                    onClick={() => handleQuickReply('YES')}
                    className="px-4 py-0.5 rounded-md bg-emerald-600 hover:bg-emerald-700 text-white text-[11px] font-bold shadow-xs"
                  >
                    ✓ YES (Activate Alerts)
                  </button>
                </div>
              )}

              {/* Input Bar */}
              <form onSubmit={handleSendMessage} className="pt-2 border-t border-stone-200 flex gap-2">
                <input
                  type="text"
                  value={inputMessage}
                  onChange={(e) => setInputMessage(e.target.value)}
                  placeholder={
                    currentStep === 'START'
                      ? 'Text MEGH to begin...'
                      : currentStep === 'LANGUAGE'
                      ? 'Reply 1, 2, 3 or 4...'
                      : currentStep === 'PIN'
                      ? 'Enter 6-digit PIN (e.g. 441501, 442104)...'
                      : currentStep === 'VILLAGE'
                      ? 'Reply village number (1 or 2)...'
                      : currentStep === 'CROP'
                      ? 'Reply crop number (1, 2 or 3)...'
                      : currentStep === 'CONSENT'
                      ? 'Reply YES to activate...'
                      : 'Type a reply...'
                  }
                  className="flex-1 bg-white border border-stone-300 rounded-xl px-3 py-2 text-xs text-stone-900 placeholder-stone-400 focus:outline-none focus:border-forest-600 shadow-inner"
                />
                <button
                  type="submit"
                  disabled={loading || !inputMessage.trim()}
                  className="px-3.5 py-2 bg-forest-800 hover:bg-forest-900 disabled:opacity-40 text-white rounded-xl text-xs font-bold flex items-center justify-center transition-colors shadow-2xs"
                >
                  <Send className="w-3.5 h-3.5" />
                </button>
              </form>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
