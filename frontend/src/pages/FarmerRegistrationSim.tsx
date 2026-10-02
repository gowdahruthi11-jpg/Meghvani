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
  Info
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
      isCallNotification: isCall
    };
    setMessages((prev) => [...prev, newMsg]);
  };

  const handleStart = async (customPhone?: string) => {
    const targetPhone = (customPhone || phone).trim();
    if (!targetPhone) {
      setError('Please provide a valid phone number');
      return;
    }
    setError(null);
    setLoading(true);

    try {
      addMessage('farmer', 'MEGH');
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
    if (!targetPhone) {
      setError('Please provide a valid phone number');
      return;
    }
    setError(null);
    setLoading(true);

    try {
      addMessage('farmer', `[Missed Call placed to Meghvani Onboarding CLI]`, true);
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

  const stepsList = [
    { key: 'LANGUAGE', label: '1. Language' },
    { key: 'PIN', label: '2. PIN Code' },
    { key: 'VILLAGE', label: '3. Village Select' },
    { key: 'CROP', label: '4. Crop Select' },
    { key: 'CONSENT', label: '5. Explicit Consent' },
    { key: 'COMPLETED', label: '6. Activated' }
  ];

  return (
    <div className="space-y-6 pb-12">
      {/* Header */}
      <div>
        <h2 className="text-2xl font-bold text-white tracking-tight flex items-center space-x-2">
          <Smartphone className="w-6 h-6 text-sky-400" />
          <span>Conversational SMS & Missed-Call Simulator</span>
        </h2>
        <p className="text-slate-400 text-sm mt-1">
          Interactive simulation of zero-smartphone farmer onboarding. Connected live to the backend state machine.
        </p>
      </div>

      {/* Main Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
        {/* Left Column: Phone Controls & State Machine Monitor */}
        <div className="lg:col-span-5 space-y-6">
          {/* Phone Config Card */}
          <div className="p-6 rounded-2xl glass-panel border border-slate-800 space-y-4">
            <h3 className="font-semibold text-white text-sm flex items-center justify-between">
              <span>Farmer CLI / Phone Identification</span>
              <span className="text-[10px] text-teal-400 bg-teal-500/10 border border-teal-500/20 px-2 py-0.5 rounded-full">
                Privacy Enforced
              </span>
            </h3>

            <div>
              <label className="text-xs text-slate-400 block mb-1">Simulated Incoming Mobile Number</label>
              <input
                type="text"
                value={phone}
                onChange={(e) => setPhone(e.target.value)}
                placeholder="+919876543210"
                className="w-full px-3 py-2 bg-slate-900 border border-slate-700 rounded-xl text-sm text-white focus:outline-none focus:border-sky-500 font-mono"
              />
              <p className="text-[11px] text-slate-500 mt-1">
                Note: In real telco SMS/Missed-call flows, the farmer never types their own phone number; it is detected from the provider packet.
              </p>
            </div>

            <div className="flex flex-wrap gap-2 pt-2">
              <button
                type="button"
                onClick={() => handleStart()}
                disabled={loading}
                className="flex-1 inline-flex items-center justify-center space-x-1.5 px-3 py-2.5 rounded-xl bg-sky-600 hover:bg-sky-500 text-white font-medium text-xs shadow-md shadow-sky-600/20 transition-all disabled:opacity-50"
              >
                <Send className="w-3.5 h-3.5" />
                <span>Text "MEGH"</span>
              </button>

              <button
                type="button"
                onClick={handleMissedCall}
                disabled={loading}
                className="flex-1 inline-flex items-center justify-center space-x-1.5 px-3 py-2.5 rounded-xl bg-teal-600 hover:bg-teal-500 text-white font-medium text-xs shadow-md shadow-teal-600/20 transition-all disabled:opacity-50"
              >
                <PhoneCall className="w-3.5 h-3.5" />
                <span>Give Missed Call</span>
              </button>

              <button
                type="button"
                onClick={handleReset}
                className="p-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 transition-colors"
                title="Reset simulation"
              >
                <RotateCcw className="w-4 h-4" />
              </button>
            </div>
          </div>

          {/* State Machine Visualizer */}
          <div className="p-6 rounded-2xl glass-panel border border-slate-800 space-y-4">
            <h3 className="font-semibold text-white text-sm">State Machine Progress</h3>
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
                        ? 'bg-sky-500/20 border border-sky-500/40 text-sky-300 font-semibold'
                        : isPast
                        ? 'bg-slate-900/40 border border-emerald-500/30 text-emerald-400'
                        : 'bg-slate-900/20 border border-slate-800 text-slate-500'
                    }`}
                  >
                    <span>{st.label}</span>
                    {isPast ? (
                      <CheckCircle className="w-4 h-4 text-emerald-400" />
                    ) : isCurrent ? (
                      <span className="w-2 h-2 rounded-full bg-sky-400 animate-pulse" />
                    ) : (
                      <span className="w-2 h-2 rounded-full bg-slate-700" />
                    )}
                  </div>
                );
              })}
            </div>

            {isCompleted && registeredFarmerId && (
              <div className="p-3 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-300 text-xs flex items-center space-x-2">
                <CheckCircle className="w-4 h-4 shrink-0 text-emerald-400" />
                <span>
                  Farmer Record <strong>#{registeredFarmerId}</strong> successfully created in database!
                </span>
              </div>
            )}
          </div>
        </div>

        {/* Right Column: Mobile Phone Chat Mockup */}
        <div className="lg:col-span-7 flex justify-center">
          <div className="w-full max-w-md bg-slate-950 rounded-[2.5rem] border-4 border-slate-800 p-3 shadow-2xl relative overflow-hidden">
            {/* Phone Speaker Notch */}
            <div className="absolute top-4 left-1/2 -translate-x-1/2 w-28 h-4 bg-slate-800 rounded-full z-20 flex items-center justify-center">
              <div className="w-3 h-3 rounded-full bg-slate-900 mr-2" />
              <div className="w-8 h-1.5 rounded-full bg-slate-900" />
            </div>

            {/* Phone Screen */}
            <div className="bg-slate-900/90 rounded-[2rem] pt-8 pb-3 px-4 h-[550px] flex flex-col justify-between border border-slate-800/80">
              {/* Header */}
              <div className="border-b border-slate-800 pb-3 flex items-center justify-between">
                <div>
                  <h4 className="font-bold text-white text-sm">Meghvani SMS Gateway</h4>
                  <p className="text-[11px] text-teal-400">Short Code: 56161 (Mock)</p>
                </div>
                <div className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
              </div>

              {/* Message History */}
              <div className="flex-1 overflow-y-auto py-3 space-y-3 pr-1 text-xs">
                {messages.length === 0 ? (
                  <div className="h-full flex flex-col items-center justify-center text-center text-slate-500 px-4 space-y-2">
                    <Smartphone className="w-8 h-8 text-slate-600" />
                    <p>Click <strong>Text "MEGH"</strong> or <strong>Give Missed Call</strong> on the left to start conversational onboarding.</p>
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
                              ? 'bg-amber-500/20 text-amber-200 border border-amber-500/30 italic text-[11px]'
                              : isSystem
                              ? 'bg-slate-800 text-slate-200 border border-slate-700/60 rounded-tl-sm'
                              : 'bg-gradient-to-r from-sky-600 to-sky-500 text-white rounded-tr-sm shadow-md'
                          }`}
                        >
                          {m.text}
                        </div>
                        <span className="text-[10px] text-slate-500 mt-0.5 px-1">{m.timestamp}</span>
                      </div>
                    );
                  })
                )}
                {loading && (
                  <div className="flex items-center space-x-1 text-slate-500 text-xs pl-2">
                    <span className="animate-bounce">●</span>
                    <span className="animate-bounce delay-100">●</span>
                    <span className="animate-bounce delay-200">●</span>
                  </div>
                )}
                <div ref={chatEndRef} />
              </div>

              {/* Input Bar */}
              <form onSubmit={handleSendMessage} className="pt-2 border-t border-slate-800 flex gap-2">
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
                      ? 'Enter 6-digit PIN (e.g. 441501)...'
                      : currentStep === 'VILLAGE'
                      ? 'Reply village number...'
                      : currentStep === 'CROP'
                      ? 'Reply crop number...'
                      : currentStep === 'CONSENT'
                      ? 'Reply YES to activate...'
                      : 'Type a reply...'
                  }
                  className="flex-1 bg-slate-950 border border-slate-700 rounded-xl px-3 py-2 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-sky-500"
                />
                <button
                  type="submit"
                  disabled={loading || !inputMessage.trim()}
                  className="px-3.5 py-2 bg-sky-600 hover:bg-sky-500 disabled:opacity-40 text-white rounded-xl text-xs font-semibold flex items-center justify-center transition-colors"
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
