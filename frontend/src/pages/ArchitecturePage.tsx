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
  ArrowDown,
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
  Compass,
  CloudRain,
  BrainCircuit,
  Sliders,
  Send,
  HelpCircle,
  Activity
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
        'Mock provider isolation in test suites (344/344 deterministic tests)'
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
      {/* ===================================================================== */}
      {/* 1. HERO SECTION (Approved Light Theme — High Contrast & Readable)     */}
      {/* ===================================================================== */}
      <div className="bg-white rounded-3xl p-6 sm:p-8 md:p-10 border border-stone-200/90 shadow-2xs space-y-4">
        <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-forest-50 text-forest-800 border border-forest-200 text-xs font-bold uppercase tracking-wider">
          <Sparkles className="w-3.5 h-3.5 text-forest-700" />
          <span>Comprehensive System Architecture</span>
        </div>

        <div>
          <h1 className="text-2xl sm:text-3xl lg:text-4xl font-extrabold text-stone-900 tracking-tight">
            Meghvani End-to-End System Blueprint
          </h1>
          <p className="text-stone-600 text-xs sm:text-sm md:text-base leading-relaxed max-w-3xl mt-2">
            Full-stack agrometeorological decision-support system engineered for hyper-localized monsoon onset, 
            break spell detection, calibrated probabilistic inference, and ICAR validated advisory delivery.
          </p>
        </div>

        {/* View Switcher Controls */}
        <div className="pt-2 flex flex-wrap items-center gap-2.5">
          <button
            onClick={() => setActiveView('diagram')}
            className={`px-4 py-2 rounded-xl text-xs font-bold transition-all flex items-center space-x-2 cursor-pointer ${
              activeView === 'diagram'
                ? 'bg-forest-800 text-white shadow-xs'
                : 'bg-stone-100 hover:bg-stone-200 text-stone-700 border border-stone-200/70'
            }`}
          >
            <Workflow className="w-4 h-4" />
            <span>Interactive Topology</span>
          </button>
          <button
            onClick={() => setActiveView('layers')}
            className={`px-4 py-2 rounded-xl text-xs font-bold transition-all flex items-center space-x-2 cursor-pointer ${
              activeView === 'layers'
                ? 'bg-forest-800 text-white shadow-xs'
                : 'bg-stone-100 hover:bg-stone-200 text-stone-700 border border-stone-200/70'
            }`}
          >
            <Layers className="w-4 h-4" />
            <span>Layer Deep-Dive (6 Layers)</span>
          </button>
          <button
            onClick={() => setActiveView('flows')}
            className={`px-4 py-2 rounded-xl text-xs font-bold transition-all flex items-center space-x-2 cursor-pointer ${
              activeView === 'flows'
                ? 'bg-forest-800 text-white shadow-xs'
                : 'bg-stone-100 hover:bg-stone-200 text-stone-700 border border-stone-200/70'
            }`}
          >
            <GitBranch className="w-4 h-4" />
            <span>End-to-End Data Flows</span>
          </button>
          <button
            onClick={() => setActiveView('specs')}
            className={`px-4 py-2 rounded-xl text-xs font-bold transition-all flex items-center space-x-2 cursor-pointer ${
              activeView === 'specs'
                ? 'bg-forest-800 text-white shadow-xs'
                : 'bg-stone-100 hover:bg-stone-200 text-stone-700 border border-stone-200/70'
            }`}
          >
            <Terminal className="w-4 h-4" />
            <span>Specs & Invariants</span>
          </button>
        </div>
      </div>

      {/* ===================================================================== */}
      {/* 2. ARCHITECTURAL CAPABILITY STATISTICS CARDS                          */}
      {/* ===================================================================== */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3.5">
        <div className="p-4 rounded-2xl bg-white border border-stone-200 shadow-2xs">
          <div className="text-[10px] font-extrabold uppercase tracking-wider text-stone-400">REST Endpoints</div>
          <div className="text-2xl font-black text-stone-900 mt-1">17</div>
          <div className="text-[11px] text-stone-500 font-medium">FastAPI Routers</div>
        </div>
        <div className="p-4 rounded-2xl bg-white border border-stone-200 shadow-2xs">
          <div className="text-[10px] font-extrabold uppercase tracking-wider text-stone-400">ORM Entities</div>
          <div className="text-2xl font-black text-stone-900 mt-1">9</div>
          <div className="text-[11px] text-stone-500 font-medium">SQLAlchemy 2.0</div>
        </div>
        <div className="p-4 rounded-2xl bg-white border border-stone-200 shadow-2xs">
          <div className="text-[10px] font-extrabold uppercase tracking-wider text-stone-400">Causal Predictors</div>
          <div className="text-2xl font-black text-stone-900 mt-1">18</div>
          <div className="text-[11px] text-stone-500 font-medium">Zero Future Leakage</div>
        </div>
        <div className="p-4 rounded-2xl bg-white border border-stone-200 shadow-2xs">
          <div className="text-[10px] font-extrabold uppercase tracking-wider text-stone-400">Agronomic Rules</div>
          <div className="text-2xl font-black text-emerald-700 mt-1">18 Validated</div>
          <div className="text-[11px] text-stone-500 font-medium">ICAR / KVK Provenance</div>
        </div>
        <div className="p-4 rounded-2xl bg-white border border-stone-200 shadow-2xs">
          <div className="text-[10px] font-extrabold uppercase tracking-wider text-stone-400">Automated Tests</div>
          <div className="text-2xl font-black text-forest-700 mt-1">344 / 344</div>
          <div className="text-[11px] text-stone-500 font-medium">100% Tests Passing</div>
        </div>
        <div className="p-4 rounded-2xl bg-white border border-stone-200 shadow-2xs">
          <div className="text-[10px] font-extrabold uppercase tracking-wider text-stone-400">Telephony Modes</div>
          <div className="text-2xl font-black text-stone-900 mt-1">4 Tiers</div>
          <div className="text-[11px] text-stone-500 font-medium">SMS, Call, WA, Web</div>
        </div>
      </div>

      {/* ===================================================================== */}
      {/* VIEW 1: INTERACTIVE TOPOLOGY DIAGRAM                                   */}
      {/* Structure: DATA SOURCES -> INGESTION -> FEATURES -> PREDICTION ->      */}
      {/*            EXPLAINABILITY -> AGRONOMIC DECISION -> DELIVERY           */}
      {/* ===================================================================== */}
      {activeView === 'diagram' && (
        <div className="bg-white rounded-3xl p-6 sm:p-8 border border-stone-200/90 shadow-2xs space-y-6">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-stone-100 pb-5">
            <div>
              <h2 className="text-xl font-bold text-stone-900 flex items-center space-x-2">
                <Workflow className="w-5 h-5 text-forest-700" />
                <span>End-to-End System Topology</span>
              </h2>
              <p className="text-xs text-stone-500 mt-1">
                7-stage pipeline showing information flow from raw weather signals to farmer advisory execution.
              </p>
            </div>
            <div className="flex items-center space-x-2">
              <span className="text-xs px-2.5 py-1 rounded-full bg-emerald-50 text-emerald-800 border border-emerald-200 font-semibold flex items-center gap-1.5">
                <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
                <span>Operational Pipeline Architecture</span>
              </span>
            </div>
          </div>

          {/* Vertical 7-Stage Pipeline */}
          <div className="space-y-4">
            {/* STAGE 1: DATA SOURCES */}
            <div className="p-5 rounded-2xl bg-amber-50/70 border border-amber-200/90">
              <div className="flex items-center justify-between mb-3">
                <span className="text-xs font-extrabold text-amber-950 uppercase tracking-wider flex items-center space-x-2">
                  <CloudRain className="w-4 h-4 text-amber-700" />
                  <span>1. Data Sources</span>
                </span>
                <span className="text-[10px] font-bold bg-amber-200/80 text-amber-900 px-2 py-0.5 rounded">
                  Telemetry & Provenance Tier
                </span>
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
                <div className="p-3 bg-white rounded-xl border border-amber-200/80 shadow-2xs">
                  <div className="text-xs font-bold text-stone-900">IMD 0.25° Gridded Rainfall</div>
                  <div className="text-[11px] text-stone-500 mt-0.5">High-resolution daily precipitation telemetry</div>
                </div>
                <div className="p-3 bg-white rounded-xl border border-amber-200/80 shadow-2xs">
                  <div className="text-xs font-bold text-stone-900">IMD Pune Historical Archives</div>
                  <div className="text-[11px] text-stone-500 mt-0.5">Long-term climatology & wet/dry spell baselines</div>
                </div>
                <div className="p-3 bg-white rounded-xl border border-amber-200/80 shadow-2xs">
                  <div className="text-xs font-bold text-stone-900">ICAR / KVK Rules Registry</div>
                  <div className="text-[11px] text-stone-500 mt-0.5">18 peer-reviewed crop & moisture rules</div>
                </div>
                <div className="p-3 bg-white rounded-xl border border-amber-200/80 shadow-2xs">
                  <div className="text-xs font-bold text-stone-900">Farmer Inbound Field Reports</div>
                  <div className="text-[11px] text-stone-500 mt-0.5">Ground-truth validation via SMS / IVR</div>
                </div>
              </div>
            </div>

            {/* Connecting Arrow */}
            <div className="flex justify-center -my-2">
              <div className="bg-stone-100 text-stone-600 px-3 py-1 rounded-full text-[10px] font-mono font-bold border border-stone-200 flex items-center space-x-1">
                <ArrowDown className="w-3 h-3 text-stone-500" />
                <span>Automated Poller & Spatial Resolution</span>
              </div>
            </div>

            {/* STAGE 2: DATA INGESTION */}
            <div className="p-5 rounded-2xl bg-blue-50/70 border border-blue-200/90">
              <div className="flex items-center justify-between mb-3">
                <span className="text-xs font-extrabold text-blue-950 uppercase tracking-wider flex items-center space-x-2">
                  <Server className="w-4 h-4 text-blue-700" />
                  <span>2. Data Ingestion & FastAPI Gateway</span>
                </span>
                <span className="text-[10px] font-bold bg-blue-200/80 text-blue-900 px-2 py-0.5 rounded">
                  17 REST Routers
                </span>
              </div>
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                <div className="p-3 bg-white rounded-xl border border-blue-200/80 shadow-2xs">
                  <div className="text-xs font-bold text-stone-900">Daily Telemetry Poller</div>
                  <div className="text-[11px] text-stone-500 mt-0.5">Ingests daily rainfall into `/observations`</div>
                </div>
                <div className="p-3 bg-white rounded-xl border border-blue-200/80 shadow-2xs">
                  <div className="text-xs font-bold text-stone-900">Centroid-to-Grid Mapper</div>
                  <div className="text-[11px] text-stone-500 mt-0.5">0.25° grid nearest-neighbor lookup</div>
                </div>
                <div className="p-3 bg-white rounded-xl border border-blue-200/80 shadow-2xs">
                  <div className="text-xs font-bold text-stone-900">PIN Spatial Resolver</div>
                  <div className="text-[11px] text-stone-500 mt-0.5">Maps postal code to block and village</div>
                </div>
                <div className="p-3 bg-white rounded-xl border border-blue-200/80 shadow-2xs">
                  <div className="text-xs font-bold text-stone-900">Inbound Telephony Gateway</div>
                  <div className="text-[11px] text-stone-500 mt-0.5">Receives SMS/IVR webhooks at `/farmers`</div>
                </div>
              </div>
            </div>

            {/* Connecting Arrow */}
            <div className="flex justify-center -my-2">
              <div className="bg-stone-100 text-stone-600 px-3 py-1 rounded-full text-[10px] font-mono font-bold border border-stone-200 flex items-center space-x-1">
                <ArrowDown className="w-3 h-3 text-stone-500" />
                <span>Causal Rolling Window Feature Extraction</span>
              </div>
            </div>

            {/* STAGE 3: PROCESSING / FEATURE ENGINEERING */}
            <div className="p-5 rounded-2xl bg-purple-50/70 border border-purple-200/90">
              <div className="flex items-center justify-between mb-3">
                <span className="text-xs font-extrabold text-purple-950 uppercase tracking-wider flex items-center space-x-2">
                  <Sliders className="w-4 h-4 text-purple-700" />
                  <span>3. Processing / Feature Engineering</span>
                </span>
                <span className="text-[10px] font-bold bg-purple-200/80 text-purple-900 px-2 py-0.5 rounded">
                  Zero Future Leakage
                </span>
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                <div className="p-3 bg-white rounded-xl border border-purple-200/80 shadow-2xs">
                  <div className="text-xs font-bold text-stone-900">18 Causal Lag Features</div>
                  <div className="text-[11px] text-stone-500 mt-0.5">Rolling 1d, 3d, 7d, 14d, 30d rainfall sums & ratios</div>
                </div>
                <div className="p-3 bg-white rounded-xl border border-purple-200/80 shadow-2xs">
                  <div className="text-xs font-bold text-stone-900">Causal Quarantine Guarantee</div>
                  <div className="text-[11px] text-stone-500 mt-0.5">Strict backward windows (t ≤ current_day)</div>
                </div>
                <div className="p-3 bg-white rounded-xl border border-purple-200/80 shadow-2xs">
                  <div className="text-xs font-bold text-stone-900">Spell & Lockout Recency</div>
                  <div className="text-[11px] text-stone-500 mt-0.5">Days since last onset and ongoing dry-spell counter</div>
                </div>
              </div>
            </div>

            {/* Connecting Arrow */}
            <div className="flex justify-center -my-2">
              <div className="bg-stone-100 text-stone-600 px-3 py-1 rounded-full text-[10px] font-mono font-bold border border-stone-200 flex items-center space-x-1">
                <ArrowDown className="w-3 h-3 text-stone-500" />
                <span>Supervised Multi-Event Inference</span>
              </div>
            </div>

            {/* STAGE 4: PREDICTION ENGINE */}
            <div className="p-5 rounded-2xl bg-indigo-50/70 border border-indigo-200/90">
              <div className="flex items-center justify-between mb-3">
                <span className="text-xs font-extrabold text-indigo-950 uppercase tracking-wider flex items-center space-x-2">
                  <Cpu className="w-4 h-4 text-indigo-700" />
                  <span>4. Prediction Engine</span>
                </span>
                <span className="text-[10px] font-bold bg-indigo-200/80 text-indigo-900 px-2 py-0.5 rounded">
                  Platt Scaling (Brier 0.118)
                </span>
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                <div className="p-3 bg-white rounded-xl border border-indigo-200/80 shadow-2xs">
                  <div className="text-xs font-bold text-stone-900">Monsoon Onset Inference</div>
                  <div className="text-[11px] text-stone-500 mt-0.5">Probabilistic onset detection with 30d debounce lockout</div>
                </div>
                <div className="p-3 bg-white rounded-xl border border-indigo-200/80 shadow-2xs">
                  <div className="text-xs font-bold text-stone-900">False-Onset & Break Risk</div>
                  <div className="text-[11px] text-stone-500 mt-0.5">Evaluates probability of 7-day post-sowing dry spell</div>
                </div>
                <div className="p-3 bg-white rounded-xl border border-indigo-200/80 shadow-2xs">
                  <div className="text-xs font-bold text-stone-900">Multi-Horizon Calibration</div>
                  <div className="text-[11px] text-stone-500 mt-0.5">7-day, 15-day, and 30-day calibrated forecasts</div>
                </div>
              </div>
            </div>

            {/* Connecting Arrow */}
            <div className="flex justify-center -my-2">
              <div className="bg-stone-100 text-stone-600 px-3 py-1 rounded-full text-[10px] font-mono font-bold border border-stone-200 flex items-center space-x-1">
                <ArrowDown className="w-3 h-3 text-stone-500" />
                <span>Feature Attribution & Agronomic Reasoning</span>
              </div>
            </div>

            {/* STAGE 5: EXPLAINABILITY (XAI) */}
            <div className="p-5 rounded-2xl bg-teal-50/70 border border-teal-200/90">
              <div className="flex items-center justify-between mb-3">
                <span className="text-xs font-extrabold text-teal-950 uppercase tracking-wider flex items-center space-x-2">
                  <BrainCircuit className="w-4 h-4 text-teal-700" />
                  <span>5. Explainability (XAI)</span>
                </span>
                <span className="text-[10px] font-bold bg-teal-200/80 text-teal-900 px-2 py-0.5 rounded">
                  Statistical Transparency
                </span>
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                <div className="p-3 bg-white rounded-xl border border-teal-200/80 shadow-2xs">
                  <div className="text-xs font-bold text-stone-900">Linear Model Weights</div>
                  <div className="text-[11px] text-stone-500 mt-0.5">Standardized feature coefficients show exact model drivers</div>
                </div>
                <div className="p-3 bg-white rounded-xl border border-teal-200/80 shadow-2xs">
                  <div className="text-xs font-bold text-stone-900">Dominant Factor Ranking</div>
                  <div className="text-[11px] text-stone-500 mt-0.5">Identifies top atmospheric features governing risk</div>
                </div>
                <div className="p-3 bg-white rounded-xl border border-teal-200/80 shadow-2xs">
                  <div className="text-xs font-bold text-stone-900">Natural Language Synthesis</div>
                  <div className="text-[11px] text-stone-500 mt-0.5">Generates Marathi & English plain-text reasoning</div>
                </div>
              </div>
            </div>

            {/* Connecting Arrow */}
            <div className="flex justify-center -my-2">
              <div className="bg-stone-100 text-stone-600 px-3 py-1 rounded-full text-[10px] font-mono font-bold border border-stone-200 flex items-center space-x-1">
                <ArrowDown className="w-3 h-3 text-stone-500" />
                <span>Deterministic Agronomic Guardrails</span>
              </div>
            </div>

            {/* STAGE 6: AGRONOMIC DECISION */}
            <div className="p-5 rounded-2xl bg-emerald-50/70 border border-emerald-200/90">
              <div className="flex items-center justify-between mb-3">
                <span className="text-xs font-extrabold text-emerald-950 uppercase tracking-wider flex items-center space-x-2">
                  <Sprout className="w-4 h-4 text-emerald-700" />
                  <span>6. Agronomic Decision & Safety Guardrails</span>
                </span>
                <span className="text-[10px] font-bold bg-emerald-200/80 text-emerald-900 px-2 py-0.5 rounded">
                  ICAR / KVK Provenance
                </span>
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                <div className="p-3 bg-white rounded-xl border border-emerald-200/80 shadow-2xs">
                  <div className="text-xs font-bold text-stone-900">Posture Decision Matrix</div>
                  <div className="text-[11px] text-stone-500 mt-0.5">SOW_NOW (≥70%), SOW_PART_NOW (45–70%), WAIT (&lt;45%)</div>
                </div>
                <div className="p-3 bg-white rounded-xl border border-emerald-200/80 shadow-2xs">
                  <div className="text-xs font-bold text-stone-900">Crop-Specific Water Logic</div>
                  <div className="text-[11px] text-stone-500 mt-0.5">Custom thresholds for Cotton, Soybean, Sorghum, Pigeon Pea</div>
                </div>
                <div className="p-3 bg-white rounded-xl border border-emerald-200/80 shadow-2xs">
                  <div className="text-xs font-bold text-stone-900">Strict Null Safety</div>
                  <div className="text-[11px] text-stone-500 mt-0.5">Unvalidated rules resolve to null; zero advice hallucination</div>
                </div>
              </div>
            </div>

            {/* Connecting Arrow */}
            <div className="flex justify-center -my-2">
              <div className="bg-stone-100 text-stone-600 px-3 py-1 rounded-full text-[10px] font-mono font-bold border border-stone-200 flex items-center space-x-1">
                <ArrowDown className="w-3 h-3 text-stone-500" />
                <span>Multi-Channel Low-Tech Dispatch</span>
              </div>
            </div>

            {/* STAGE 7: FARMER / OFFICER DELIVERY */}
            <div className="p-5 rounded-2xl bg-amber-50/70 border border-amber-200/90">
              <div className="flex items-center justify-between mb-3">
                <span className="text-xs font-extrabold text-amber-950 uppercase tracking-wider flex items-center space-x-2">
                  <Radio className="w-4 h-4 text-amber-700" />
                  <span>7. Channel & Farmer Accessibility Layer</span>
                </span>
                <span className="text-[10px] font-bold bg-amber-200/80 text-amber-900 px-2 py-0.5 rounded">
                  Dual-Vernacular (Marathi & English)
                </span>
              </div>
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                <div className="p-3 bg-white rounded-xl border border-amber-200/80 shadow-2xs text-center">
                  <PhoneCall className="w-5 h-5 text-amber-700 mx-auto mb-1.5" />
                  <div className="text-xs font-bold text-stone-900">IVR Voice Call</div>
                  <div className="text-[10px] text-stone-500 mt-0.5">Automated voice retry for critical weather alerts</div>
                </div>
                <div className="p-3 bg-white rounded-xl border border-amber-200/80 shadow-2xs text-center">
                  <MessageSquare className="w-5 h-5 text-amber-700 mx-auto mb-1.5" />
                  <div className="text-xs font-bold text-stone-900">SMS 'MEGH' Gateway</div>
                  <div className="text-[10px] text-stone-500 mt-0.5">Low-bandwidth two-way registration & advice</div>
                </div>
                <div className="p-3 bg-white rounded-xl border border-amber-200/80 shadow-2xs text-center">
                  <Zap className="w-5 h-5 text-amber-700 mx-auto mb-1.5" />
                  <div className="text-xs font-bold text-stone-900">WhatsApp Dispatch</div>
                  <div className="text-[10px] text-stone-500 mt-0.5">Rich advisory cards with localized maps</div>
                </div>
                <div className="p-3 bg-white rounded-xl border border-amber-200/80 shadow-2xs text-center">
                  <Compass className="w-5 h-5 text-amber-700 mx-auto mb-1.5" />
                  <div className="text-xs font-bold text-stone-900">Officer Dashboard</div>
                  <div className="text-[10px] text-stone-500 mt-0.5">Spatial Vidarbha GIS analysis & broadcast</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* ===================================================================== */}
      {/* VIEW 2: LAYER DEEP-DIVE (6 Full Architectural Layers)                  */}
      {/* ===================================================================== */}
      {activeView === 'layers' && (
        <div className="space-y-6">
          {/* Layer Filter Tabs */}
          <div className="flex flex-wrap items-center gap-2">
            <button
              onClick={() => setActiveLayer('all')}
              className={`px-3.5 py-1.5 rounded-xl text-xs font-bold transition-all cursor-pointer ${
                activeLayer === 'all'
                  ? 'bg-forest-800 text-white shadow-xs'
                  : 'bg-white text-stone-600 border border-stone-200 hover:bg-stone-50'
              }`}
            >
              All Layers (6)
            </button>
            {layers.map(layer => (
              <button
                key={layer.id}
                onClick={() => setActiveLayer(layer.id)}
                className={`px-3.5 py-1.5 rounded-xl text-xs font-bold transition-all flex items-center space-x-1.5 cursor-pointer ${
                  activeLayer === layer.id
                    ? 'bg-forest-800 text-white shadow-xs'
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
                  className="bg-white rounded-3xl p-6 border border-stone-200/90 shadow-2xs flex flex-col justify-between hover:border-forest-300 transition-all space-y-5"
                >
                  <div className="space-y-4">
                    {/* Header */}
                    <div className="flex items-start justify-between">
                      <div className="flex items-center space-x-3">
                        <div className={`w-10 h-10 rounded-2xl bg-gradient-to-br ${layer.color} text-white flex items-center justify-center shadow-xs`}>
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
                  <div className="pt-3 border-t border-stone-100 bg-stone-50/70 -mx-6 -mb-6 p-4 rounded-b-3xl">
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

      {/* ===================================================================== */}
      {/* VIEW 3: END-TO-END WORKFLOWS                                           */}
      {/* ===================================================================== */}
      {activeView === 'flows' && (
        <div className="bg-white rounded-3xl p-6 sm:p-8 border border-stone-200/90 shadow-2xs space-y-6">
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
                  className={`px-3.5 py-1.5 rounded-xl text-xs font-bold transition-all cursor-pointer ${
                    selectedFlow === i
                      ? 'bg-forest-800 text-white shadow-xs'
                      : 'bg-stone-100 text-stone-600 hover:bg-stone-200 border border-stone-200/60'
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

      {/* ===================================================================== */}
      {/* VIEW 4: SPECS & INVARIANTS                                             */}
      {/* ===================================================================== */}
      {activeView === 'specs' && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Decision Engine Truth Table */}
          <div className="bg-white rounded-3xl p-6 border border-stone-200/90 shadow-2xs space-y-4">
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
          <div className="bg-white rounded-3xl p-6 border border-stone-200/90 shadow-2xs space-y-4">
            <div className="flex items-center justify-between border-b border-stone-100 pb-3">
              <h3 className="text-sm font-extrabold text-stone-900 flex items-center space-x-2">
                <ShieldCheck className="w-4 h-4 text-forest-700" />
                <span>Safety & Provenance Verification</span>
              </h3>
              <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-forest-100 text-forest-800">
                344/344 Tests
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
                  Prototypes trained on single-year partitions explicitly broadcast <code>is_operational: false</code> 
                  across API responses until multi-year historical backtesting is loaded.
                </p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* ===================================================================== */}
      {/* 5. DOCUMENTATION & REPOSITORY BLUEPRINT FOOTER                        */}
      {/* ===================================================================== */}
      <div className="p-6 rounded-3xl bg-forest-900 text-white flex flex-col md:flex-row items-center justify-between gap-4 shadow-sm border border-forest-800">
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
