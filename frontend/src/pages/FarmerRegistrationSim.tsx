import React, { useState, useEffect, useRef } from 'react';
import { api } from '../services/api';
import { Block, Crop, Farmer, CommunicationGatewayStatus, VoiceAlertResponse } from '../types';
import {
  Smartphone,
  Send,
  PhoneCall,
  Phone,
  PhoneOff,
  RotateCcw,
  CheckCircle2,
  ShieldAlert,
  ArrowRight,
  Info,
  Check,
  Play,
  Pause,
  FastForward,
  RefreshCw,
  Radio,
  Layers,
  Sparkles,
  MapPin,
  Sprout,
  Clock,
  ExternalLink,
  ShieldCheck,
  Wifi,
  Signal,
  Battery,
  AlertTriangle,
  Volume2,
  VolumeX,
  Activity
} from 'lucide-react';

interface ChatMessage {
  id: string;
  sender: 'system' | 'farmer';
  text: string;
  timestamp: string;
  isCallNotification?: boolean;
}

type MobileScreenMode = 'SMS' | 'INCOMING_CALL' | 'CALL_ACTIVE';

export const FarmerRegistrationSim: React.FC = () => {
  // Mobile phone number for simulation
  const [phone, setPhone] = useState('+919876500001');
  const [inputMessage, setInputMessage] = useState('');
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [currentStep, setCurrentStep] = useState<string>('START');
  const [isCompleted, setIsCompleted] = useState<boolean>(false);
  const [registeredFarmerId, setRegisteredFarmerId] = useState<number | null>(null);
  const [farmerDetails, setFarmerDetails] = useState<Farmer | null>(null);
  const [gatewayStatus, setGatewayStatus] = useState<CommunicationGatewayStatus | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Auto-play / Presentation Walkthrough State
  const [isAutoPlaying, setIsAutoPlaying] = useState<boolean>(false);
  const [autoPlayIndex, setAutoPlayIndex] = useState<number>(0);
  const autoPlayTimerRef = useRef<any>(null);

  // Voice Alert Experience State
  const [screenMode, setScreenMode] = useState<MobileScreenMode>('SMS');
  const [voiceAlertData, setVoiceAlertData] = useState<VoiceAlertResponse | null>(null);
  const [voiceTriggerLoading, setVoiceTriggerLoading] = useState<boolean>(false);
  const [selectedVoiceLanguage, setSelectedVoiceLanguage] = useState<string>('mr');
  const [isCallPlaying, setIsCallPlaying] = useState<boolean>(false);
  const [callDuration, setCallDuration] = useState<number>(0);
  const callDurationTimerRef = useRef<any>(null);
  const audioElementRef = useRef<HTMLAudioElement | null>(null);
  const currentUtteranceRef = useRef<any>(null);

  // Audio Pipeline Diagnostics State (Section 16)
  const [audioDiagnostic, setAudioDiagnostic] = useState<{
    provider: string;
    model: string;
    language: string;
    speaker: string;
    audioReady: 'READY' | 'NOT READY';
    audioBytes: number;
    duration: number;
    html5AudioState: 'READY' | 'PLAYING' | 'PAUSED' | 'ENDED' | 'ERROR';
    error: string;
  }>({
    provider: 'None',
    model: 'bulbul:v3',
    language: 'mr-IN',
    speaker: 'shubh',
    audioReady: 'NOT READY',
    audioBytes: 0,
    duration: 0,
    html5AudioState: 'READY',
    error: 'None',
  });

  // Reference for scrolling chat container internally without affecting window scroll
  const chatContainerRef = useRef<HTMLDivElement>(null);

  // Auto-scroll chat container ONLY (does NOT scroll or jump the page window)
  useEffect(() => {
    if (chatContainerRef.current) {
      chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight;
    }
  }, [messages, loading]);

  // Load Communication Gateway Status on Mount
  useEffect(() => {
    const fetchStatus = async () => {
      try {
        const st = await api.getCommunicationStatus();
        setGatewayStatus(st);
      } catch (err) {
        console.warn('Could not load communication status:', err);
      }
    };
    fetchStatus();
  }, []);

  // When farmer is registered, fetch details from backend database
  useEffect(() => {
    if (registeredFarmerId) {
      api.getFarmer(registeredFarmerId)
        .then((f) => setFarmerDetails(f))
        .catch((err) => console.warn('Could not fetch farmer record:', err));
    }
  }, [registeredFarmerId]);

  // Cleanup audio & timer on unmount
  useEffect(() => {
    return () => {
      if (callDurationTimerRef.current) clearInterval(callDurationTimerRef.current);
      if (audioElementRef.current) {
        audioElementRef.current.pause();
        audioElementRef.current = null;
      }
      if (typeof window !== 'undefined' && 'speechSynthesis' in window) {
        window.speechSynthesis.cancel();
      }
    };
  }, []);

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

  // Helper to send message through existing backend API
  const executeMessage = async (msgText: string, isMissedCall = false) => {
    setLoading(true);
    setError(null);

    try {
      let res;
      if (isMissedCall) {
        addMessage('farmer', '[Missed Call placed to Meghvani Onboarding Number: 1800-MEGHVANI]', true);
        res = await api.simulateMissedCall(phone);
      } else if (msgText.toUpperCase() === 'MEGH' && messages.length === 0) {
        addMessage('farmer', 'MEGH');
        res = await api.startRegistration(phone);
      } else {
        addMessage('farmer', msgText);
        res = await api.sendRegistrationMessage(phone, msgText);
      }

      addMessage('system', res.reply_message);
      setCurrentStep(res.current_step);
      setIsCompleted(res.is_completed);
      if (res.registered_farmer_id) {
        setRegisteredFarmerId(res.registered_farmer_id);
      }
      return res;
    } catch (err: any) {
      const errMsg = err.message || 'Error processing message';
      setError(errMsg);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const handleStart = async (customPhone?: string) => {
    if (loading) return;
    const targetPhone = (customPhone || phone).trim();
    if (!targetPhone) return;

    handleReset();
    await executeMessage('MEGH');
  };

  const handleMissedCall = async () => {
    if (loading) return;
    handleReset();
    await executeMessage('', true);
  };

  const handleSendMessage = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    const msg = inputMessage.trim();
    if (!msg || loading) return;

    setInputMessage('');
    await executeMessage(msg);
  };

  const handleQuickReply = async (replyText: string) => {
    if (loading) return;
    setInputMessage('');
    await executeMessage(replyText);
  };

  const handleReset = () => {
    if (autoPlayTimerRef.current) {
      clearTimeout(autoPlayTimerRef.current);
      autoPlayTimerRef.current = null;
    }
    if (callDurationTimerRef.current) {
      clearInterval(callDurationTimerRef.current);
      callDurationTimerRef.current = null;
    }
    if (audioElementRef.current) {
      audioElementRef.current.pause();
      audioElementRef.current = null;
    }
    if (typeof window !== 'undefined' && 'speechSynthesis' in window) {
      window.speechSynthesis.cancel();
    }
    setIsAutoPlaying(false);
    setAutoPlayIndex(0);
    setScreenMode('SMS');
    setVoiceAlertData(null);
    setIsCallPlaying(false);
    setCallDuration(0);
    setMessages([]);
    setCurrentStep('START');
    setIsCompleted(false);
    setRegisteredFarmerId(null);
    setFarmerDetails(null);
    setInputMessage('');
    setError(null);
  };

  // Generate a random valid Indian mobile number for fresh judge demos
  const handleRandomizeNumber = () => {
    const randomSuffix = Math.floor(1000 + Math.random() * 9000);
    const newNum = `+9198765${randomSuffix}`;
    setPhone(newNum);
    handleReset();
    return newNum;
  };

  // Re-register the current phone number from Step 1 (deactivates existing profile in DB)
  const handleReRegister = async () => {
    if (loading) return;
    handleReset();
    setLoading(true);
    setError(null);
    try {
      addMessage('farmer', 'MEGH (Re-Register)');
      const res = await api.startRegistration(phone, true);
      addMessage('system', res.reply_message);
      setCurrentStep(res.current_step);
      setIsCompleted(res.is_completed);
      setRegisteredFarmerId(null);
      setFarmerDetails(null);
    } catch (err: any) {
      setError(err.message || 'Error re-registering farmer.');
    } finally {
      setLoading(false);
    }
  };

  // Generate a brand new phone number and start fresh onboarding
  const handleNewFarmerDemo = async () => {
    if (loading) return;
    const randomSuffix = Math.floor(1000 + Math.random() * 9000);
    const newNum = `+9198765${randomSuffix}`;
    setPhone(newNum);
    handleReset();
    setLoading(true);
    setError(null);
    try {
      addMessage('farmer', 'MEGH');
      const res = await api.startRegistration(newNum, false);
      addMessage('system', res.reply_message);
      setCurrentStep(res.current_step);
      setIsCompleted(res.is_completed);
      setRegisteredFarmerId(null);
      setFarmerDetails(null);
    } catch (err: any) {
      setError(err.message || 'Error starting new farmer demo.');
    } finally {
      setLoading(false);
    }
  };

  // -------------------------------------------------------------
  // AI VOICE ALERT TRIGGER & LIFECYCLE
  // -------------------------------------------------------------
  const handleTriggerVoiceAlert = async (languageOverride?: string) => {
    if (voiceTriggerLoading) return;
    setVoiceTriggerLoading(true);
    setError(null);

    try {
      const lang = languageOverride || selectedVoiceLanguage;
      const res = await api.triggerVoiceAlert({
        farmer_id: registeredFarmerId || undefined,
        language: lang,
        force_high_risk: true,
        alert_type: 'HEAVY_RAIN'
      });

      console.log("VOICE ALERT RESPONSE", {
        provider: res.provider,
        provider_label: res.provider_label,
        language: res.language,
        audio_content_exists: Boolean(res.audio_content),
        audio_content_length: res.audio_content?.length || 0,
        audio_format: res.audio_format || 'audio/wav',
        audio_bytes: res.audio_bytes || 0,
        speaker: res.speaker || 'shubh',
        model: res.model || 'bulbul:v3',
      });

      setVoiceAlertData(res);
      setCallDuration(0);
      setIsCallPlaying(false);

      setAudioDiagnostic(prev => ({
        ...prev,
        provider: res.provider === 'SARVAM_AI' ? 'Sarvam AI' : 'Demo Voice',
        model: res.model || 'bulbul:v3',
        language: res.language || 'mr-IN',
        speaker: res.speaker || 'shubh',
        audioReady: res.audio_content ? 'READY' : 'NOT READY',
        audioBytes: res.audio_bytes || (res.audio_content ? Math.floor(res.audio_content.length * 0.75) : 0),
        duration: 0,
        html5AudioState: 'READY',
        error: 'None',
      }));

      // Transition mobile screen to State B: INCOMING CALL
      setScreenMode('INCOMING_CALL');
    } catch (err: any) {
      setError(err.message || 'Failed to trigger AI voice alert.');
    } finally {
      setVoiceTriggerLoading(false);
    }
  };

  const setupAudioElement = (audioDataUri: string): HTMLAudioElement => {
    if (audioElementRef.current) {
      audioElementRef.current.pause();
      audioElementRef.current = null;
    }

    const audio = new Audio(audioDataUri);
    audioElementRef.current = audio;

    audio.onloadedmetadata = () => {
      console.log("VOICE AUDIO LOADED METADATA", {
        srcPreview: audio.src.slice(0, 50) + "...",
        duration: audio.duration,
      });
      setAudioDiagnostic(prev => ({
        ...prev,
        duration: Math.round(audio.duration || 0),
        audioReady: 'READY',
      }));
    };

    audio.oncanplay = () => {
      console.log("VOICE AUDIO CAN PLAY", { duration: audio.duration });
      setAudioDiagnostic(prev => ({ ...prev, html5AudioState: 'READY' }));
    };

    audio.onplay = () => {
      console.log("VOICE AUDIO PLAY (USER INITIATED)");
      setIsCallPlaying(true);
      setAudioDiagnostic(prev => ({ ...prev, html5AudioState: 'PLAYING' }));
    };

    audio.onplaying = () => {
      console.log("VOICE AUDIO PLAYING (AUDIBLE SOUND ACTIVE)");
      setIsCallPlaying(true);
      setAudioDiagnostic(prev => ({ ...prev, html5AudioState: 'PLAYING' }));
    };

    audio.onpause = () => {
      console.log("VOICE AUDIO PAUSED");
      setIsCallPlaying(false);
      setAudioDiagnostic(prev => ({ ...prev, html5AudioState: 'PAUSED' }));
    };

    audio.ontimeupdate = () => {
      setCallDuration(Math.floor(audio.currentTime));
    };

    audio.onended = () => {
      console.log("VOICE AUDIO ENDED");
      setIsCallPlaying(false);
      setAudioDiagnostic(prev => ({ ...prev, html5AudioState: 'ENDED' }));
      handleCallAudioFinished();
    };

    audio.onerror = (e) => {
      const errCode = audio.error?.code;
      const errMsg = audio.error?.message || `HTML5 Audio Error Code ${errCode}`;
      console.error("VOICE AUDIO ERROR", { code: errCode, message: errMsg, event: e });
      setIsCallPlaying(false);
      setAudioDiagnostic(prev => ({ ...prev, html5AudioState: 'ERROR', error: errMsg }));
    };

    audio.onwaiting = () => {
      console.log("VOICE AUDIO WAITING / BUFFERING");
    };

    audio.onstalled = () => {
      console.warn("VOICE AUDIO STALLED");
    };

    return audio;
  };

  const handleAnswerCall = async () => {
    if (!voiceAlertData) return;
    setScreenMode('CALL_ACTIVE');
    setCallDuration(0);

    // 1. Log answered event on backend
    try {
      await api.sendVoiceEvent({
        farmer_id: voiceAlertData.farmer_id,
        alert_id: voiceAlertData.alert_id || undefined,
        event: 'ANSWERED'
      });
    } catch (e) {
      console.warn('Voice answer event error:', e);
    }

    // 2. Play Audio directly within this user click interaction (Autoplay safe)
    if (voiceAlertData.audio_content) {
      try {
        const audio = setupAudioElement(voiceAlertData.audio_content);
        audio.load();
        const playPromise = audio.play();
        if (playPromise !== undefined) {
          await playPromise;
          console.log("HTML5 Audio play promise resolved successfully.");
        }
      } catch (err: any) {
        console.warn('Audio play error, falling back to speech synthesis:', err);
        setAudioDiagnostic(prev => ({ ...prev, html5AudioState: 'ERROR', error: err?.message || String(err) }));
        playBrowserSpeechFallback(voiceAlertData.advisory_text, voiceAlertData.language);
      }
    } else {
      // Browser Speech Synthesis Fallback
      playBrowserSpeechFallback(voiceAlertData.advisory_text, voiceAlertData.language);
    }
  };

  const playBrowserSpeechFallback = (text: string, langCode: string) => {
    if (typeof window === 'undefined' || !('speechSynthesis' in window)) {
      setIsCallPlaying(false);
      setAudioDiagnostic(prev => ({ ...prev, html5AudioState: 'ERROR', error: 'speechSynthesis not supported' }));
      return;
    }

    // Unpause if suspended
    if (window.speechSynthesis.paused) {
      window.speechSynthesis.resume();
    }
    window.speechSynthesis.cancel();

    const voices = window.speechSynthesis.getVoices();
    console.log("Available browser voices:", voices.map(v => `${v.name} (${v.lang})`));

    // Try finding an Indic voice (Marathi or Hindi)
    let selectedVoice = voices.find(v => v.lang.toLowerCase().includes('mr')) ||
                        voices.find(v => v.lang.toLowerCase().includes('hi'));

    let textToSpeak = text;
    let speechLang = langCode || 'mr-IN';

    // If NO Indic voice is installed on Windows (only English like David/Zira),
    // an English voice CANNOT speak Devanagari script (it drops it in 0.0 sec).
    // Therefore, speak the English farmer instruction aloud so the user can HEAR it!
    if (!selectedVoice) {
      const englishVoice = voices.find(v => v.lang.toLowerCase().includes('en-in')) ||
                           voices.find(v => v.lang.toLowerCase().startsWith('en')) ||
                           voices[0];
      if (englishVoice) {
        selectedVoice = englishVoice;
        speechLang = englishVoice.lang;
        textToSpeak = "Meghvani Weather Alert for your area. Heavy rainfall is expected. Do not sow seeds today. Wait until rainfall conditions stabilize.";
        console.log("No Indic voice on OS. Speaking English farmer warning aloud:", textToSpeak);
      }
    }

    const utterance = new SpeechSynthesisUtterance(textToSpeak);
    if (selectedVoice) {
      utterance.voice = selectedVoice;
      utterance.lang = selectedVoice.lang;
    } else {
      utterance.lang = speechLang;
    }
    utterance.rate = 0.95;
    utterance.pitch = 1.0;

    utterance.onstart = () => {
      console.log("Browser SpeechSynthesis started speaking (AUDIBLE). speaking =", window.speechSynthesis.speaking);
      setIsCallPlaying(true);
      setAudioDiagnostic(prev => ({ ...prev, html5AudioState: 'PLAYING' }));
    };

    utterance.onend = () => {
      console.log("Browser SpeechSynthesis completed.");
      if (callDurationTimerRef.current) clearInterval(callDurationTimerRef.current);
      setIsCallPlaying(false);
      setAudioDiagnostic(prev => ({ ...prev, html5AudioState: 'ENDED' }));
      handleCallAudioFinished();
    };

    utterance.onerror = (e) => {
      console.error("Browser SpeechSynthesis error:", e.error);
      if (callDurationTimerRef.current) clearInterval(callDurationTimerRef.current);
      setIsCallPlaying(false);
      setAudioDiagnostic(prev => ({ ...prev, html5AudioState: 'ERROR', error: e.error || 'speechSynthesis error' }));
    };

    // Keep alive in ref to avoid Chromium garbage collection
    currentUtteranceRef.current = utterance;

    // Delay slightly after cancel() to avoid Chromium cancel race condition
    setTimeout(() => {
      window.speechSynthesis.speak(utterance);
      console.log("Called window.speechSynthesis.speak. speaking =", window.speechSynthesis.speaking);
    }, 60);

    if (callDurationTimerRef.current) clearInterval(callDurationTimerRef.current);
    callDurationTimerRef.current = setInterval(() => {
      setCallDuration((prev) => prev + 1);
    }, 1000);
  };

  const handleCallAudioFinished = async () => {
    if (!voiceAlertData) return;
    try {
      await api.sendVoiceEvent({
        farmer_id: voiceAlertData.farmer_id,
        alert_id: voiceAlertData.alert_id || undefined,
        event: 'COMPLETED',
        duration_seconds: callDuration
      });
    } catch (e) {
      console.warn('Voice completion event error:', e);
    }
  };

  const handleTogglePlayPause = async () => {
    if (audioElementRef.current) {
      if (isCallPlaying) {
        audioElementRef.current.pause();
      } else {
        try {
          await audioElementRef.current.play();
        } catch (err: any) {
          console.warn('Audio play error:', err);
        }
      }
    } else if (voiceAlertData?.audio_content) {
      const audio = setupAudioElement(voiceAlertData.audio_content);
      audio.currentTime = callDuration;
      try {
        await audio.play();
      } catch (err: any) {
        console.warn('Audio play error:', err);
      }
    } else if (typeof window !== 'undefined' && 'speechSynthesis' in window) {
      if (isCallPlaying) {
        window.speechSynthesis.pause();
        if (callDurationTimerRef.current) clearInterval(callDurationTimerRef.current);
        setIsCallPlaying(false);
        setAudioDiagnostic(prev => ({ ...prev, html5AudioState: 'PAUSED' }));
      } else {
        if (window.speechSynthesis.paused) {
          window.speechSynthesis.resume();
          if (callDurationTimerRef.current) clearInterval(callDurationTimerRef.current);
          callDurationTimerRef.current = setInterval(() => {
            setCallDuration((prev) => prev + 1);
          }, 1000);
          setIsCallPlaying(true);
          setAudioDiagnostic(prev => ({ ...prev, html5AudioState: 'PLAYING' }));
        } else if (voiceAlertData) {
          playBrowserSpeechFallback(voiceAlertData.advisory_text, voiceAlertData.language);
        }
      }
    }
  };

  const handleReplayCall = async () => {
    if (!voiceAlertData) return;
    setCallDuration(0);

    try {
      await api.sendVoiceEvent({
        farmer_id: voiceAlertData.farmer_id,
        alert_id: voiceAlertData.alert_id || undefined,
        event: 'REPLAY'
      });
    } catch (e) {
      console.warn('Voice replay event error:', e);
    }

    if (audioElementRef.current) {
      audioElementRef.current.currentTime = 0;
      try {
        await audioElementRef.current.play();
      } catch (err: any) {
        console.warn('Audio replay error:', err);
      }
    } else if (voiceAlertData.audio_content) {
      const audio = setupAudioElement(voiceAlertData.audio_content);
      try {
        await audio.play();
      } catch (err: any) {
        console.warn('Audio replay error:', err);
      }
    } else {
      playBrowserSpeechFallback(voiceAlertData.advisory_text, voiceAlertData.language);
    }
  };

  const handleEndCall = async () => {
    if (callDurationTimerRef.current) clearInterval(callDurationTimerRef.current);
    if (audioElementRef.current) {
      audioElementRef.current.pause();
      audioElementRef.current = null;
    }
    if (typeof window !== 'undefined' && 'speechSynthesis' in window) {
      window.speechSynthesis.cancel();
    }

    setIsCallPlaying(false);
    setAudioDiagnostic(prev => ({ ...prev, html5AudioState: 'READY' }));

    if (voiceAlertData) {
      try {
        await api.sendVoiceEvent({
          farmer_id: voiceAlertData.farmer_id,
          alert_id: voiceAlertData.alert_id || undefined,
          event: 'COMPLETED',
          duration_seconds: callDuration
        });
      } catch (e) {}

      // Add call log record into SMS chat timeline
      const durationStr = `00:${callDuration < 10 ? '0' : ''}${callDuration}`;
      const providerBadge = voiceAlertData.provider === 'SARVAM_AI'
        ? '● AI VOICE — SARVAM BULBUL v3'
        : 'DEMO VOICE — SARVAM NOT CONNECTED';
      addMessage(
        'system',
        `📞 [Meghvani AI Voice Alert Completed — Duration: ${durationStr}]\n` +
        `Escalation: HIGH_RISK Weather Event (${voiceAlertData.alert_type})\n` +
        `Advisory: "${voiceAlertData.advisory_text}"\n` +
        `Status: Voice Alert Played (${providerBadge})`
      );
    }

    setScreenMode('SMS');
  };

  const handleDeclineCall = async () => {
    if (voiceAlertData) {
      try {
        await api.sendVoiceEvent({
          farmer_id: voiceAlertData.farmer_id,
          alert_id: voiceAlertData.alert_id || undefined,
          event: 'DECLINED'
        });
      } catch (e) {}

      addMessage(
        'system',
        `📞 [Meghvani Voice Call Declined by Farmer]\n` +
        `Automatic SMS fallback delivered: "${voiceAlertData.advisory_text}"`
      );
    }
    setScreenMode('SMS');
  };

  // -------------------------------------------------------------
  // DEMO / REPLAY SEQUENCE: Full Journey from MEGH -> STATUS
  // -------------------------------------------------------------
  const DEMO_SEQUENCE = [
    { label: '1. Initiate Onboarding (MEGH)', text: 'MEGH', wait: 1400 },
    { label: '2. Select Marathi (2)', text: '2', wait: 1400 },
    { label: '3. Enter PIN (441501)', text: '441501', wait: 1400 },
    { label: '4. Select Kalmeshwar (1)', text: '1', wait: 1400 },
    { label: '5. Select Soybean (1)', text: '1', wait: 1400 },
    { label: '6. Explicit Consent (YES)', text: 'YES', wait: 1600 },
    { label: '7. Query Advisory (STATUS)', text: 'STATUS', wait: 1600 },
  ];

  // Advance single step in Demo sequence
  const handleNextDemoStep = async () => {
    if (loading) return;
    if (autoPlayIndex >= DEMO_SEQUENCE.length) {
      return;
    }
    const stepObj = DEMO_SEQUENCE[autoPlayIndex];
    setAutoPlayIndex((prev) => prev + 1);
    await executeMessage(stepObj.text);
  };

  // Auto-play complete story with realistic pacing
  const handleToggleAutoPlay = () => {
    if (isAutoPlaying) {
      if (autoPlayTimerRef.current) clearTimeout(autoPlayTimerRef.current);
      setIsAutoPlaying(false);
    } else {
      setIsAutoPlaying(true);
      if (messages.length === 0 || currentStep === 'STATUS') {
        handleReset();
        setIsAutoPlaying(true);
        runAutoPlayStep(0);
      } else {
        runAutoPlayStep(autoPlayIndex);
      }
    }
  };

  const runAutoPlayStep = async (stepIdx: number) => {
    if (stepIdx >= DEMO_SEQUENCE.length) {
      setIsAutoPlaying(false);
      setAutoPlayIndex(DEMO_SEQUENCE.length);
      return;
    }

    const stepObj = DEMO_SEQUENCE[stepIdx];
    setAutoPlayIndex(stepIdx + 1);

    try {
      await executeMessage(stepObj.text);
      if (stepIdx + 1 < DEMO_SEQUENCE.length) {
        autoPlayTimerRef.current = setTimeout(() => {
          runAutoPlayStep(stepIdx + 1);
        }, stepObj.wait);
      } else {
        setIsAutoPlaying(false);
      }
    } catch (err) {
      setIsAutoPlaying(false);
    }
  };

  // Navigation to Alert Center
  const navigateToAlertCenter = () => {
    window.dispatchEvent(new CustomEvent('meghvani:navigate', { detail: { tab: 'alerts' } }));
  };

  // State machine step definitions
  const stepsList = [
    { key: 'LANGUAGE', label: '1. Language Select', icon: '🌐' },
    { key: 'PIN', label: '2. Postal PIN Code', icon: '📍' },
    { key: 'VILLAGE', label: '3. Village Identification', icon: '🏡' },
    { key: 'CROP', label: '4. Crop Classification', icon: '🌱' },
    { key: 'CONSENT', label: '5. Explicit Consent (DPDP)', icon: '🔒' },
    { key: 'COMPLETED', label: '6. Account Activated', icon: '✓' },
    { key: 'STATUS', label: '7. Dynamic Advisory (XAI)', icon: '🌧️' },
  ];

  return (
    <div className="space-y-6 pb-12">
      {/* Header Banner */}
      <div className="agri-card p-6 bg-white border-stone-200 shadow-xs">
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
          <div>
            <div className="flex items-center space-x-2.5">
              <span className="text-2xl p-2 rounded-xl bg-forest-50 border border-forest-200">📱</span>
              <div>
                <div className="flex items-center space-x-2">
                  <h2 className="text-xl sm:text-2xl font-black text-stone-900 tracking-tight">
                    Farmer Mobile Onboarding & AI Voice Alert
                  </h2>
                  <span className="text-[10px] font-black uppercase px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-900 border border-emerald-300">
                    Voice + SMS
                  </span>
                </div>
                <p className="text-xs text-stone-600 mt-0.5 max-w-2xl leading-relaxed">
                  Zero-smartphone conversational SMS interface running on Meghvani's real telecom state machine,
                  with automatic escalation to AI Voice Calls (Sarvam AI Bulbul v3) for HIGH-RISK monsoon events.
                </p>
              </div>
            </div>
          </div>

          <div className="flex flex-wrap items-center gap-2.5">
            {/* Gateway Status Badge */}
            <div className="flex items-center space-x-2 px-3 py-1.5 rounded-xl bg-stone-100 border border-stone-300 text-xs font-semibold text-stone-800">
              <span className={`w-2 h-2 rounded-full ${gatewayStatus?.is_live ? 'bg-emerald-500 animate-pulse' : 'bg-amber-500'}`} />
              <span>
                {gatewayStatus?.mode === 'LIVE SMS (TRIAL)'
                  ? 'Twilio Trial Gateway'
                  : gatewayStatus?.is_live
                  ? 'Live Twilio Gateway'
                  : 'Mock Telecom Provider'}
              </span>
            </div>

            {/* Jump to Alert Center */}
            <button
              type="button"
              onClick={navigateToAlertCenter}
              className="inline-flex items-center space-x-1.5 px-3 py-1.5 rounded-xl bg-stone-50 hover:bg-stone-100 text-stone-700 border border-stone-300 text-xs font-bold transition-all shadow-2xs"
              title="Open full audit log in Alert Center"
            >
              <Radio className="w-3.5 h-3.5 text-forest-700" />
              <span>Alert Center Audit</span>
              <ExternalLink className="w-3 h-3 text-stone-400" />
            </button>
          </div>
        </div>

        {/* DEMO / REPLAY CONTROL BAR */}
        <div className="mt-5 pt-4 border-t border-stone-100 flex flex-wrap items-center justify-between gap-3 bg-[#FBFBFA] p-3.5 rounded-2xl border border-stone-200/80">
          <div className="flex items-center space-x-2">
            <span className="text-xs font-extrabold text-stone-900 uppercase tracking-wider flex items-center gap-1.5">
              <Sparkles className="w-4 h-4 text-forest-700" />
              SIH Presentation Control:
            </span>
            <span className="text-[11px] text-stone-500 hidden sm:inline">
              Step {autoPlayIndex} of {DEMO_SEQUENCE.length} in SMS journey
            </span>
          </div>

          <div className="flex flex-wrap items-center gap-2">
            {/* Trigger Voice Alert (HIGH_RISK) */}
            <button
              type="button"
              onClick={() => handleTriggerVoiceAlert()}
              disabled={voiceTriggerLoading}
              className="inline-flex items-center space-x-1.5 px-3.5 py-1.5 rounded-xl bg-red-600 hover:bg-red-700 text-white text-xs font-bold transition-all shadow-xs disabled:opacity-50"
              title="Trigger high-risk voice escalation call to farmer"
            >
              <PhoneCall className="w-3.5 h-3.5 animate-pulse" />
              <span>{voiceTriggerLoading ? 'Generating Voice...' : 'Trigger Voice Alert (HIGH_RISK)'}</span>
            </button>

            <button
              type="button"
              onClick={handleToggleAutoPlay}
              disabled={loading && !isAutoPlaying}
              className={`inline-flex items-center space-x-1.5 px-3.5 py-1.5 rounded-xl text-xs font-bold transition-all shadow-xs ${
                isAutoPlaying
                  ? 'bg-amber-600 hover:bg-amber-700 text-white'
                  : 'bg-forest-800 hover:bg-forest-900 text-white'
              }`}
            >
              {isAutoPlaying ? <Pause className="w-3.5 h-3.5" /> : <Play className="w-3.5 h-3.5 fill-current" />}
              <span>{isAutoPlaying ? 'Pause Walkthrough' : 'Auto-Play SMS Journey'}</span>
            </button>

            <button
              type="button"
              onClick={handleNextDemoStep}
              disabled={loading || isAutoPlaying || autoPlayIndex >= DEMO_SEQUENCE.length}
              className="inline-flex items-center space-x-1 px-3 py-1.5 rounded-xl bg-white hover:bg-stone-100 text-stone-800 border border-stone-300 text-xs font-bold transition-colors disabled:opacity-40 shadow-2xs"
            >
              <span>Next Step</span>
              <FastForward className="w-3.5 h-3.5 text-forest-700" />
            </button>

            <button
              type="button"
              onClick={handleNewFarmerDemo}
              disabled={loading}
              className="inline-flex items-center space-x-1.5 px-3 py-1.5 rounded-xl bg-forest-100 hover:bg-forest-200 text-forest-900 border border-forest-300 text-xs font-bold transition-colors shadow-2xs"
              title="Generate a brand new phone number and start onboarding from scratch"
            >
              <Sparkles className="w-3.5 h-3.5 text-forest-700" />
              <span>New Farmer Demo</span>
            </button>

            <button
              type="button"
              onClick={handleReset}
              className="inline-flex items-center space-x-1 px-3 py-1.5 rounded-xl bg-white hover:bg-stone-100 text-stone-700 border border-stone-300 text-xs font-semibold transition-colors shadow-2xs"
              title="Reset conversation state"
            >
              <RotateCcw className="w-3.5 h-3.5" />
              <span>Reset</span>
            </button>
          </div>
        </div>
      </div>

      {/* Main Grid: Left Controls & State / Right Mobile Phone Mockup */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
        {/* Left Column (5 cols): Controls, Routing Matrix & State Visualizer */}
        <div className="lg:col-span-5 space-y-6">
          {/* AI Voice Alert Escalation Control Card */}
          <div className="agri-card p-5 bg-white border-stone-200 space-y-4">
            <div className="flex items-center justify-between pb-2.5 border-b border-stone-100">
              <h3 className="font-bold text-stone-900 text-sm flex items-center gap-1.5">
                <Volume2 className="w-4 h-4 text-red-600" />
                AI Voice Alert Simulation
              </h3>
              <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-red-100 text-red-800 border border-red-300">
                HIGH_RISK Trigger
              </span>
            </div>

            <p className="text-xs text-stone-600 leading-relaxed">
              When extreme rainfall or severe false onset risk is detected, Meghvani escalates communication from standard SMS to an interactive <strong>AI Voice Call</strong> in the farmer's native language.
            </p>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-xs">
              <div>
                <label className="text-[11px] font-semibold text-stone-700 block mb-1">
                  Advisory Language
                </label>
                <select
                  value={selectedVoiceLanguage}
                  onChange={(e) => setSelectedVoiceLanguage(e.target.value)}
                  className="w-full px-2.5 py-1.5 bg-stone-50 border border-stone-300 rounded-lg text-xs text-stone-800 focus:outline-none focus:border-forest-600 font-medium"
                >
                  <option value="mr">Marathi (मराठी) - Primary</option>
                  <option value="hi">Hindi (हिन्दी)</option>
                  <option value="kn">Kannada (ಕನ್ನಡ)</option>
                  <option value="en">English (en-IN)</option>
                </select>
              </div>

              <div>
                <label className="text-[11px] font-semibold text-stone-700 block mb-1">
                  Voice Model
                </label>
                <div className="px-2.5 py-1.5 bg-stone-100 border border-stone-200 rounded-lg text-xs font-mono font-bold text-stone-700 truncate">
                  Sarvam Bulbul v3
                </div>
              </div>
            </div>

            <div className="pt-1">
              <button
                type="button"
                onClick={() => handleTriggerVoiceAlert()}
                disabled={voiceTriggerLoading}
                className="w-full inline-flex items-center justify-center space-x-2 px-4 py-2.5 rounded-xl bg-red-600 hover:bg-red-700 text-white font-bold text-xs shadow-sm transition-all disabled:opacity-50"
              >
                <PhoneCall className="w-4 h-4 animate-bounce" />
                <span>Simulate Incoming Voice Alert</span>
              </button>
            </div>

            {/* VOICE ADVISORY PREVIEW & VERIFICATION CARD */}
            {voiceAlertData && (
              <div className="p-3.5 bg-stone-50 rounded-xl border border-stone-200 space-y-2 text-xs animate-fadeIn">
                <div className="flex items-center justify-between border-b border-stone-200 pb-1.5">
                  <span className="font-extrabold uppercase tracking-wider text-forest-900 text-[11px] flex items-center gap-1.5">
                    <Volume2 className="w-3.5 h-3.5 text-forest-700" />
                    VOICE ADVISORY
                  </span>
                  <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
                    voiceAlertData.audio_content ? 'bg-emerald-100 text-emerald-800 border border-emerald-200' : 'bg-amber-100 text-amber-800 border border-amber-200'
                  }`}>
                    Audio: {voiceAlertData.audio_content ? 'Ready' : (voiceAlertData.provider === 'SARVAM_AI' ? 'Ready' : 'Browser Ready')}
                  </span>
                </div>

                <div className="grid grid-cols-2 gap-2 text-[11px]">
                  <div>
                    <span className="text-[10px] text-stone-500 font-medium block">Language:</span>
                    <span className="font-bold text-stone-800">{voiceAlertData.language_name}</span>
                  </div>
                  <div>
                    <span className="text-[10px] text-stone-500 font-medium block">Alert:</span>
                    <span className="font-bold text-stone-800">{voiceAlertData.alert_type === 'HEAVY_RAIN' ? 'Heavy Rain' : voiceAlertData.alert_type}</span>
                  </div>
                  <div>
                    <span className="text-[10px] text-stone-500 font-medium block">Risk:</span>
                    <span className="font-bold text-red-600 font-mono">{voiceAlertData.risk_level}</span>
                  </div>
                  <div>
                    <span className="text-[10px] text-stone-500 font-medium block">Provider:</span>
                    <span className="font-bold text-stone-800">{voiceAlertData.provider === 'SARVAM_AI' ? 'Sarvam AI' : 'Demo Voice'}</span>
                  </div>
                  <div>
                    <span className="text-[10px] text-stone-500 font-medium block">Model:</span>
                    <span className="font-mono text-stone-700">{voiceAlertData.model === 'bulbul:v3' ? 'Bulbul v3' : voiceAlertData.model}</span>
                  </div>
                  <div>
                    <span className="text-[10px] text-stone-500 font-medium block">Speaker:</span>
                    <span className="font-mono text-stone-700 font-semibold">{voiceAlertData.speaker || 'shubh'} ({voiceAlertData.speech_sample_rate ? `${voiceAlertData.speech_sample_rate / 1000}kHz` : '24kHz'})</span>
                  </div>
                </div>

                <div className="pt-1 border-t border-stone-200">
                  <span className="text-[10px] text-stone-500 font-medium block mb-1">Spoken Advisory:</span>
                  <p className="p-2.5 bg-white border border-stone-200 rounded-lg text-stone-900 font-medium leading-relaxed italic text-xs">
                    "{voiceAlertData.advisory_text}"
                  </p>
                </div>

                {/* VOICE AUDIO DIAGNOSTICS PANEL (Sections 9 & 16) */}
                <div className="mt-3 p-3 bg-stone-900 text-stone-100 rounded-lg border border-stone-800 space-y-2 text-xs font-mono">
                  <div className="flex items-center justify-between border-b border-stone-800 pb-1.5">
                    <span className="font-extrabold uppercase tracking-wider text-amber-400 text-[10px] flex items-center gap-1.5">
                      <Activity className="w-3.5 h-3.5 text-amber-400" />
                      VOICE AUDIO DIAGNOSTICS
                    </span>
                    <span className="text-[9px] px-1.5 py-0.5 rounded bg-stone-800 text-stone-300 font-bold">
                      DEBUG
                    </span>
                  </div>

                  <div className="grid grid-cols-2 gap-x-2 gap-y-1 text-[10px]">
                    <div>
                      <span className="text-stone-400 block text-[9px]">Provider:</span>
                      <span className="font-bold text-white">{audioDiagnostic.provider !== 'None' ? audioDiagnostic.provider : (voiceAlertData.provider === 'SARVAM_AI' ? 'Sarvam AI' : 'Demo Voice')}</span>
                    </div>
                    <div>
                      <span className="text-stone-400 block text-[9px]">Model:</span>
                      <span className="font-bold text-white">{audioDiagnostic.model || 'bulbul:v3'}</span>
                    </div>
                    <div>
                      <span className="text-stone-400 block text-[9px]">Language:</span>
                      <span className="font-bold text-white">{audioDiagnostic.language || 'mr-IN'}</span>
                    </div>
                    <div>
                      <span className="text-stone-400 block text-[9px]">Speaker:</span>
                      <span className="font-bold text-white">{audioDiagnostic.speaker || 'shubh'}</span>
                    </div>
                    <div>
                      <span className="text-stone-400 block text-[9px]">Audio:</span>
                      <span className={`font-bold ${audioDiagnostic.audioReady === 'READY' ? 'text-emerald-400' : 'text-amber-400'}`}>
                        {audioDiagnostic.audioReady}
                      </span>
                    </div>
                    <div>
                      <span className="text-stone-400 block text-[9px]">Audio bytes:</span>
                      <span className="font-bold text-white">{audioDiagnostic.audioBytes > 0 ? `${audioDiagnostic.audioBytes.toLocaleString()} B` : (voiceAlertData.audio_bytes ? `${voiceAlertData.audio_bytes.toLocaleString()} B` : '0 B')}</span>
                    </div>
                    <div>
                      <span className="text-stone-400 block text-[9px]">Duration:</span>
                      <span className="font-bold text-white">{audioDiagnostic.duration > 0 ? `${audioDiagnostic.duration} sec` : (callDuration > 0 ? `${callDuration} sec` : '--')}</span>
                    </div>
                    <div>
                      <span className="text-stone-400 block text-[9px]">HTML5 Audio:</span>
                      <span className={`font-bold ${
                        audioDiagnostic.html5AudioState === 'PLAYING'
                          ? 'text-emerald-400'
                          : audioDiagnostic.html5AudioState === 'ERROR'
                          ? 'text-red-400'
                          : 'text-sky-300'
                      }`}>
                        {audioDiagnostic.html5AudioState}
                      </span>
                    </div>
                  </div>

                  <div className="pt-1 border-t border-stone-800 text-[9px] flex items-center justify-between text-stone-400">
                    <span>AUDIO SOURCE:</span>
                    <span className="font-semibold text-stone-200 truncate max-w-[150px]">
                      {voiceAlertData.audio_content ? 'data:audio/wav;base64,...' : 'Browser TTS (speechSynthesis)'}
                    </span>
                  </div>

                  {audioDiagnostic.error !== 'None' && (
                    <div className="pt-1 text-[9px] text-red-400 border-t border-stone-800">
                      Error: {audioDiagnostic.error}
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>

          {/* 3-Tier Communication Routing Matrix Card */}
          <div className="agri-card p-5 bg-white border-stone-200 space-y-3">
            <div className="flex items-center justify-between pb-2 border-b border-stone-100">
              <h3 className="font-bold text-stone-900 text-xs uppercase tracking-wider flex items-center gap-1.5">
                <Layers className="w-3.5 h-3.5 text-forest-700" />
                Communication Routing Architecture
              </h3>
              <span className="text-[10px] text-stone-500 font-mono">Multi-Channel</span>
            </div>

            <div className="space-y-2 text-xs">
              <div className="flex items-center justify-between p-2 rounded-lg bg-stone-50 border border-stone-200">
                <div className="flex items-center space-x-2">
                  <span className="w-2 h-2 rounded-full bg-emerald-500" />
                  <span className="font-bold text-stone-800">NORMAL</span>
                  <span className="text-[10px] text-stone-500">(Prob &lt; 0.50)</span>
                </div>
                <span className="font-mono text-[10px] font-bold text-stone-700 px-2 py-0.5 rounded bg-stone-200/70">
                  SMS
                </span>
              </div>

              <div className="flex items-center justify-between p-2 rounded-lg bg-amber-50/60 border border-amber-200">
                <div className="flex items-center space-x-2">
                  <span className="w-2 h-2 rounded-full bg-amber-500" />
                  <span className="font-bold text-amber-900">IMPORTANT</span>
                  <span className="text-[10px] text-amber-700">(0.50 ≤ P &lt; 0.75)</span>
                </div>
                <span className="font-mono text-[10px] font-bold text-amber-900 px-2 py-0.5 rounded bg-amber-200/70">
                  SMS + WhatsApp
                </span>
              </div>

              <div className="flex items-center justify-between p-2 rounded-lg bg-red-50/80 border border-red-300 shadow-2xs">
                <div className="flex items-center space-x-2">
                  <span className="w-2 h-2 rounded-full bg-red-600 animate-ping" />
                  <span className="font-extrabold text-red-900">HIGH_RISK</span>
                  <span className="text-[10px] text-red-700">(Prob ≥ 0.75)</span>
                </div>
                <span className="font-mono text-[10px] font-extrabold text-white px-2 py-0.5 rounded bg-red-700 shadow-2xs">
                  VOICE + SMS
                </span>
              </div>
            </div>
          </div>

          {/* State Machine Progress Tracker */}
          <div className="agri-card p-5 bg-white border-stone-200 space-y-3.5">
            <div className="flex items-center justify-between pb-2 border-b border-stone-100">
              <h3 className="font-bold text-stone-900 text-sm flex items-center gap-1.5">
                <Clock className="w-4 h-4 text-forest-700" />
                Registration State Machine
              </h3>
              <span className="text-[10px] font-mono px-2 py-0.5 rounded-md bg-stone-100 text-stone-700 font-bold">
                {currentStep}
              </span>
            </div>

            <div className="space-y-1.5">
              {stepsList.map((st, idx) => {
                const isCurrent = currentStep === st.key;
                const isPast =
                  isCompleted ||
                  (idx < stepsList.findIndex((s) => s.key === currentStep) &&
                    currentStep !== 'START');

                return (
                  <div
                    key={st.key}
                    className={`flex items-center justify-between p-2 rounded-xl text-xs transition-all ${
                      isCurrent
                        ? 'bg-forest-50 border border-forest-300 text-forest-900 font-bold shadow-2xs'
                        : isPast
                        ? 'bg-emerald-50/70 border border-emerald-200 text-emerald-800 font-semibold'
                        : 'bg-stone-50 border border-stone-200/80 text-stone-400'
                    }`}
                  >
                    <div className="flex items-center space-x-2">
                      <span className="text-xs">{st.icon}</span>
                      <span>{st.label}</span>
                    </div>
                    {isPast ? (
                      <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                    ) : isCurrent ? (
                      <span className="w-2 h-2 rounded-full bg-forest-600 animate-pulse" />
                    ) : (
                      <span className="w-1.5 h-1.5 rounded-full bg-stone-300" />
                    )}
                  </div>
                );
              })}
            </div>
          </div>

          {/* Live Farmer Record Telemetry (From Backend Database) */}
          <div className="agri-card p-5 bg-white border-stone-200 space-y-3">
            <div className="flex items-center justify-between border-b border-stone-100 pb-2">
              <div className="flex items-center gap-1.5">
                <Sprout className="w-4 h-4 text-forest-700" />
                <h4 className="font-bold text-stone-900 text-xs uppercase tracking-wider">
                  Live Farmer Profile in Database
                </h4>
              </div>
              <span className="text-[10px] font-bold text-forest-800 bg-forest-50 px-2 py-0.5 rounded-full border border-forest-200">
                {registeredFarmerId ? `Record #${registeredFarmerId}` : 'Not Activated'}
              </span>
            </div>

            {registeredFarmerId ? (
              <div className="space-y-2 text-xs">
                <div className="grid grid-cols-2 gap-2">
                  <div className="p-2.5 rounded-lg bg-stone-50 border border-stone-200">
                    <span className="text-[10px] text-stone-500 font-medium block">Phone (Masked)</span>
                    <span className="font-mono font-bold text-stone-900">
                      {farmerDetails?.phone_number_masked || '******0001'}
                    </span>
                  </div>
                  <div className="p-2.5 rounded-lg bg-stone-50 border border-stone-200">
                    <span className="text-[10px] text-stone-500 font-medium block">Language</span>
                    <span className="font-bold text-forest-900">
                      {farmerDetails?.preferred_language === 'mr' ? 'Marathi (मराठी)' : farmerDetails?.preferred_language || 'Marathi'}
                    </span>
                  </div>
                  <div className="p-2.5 rounded-lg bg-stone-50 border border-stone-200">
                    <span className="text-[10px] text-stone-500 font-medium block">Village / PIN</span>
                    <span className="font-bold text-stone-900">
                      Kalmeshwar (441501)
                    </span>
                  </div>
                  <div className="p-2.5 rounded-lg bg-stone-50 border border-stone-200">
                    <span className="text-[10px] text-stone-500 font-medium block">Crop Category</span>
                    <span className="font-bold text-forest-900">Soybean (सोयाबीन)</span>
                  </div>
                </div>

                <div className="p-2.5 rounded-lg bg-emerald-50 border border-emerald-200 text-emerald-900 flex items-center justify-between text-[11px]">
                  <span className="font-semibold flex items-center gap-1">
                    <ShieldCheck className="w-3.5 h-3.5 text-emerald-700" />
                    Explicit Consent Verified
                  </span>
                  <span className="font-mono text-[10px] text-emerald-800">DPDP Compliant</span>
                </div>

                <div className="pt-2 border-t border-stone-200 flex items-center justify-between gap-2">
                  <button
                    type="button"
                    onClick={handleReRegister}
                    className="inline-flex items-center space-x-1 px-2.5 py-1.5 rounded-lg bg-forest-800 hover:bg-forest-900 text-white text-[11px] font-bold shadow-2xs transition-colors"
                    title="Deactivate this profile and re-register from Step 1"
                  >
                    <RotateCcw className="w-3 h-3" />
                    <span>Register Again</span>
                  </button>
                  <button
                    type="button"
                    onClick={handleNewFarmerDemo}
                    className="inline-flex items-center space-x-1 px-2.5 py-1.5 rounded-lg bg-stone-100 hover:bg-stone-200 text-stone-800 border border-stone-300 text-[11px] font-semibold shadow-2xs transition-colors"
                    title="Generate a brand new phone number for fresh registration demo"
                  >
                    <Sparkles className="w-3 h-3 text-forest-700" />
                    <span>New Number Demo</span>
                  </button>
                </div>
              </div>
            ) : (
              <div className="p-3.5 rounded-xl bg-stone-50 border border-dashed border-stone-200 text-center text-xs text-stone-500">
                Complete the conversational flow or click <strong>Trigger Voice Alert</strong> to demonstrate the farmer profile.
              </div>
            )}
          </div>
        </div>

        {/* Right Column (7 cols): Visual Mobile Phone Mockup */}
        <div className="lg:col-span-7 flex justify-center">
          <div className="w-full max-w-[400px] sm:max-w-[420px] bg-stone-900 rounded-[3rem] border-[8px] border-stone-800 p-2.5 shadow-2xl relative flex flex-col ring-1 ring-stone-700/60">
            {/* Phone Speaker & Dynamic Island Notch */}
            <div className="absolute top-4 left-1/2 -translate-x-1/2 w-28 h-4 bg-stone-800 rounded-full z-30 flex items-center justify-center space-x-2">
              <div className="w-2.5 h-2.5 rounded-full bg-stone-950" />
              <div className="w-8 h-1 bg-stone-900 rounded-full" />
            </div>

            {/* Phone Screen Container */}
            <div className="bg-[#FAF9F5] rounded-[2.2rem] pt-8 pb-3 px-3.5 h-[620px] flex flex-col justify-between border border-stone-300 relative overflow-hidden">
              
              {/* TOP STATUS BAR (As in prompt mockup: Meghvani  2:14 PM) */}
              <div className="flex items-center justify-between px-2 pt-1 pb-2 border-b border-stone-200/80 text-[11px] font-semibold text-stone-700">
                <div className="flex items-center space-x-1.5">
                  <span className="font-bold tracking-tight text-stone-900">Meghvani</span>
                  <Signal className="w-3 h-3 text-stone-600" />
                  <Wifi className="w-3 h-3 text-stone-600" />
                </div>
                <div className="flex items-center space-x-1.5">
                  <span className="font-mono font-bold text-stone-800">2:14 PM</span>
                  <div className="w-4 h-2 rounded-xs border border-stone-600 p-0.5 flex items-center">
                    <div className="w-full h-full bg-emerald-600 rounded-2xs" />
                  </div>
                </div>
              </div>

              {/* ========================================================= */}
              {/* STATE B: INCOMING CALL INTERFACE                           */}
              {/* ========================================================= */}
              {screenMode === 'INCOMING_CALL' && (
                <div className="flex-1 flex flex-col justify-between py-6 px-4 text-center animate-fadeIn">
                  <div className="space-y-4 pt-6">
                    <div>
                      <h3 className="text-2xl font-black text-stone-900 tracking-tight">Meghvani</h3>
                      <div className="inline-flex items-center space-x-1.5 px-3 py-1 rounded-full bg-red-50 border border-red-200 text-red-700 text-xs font-bold mt-2 shadow-2xs">
                        <span>🌧️</span>
                        <span>Weather Alert</span>
                      </div>
                    </div>

                    <div className="pt-3">
                      <span className="text-xs font-semibold text-stone-500 uppercase tracking-wider block">
                        Incoming Call
                      </span>
                    </div>

                    {/* Subtle Incoming Call Pulse Animation */}
                    <div className="relative py-6 flex justify-center items-center">
                      <div className="absolute w-24 h-24 rounded-full bg-forest-600/10 animate-ping opacity-75" />
                      <div className="absolute w-20 h-20 rounded-full bg-forest-600/15 animate-pulse" />
                      <div className="relative z-10 w-16 h-16 rounded-full bg-forest-800 text-white flex items-center justify-center text-2xl shadow-md border-2 border-white">
                        <Volume2 className="w-7 h-7 text-white" />
                      </div>
                    </div>

                    <div className="bg-stone-50/80 p-3 rounded-xl border border-stone-200 text-xs text-stone-700 max-w-[280px] mx-auto">
                      <span className="font-extrabold text-stone-900 text-sm block">"Meghvani Alert"</span>
                      <span className="block text-[11px] text-stone-500 mt-0.5">
                        {voiceAlertData?.village || 'Kalmeshwar'} • {voiceAlertData?.crop || 'Soybean'}
                      </span>
                    </div>
                  </div>

                  {/* Accept / Decline Action Buttons */}
                  <div className="pb-4 pt-6 flex items-center justify-around px-4">
                    <button
                      type="button"
                      onClick={handleDeclineCall}
                      className="flex flex-col items-center space-y-1.5 group cursor-pointer"
                    >
                      <div className="w-14 h-14 rounded-full bg-red-600 hover:bg-red-700 text-white flex items-center justify-center shadow-md transition-all group-hover:scale-105 active:scale-95">
                        <PhoneOff className="w-6 h-6" />
                      </div>
                      <span className="text-xs font-bold text-stone-700">Decline</span>
                    </button>

                    <button
                      type="button"
                      onClick={handleAnswerCall}
                      className="flex flex-col items-center space-y-1.5 group cursor-pointer"
                    >
                      <div className="w-14 h-14 rounded-full bg-emerald-600 hover:bg-emerald-700 text-white flex items-center justify-center shadow-md transition-all group-hover:scale-105 active:scale-95 animate-pulse">
                        <Phone className="w-6 h-6" />
                      </div>
                      <span className="text-xs font-bold text-emerald-800">Answer</span>
                    </button>
                  </div>
                </div>
              )}

              {/* ========================================================= */}
              {/* STATE C: ACTIVE CALL & VOICE ADVISORY PLAYBACK             */}
              {/* ========================================================= */}
              {screenMode === 'CALL_ACTIVE' && (
                <div className="flex-1 flex flex-col justify-between py-3 px-2 text-center animate-fadeIn overflow-y-auto">
                  <div className="space-y-2.5">
                    <div>
                      <h3 className="text-base font-black text-stone-900">Meghvani</h3>
                      <div className="flex items-center justify-center space-x-1.5 mt-0.5">
                        <span className={`w-2 h-2 rounded-full ${isCallPlaying ? 'bg-emerald-500 animate-pulse' : 'bg-stone-400'}`} />
                        <span className="text-xs font-extrabold text-forest-900">AI Voice Alert</span>
                      </div>
                    </div>

                    {/* Sarvam Provider & Disclaimer Badge */}
                    <div className="inline-flex items-center space-x-1.5 px-3 py-1 rounded-full bg-stone-100 border border-stone-200 text-[10px] font-semibold text-stone-700">
                      <span className={`w-1.5 h-1.5 rounded-full ${voiceAlertData?.provider === 'SARVAM_AI' ? 'bg-emerald-600' : 'bg-amber-500'}`} />
                      <span>
                        {voiceAlertData?.provider === 'SARVAM_AI'
                          ? '● AI VOICE — SARVAM BULBUL v3'
                          : 'DEMO VOICE — SARVAM NOT CONNECTED'}
                      </span>
                    </div>

                    {/* Animated Audio Waveform */}
                    <div className="py-1">
                      <div className="flex items-center justify-center space-x-1.5 h-10 py-1">
                        {[40, 75, 95, 60, 85, 50, 70].map((h, i) => (
                          <div
                            key={i}
                            className={`w-1.5 rounded-full transition-all duration-300 ${
                              isCallPlaying ? 'bg-forest-700 animate-pulse' : 'bg-stone-300'
                            }`}
                            style={{
                              height: isCallPlaying ? `${h}%` : '20%',
                              animationDelay: `${i * 120}ms`,
                            }}
                          />
                        ))}
                      </div>
                      <span className="text-xs font-mono font-bold text-stone-600">
                        00:{callDuration < 10 ? '0' : ''}{callDuration}
                      </span>
                    </div>

                    {/* Audio Controls */}
                    <div className="flex items-center justify-center space-x-3 pt-0.5">
                      <button
                        type="button"
                        onClick={handleTogglePlayPause}
                        className="px-3 py-1.5 rounded-xl bg-forest-800 hover:bg-forest-900 text-white text-xs font-bold flex items-center space-x-1.5 shadow-2xs"
                      >
                        {isCallPlaying ? <Pause className="w-3.5 h-3.5" /> : <Play className="w-3.5 h-3.5 fill-current" />}
                        <span>{isCallPlaying ? 'Pause' : 'Play'}</span>
                      </button>

                      <button
                        type="button"
                        onClick={handleReplayCall}
                        className="px-3 py-1.5 rounded-xl bg-white hover:bg-stone-100 text-stone-800 border border-stone-300 text-xs font-bold flex items-center space-x-1 shadow-2xs"
                        title="Replay from audio cache"
                      >
                        <RotateCcw className="w-3.5 h-3.5" />
                        <span>Replay</span>
                      </button>
                    </div>

                    {/* WHAT THE FARMER HEARS Section */}
                    <div className="agri-card p-3 bg-white border-stone-200 text-left space-y-2.5 shadow-2xs">
                      <div className="flex items-center justify-between border-b border-stone-100 pb-1.5">
                        <span className="text-[10px] font-black uppercase tracking-wider text-forest-900 flex items-center gap-1">
                          <Volume2 className="w-3.5 h-3.5 text-forest-700" />
                          WHAT THE FARMER HEARS
                        </span>
                        <span className="text-[9px] font-bold px-1.5 py-0.5 rounded bg-red-100 text-red-800">
                          {voiceAlertData?.risk_level || 'HIGH'} RISK ({voiceAlertData?.probability_pct ?? 82}%)
                        </span>
                      </div>

                      {/* Prominent spoken warning quote */}
                      <div className="p-2.5 bg-stone-50 rounded-lg border border-stone-200">
                        <p className="text-xs text-stone-900 font-bold leading-relaxed">
                          "{voiceAlertData?.advisory_text || 'तुमच्या भागात मुसळधार पावसाची शक्यता आहे. आज पेरणी करू नका. पावसाची परिस्थिती स्थिर होईपर्यंत थांबा.'}"
                        </p>
                      </div>

                      <div className="grid grid-cols-2 gap-1.5 text-[10px] pt-0.5 text-stone-600 border-t border-stone-100">
                        <div>
                          <span className="text-stone-400 block font-medium">Language</span>
                          <span className="font-bold text-stone-800">
                            {voiceAlertData?.language_name || 'Marathi'} ({voiceAlertData?.language || 'mr-IN'})
                          </span>
                        </div>
                        <div>
                          <span className="text-stone-400 block font-medium">Alert / Crop</span>
                          <span className="font-bold text-stone-800">
                            {voiceAlertData?.alert_type || 'HEAVY_RAIN'} · {voiceAlertData?.crop_localized || voiceAlertData?.crop || 'Soybean'}
                          </span>
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* End Call Button */}
                  <div className="pt-2">
                    <button
                      type="button"
                      onClick={handleEndCall}
                      className="w-full inline-flex items-center justify-center space-x-2 py-2.5 rounded-xl bg-red-600 hover:bg-red-700 text-white font-bold text-xs shadow-xs"
                    >
                      <PhoneOff className="w-4 h-4" />
                      <span>End Call</span>
                    </button>
                  </div>
                </div>
              )}

              {/* ========================================================= */}
              {/* STATE A: NORMAL SMS CONVERSATION (EXISTING FLOW)          */}
              {/* ========================================================= */}
              {screenMode === 'SMS' && (
                <>
                  {/* SMS Contact Header Bar */}
                  <div className="py-2 px-1 flex items-center justify-between border-b border-stone-200 bg-white/70 backdrop-blur-xs -mx-3.5 px-3.5">
                    <div className="flex items-center space-x-2.5">
                      <div className="w-8 h-8 rounded-full bg-forest-800 text-white flex items-center justify-center text-sm shadow-xs font-bold">
                        🌧️
                      </div>
                      <div>
                        <div className="flex items-center space-x-1">
                          <h4 className="font-extrabold text-stone-900 text-xs">Meghvani</h4>
                          <CheckCircle2 className="w-3 h-3 text-emerald-600 fill-emerald-100" />
                        </div>
                        <p className="text-[10px] text-stone-500 font-mono">
                          {gatewayStatus?.twilio_phone_number_masked
                            ? `Short Code: ${gatewayStatus.twilio_phone_number_masked}`
                            : 'Short Code: 56161 (Meghvani SMS)'}
                        </p>
                      </div>
                    </div>

                    <div className="flex items-center space-x-1 text-[10px] font-semibold text-forest-800 bg-forest-50 px-2 py-0.5 rounded-full border border-forest-200">
                      <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
                      <span>SMS Gateway</span>
                    </div>
                  </div>

                  {/* Twilio Trial Mode Notice Banner */}
                  {gatewayStatus?.is_trial_mode && (
                    <div className="bg-amber-50 border-b border-amber-200 -mx-3.5 px-3.5 py-1 text-[10px] text-amber-900 flex items-center justify-between">
                      <span className="font-bold flex items-center gap-1 truncate">
                        <ShieldAlert className="w-3.5 h-3.5 text-amber-600 shrink-0" />
                        Twilio Trial — predefined SMS template
                      </span>
                      <span className="text-[9px] font-semibold bg-amber-200/80 px-1.5 py-0.2 rounded text-amber-900 shrink-0">
                        sms_2fa
                      </span>
                    </div>
                  )}

                  {/* Conversation Messages Area */}
                  <div ref={chatContainerRef} className="flex-1 overflow-y-auto py-3 space-y-3 pr-1 text-xs">
                    {/* Simulated timestamp header */}
                    <div className="text-center my-1">
                      <span className="text-[10px] bg-stone-200/60 text-stone-600 font-semibold px-2.5 py-0.5 rounded-full">
                        Today • Verified Telecom Pipeline
                      </span>
                    </div>

                    {messages.length === 0 ? (
                      <div className="h-full flex flex-col items-center justify-center text-center text-stone-400 px-4 space-y-2.5">
                        <Smartphone className="w-10 h-10 text-stone-300 stroke-1" />
                        <div>
                          <p className="text-xs font-bold text-stone-700">No messages yet</p>
                          <p className="text-[11px] text-stone-500 mt-0.5">
                            Click <strong>Text "MEGH"</strong> below or use <strong>Trigger Voice Alert</strong> to test high-risk call escalation.
                          </p>
                        </div>
                      </div>
                    ) : (
                      messages.map((m) => {
                        const isSystem = m.sender === 'system';
                        return (
                          <div
                            key={m.id}
                            className={`flex flex-col ${isSystem ? 'items-start' : 'items-end'}`}
                          >
                            {isSystem && (
                              <span className="text-[10px] font-bold text-forest-800 ml-1 mb-0.5">
                                Meghvani
                              </span>
                            )}
                            <div
                              className={`max-w-[85%] rounded-2xl px-3.5 py-2.5 whitespace-pre-line leading-relaxed text-xs ${
                                m.isCallNotification
                                  ? 'bg-amber-100 text-amber-900 border border-amber-300 italic text-[11px]'
                                  : isSystem
                                  ? 'bg-white text-stone-900 border border-stone-200/90 shadow-2xs rounded-tl-xs'
                                  : 'bg-forest-800 text-white rounded-tr-xs shadow-xs'
                              }`}
                            >
                              {m.text}
                            </div>
                            <div className="flex items-center space-x-1 mt-0.5 px-1">
                              <span className="text-[9px] text-stone-400">{m.timestamp}</span>
                              {!isSystem && (
                                <span className="text-[9px] text-forest-700 font-bold">✓✓</span>
                              )}
                            </div>
                          </div>
                        );
                      })
                    )}

                    {loading && (
                      <div className="flex items-center space-x-1.5 text-forest-700 text-xs pl-2 py-1">
                        <span className="text-[10px] text-stone-500 font-medium">Meghvani is generating response</span>
                        <span className="animate-bounce">●</span>
                        <span className="animate-bounce delay-100">●</span>
                        <span className="animate-bounce delay-200">●</span>
                      </div>
                    )}
                  </div>

                  {/* CONTEXTUAL QUICK ACTION SUGGESTIONS CHIPS */}
                  {currentStep === 'START' && messages.length === 0 && (
                    <div className="py-1.5 px-1 flex flex-wrap items-center gap-1.5 border-t border-stone-200 bg-stone-50/80 rounded-xl mb-1">
                      <span className="text-[10px] text-stone-500 font-bold uppercase tracking-wider pl-1">
                        Quick Start:
                      </span>
                      <button
                        type="button"
                        onClick={() => handleStart()}
                        className="px-2.5 py-1 rounded-lg bg-forest-800 hover:bg-forest-900 text-white text-[11px] font-bold shadow-2xs"
                      >
                        💬 Text "MEGH"
                      </button>
                      <button
                        type="button"
                        onClick={handleMissedCall}
                        className="px-2.5 py-1 rounded-lg bg-teal-700 hover:bg-teal-800 text-white text-[11px] font-bold shadow-2xs"
                      >
                        📞 Missed Call
                      </button>
                      <button
                        type="button"
                        onClick={handleNewFarmerDemo}
                        className="px-2.5 py-1 rounded-lg bg-stone-100 hover:bg-stone-200 text-stone-800 border border-stone-300 text-[11px] font-semibold shadow-2xs flex items-center gap-1"
                        title="Generate a brand new test phone number for fresh demo"
                      >
                        <Sparkles className="w-3 h-3 text-forest-700" />
                        <span>New Number Demo</span>
                      </button>
                    </div>
                  )}

                  {currentStep === 'LANGUAGE' && (
                    <div className="py-1.5 px-1 flex flex-wrap items-center gap-1 border-t border-stone-200 bg-stone-50/80 rounded-xl mb-1">
                      <span className="text-[10px] text-stone-500 font-bold uppercase tracking-wider pl-1">
                        Language:
                      </span>
                      <button
                        type="button"
                        onClick={() => handleQuickReply('1')}
                        className="px-2 py-0.5 rounded-md bg-stone-100 hover:bg-forest-100 text-stone-800 text-[10px] font-semibold border border-stone-300"
                      >
                        1: Hindi
                      </button>
                      <button
                        type="button"
                        onClick={() => handleQuickReply('2')}
                        className="px-2.5 py-0.5 rounded-md bg-forest-100 hover:bg-forest-200 text-forest-900 text-[10px] font-bold border border-forest-300 shadow-2xs"
                      >
                        2: Marathi
                      </button>
                      <button
                        type="button"
                        onClick={() => handleQuickReply('3')}
                        className="px-2 py-0.5 rounded-md bg-stone-100 hover:bg-forest-100 text-stone-800 text-[10px] font-semibold border border-stone-300"
                      >
                        3: Kannada
                      </button>
                      <button
                        type="button"
                        onClick={() => handleQuickReply('4')}
                        className="px-2 py-0.5 rounded-md bg-stone-100 hover:bg-forest-100 text-stone-800 text-[10px] font-semibold border border-stone-300"
                      >
                        4: English
                      </button>
                    </div>
                  )}

                  {currentStep === 'PIN' && (
                    <div className="py-1.5 px-1 flex flex-wrap items-center gap-1 border-t border-stone-200 bg-stone-50/80 rounded-xl mb-1">
                      <span className="text-[10px] text-stone-500 font-bold uppercase tracking-wider pl-1">
                        PIN Code:
                      </span>
                      <button
                        type="button"
                        onClick={() => handleQuickReply('441501')}
                        className="px-2.5 py-0.5 rounded-md bg-forest-100 hover:bg-forest-200 text-forest-900 border border-forest-300 text-[10px] font-bold shadow-2xs"
                      >
                        📍 441501 (Nagpur)
                      </button>
                      <button
                        type="button"
                        onClick={() => handleQuickReply('442104')}
                        className="px-2 py-0.5 rounded-md bg-stone-100 hover:bg-forest-100 text-stone-800 border border-stone-300 text-[10px] font-medium"
                      >
                        📍 442104 (Wardha)
                      </button>
                      <button
                        type="button"
                        onClick={() => handleQuickReply('444904')}
                        className="px-2 py-0.5 rounded-md bg-stone-100 hover:bg-forest-100 text-stone-800 border border-stone-300 text-[10px] font-medium"
                      >
                        📍 444904 (Amravati)
                      </button>
                    </div>
                  )}

                  {currentStep === 'VILLAGE' && (
                    <div className="py-1.5 px-1 flex flex-wrap items-center gap-1.5 border-t border-stone-200 bg-stone-50/80 rounded-xl mb-1">
                      <span className="text-[10px] text-stone-500 font-bold uppercase tracking-wider pl-1">
                        Village:
                      </span>
                      <button
                        type="button"
                        onClick={() => handleQuickReply('1')}
                        className="px-3 py-0.5 rounded-md bg-forest-100 hover:bg-forest-200 text-forest-900 border border-forest-300 text-[10px] font-bold shadow-2xs"
                      >
                        1: Kalmeshwar
                      </button>
                      <button
                        type="button"
                        onClick={() => handleQuickReply('2')}
                        className="px-3 py-0.5 rounded-md bg-stone-100 hover:bg-stone-200 text-stone-800 border border-stone-300 text-[10px] font-medium"
                      >
                        2: Mohpa
                      </button>
                    </div>
                  )}

                  {currentStep === 'CROP' && (
                    <div className="py-1.5 px-1 flex flex-wrap items-center gap-1 border-t border-stone-200 bg-stone-50/80 rounded-xl mb-1">
                      <span className="text-[10px] text-stone-500 font-bold uppercase tracking-wider pl-1">
                        Crop:
                      </span>
                      <button
                        type="button"
                        onClick={() => handleQuickReply('1')}
                        className="px-2.5 py-0.5 rounded-md bg-forest-100 hover:bg-forest-200 text-forest-900 border border-forest-300 text-[10px] font-bold shadow-2xs"
                      >
                        1: Soybean (सोयाबीन)
                      </button>
                      <button
                        type="button"
                        onClick={() => handleQuickReply('2')}
                        className="px-2 py-0.5 rounded-md bg-stone-100 hover:bg-stone-200 text-stone-800 border border-stone-300 text-[10px] font-medium"
                      >
                        2: Cotton (कापूस)
                      </button>
                      <button
                        type="button"
                        onClick={() => handleQuickReply('3')}
                        className="px-2 py-0.5 rounded-md bg-stone-100 hover:bg-stone-200 text-stone-800 border border-stone-300 text-[10px] font-medium"
                      >
                        3: Tur (तूर)
                      </button>
                    </div>
                  )}

                  {currentStep === 'CONSENT' && (
                    <div className="py-1.5 px-1 flex flex-wrap items-center gap-2 border-t border-stone-200 bg-stone-50/80 rounded-xl mb-1">
                      <span className="text-[10px] text-stone-500 font-bold uppercase tracking-wider pl-1">
                        Consent:
                      </span>
                      <button
                        type="button"
                        onClick={() => handleQuickReply('YES')}
                        className="px-4 py-1 rounded-lg bg-emerald-600 hover:bg-emerald-700 text-white text-[11px] font-bold shadow-xs flex items-center gap-1"
                      >
                        <Check className="w-3 h-3 stroke-[3]" />
                        <span>YES (Opt-In & Activate)</span>
                      </button>
                    </div>
                  )}

                  {(isCompleted || currentStep === 'STATUS' || currentStep === 'ALREADY_REGISTERED') && (
                    <div className="py-1.5 px-1 flex flex-wrap items-center gap-1.5 border-t border-stone-200 bg-stone-50/80 rounded-xl mb-1">
                      <span className="text-[10px] text-stone-500 font-bold uppercase tracking-wider pl-1">
                        Actions:
                      </span>
                      <button
                        type="button"
                        onClick={handleReRegister}
                        className="px-2.5 py-1 rounded-lg bg-emerald-700 hover:bg-emerald-800 text-white text-[10px] font-bold shadow-xs flex items-center gap-1 transition-colors"
                        title="Deactivate previous profile and register again from Step 1"
                      >
                        <RotateCcw className="w-3 h-3" />
                        <span>Register Again</span>
                      </button>
                      <button
                        type="button"
                        onClick={handleNewFarmerDemo}
                        className="px-2.5 py-1 rounded-lg bg-forest-800 hover:bg-forest-900 text-white text-[10px] font-bold shadow-xs flex items-center gap-1 transition-colors"
                        title="Generate a brand new test phone number"
                      >
                        <Sparkles className="w-3 h-3 text-amber-300" />
                        <span>New Number Demo</span>
                      </button>
                      <button
                        type="button"
                        onClick={() => handleQuickReply('STATUS')}
                        className="px-2 py-1 rounded-lg bg-stone-100 hover:bg-stone-200 text-stone-800 border border-stone-300 text-[10px] font-semibold flex items-center gap-1 transition-colors"
                      >
                        <span>📊 Advisory</span>
                      </button>
                      <button
                        type="button"
                        onClick={() => handleTriggerVoiceAlert()}
                        className="px-2 py-1 rounded-lg bg-red-600 hover:bg-red-700 text-white text-[10px] font-bold shadow-xs flex items-center gap-1 transition-colors"
                      >
                        <PhoneCall className="w-3 h-3" />
                        <span>Voice Call</span>
                      </button>
                    </div>
                  )}

                  {/* SMS Input Bar */}
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
                          ? 'Enter 6-digit PIN (e.g. 441501)...'
                          : currentStep === 'VILLAGE'
                          ? 'Reply village number (1 or 2)...'
                          : currentStep === 'CROP'
                          ? 'Reply crop number (1, 2 or 3)...'
                          : currentStep === 'CONSENT'
                          ? 'Reply YES to confirm...'
                          : isCompleted
                          ? 'Text STATUS to check advisory...'
                          : 'Type a message...'
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
                </>
              )}

              {/* Bottom Phone Bar Indicator */}
              <div className="w-24 h-1 bg-stone-300 rounded-full mx-auto mt-2 shrink-0" />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
