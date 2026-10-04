# MEGHVANI — PHASE 5C: FARMER ADVISORY & LANGUAGE LAYER

## 1. Objective
The objective of Phase 5C is to convert an evaluated Meghvani prototype decision combined with a validated agronomic rule into clear, localized, farmer-facing messages across multiple delivery channels (SMS, WhatsApp, and Voice/IVR).

The language layer acts strictly as a **translation, simplification, and channel formatting interface**. It is **not** an agricultural reasoning engine and cannot invent farming practices, add chemical recommendations, or modify scientific thresholds.

```
Forecast Probability
        ↓
Prototype Decision (SOW_NOW / SOW_PART_NOW / WAIT)
        ↓
Validated Agronomic Rule (ICAR-CRIDA / CICR / Dr. PDKV / Maha Agri Dept)
        ↓
Advisory Message Generator
        ↓
Language Selection (English / Hindi / Marathi)
        ↓
Channel Formatting (SMS / WhatsApp / Voice-ready text)
```

---

## 2. Architecture
The advisory messaging architecture is implemented in:
- [`backend/app/advisory/message_generator.py`](file:///c:/Users/Acer/Desktop/MEGHVANI_Hrit/meghvani/backend/app/advisory/message_generator.py)
- [`backend/app/api/advisory.py`](file:///c:/Users/Acer/Desktop/MEGHVANI_Hrit/meghvani/backend/app/api/advisory.py) (`GET /api/advisory/{block_id}/message`)

It remains decoupled from telecom/communication delivery services (no external SMS gateway, WhatsApp Business API, or IVR telephony is invoked).

---

## 3. Supported Languages
The language layer explicitly supports three localized languages through the `MessageLanguage` enumeration:
1. **English (`en`)**: Clean, accessible terminology without academic or statistical jargon (e.g., no mention of Brier scores, ROC-AUC, or calibration curves).
2. **Hindi (`hi`)**: Simple agricultural phrasing suited for Central/Northern agricultural communities.
3. **Marathi (`mr`)**: Localized for the target Vidarbha agro-climatic zone of Maharashtra (e.g., proper agronomic terminology such as *वाफसा* for seedbed moisture readiness).

*Fallback Behavior*: Any unconfigured or invalid language code safely defaults to English (`en`).

### Crop Nomenclature Across Languages
| Crop ID | English | Hindi | Marathi |
|---|---|---|---|
| `soybean` | Soybean | सोयाबीन | सोयाबीन |
| `cotton` | Cotton | कपास | कापूस |
| `pigeonpea` | Pigeonpea (Tur) | अरहर (तूर) | तूर |

---

## 4. Message Types
The service implements six core message types (`MessageType`):
1. **`SOW_NOW`**: Triggered when the prototype decision is `SOW_NOW` and a `VALIDATED` agronomic rule exists for the crop and geography.
2. **`WAIT`**: Triggered when the prototype decision is `WAIT` and a `VALIDATED` agronomic rule exists.
3. **`SOW_PART_NOW`**: Because all candidate partial-sowing rules remain `REVIEW_REQUIRED`, this posture safely returns status `NO_VALIDATED_RULE` without giving unverified intercropping instructions.
4. **`NO_VALIDATED_RULE`**: Safe neutral notification used whenever a rule is missing, unvalidated, or awaiting review.
5. **`FORECAST_UNAVAILABLE`**: Neutral status used if hyperlocal forecast data is missing for the block.
6. **`PROTOTYPE_WARNING`**: Mandatory footer disclaimer attached to all outgoing communications.

---

## 5. Farmer vs. Officer Information Separation
To avoid confusing farmers while maintaining complete auditability for agronomists and officials, Meghvani distinguishes between farmer-facing communications and officer-facing inspection data:

| Dimension | Farmer-Facing Message | Officer / Reviewer API |
|---|---|---|
| **Probability** | Qualitative risk category (*"low risk"*, *"high risk"*) | Exact probability (e.g. `0.24`, `0.72`) + calibration status |
| **Model Metrics** | Hidden | Brier score, holdout test period, event counts |
| **Agronomic Instructions** | Simple action (e.g. wait for 75–100 mm rain) | Full rationale, section citations, publication dates |
| **Provenance Boundary** | Explicit source attribution | Full boundary statement (`source_vs_model_boundary`) |
| **Language** | Localized (English / Hindi / Marathi) | Multilingual + technical metadata |

---

## 6. Source / Model Separation (Provenance Integrity)
Farmer-facing messages strictly separate the institutional agricultural source from Meghvani's predictive model:
- **Meghvani's Forecast**: Informs the farmer regarding weather/monsoon false-onset risk (*"Current forecast indicates low false-onset risk"*).
- **Institutional Guidance**: Tells the farmer what agricultural condition must be met (*"Based on registered agricultural guidance from ICAR-CRIDA, ensure adequate soil moisture and rainfall (75-100 mm) before proceeding with sowing"*).
- **No False Attribution**: The message never states or implies that ICAR, CICR, or PDKV predicted the 30% or 60% probability.

---

## 7. The Validation Gate
The advisory message generator enforces the fundamental safety invariant:
$$\text{NO VALIDATED RULE} \implies \text{NO FARMING ADVICE}$$

If an agronomic rule is marked `UNVALIDATED` or `REVIEW_REQUIRED`:
1. No specific farming action is recommended.
2. No intercropping or seed rates are dispensed.
3. The response returns `advisory_status: "NO_VALIDATED_RULE"`.
4. The farmer is advised to consult local agricultural officers until verified guidance is available.

---

## 8. Channel Formatting
The service provides dedicated formatters for three communication modalities:

### A. SMS (`format_for_sms`)
- Character-conscious, single plain-text string.
- No markdown formatting or asterisks.
- Concise prototype disclaimer enclosed in brackets.

### B. WhatsApp (`format_for_whatsapp`)
- Rich typography with readable section breaks.
- Bold headlines and contextual icons (🌾 for active advice, ℹ️ for status updates).
- Clear, distinct disclaimer footer.

### C. Voice / IVR (`format_for_voice`)
- Natural spoken cadence for text-to-speech engines.
- Abbreviations expanded:
  - `"75-100 mm"` $\to$ `"75 to 100 millimeters"` (English), `"75 से 100 मिलीमीटर"` (Hindi), `"७५ ते १०० मिलीमीटर"` (Marathi).
  - `"ICAR-CRIDA"` $\to$ `"ICAR CRIDA"`, `"Dr. PDKV"` $\to$ `"Doctor PDKV"`.
- All markdown syntax, asterisks, brackets, and emojis removed.
- Includes spoken greeting and spoken advisory disclaimer.

---

## 9. Safety Constraints
1. **Zero Field Hallucination**: The service never recommends fertilizers (urea, DAP, NPK), pesticides, fungicides, seed rates (kg/ha), or specific irrigation volumes.
2. **No Communication Dispatch**: No real SMS, WhatsApp, or Voice gateway is invoked.
3. **Non-Operational Mandate**: Every response carries `is_operational = false` and prototype warning disclaimers.

---

## 10. Example Generated Messages

### Example 1: Soybean `SOW_NOW` (Marathi, WhatsApp)
```
🌾 *Meghvani Advisory | सोयाबीन*

मेघवाणी अपडेट — सोयाबीन:
सध्याच्या अंदाजानुसार पावसाच्या सुरुवातीबाबतचा धोका (False Onset) कमी आहे. ICAR-Central Research Institute for Dryland Agriculture (CRIDA) च्या अधिकृत कृषी मार्गदर्शक सूचनांनुसार, पेरणीपूर्वी पुरेशा पावसाची (७५-१०० मिमी) व योग्य वाफसा स्थितीची खात्री करा.

⚠️ _मेघवाणी प्रायोगिक सल्ला — स्थानिक कृषी तज्ज्ञांच्या मार्गदर्शनाचा पर्याय नाही._
```

### Example 2: Cotton `WAIT` (Hindi, SMS)
```
मेघवाणी अपडेट — कपास:
वर्तमान पूर्वानुमान के अनुसार गलत मानसून शुरुआत का जोखिम अधिक है। ICAR-Central Institute for Cotton Research (CICR), Nagpur द्वारा पंजीकृत कृषि दिशा-निर्देशों के अनुसार, बुवाई रोकें और पर्याप्त वर्षा (75-100 मिमी) व मिट्टी में नमी आने तक प्रतीक्षा करें।
[मेघवाणी प्रोटोटाइप सलाह — स्थानीय कृषि विशेषज्ञ के मार्गदर्शन का विकल्प नहीं है।]
```

### Example 3: Pigeonpea `WAIT` (English, Voice)
```
This is an automated Meghvani weather and crop advisory for Pigeonpea (Tur). Meghvani update for Pigeonpea (Tur):. Current forecast indicates elevated false onset risk. Based on registered agricultural guidance from Dr. Panjabrao Deshmukh Krishi Vidyapeeth Dr. PDKV, Akola, delay sowing until adequate rainfall 75 to 100 millimeters and sustained soil moisture are established. Please note: this is a prototype advisory and does not replace local agricultural expert advice.
```

---

## 11. Current Limitations
1. **Experimental Baseline**: Advisories are driven by a single historical year (2025) baseline with uncalibrated probabilities.
2. **Geographical Scope**: Sourced recommendations currently apply strictly to the Vidarbha region of Maharashtra.
3. **Partial Sowing On Hold**: Candidate intercropping rules for `SOW_PART_NOW` remain flagged `REVIEW_REQUIRED`.

---

## 12. Future Communication Integration (Post-Pilot)
In future operational phases (subsequent to multi-year model calibration and field validation):
- Real SMS gateway integration (e.g. CDAC / Kisan SMS).
- WhatsApp Business API with interactive button responses.
- Regional IVR telephony with recording fallbacks.
- Farmer opt-in and consent registry enforcement.
