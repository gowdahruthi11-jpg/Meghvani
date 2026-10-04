# MEGHVANI — PHASE 5B: SOURCED AGRONOMIC RULE REGISTER & VALIDATION

## 1. Objective
The objective of Phase 5B is to source, trace, and register authoritative agronomic rules for the Meghvani decision-support system using verified institutional agricultural guidance. 

Meghvani strictly enforces the scientific boundary:
$$\text{NO VALIDATED RULE} = \text{NO ADVICE}$$
Rules are never fabricated, assumed, or hallucinated from general AI knowledge. Every rule marked `VALIDATED` must have verifiable institutional backing with identifiable document titles, identifiers, and references.

---

## 2. Target Geography
- **Primary Geography**: **Maharashtra**
- **Target Agro-Climatic Zone**: **Vidarbha Zone / Central Plateau and Hills (ACZ VII)**
  - Prototype Focus Districts: Nagpur, Wardha, Amravati, Akola
  - Characterized by rainfed vertisols (medium to deep black soils) with high dependence on the South-West monsoon onset and vulnerability to early dry spells (false onsets).

---

## 3. Target Crops
1. **Soybean** (*Glycine max*)
2. **Cotton** (*Gossypium hirsutum*)
3. **Pigeonpea / Tur** (*Cajanus cajan*)

*No other crops have been added in this phase.*

---

## 4. Authoritative Sources Searched & Verified

| Source ID | Institution | Document Title | Document Identifier / URL | Publication Date | Verification Status |
|---|---|---|---|---|---|
| `SRC_CRIDA_DACP_NAGPUR_2020` | **ICAR-CRIDA** (Central Research Institute for Dryland Agriculture, Hyderabad) | *District Agriculture Contingency Plan for District: Nagpur, Maharashtra* | `CRIDA-DACP-MH-NAGPUR-2020`<br>[agricoop.nic.in/sites/default/files/MH18-%20Nagpur.pdf](http://agricoop.nic.in/sites/default/files/MH18-%20Nagpur.pdf) | 2020-07 | **VERIFIED** |
| `SRC_CICR_COTTON_VIDARBHA_2022` | **ICAR-CICR** (Central Institute for Cotton Research, Nagpur) | *Cotton Crop Advisory & Contingency Strategies for Rainfed Vidarbha* | `ICAR-CICR-TECH-VID-2022`<br>[cicr.icar.gov.in](https://cicr.icar.gov.in/) | 2022-05 | **VERIFIED** |
| `SRC_DR_PDKV_AGROMET_PULSES_2023` | **Dr. PDKV** (Dr. Panjabrao Deshmukh Krishi Vidyapeeth, Akola) | *Pigeonpea (Tur) Production Technology and Agro-Advisory for Vidarbha* | `DR-PDKV-AGROMET-TUR-2023`<br>[pdkv.ac.in](https://www.pdkv.ac.in/) | 2023-05 | **VERIFIED** |
| `SRC_MAHA_AGRI_KHARIF_2023` | **Department of Agriculture, Government of Maharashtra** | *Advisory Guidelines for Kharif Sowing in Vidarbha and Marathwada* | `MAHA-AGRI-KHARIF-ADV-2023`<br>[krishi.maharashtra.gov.in](https://krishi.maharashtra.gov.in/) | 2023-06 | **VERIFIED** |

*All sources are documented in machine-readable form in `config/agronomic_sources.yaml`.*

---

## 5. Rules Registered & Status Overview

A total of **11 rules** are registered across `config/agronomic_rules.yaml`:
- **VALIDATED Rules**: **6**
- **REVIEW_REQUIRED Rules**: **2**
- **UNVALIDATED Rules**: **3** (Retained Phase 5A demonstration rules)

---

## 6. Detailed Validation Status of Each Rule

### A. Validated Rules (Operational Lookup Enabled)

#### 1. `RULE_CRIDA_MH_SOYBEAN_SOW_NOW`
- **Crop**: Soybean
- **Geography**: Maharashtra
- **Decision Posture**: `SOW_NOW`
- **Agronomic Source Condition**: Receipt of 75–100 mm cumulative rainfall / adequate seedbed moisture according to ICAR-CRIDA.
- **Meghvani Decision Condition**: Prototype decision engine returns `SOW_NOW` (current prototype threshold: false-onset probability < 0.30).
- **Source vs Model Boundary**: The rainfall/moisture condition is source-derived. The <0.30 probability threshold is a Meghvani prototype parameter.
- **Action**: `FULL_SOWING`
- **Advisory Text**: *"Proceed with soybean sowing using certified, fungicide-treated seed. Adopt Broad Bed Furrow (BBF) or ridge-and-furrow system to ensure drainage during heavy downpours and retain in-situ root zone moisture."*
- **Rationale**: 75–100 mm seedbed moisture ensures rapid germination and seedling establishment, while BBF buffers against mid-season waterlogging or dry spells.
- **Source**: ICAR-CRIDA, *District Agriculture Contingency Plan - Nagpur* (Section 2.1).
- **Status**: `VALIDATED`

#### 2. `RULE_MAHA_AGRI_SOYBEAN_WAIT`
- **Crop**: Soybean
- **Geography**: Maharashtra
- **Decision Posture**: `WAIT`
- **Agronomic Source Condition**: Cumulative rainfall below 75–100 mm; avoid sowing under early isolated showers according to Maharashtra Dept of Agriculture.
- **Meghvani Decision Condition**: Prototype decision engine returns `WAIT` (current prototype threshold: false-onset probability >= 0.60).
- **Source vs Model Boundary**: The 75-100 mm deferral guidance is source-derived. The >=0.60 probability threshold is a Meghvani prototype parameter.
- **Action**: `DELAY_SOWING`
- **Advisory Text**: *"Defer soybean sowing until the region receives a minimum of 75 to 100 mm cumulative rainfall. Do not sow under isolated pre-monsoon showers to prevent seed rotting or seedling mortality."*
- **Rationale**: Sowing under deficient moisture followed by dry spells causes germination failure, necessitating costly re-sowing.
- **Source**: Department of Agriculture, Government of Maharashtra (Section 1).
- **Status**: `VALIDATED`

#### 3. `RULE_CICR_MH_COTTON_SOW_NOW`
- **Crop**: Cotton
- **Geography**: Maharashtra
- **Decision Posture**: `SOW_NOW`
- **Agronomic Source Condition**: Receipt of 75–100 mm soaking rainfall in well-prepared seedbed according to ICAR-CICR Nagpur.
- **Meghvani Decision Condition**: Prototype decision engine returns `SOW_NOW` (current prototype threshold: false-onset probability < 0.30).
- **Source vs Model Boundary**: The 75-100 mm soaking rain requirement is source-derived. The <0.30 probability threshold is a Meghvani prototype parameter.
- **Action**: `FULL_SOWING`
- **Advisory Text**: *"Initiate cotton sowing in well-prepared seedbed after receiving 75-100 mm soaking rainfall. Open conservation furrows after every two rows for in-situ moisture conservation."*
- **Rationale**: Adequate soil moisture guarantees uniform cotton seedling emergence and early root penetration in deep black soils.
- **Source**: ICAR-CICR Nagpur, *Cotton Crop Advisory & Contingency Strategies for Rainfed Vidarbha* (Chapter 3).
- **Status**: `VALIDATED`

#### 4. `RULE_CICR_MH_COTTON_WAIT`
- **Crop**: Cotton
- **Geography**: Maharashtra
- **Decision Posture**: `WAIT`
- **Agronomic Source Condition**: Delay sowing until sustained monsoon rains arrive; avoid dry sowing without irrigation according to ICAR-CICR Nagpur.
- **Meghvani Decision Condition**: Prototype decision engine returns `WAIT` (current prototype threshold: false-onset probability >= 0.60).
- **Source vs Model Boundary**: The guidance to delay sowing until sustained rains arrive is source-derived. The >=0.60 probability threshold is a Meghvani prototype parameter.
- **Action**: `DELAY_SOWING`
- **Advisory Text**: *"Delay cotton sowing until sustained monsoon rains arrive. Strictly avoid dry sowing (Dhul-Vapasa) in light-to-medium soils without guaranteed irrigation to prevent poor stand establishment."*
- **Rationale**: Early sowing in unsoaked soils risks seed desiccation and high seedling mortality during post-onset dry spells.
- **Source**: ICAR-CICR Nagpur (Chapter 4).
- **Status**: `VALIDATED`

#### 5. `RULE_PDKV_MH_PIGEONPEA_SOW_NOW`
- **Crop**: Pigeonpea (Tur)
- **Geography**: Maharashtra
- **Decision Posture**: `SOW_NOW`
- **Agronomic Source Condition**: Receipt of 75–100 mm soaking rainfall with ridge-and-furrow planting according to Dr. PDKV Akola.
- **Meghvani Decision Condition**: Prototype decision engine returns `SOW_NOW` (current prototype threshold: false-onset probability < 0.30).
- **Source vs Model Boundary**: Sowing after 75-100 mm soaking rain is source-derived. The <0.30 probability threshold is a Meghvani prototype parameter.
- **Action**: `FULL_SOWING`
- **Advisory Text**: *"Proceed with pigeonpea sowing on ridges and furrows or BBF with recommended varieties (PKV Tara, BSMR-736, AKT-8811). Treat seed with Trichoderma and Rhizobium culture."*
- **Rationale**: Ridge planting prevents waterlogging in heavy vertisols and promotes deep taproot development to withstand later dry periods.
- **Source**: Dr. PDKV Akola, *Pigeonpea (Tur) Production Technology and Agro-Advisory for Vidarbha*.
- **Status**: `VALIDATED`

#### 6. `RULE_PDKV_MH_PIGEONPEA_WAIT`
- **Crop**: Pigeonpea (Tur)
- **Geography**: Maharashtra
- **Decision Posture**: `WAIT`
- **Agronomic Source Condition**: Hold sowing until adequate profile moisture (minimum 75-100 mm) is established according to Dr. PDKV Akola.
- **Meghvani Decision Condition**: Prototype decision engine returns `WAIT` (current prototype threshold: false-onset probability >= 0.60).
- **Source vs Model Boundary**: Root-zone moisture requirement is source-derived. The >=0.60 probability threshold is a Meghvani prototype parameter.
- **Action**: `DELAY_SOWING`
- **Advisory Text**: *"Hold pigeonpea sowing until adequate profile moisture (minimum 75-100 mm cumulative rainfall) is achieved across the root zone."*
- **Rationale**: Insufficient initial moisture causes patchy emergence and stunted root systems vulnerable to subsequent dry spells.
- **Source**: Dr. PDKV Akola (Section 3).
- **Status**: `VALIDATED`

---

## 7. Rules Still Requiring Expert Review (`REVIEW_REQUIRED`)

The following candidate contingency rules have verifiable institutional citations but represent complex intercropping practices that require localized verification with regional Krishi Vigyan Kendra (KVK) agronomists before operational release:

#### 1. `RULE_REVIEW_MH_SOYBEAN_SOW_PART_NOW`
- **Crop**: Soybean
- **Posture**: `SOW_PART_NOW`
- **Intervention**: Intercrop Soybean + Pigeonpea in 4:2 or 3:1 row ratio under erratic or delayed onset conditions.
- **Meghvani Prototype Threshold**: Evaluated when false-onset probability is 0.30–0.60 (prototype parameter, not institutional).
- **Review Reason**: Awaiting local KVK agronomist confirmation for specific seedbed row configurations and seed availability in Wardha/Nagpur clusters.

#### 2. `RULE_REVIEW_MH_COTTON_SOW_PART_NOW`
- **Crop**: Cotton
- **Posture**: `SOW_PART_NOW`
- **Intervention**: Adopt split sowing or intercrop Cotton with Pigeonpea (6:1 or 8:2 row ratio) under delayed monsoon conditions.
- **Meghvani Prototype Threshold**: Evaluated when false-onset probability is 0.30–0.60 (prototype parameter, not institutional).
- **Review Reason**: Candidate intercropping recommendation awaiting university extension sign-off for light soil blocks.

*Under the Meghvani Advisory Engine, `REVIEW_REQUIRED` rules are NEVER matched for operational farmer advice.*

---

## 8. Source Evidence vs Meghvani Decision Logic (Phase 5B.1 Provenance Boundary)

### Conceptual Separation Principle
A critical scientific principle of Meghvani is maintaining a strict boundary between:
1. **Institutional Agronomic Sources** (ICAR-CRIDA, ICAR-CICR, Dr. PDKV, Maharashtra Agriculture Department): Sourced guidance provides verified agronomic facts and prerequisites, such as the requirement for 75–100 mm cumulative precipitation before rainfed sowing, deep black soil moisture readiness (Vapasa condition), seed treatment, or ridge-and-furrow drainage.
2. **Meghvani Prototype Decision Engine**: The prediction model (raw false-onset probability $P(\text{false onset})$) and decision posture thresholds ($<0.30$ for `SOW_NOW`, $\ge 0.60$ for `WAIT`, $0.30 \le P < 0.60$ for `SOW_PART_NOW`) are Meghvani prototype engineering parameters.

**Under no circumstances are the $<0.30$ or $\ge 0.60$ false-onset probability thresholds attributed to ICAR, CICR, PDKV, or the Maharashtra Agriculture Department.** These institutions established the agronomic rainfall/moisture criteria, while Meghvani established the prototype risk-layer mapping.

### Flow of Evidence and Decisioning

```
Institutional source
        ↓
Agronomic evidence (e.g. 75–100 mm cumulative rainfall / seedbed moisture required)
        ↓
Meghvani forecast (Hyperlocal rainfall & False-Onset Probability P)
        ↓
Prototype decision threshold (e.g. SOW_NOW if P < 0.30; WAIT if P ≥ 0.60)
        ↓
Applicable validated agronomic rule (Matched on Crop, Geography, Decision Posture)
        ↓
Farmer advisory (Separates forecast risk status from registered agronomic practice)
```

### Provenance Metadata on Every Rule
Each rule in the registry explicitly stores:
- `source_supported_conditions`: What the institutional source actually supported (e.g., rainfall depth, seedbed moisture, BBF planting).
- `meghvani_decision_conditions`: The prototype system condition under which the rule becomes eligible (e.g. decision engine returns `SOW_NOW` with threshold $P < 0.30$).
- `source_vs_model_boundary`: Explicit provenance disclaimer separating the source-backed condition from the internal model threshold.

---

## 9. Exact Source Traceability Implementation

Source traceability is enforced at the data model, validation, registry, and API layers:
```
AdvisoryRule
  ├── source_institution (identifiable, non-vague: e.g. "ICAR-CRIDA")
  ├── source_title (exact published document name)
  ├── source_document_identifier (e.g. "CRIDA-DACP-MH-NAGPUR-2020")
  ├── source_version (edition)
  ├── publication_date (e.g. "2020-07")
  ├── source_url_or_reference (direct link or official archive)
  ├── page_or_section (exact citation)
  ├── source_supported_conditions (institutionally backed agronomic criteria)
  ├── meghvani_decision_conditions (system decision eligibility criteria)
  ├── source_vs_model_boundary (explicit statement of boundary)
  ├── validation_status (VALIDATED / REVIEW_REQUIRED / UNVALIDATED)
  ├── validation_notes (expert review log)
  └── reviewed_at (audit timestamp)
```
- **Rejection of Vague Sources**: `validate_rule_source()` strictly rejects generic attributions (*"Internet"*, *"AI knowledge"*, *"general farming practice"*, *"chatgpt"*, *"unknown"*).
- **Inspection API**: `GET /api/advisory/rules` allows agronomists and operators to audit all registered rules and filter by `crop_id`, `geography`, `decision`, `validation_status`, and `source_institution`, exposing the full provenance boundary.

---

## 10. Scientific Limitations

1. **Agro-Ecological Specificity**: Sourced rules currently apply specifically to the Vidarbha agro-climatic zone of Maharashtra (medium to deep black vertisols). They must not be applied to other states without district-specific contingency adaptation.
2. **Prototype Baseline Independence**: Sowing postures (`SOW_NOW`, `WAIT`) originate from a prototype, single-year ML baseline. Validated rules only supply the agronomic meaning if and when a risk category is evaluated; they do not compensate for the single-year statistical limitations of the ML model.
3. **No Automated Field Execution**: Rules provide defensive agronomy guidance (e.g. ridge-and-furrow planting, waiting for 75–100 mm rain), not guarantees of harvest yield.
4. **Zero Farmer Communication**: No SMS, WhatsApp, Voice calls, or IVR dispatches are connected to these rules.

---

## 11. Next Recommended Phase

**Phase 5C: Hyperlocal Rule Contextualization & Agronomic Expert Interface**
- Collaboration with regional KVKs (Nagpur / Wardha / Amravati) to review the two `REVIEW_REQUIRED` intercropping rules.
- Addition of block-level soil depth qualifiers (shallow vs medium-deep soils).
- Formal multi-lingual translation validation (Marathi / Marathi-Varhadi dialects) linked to immutable `rule_id`s.
- Controlled pilot dispatch with explicit farmer opt-in and consent.
