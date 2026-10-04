import React, { useState } from 'react';
import {
  Layers,
  Cpu,
  Server,
  Database,
  Radio,
  Sprout,
  ShieldCheck,
  CheckCircle2,
  AlertTriangle,
  ArrowRight,
  GitBranch,
  Terminal,
  FileCode,
  ExternalLink,
  BookOpen,
  Sparkles,
  Zap,
  PhoneCall,
  MessageSquare,
  Workflow,
  Boxes,
  Lock,
  Compass
} from 'lucide-react';

interface LayerItem {
  id: string;
  name: string;
  category: string;
  icon: any;
  color: string;
  badge: string;
  summary: string;
  technologies: string[];
  components: string[];
  keyInvariants: string[];
}

export const ArchitecturePage: React.FC = () => {
  const [activeLayer, setActiveLayer] = useState<string>('all');
  const [activeView, setActiveView] = useState<'diagram' | 'layers' | 'flows' | 'specs'>('diagram');
  const [selectedFlow, setSelectedFlow] = useState<number>(0);

  const layers: LayerItem[] = [
    {
      id: 'interface',
      name: 'Layer 1: Farmer & Interface Layer',
      category: 'Client & Channel Tier',
      icon: Radio,
      color: 'from-amber-500 to-orange-600',
      badge: 'Multilingual / Low-Tech',
      summary: 'Inclusive accessibility for low-resource feature phones up to web dashboards. Delivers agrometeorological advisories and collects farmer ground truth.',
      technologies: ['SMS (GSM 03.38)', 'IVR Voice Call', 'WhatsApp Business API', 'React 18 + TypeScript', 'Tailwind CSS'],
      components: [
        'Low-bandwidth SMS State Machine (MEGH keyword)',
        'Voice Fallback Dispatcher (Automated dialer for critical alerts)',
        'WhatsApp Agronomic Chatbot with regional vernacular templates',
        'Officer & Field Agronomist Web Console (18 dynamic modules)'
      ],
      keyInvariants: [
        'Zero smartphone prerequisite for critical risk advisories',
        'Dual-language support (English and Marathi/Hindi)',
        'Rate-limiting and opt-in consent preserved on mobile numbers'
      ]
    },
    {
      id: 'gateway',
      name: 'Layer 2: API Gateway & Application Server',
      category: 'Application Tier',
      icon: Server,
      color: 'from-blue-600 to-indigo-700',
      badge: 'FastAPI / Pydantic v2',
      summary: 'High-performance asynchronous REST API with 17 specialized domain routers, request lifecycle validation, and dependency injection.',
      technologies: ['FastAPI 0.111+', 'Uvicorn ASGI', 'Pydantic v2', 'PyYAML Config Engine', 'Python 3.11+'],
      components: [
        '17 API Routers (/health, /blocks, /prediction, /advisory, /validation, etc.)',
        'CORS & Lifespan Event Handlers (startup DB verification & model loading)',
        'Typed Response Contracts with zero undeclared schema leakage',
        'Dependency Injection for DB Session Local & Service Instances'
      ],
      keyInvariants: [
        'Strict schema enforcement on all input and output payloads',
        'Stateless API instances allowing horizontal scaling',
        'Operational flags (is_operational=false on single-year prototypes)'
      ]
    },
    {
      id: 'science',
      name: 'Layer 3: Agrometeorological & ML Pipeline',
      category: 'Science Tier',
      icon: Cpu,
      color: 'from-purple-600 to-violet-700',
      badge: 'Zero-Leakage ML',
      summary: 'Predictive intelligence engine engineered for Monsoon onset, break spells, and dry spell warnings using strictly causal lag features.',
      technologies: ['Scikit-Learn', 'Pandas & NumPy', 'SciPy Stats', 'Platt Scaling (Logistic Regression)', 'Joblib'],
      components: [
        '18 Causal Feature Generators (1d, 3d, 5d, 7d, 14d, 30d rolling sums & spells)',
        'Monsoon Event Detector (Debounced onset >=25mm, Break spells >=5 days)',
        'Chronological Temporal Splitter (prevents historical time leakage)',
        'Platt Calibrator (maps raw margins to true frequentist probabilities)',
        'Skill Verifier (Brier Score & Brier Skill Score against climatology)'
      ],
      keyInvariants: [
        'Absolute zero future data leakage during lag calculation',
        '30-day debounce lockout on onset triggers preventing double fires',
        'Multi-year out-of-sample evaluation before production activation'
      ]
    },
    {
      id: 'decision',
      name: 'Layer 4: Agronomic Decision & Advisory Safety',
      category: 'Agronomic Rules Tier',
      icon: Sprout,
      color: 'from-emerald-600 to-teal-700',
      badge: 'ICAR / KVK Validated',
      summary: 'Translates probabilistic weather forecasts into concrete, actionable sowing postures with strict null safety and institutional attribution.',
      technologies: ['Agronomic Rule Registry', 'YAML Sourced Rules', 'Scientific Provenance Engine'],
      components: [
        'Sowing Posture Evaluator (SOW_NOW >=70%, SOW_PART_NOW 45-70%, WAIT <45%)',
        'Break Warning Posture Evaluator (P_break >=60% triggers moisture defense)',
        'Strict Null Safety Engine (returns null advisory instead of hallucinating)',
        'Source Provenance Register (ICAR, KVK, Anand Agricultural University)'
      ],
      keyInvariants: [
        'Unvalidated rules can never dispatch operational recommendations',
        'Every advice packet contains explicit institutional citation',
        'Dual probability bounds must satisfy both onset and break criteria'
      ]
    },
    {
      id: 'data',
      name: 'Layer 5: Persistence & Data Management',
      category: 'Storage Tier',
      icon: Database,
      color: 'from-cyan-600 to-blue-700',
      badge: 'SQLAlchemy 2.0 / PostGIS',
      summary: 'Relational & geospatial data persistence with normalized schemas, transactional safety, and automated Alembic schema migrations.',
      technologies: ['SQLAlchemy 2.0 ORM', 'SQLite (Development)', 'PostgreSQL 16 + PostGIS (Production)', 'Alembic'],
      components: [
        '9 SQLAlchemy Entities (Block, Village, Crop, Farmer, Weather, etc.)',
        'PIN-Code Spatial Resolver (matches farmer location to closest block centroid)',
        'Crowd-Sourced Farmer Observation Store (ground-truth validation)',
        'Audit Logging for Dispatched Alerts & Verification History'
      ],
      keyInvariants: [
        'PII sanitization (farmer mobile hashed or protected in officer views)',
        'Full relational integrity across Blocks -> Villages -> Farmers',
        'Idempotent seeding scripts for reproducible development runs'
      ]
    },
    {
      id: 'communication',
      name: 'Layer 6: Multi-Channel Dispatch & Telephony',
      category: 'Orchestration Tier',
      icon: Workflow,
      color: 'from-rose-600 to-pink-700',
      badge: 'Severity-Driven Fallback',
      summary: 'Automated multi-channel message dispatcher that routes advisories based on severity level, recipient connectivity, and delivery receipts.',
      technologies: ['Mock Communications Provider', 'Twilio / Exotel Adapter Ready', 'Async Task Queue'],
      components: [
        'Severity Router (CRITICAL -> Voice Call + SMS, HIGH -> WhatsApp + SMS)',
        'Exponential Backoff Retry Engine (handles network congestion and unreachable towers)',
        'Fallback Escalation (Voice retry failure triggers high-priority SMS)',
        'Message Delivery Audit Tracker (timestamped transmission states)'
      ],
      keyInvariants: [
        'Critical alerts must exhaust multi-tier channel failover before terminating',
        'Duplicate alert suppression window (prevents repetitive farmer fatigue)',
        'Mock provider isolation in test suites (166/166 deterministic tests)'
      ]
    }
  ];

  const flows = [
    {
      title: 'Monsoon Onset -> Agronomic Advisory Dispatch Flow',
      subtitle: 'From satellite/gauge daily rainfall ingestion to vernacular farmer SMS advice',
      steps: [
        {
          stage: '1. Ingestion',
          title: 'Daily Rainfall Ingested & Validated',
          desc: 'Raw gauge/IMD rainfall data (mm) is ingested via API or batch CSV. Non-negative constraints and date continuity are verified.',
          tag: 'Data Pipeline'
        },
        {
          stage: '2. Features',
          title: 'Causal Lag Feature Engineering',
          desc: 'Rolling rainfall sums (3d, 7d, 14d, 30d) and dry/wet spell metrics are calculated with strict backward-looking windows (zero future leakage).',
          tag: 'Feature Store'
        },
        {
          stage: '3. Prediction',
          title: 'Probabilistic Inference & Platt Calibration',
          desc: 'Baseline models compute raw onset and break margins. Platt scaling converts scores into calibrated probabilities: P(onset) and P(break).',
          tag: 'ML Model'
        },
        {
          stage: '4. Decision',
          title: 'Threshold-Based Posture Assessment',
          desc: 'If P(onset) >= 0.70 and P(break) < 0.30 -> SOW_NOW. If P(break) >= 0.60 -> WAIT. Posture evaluated against crop water requirements.',
          tag: 'Decision Engine'
        },
        {
          stage: '5. Advisory',
          title: 'ICAR / KVK Validated Rule Resolution',
          desc: 'Matched against agronomic rules registry. If validated, crop-specific instructions in Marathi/English are compiled with source citation.',
          tag: 'Advisory Registry'
        },
        {
          stage: '6. Dispatch',
          title: 'Channel Routing & Regional Delivery',
          desc: 'Alert dispatcher checks farmer preferred channel. Delivers via SMS/WhatsApp with voice call escalation if high weather alert active.',
          tag: 'Communication'
        }
      ]
    },
    {
      title: 'Farmer Registration & Low-Tech SMS Conversational Flow',
      subtitle: 'Self-service registration without requiring a smartphone or internet access',
      steps: [
        {
          stage: 'Step 1',
          title: 'Farmer sends "MEGH" SMS',
          desc: 'Farmer sends keyword "MEGH" to dedicated gateway. Session is initiated in state: AWAITING_PIN.',
          tag: 'Inbound SMS'
        },
        {
          stage: 'Step 2',
          title: 'PIN-Code Prompt & Spatial Resolution',
          desc: 'Gateway asks for 6-digit postal PIN. LocationService resolves PIN to Maharashtra district, block, and nearest village centroid.',
          tag: 'Location Service'
        },
        {
          stage: 'Step 3',
          title: 'Farmer Name & Language Consent',
          desc: 'Farmer provides name and confirms communication language (Marathi / English). State advances to AWAITING_CROPS.',
          tag: 'State Machine'
        },
        {
          stage: 'Step 4',
          title: 'Kharif Crop Selection',
          desc: 'Farmer replies with crop codes (e.g., 1 for Cotton, 2 for Soybean). Farmer profile is saved in DB with status: ACTIVE.',
          tag: 'Database Persistence'
        },
        {
          stage: 'Step 5',
          title: 'Confirmation & Hyperlocal Welcome Advisory',
          desc: 'System sends confirmation SMS with current block monsoon status and sowing guidance for their selected crops.',
          tag: 'Welcome Dispatch'
        }
      ]
    }
  ];

  const filteredLayers = activeLayer === 'all' 
    ? layers 
    : layers.filter(l => l.id === activeLayer);

  return (
    <div className="space-y-8 pb-12">
      {/* Header Banner */}
      <div className="relative overflow-hidden rounded-3xl bg-linear-to-r from-stone-900 via-forest-950 to-stone-900 text-white p-8 sm:p-10 shadow-xl border border-stone-800">
        <div className="absolute top-0 right-0 -mt-10 -mr-10 w-96 h-96 bg-forest-600/10 rounded-full blur-3xl pointer-events-none" />
        <div className="relative z-10 max-w-4xl">
          <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-forest-500/20 text-forest-300 border border-forest-500/30 text-xs font-semibold uppercase tracking-wider mb-4">
            <Sparkles className="w-3.5 h-3.5 text-forest-300" />
            <span>Comprehensive System Architecture</span>
          </div>
          <h1 className="text-3xl sm:text-4xl font-extrabold tracking-tight text-white mb-3">
            Meghvani End-to-End System Blueprint
          </h1>
          <p className="text-stone-300 text-sm sm:text-base leading-relaxed">
            Full-stack agrometeorological decision-support system engineered for hyper-localized monsoon onset, 
            break spell detection, calibrated probabilistic inference, and ICAR-validated advisory delivery.
          </p>

          <div className="mt-6 flex flex-wrap items-center gap-3">
            <button
              onClick={() => setActiveView('diagram')}
              className={`px-4 py-2 rounded-xl text-xs font-bold transition-all flex items-center space-x-2 ${
                activeView === 'diagram'
                  ? 'bg-forest-600 text-white shadow-md'
                  : 'bg-white/10 hover:bg-white/15 text-stone-200'
              }`}
            >
              <Workflow className="w-4 h-4" />
              <span>Interactive Topology</span>
            </button>
            <button
              onClick={() => setActiveView('layers')}
              className={`px-4 py-2 rounded-xl text-xs font-bold transition-all flex items-center space-x-2 ${
                activeView === 'layers'
                  ? 'bg-forest-600 text-white shadow-md'
                  : 'bg-white/10 hover:bg-white/15 text-stone-200'
              }`}
            >
              <Layers className="w-4 h-4" />
              <span>Layer Deep-Dive (6 Layers)</span>
            </button>
            <button
              onClick={() => setActiveView('flows')}
              className={`px-4 py-2 rounded-xl text-xs font-bold transition-all flex items-center space-x-2 ${
                activeView === 'flows'
                  ? 'bg-forest-600 text-white shadow-md'
                  : 'bg-white/10 hover:bg-white/15 text-stone-200'
              }`}
            >
              <GitBranch className="w-4 h-4" />
              <span>End-to-End Data Flows</span>
            </button>
            <button
              onClick={() => setActiveView('specs')}
              className={`px-4 py-2 rounded-xl text-xs font-bold transition-all flex items-center space-x-2 ${
                activeView === 'specs'
                  ? 'bg-forest-600 text-white shadow-md'
                  : 'bg-white/10 hover:bg-white/15 text-stone-200'
              }`}
            >
              <Terminal className="w-4 h-4" />
              <span>Specs & Invariants</span>
            </button>
          </div>
        </div>
      </div>

      {/* Key Architectural Metrics Banner */}
      <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-3 sm:gap-4">
        <div className="p-4 rounded-2xl bg-white border border-stone-200 shadow-xs">
          <div className="text-[10px] font-extrabold uppercase tracking-wider text-stone-400">REST Endpoints</div>
          <div className="text-2xl font-black text-stone-900 mt-1">17</div>
          <div className="text-[11px] text-stone-500 font-medium">FastAPI Routers</div>
        </div>
        <div className="p-4 rounded-2xl bg-white border border-stone-200 shadow-xs">
          <div className="text-[10px] font-extrabold uppercase tracking-wider text-stone-400">ORM Entities</div>
          <div className="text-2xl font-black text-stone-900 mt-1">9</div>
          <div className="text-[11px] text-stone-500 font-medium">SQLAlchemy 2.0</div>
        </div>
        <div className="p-4 rounded-2xl bg-white border border-stone-200 shadow-xs">
          <div className="text-[10px] font-extrabold uppercase tracking-wider text-stone-400">Causal Predictors</div>
          <div className="text-2xl font-black text-purple-700 mt-1">18</div>
          <div className="text-[11px] text-stone-500 font-medium">Zero Future Leakage</div>
        </div>
        <div className="p-4 rounded-2xl bg-white border border-stone-200 shadow-xs">
          <div className="text-[10px] font-extrabold uppercase tracking-wider text-stone-400">Agronomic Rules</div>
          <div className="text-2xl font-black text-emerald-700 mt-1">6 Validated</div>
          <div className="text-[11px] text-stone-500 font-medium">ICAR / KVK Provenance</div>
        </div>
        <div className="p-4 rounded-2xl bg-white border border-stone-200 shadow-xs">
          <div className="text-[10px] font-extrabold uppercase tracking-wider text-stone-400">Automated Tests</div>
          <div className="text-2xl font-black text-forest-700 mt-1">166 / 166</div>
          <div className="text-[11px] text-stone-500 font-medium">100% Tests Passing</div>
        </div>
        <div className="p-4 rounded-2xl bg-white border border-stone-200 shadow-xs">
          <div className="text-[10px] font-extrabold uppercase tracking-wider text-stone-400">Telephony Modes</div>
          <div className="text-2xl font-black text-amber-700 mt-1">4 Tiers</div>
          <div className="text-[11px] text-stone-500 font-medium">SMS, Call, WA, Web</div>
        </div>
      </div>

      {/* VIEW 1: INTERACTIVE TOPOLOGY DIAGRAM */}
      {activeView === 'diagram' && (
        <div className="bg-white rounded-3xl p-6 sm:p-8 border border-stone-200 shadow-xs space-y-6">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-stone-100 pb-5">
            <div>
              <h2 className="text-xl font-bold text-stone-900 flex items-center space-x-2">
                <Workflow className="w-5 h-5 text-forest-700" />
                <span>End-to-End System Topology</span>
              </h2>
              <p className="text-xs text-stone-500 mt-1">
                Architectural stack showing information flow from raw weather signals to farmer advisory execution.
              </p>
            </div>
            <div className="flex items-center space-x-2">
              <span className="text-xs px-2.5 py-1 rounded-full bg-emerald-50 text-emerald-800 border border-emerald-200 font-semibold">
                ● High Availability Architecture
              </span>
            </div>
          </div>

          {/* Visual Layer Diagram */}
          <div className="space-y-4">
            {/* Top Tier: Channels */}
            <div className="p-5 rounded-2xl bg-linear-to-r from-amber-50 to-orange-50 border border-amber-200/80">
              <div className="flex items-center justify-between mb-3">
                <span className="text-xs font-extrabold text-amber-900 uppercase tracking-wider flex items-center space-x-1.5">
                  <Radio className="w-4 h-4 text-amber-700" />
                  <span>Channel & Farmer Accessibility Layer</span>
                </span>
                <span className="text-[10px] font-bold bg-amber-200/80 text-amber-900 px-2 py-0.5 rounded">
                  Dual-Vernacular (Marathi & English)
                </span>
              </div>
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                <div className="p-3 bg-white/90 rounded-xl border border-amber-200 shadow-2xs text-center">
                  <PhoneCall className="w-5 h-5 text-amber-700 mx-auto mb-1" />
                  <div className="text-xs font-bold text-stone-900">IVR Voice Call</div>
                  <div className="text-[10px] text-stone-500">Automated retry for critical alerts</div>
                </div>
                <div className="p-3 bg-white/90 rounded-xl border border-amber-200 shadow-2xs text-center">
                  <MessageSquare className="w-5 h-5 text-amber-700 mx-auto mb-1" />
                  <div className="text-xs font-bold text-stone-900">SMS 'MEGH' Gateway</div>
                  <div className="text-[10px] text-stone-500">Conversational registration & advice</div>
                </div>
                <div className="p-3 bg-white/90 rounded-xl border border-amber-200 shadow-2xs text-center">
                  <Zap className="w-5 h-5 text-amber-700 mx-auto mb-1" />
                  <div className="text-xs font-bold text-stone-900">WhatsApp Dispatch</div>
                  <div className="text-[10px] text-stone-500">Rich advisory with map snippets</div>
                </div>
                <div className="p-3 bg-white/90 rounded-xl border border-amber-200 shadow-2xs text-center">
                  <Compass className="w-5 h-5 text-amber-700 mx-auto mb-1" />
                  <div className="text-xs font-bold text-stone-900">Officer Dashboard</div>
                  <div className="text-[10px] text-stone-500">Spatial analysis & alert broadcast</div>
                </div>
              </div>
            </div>

            {/* Connecting Arrow */}
            <div className="flex justify-center -my-2">
              <div className="bg-stone-100 text-stone-500 px-3 py-1 rounded-full text-[10px] font-mono font-bold border border-stone-200 flex items-center space-x-1">
                <span>↕ HTTPS REST / Webhook Payloads</span>
              </div>
            </div>

            {/* Tier 2: FastAPI Gateway */}
            <div className="p-5 rounded-2xl bg-linear-to-r from-blue-50 to-indigo-50 border border-blue-200/80">
              <div className="flex items-center justify-between mb-3">
                <span className="text-xs font-extrabold text-blue-900 uppercase tracking-wider flex items-center space-x-1.5">
                  <Server className="w-4 h-4 text-blue-700" />
                  <span>FastAPI Application Gateway & Controller Tier</span>
                </span>
                <span className="text-[10px] font-bold bg-blue-200/80 text-blue-900 px-2 py-0.5 rounded">
                  17 REST Routers
                </span>
              </div>
              <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-6 gap-2">
                {['/health', '/blocks', '/villages', '/crops', '/farmers', '/registration', '/observations', '/alerts', '/weather', '/prediction', '/forecast', '/advisory'].map(endpoint => (
                  <div key={endpoint} className="p-2 bg-white/90 rounded-lg border border-blue-200 text-center text-[11px] font-mono font-semibold text-blue-950">
                    {endpoint}
                  </div>
                ))}
              </div>
            </div>

            {/* Connecting Arrow */}
            <div className="flex justify-center -my-2">
              <div className="bg-stone-100 text-stone-500 px-3 py-1 rounded-full text-[10px] font-mono font-bold border border-stone-200 flex items-center space-x-1">
                <span>↓ Python Service Invocations & Event Bus</span>
              </div>
            </div>

            {/* Tier 3: Core Service & Intelligence Engines */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {/* Machine Learning Engine */}
              <div className="p-5 rounded-2xl bg-linear-to-br from-purple-50 to-violet-50 border border-purple-200/80">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-xs font-extrabold text-purple-900 uppercase tracking-wider flex items-center space-x-1.5">
                    <Cpu className="w-4 h-4 text-purple-700" />
                    <span>ML & Agrometeorology Engine</span>
                  </span>
                  <span className="text-[10px] font-bold bg-purple-200 text-purple-900 px-2 py-0.5 rounded">
                    Platt Scaling
                  </span>
                </div>
                <ul className="text-xs text-purple-950 space-y-1.5 mt-3">
                  <li className="flex items-center space-x-2">
                    <CheckCircle2 className="w-3.5 h-3.5 text-purple-600 shrink-0" />
                    <span><strong>18 Causal Features</strong> (Rolling 1d, 3d, 7d, 14d, 30d sums)</span>
                  </li>
                  <li className="flex items-center space-x-2">
                    <CheckCircle2 className="w-3.5 h-3.5 text-purple-600 shrink-0" />
                    <span><strong>Event Detector</strong> (30-day lockout debounced onset)</span>
                  </li>
                  <li className="flex items-center space-x-2">
                    <CheckCircle2 className="w-3.5 h-3.5 text-purple-600 shrink-0" />
                    <span><strong>Brier Score Verification</strong> (Against climatology baseline)</span>
                  </li>
                </ul>
              </div>

              {/* Decision & Advisory Engine */}
              <div className="p-5 rounded-2xl bg-linear-to-br from-emerald-50 to-teal-50 border border-emerald-200/80">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-xs font-extrabold text-emerald-900 uppercase tracking-wider flex items-center space-x-1.5">
                    <Sprout className="w-4 h-4 text-emerald-700" />
                    <span>Agronomic Decision & Safety Engine</span>
                  </span>
                  <span className="text-[10px] font-bold bg-emerald-200 text-emerald-900 px-2 py-0.5 rounded">
                    ICAR Provenance
                  </span>
                </div>
                <ul className="text-xs text-emerald-950 space-y-1.5 mt-3">
                  <li className="flex items-center space-x-2">
                    <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600 shrink-0" />
                    <span><strong>Posture Rules:</strong> SOW_NOW (≥70%), SOW_PART_NOW (45-70%), WAIT</span>
                  </li>
                  <li className="flex items-center space-x-2">
                    <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600 shrink-0" />
                    <span><strong>Strict Null Safety:</strong> Unvalidated combinations return null advice</span>
                  </li>
                  <li className="flex items-center space-x-2">
                    <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600 shrink-0" />
                    <span><strong>Institutional Attribution:</strong> ICAR, KVK Nagpur, AAU sources</span>
                  </li>
                </ul>
              </div>
            </div>

            {/* Connecting Arrow */}
            <div className="flex justify-center -my-2">
              <div className="bg-stone-100 text-stone-500 px-3 py-1 rounded-full text-[10px] font-mono font-bold border border-stone-200 flex items-center space-x-1">
                <span>↓ SQLAlchemy 2.0 ORM & Async Engine</span>
              </div>
            </div>

            {/* Bottom Tier: Storage & Persistence */}
            <div className="p-5 rounded-2xl bg-linear-to-r from-cyan-50 to-sky-50 border border-cyan-200/80">
              <div className="flex items-center justify-between mb-3">
                <span className="text-xs font-extrabold text-cyan-900 uppercase tracking-wider flex items-center space-x-1.5">
                  <Database className="w-4 h-4 text-cyan-700" />
                  <span>Persistence & Geospatial Storage Layer</span>
                </span>
                <span className="text-[10px] font-bold bg-cyan-200 text-cyan-900 px-2 py-0.5 rounded">
                  SQLite (Dev) / PostgreSQL + PostGIS (Prod)
                </span>
              </div>
              <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 gap-2 text-center">
                {['blocks', 'villages', 'crops', 'farmers', 'weather_obs', 'reg_sessions', 'farmer_obs', 'alert_logs', 'model_evals'].map(table => (
                  <div key={table} className="p-2 bg-white/90 rounded-lg border border-cyan-200 text-[11px] font-mono text-cyan-950 font-bold">
                    {table}
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* VIEW 2: LAYER DEEP-DIVE */}
      {activeView === 'layers' && (
        <div className="space-y-6">
          {/* Layer Filter Tabs */}
          <div className="flex flex-wrap items-center gap-2">
            <button
              onClick={() => setActiveLayer('all')}
              className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all ${
                activeLayer === 'all'
                  ? 'bg-forest-800 text-white'
                  : 'bg-white text-stone-600 border border-stone-200 hover:bg-stone-50'
              }`}
            >
              All Layers (6)
            </button>
            {layers.map(layer => (
              <button
                key={layer.id}
                onClick={() => setActiveLayer(layer.id)}
                className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all flex items-center space-x-1.5 ${
                  activeLayer === layer.id
                    ? 'bg-forest-800 text-white'
                    : 'bg-white text-stone-600 border border-stone-200 hover:bg-stone-50'
                }`}
              >
                <span>{layer.name.split(':')[0]}</span>
              </button>
            ))}
          </div>

          {/* Cards for Layers */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {filteredLayers.map(layer => {
              const Icon = layer.icon;
              return (
                <div
                  key={layer.id}
                  className="bg-white rounded-3xl p-6 border border-stone-200 shadow-xs flex flex-col justify-between hover:border-forest-300 transition-all space-y-5"
                >
                  <div className="space-y-4">
                    {/* Header */}
                    <div className="flex items-start justify-between">
                      <div className="flex items-center space-x-3">
                        <div className={`w-10 h-10 rounded-2xl bg-linear-to-br ${layer.color} text-white flex items-center justify-center shadow-xs`}>
                          <Icon className="w-5 h-5" />
                        </div>
                        <div>
                          <div className="text-[10px] font-extrabold text-stone-400 uppercase tracking-wider">
                            {layer.category}
                          </div>
                          <h3 className="text-base font-extrabold text-stone-900">
                            {layer.name}
                          </h3>
                        </div>
                      </div>
                      <span className="text-[10px] font-extrabold uppercase px-2 py-0.5 rounded bg-stone-100 text-stone-700 border border-stone-200">
                        {layer.badge}
                      </span>
                    </div>

                    <p className="text-xs text-stone-600 leading-relaxed">
                      {layer.summary}
                    </p>

                    {/* Tech Badges */}
                    <div>
                      <div className="text-[10px] font-bold text-stone-400 uppercase tracking-wider mb-1.5">
                        Technologies & Standards
                      </div>
                      <div className="flex flex-wrap gap-1.5">
                        {layer.technologies.map(t => (
                          <span key={t} className="text-[10px] font-semibold px-2 py-0.5 rounded-md bg-stone-100 text-stone-800 border border-stone-200">
                            {t}
                          </span>
                        ))}
                      </div>
                    </div>

                    {/* Core Components */}
                    <div>
                      <div className="text-[10px] font-bold text-stone-400 uppercase tracking-wider mb-1.5">
                        Core Modules & Entities
                      </div>
                      <div className="space-y-1">
                        {layer.components.map(c => (
                          <div key={c} className="text-xs text-stone-700 flex items-start space-x-1.5">
                            <span className="text-forest-600 font-bold">•</span>
                            <span>{c}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>

                  {/* Invariants Footer */}
                  <div className="pt-3 border-t border-stone-100 bg-stone-50/60 -mx-6 -mb-6 p-4 rounded-b-3xl">
                    <div className="text-[10px] font-bold text-stone-500 uppercase tracking-wider mb-1 flex items-center space-x-1">
                      <Lock className="w-3 h-3 text-stone-400" />
                      <span>Architectural Invariants</span>
                    </div>
                    <ul className="space-y-1">
                      {layer.keyInvariants.map(inv => (
                        <li key={inv} className="text-[11px] text-stone-600 flex items-center space-x-1.5">
                          <CheckCircle2 className="w-3 h-3 text-forest-600 shrink-0" />
                          <span>{inv}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* VIEW 3: END-TO-END FLOWS */}
      {activeView === 'flows' && (
        <div className="bg-white rounded-3xl p-6 sm:p-8 border border-stone-200 shadow-xs space-y-6">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-stone-100 pb-5">
            <div>
              <h2 className="text-xl font-bold text-stone-900 flex items-center space-x-2">
                <GitBranch className="w-5 h-5 text-forest-700" />
                <span>End-to-End Operational Workflows</span>
              </h2>
              <p className="text-xs text-stone-500 mt-1">
                Step-by-step transaction flow from trigger to verified farmer feedback.
              </p>
            </div>
            <div className="flex items-center space-x-2">
              {flows.map((f, i) => (
                <button
                  key={f.title}
                  onClick={() => setSelectedFlow(i)}
                  className={`px-3 py-1.5 rounded-xl text-xs font-bold transition-all ${
                    selectedFlow === i
                      ? 'bg-forest-800 text-white shadow-xs'
                      : 'bg-stone-100 text-stone-600 hover:bg-stone-200'
                  }`}
                >
                  Workflow {i + 1}
                </button>
              ))}
            </div>
          </div>

          <div className="p-4 rounded-2xl bg-stone-50 border border-stone-200">
            <h3 className="text-sm font-extrabold text-stone-900">{flows[selectedFlow].title}</h3>
            <p className="text-xs text-stone-500 mt-0.5">{flows[selectedFlow].subtitle}</p>
          </div>

          <div className="relative pl-6 sm:pl-8 space-y-6 before:absolute before:left-3 sm:before:left-4 before:top-3 before:bottom-3 before:w-0.5 before:bg-forest-200">
            {flows[selectedFlow].steps.map((step, idx) => (
              <div key={step.stage} className="relative group">
                {/* Step indicator dot */}
                <div className="absolute -left-6 sm:-left-8 top-1 w-6 h-6 rounded-full bg-forest-800 text-white font-extrabold text-[10px] flex items-center justify-center ring-4 ring-white shadow-xs">
                  {idx + 1}
                </div>
                <div className="p-4 rounded-2xl bg-white border border-stone-200/90 shadow-2xs group-hover:border-forest-300 transition-all">
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-[11px] font-black text-forest-800 uppercase tracking-wider">
                      {step.stage}
                    </span>
                    <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-forest-50 text-forest-700 border border-forest-200">
                      {step.tag}
                    </span>
                  </div>
                  <h4 className="text-sm font-extrabold text-stone-900">{step.title}</h4>
                  <p className="text-xs text-stone-600 mt-1 leading-relaxed">{step.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* VIEW 4: SPECS & INVARIANTS */}
      {activeView === 'specs' && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Decision Engine Truth Table */}
          <div className="bg-white rounded-3xl p-6 border border-stone-200 shadow-xs space-y-4">
            <div className="flex items-center justify-between border-b border-stone-100 pb-3">
              <h3 className="text-sm font-extrabold text-stone-900 flex items-center space-x-2">
                <Sprout className="w-4 h-4 text-emerald-700" />
                <span>Agronomic Decision Logic Matrix</span>
              </h3>
              <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-emerald-100 text-emerald-800">
                Phase 4B Specification
              </span>
            </div>
            <p className="text-xs text-stone-500">
              Deterministic threshold-to-posture mapping. Prevents false-onset seedling mortality.
            </p>
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead>
                  <tr className="border-b border-stone-200 text-stone-400 font-extrabold text-[10px] uppercase">
                    <th className="py-2">P(Onset)</th>
                    <th className="py-2">P(Break)</th>
                    <th className="py-2">Posture</th>
                    <th className="py-2">Action / Rationale</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-stone-100 text-stone-700">
                  <tr>
                    <td className="py-2 font-mono font-bold text-emerald-700">&ge; 0.70</td>
                    <td className="py-2 font-mono">&lt; 0.30</td>
                    <td className="py-2"><span className="font-extrabold text-emerald-700 bg-emerald-50 px-1.5 py-0.5 rounded">SOW_NOW</span></td>
                    <td className="py-2 text-[11px]">Optimal moisture, low break probability</td>
                  </tr>
                  <tr>
                    <td className="py-2 font-mono font-bold text-amber-700">0.45 – 0.69</td>
                    <td className="py-2 font-mono">&lt; 0.40</td>
                    <td className="py-2"><span className="font-extrabold text-amber-700 bg-amber-50 px-1.5 py-0.5 rounded">SOW_PART_NOW</span></td>
                    <td className="py-2 text-[11px]">Partial sowing to stagger germination risk</td>
                  </tr>
                  <tr>
                    <td className="py-2 font-mono text-stone-500">&lt; 0.45</td>
                    <td className="py-2 font-mono">Any</td>
                    <td className="py-2"><span className="font-extrabold text-rose-700 bg-rose-50 px-1.5 py-0.5 rounded">WAIT</span></td>
                    <td className="py-2 text-[11px]">Insufficient soil moisture guaranteed</td>
                  </tr>
                  <tr>
                    <td className="py-2 font-mono text-stone-500">Any</td>
                    <td className="py-2 font-mono font-bold text-rose-700">&ge; 0.60</td>
                    <td className="py-2"><span className="font-extrabold text-rose-700 bg-rose-50 px-1.5 py-0.5 rounded">WAIT</span></td>
                    <td className="py-2 text-[11px]">High risk of mid-season dry spell mortality</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          {/* Test Coverage & Safety Invariants */}
          <div className="bg-white rounded-3xl p-6 border border-stone-200 shadow-xs space-y-4">
            <div className="flex items-center justify-between border-b border-stone-100 pb-3">
              <h3 className="text-sm font-extrabold text-stone-900 flex items-center space-x-2">
                <ShieldCheck className="w-4 h-4 text-forest-700" />
                <span>Safety & Provenance Verification</span>
              </h3>
              <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-forest-100 text-forest-800">
                166/166 Tests
              </span>
            </div>
            <div className="space-y-3">
              <div className="p-3 rounded-xl bg-stone-50 border border-stone-200 text-xs">
                <div className="font-bold text-stone-900 flex items-center space-x-1.5">
                  <CheckCircle2 className="w-4 h-4 text-forest-700" />
                  <span>Strict Null Safety on Unvalidated Recommendations</span>
                </div>
                <p className="text-stone-600 mt-1 text-[11px]">
                  If an agronomic rule is marked <code>UNVALIDATED</code> or lacks KVK review, 
                  <code>advisory_text</code> resolves to <code>null</code>. The system never outputs hallucinatory or unvetted advice.
                </p>
              </div>

              <div className="p-3 rounded-xl bg-stone-50 border border-stone-200 text-xs">
                <div className="font-bold text-stone-900 flex items-center space-x-1.5">
                  <CheckCircle2 className="w-4 h-4 text-forest-700" />
                  <span>Causal Lag Integrity & Feature Quarantine</span>
                </div>
                <p className="text-stone-600 mt-1 text-[11px]">
                  All rolling sum windows are strictly bounded by <code>t &le; current_day</code>. 
                  Zero look-ahead information leaks into predictive model tensors.
                </p>
              </div>

              <div className="p-3 rounded-xl bg-stone-50 border border-stone-200 text-xs">
                <div className="font-bold text-stone-900 flex items-center space-x-1.5">
                  <CheckCircle2 className="w-4 h-4 text-forest-700" />
                  <span>Single-Year Dataset Honesty Flag</span>
                </div>
                <p className="text-stone-600 mt-1 text-[11px]">
                  Prototypes trained on 2025 single-year partitions explicitly broadcast <code>is_operational: false</code> 
                  across API responses until multi-year historical backtesting is loaded.
                </p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Docs & Architecture Files Reference */}
      <div className="p-6 rounded-3xl bg-forest-900 text-white flex flex-col md:flex-row items-center justify-between gap-4">
        <div className="flex items-center space-x-4">
          <div className="w-12 h-12 rounded-2xl bg-white/10 flex items-center justify-center shrink-0">
            <FileCode className="w-6 h-6 text-forest-300" />
          </div>
          <div>
            <h4 className="text-base font-bold text-white">Full System Architecture Artifacts</h4>
            <p className="text-xs text-forest-200">
              Interactive HTML visualizer and complete Markdown specification are accessible in your repository.
            </p>
          </div>
        </div>
        <div className="flex items-center space-x-3">
          <span className="text-xs font-mono bg-forest-950 px-3 py-1.5 rounded-lg border border-forest-700/60 text-forest-200">
            meghvani/docs/system_architecture.html
          </span>
        </div>
      </div>
    </div>
  );
};
