import React, { useState, useEffect } from 'react';
import { Smartphone, MessageSquare, PhoneCall, Radio, Copy, Check, ShieldAlert, Volume2, VolumeX } from 'lucide-react';

interface FarmerMessageCardProps {
  farmerName?: string;
  phone?: string;
  village?: string;
  crop?: string;
  decision?: 'SOW_NOW' | 'SOW_PART_NOW' | 'WAIT';
  messageEn?: string;
  messageMr?: string;
  messageHi?: string;
}

export const FarmerMessageCard: React.FC<FarmerMessageCardProps> = ({
  farmerName = 'Ramesh Patil',
  phone = '+91 98220 12345',
  village = 'Kalmeshwar',
  crop = 'Soybean',
  decision = 'SOW_NOW',
  messageEn = 'Meghvani Advisory: Favorable monsoon onset conditions predicted for Kalmeshwar block. You may proceed with sowing Soybean. Ensure adequate seed-bed moisture (>75mm rainfall).',
  messageMr = 'मेघवाणी सल्ला: कळमेश्वर तालुक्यात समाधानकारक मान्सून आगमन स्थिती अपेक्षित आहे. सोयाबीनची पेरणी करण्यास हरकत नाही. जमिनीत किमान ७५-१०० मिमी ओलावा असल्याची खात्री करा.',
  messageHi = 'मेघवाणी कृषि सलाह: कलमेश्वर ब्लॉक में अनुकूल मानसून आगमन की संभावना है। आप सोयाबीन की बुवाई शुरू कर सकते हैं। खेत में पर्याप्त नमी सुनिश्चित करें।',
}) => {
  const [selectedLang, setSelectedLang] = useState<'mr' | 'hi' | 'en'>('mr');
  const [selectedChannel, setSelectedChannel] = useState<'sms' | 'whatsapp' | 'voice'>('whatsapp');
  const [copied, setCopied] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);

  const currentMessage = selectedLang === 'mr' ? messageMr : selectedLang === 'hi' ? messageHi : messageEn;

  // Cleanup speech synthesis on unmount or lang change
  useEffect(() => {
    return () => {
      if (typeof window !== 'undefined' && 'speechSynthesis' in window) {
        window.speechSynthesis.cancel();
      }
    };
  }, [selectedLang]);

  const handleCopy = () => {
    navigator.clipboard.writeText(currentMessage);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleSpeak = () => {
    if (typeof window === 'undefined' || !('speechSynthesis' in window)) {
      alert('Speech synthesis is not supported by your browser.');
      return;
    }

    if (isSpeaking) {
      window.speechSynthesis.cancel();
      setIsSpeaking(false);
      return;
    }

    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(currentMessage);
    utterance.lang = selectedLang === 'mr' ? 'mr-IN' : selectedLang === 'hi' ? 'hi-IN' : 'en-IN';
    utterance.rate = 0.9; // Slightly slower for agricultural clarity

    utterance.onend = () => setIsSpeaking(false);
    utterance.onerror = () => setIsSpeaking(false);

    setIsSpeaking(true);
    window.speechSynthesis.speak(utterance);
  };

  return (
    <div className="agri-card p-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-stone-200">
        <div className="flex items-center space-x-2.5">
          <div className="w-10 h-10 rounded-xl bg-forest-50 border border-forest-200 flex items-center justify-center text-forest-800">
            <Smartphone className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <h3 className="text-base font-bold text-stone-900 tracking-tight">Farmer Communication Card</h3>
              <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-amber-100 text-amber-900 border border-amber-300 uppercase tracking-wider">
                Simulated Delivery
              </span>
            </div>
            <p className="text-xs text-stone-600 mt-0.5">
              Localized agricultural advisory formatted for basic phones & smartphones.
            </p>
          </div>
        </div>

        {/* Language Tabs - Enhanced for >=44px Touch Targets */}
        <div className="flex items-center space-x-1.5 p-1 bg-stone-100 rounded-xl border border-stone-200 self-start sm:self-auto text-xs font-semibold">
          <button
            onClick={() => setSelectedLang('mr')}
            className={`min-h-[44px] px-4 py-2 rounded-lg transition-all flex items-center justify-center ${
              selectedLang === 'mr' ? 'bg-white text-forest-900 shadow-xs border border-stone-200 font-bold' : 'text-stone-700 hover:text-stone-900'
            }`}
          >
            मराठी (Marathi)
          </button>
          <button
            onClick={() => setSelectedLang('hi')}
            className={`min-h-[44px] px-4 py-2 rounded-lg transition-all flex items-center justify-center ${
              selectedLang === 'hi' ? 'bg-white text-forest-900 shadow-xs border border-stone-200 font-bold' : 'text-stone-700 hover:text-stone-900'
            }`}
          >
            हिंदी (Hindi)
          </button>
          <button
            onClick={() => setSelectedLang('en')}
            className={`min-h-[44px] px-4 py-2 rounded-lg transition-all flex items-center justify-center ${
              selectedLang === 'en' ? 'bg-white text-forest-900 shadow-xs border border-stone-200 font-bold' : 'text-stone-700 hover:text-stone-900'
            }`}
          >
            English
          </button>
        </div>
      </div>

      {/* Recipient Details & Channel Tabs */}
      <div className="mt-4 flex flex-col md:flex-row md:items-center justify-between gap-3 p-3 rounded-xl bg-stone-50 border border-stone-200/80 text-xs">
        <div className="flex flex-wrap items-center gap-3 text-stone-600">
          <span><strong>Farmer:</strong> {farmerName}</span>
          <span>•</span>
          <span><strong>Village:</strong> {village}</span>
          <span>•</span>
          <span><strong>Crop:</strong> {crop}</span>
          <span>•</span>
          <span><strong>Phone:</strong> {phone}</span>
        </div>

        <div className="flex items-center space-x-1 shrink-0">
          <button
            onClick={() => setSelectedChannel('whatsapp')}
            className={`min-h-[44px] px-3.5 py-2 rounded-lg text-xs font-semibold flex items-center space-x-1.5 border ${
              selectedChannel === 'whatsapp'
                ? 'bg-emerald-600 text-white border-emerald-600 shadow-xs'
                : 'bg-white text-stone-700 border-stone-200 hover:bg-stone-50'
            }`}
          >
            <MessageSquare className="w-4 h-4" />
            <span>WhatsApp</span>
          </button>
          <button
            onClick={() => setSelectedChannel('sms')}
            className={`min-h-[44px] px-3.5 py-2 rounded-lg text-xs font-semibold flex items-center space-x-1.5 border ${
              selectedChannel === 'sms'
                ? 'bg-sky-600 text-white border-sky-600 shadow-xs'
                : 'bg-white text-stone-700 border-stone-200 hover:bg-stone-50'
            }`}
          >
            <Radio className="w-4 h-4" />
            <span>SMS</span>
          </button>
          <button
            onClick={() => setSelectedChannel('voice')}
            className={`min-h-[44px] px-3.5 py-2 rounded-lg text-xs font-semibold flex items-center space-x-1.5 border ${
              selectedChannel === 'voice'
                ? 'bg-amber-600 text-white border-amber-600 shadow-xs'
                : 'bg-white text-stone-700 border-stone-200 hover:bg-stone-50'
            }`}
          >
            <PhoneCall className="w-4 h-4" />
            <span>Voice / IVR</span>
          </button>
        </div>
      </div>

      {/* Message Preview Box */}
      <div className="mt-4 relative rounded-xl border border-stone-200 bg-white p-4 shadow-inner">
        <div className="flex items-center justify-between pb-2 mb-2 border-b border-stone-100 text-[11px] text-stone-600">
          <span className="font-semibold uppercase tracking-wider text-forest-800">
            {selectedChannel === 'whatsapp' ? '💬 WhatsApp Advisory Format' : selectedChannel === 'sms' ? '📱 GSM 7-Bit SMS Payload' : '📞 Multilingual Voice Script'}
          </span>
          <div className="flex items-center gap-2">
            {/* Web Speech API Readout Button */}
            <button
              onClick={handleSpeak}
              className={`min-h-[44px] px-3 py-1.5 rounded-lg flex items-center space-x-1.5 text-xs font-semibold transition-all border ${
                isSpeaking
                  ? 'bg-rose-100 text-rose-800 border-rose-300 animate-pulse'
                  : 'bg-forest-50 text-forest-800 border-forest-200 hover:bg-forest-100'
              }`}
              title="Listen to advisory using Web Speech API"
            >
              {isSpeaking ? (
                <>
                  <VolumeX className="w-4 h-4 text-rose-600" />
                  <span>Stop Speech</span>
                </>
              ) : (
                <>
                  <Volume2 className="w-4 h-4 text-forest-700" />
                  <span>Read Aloud ({selectedLang === 'mr' ? 'ऐका' : selectedLang === 'hi' ? 'सुनिए' : 'Listen'})</span>
                </>
              )}
            </button>

            <button
              onClick={handleCopy}
              className="min-h-[44px] px-3 py-1.5 rounded-lg flex items-center space-x-1 text-stone-600 hover:text-stone-900 border border-stone-200 hover:bg-stone-50 transition-colors"
            >
              {copied ? <Check className="w-4 h-4 text-emerald-600" /> : <Copy className="w-4 h-4" />}
              <span>{copied ? 'Copied' : 'Copy'}</span>
            </button>
          </div>
        </div>

        <p className="text-sm text-stone-900 leading-relaxed font-sans whitespace-pre-wrap">
          {currentMessage}
        </p>

        {selectedChannel === 'voice' && (
          <div className="mt-3 p-2.5 rounded-lg bg-amber-50 border border-amber-200 text-[11px] text-amber-900 flex items-center space-x-2">
            <PhoneCall className="w-4 h-4 text-amber-700 shrink-0" />
            <span>
              Voice IVR audio generated with regional phonetic accents. Automated retry triggers SMS fallback if call is unanswered.
            </span>
          </div>
        )}
      </div>

      {/* Safety Notice */}
      <div className="mt-4 flex items-center space-x-2 text-[11px] text-stone-600 bg-stone-100/70 p-2.5 rounded-lg border border-stone-200/80">
        <ShieldAlert className="w-4 h-4 text-amber-600 shrink-0" />
        <span>
          <strong>Simulated Dispatch:</strong> External SMS/WhatsApp gateways are isolated (<code>external_dispatch = false</code>). No real telecom costs or dispatches are triggered.
        </span>
      </div>
    </div>
  );
};
