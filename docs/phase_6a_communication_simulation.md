# Meghvani Phase 6A: Communication Simulation & Alert Routing

> **CRITICAL NOTICE**: **Phase 6A does not send real SMS, WhatsApp messages, or phone calls.**  
> All communications are mock-simulated (`is_operational = false`, `external_dispatch = false`). No real telecom or messaging provider credentials exist in the system.

---

## 1. Objective

Phase 6A builds the end-to-end communication simulation and alert-routing layer connecting Meghvani's validated agronomic decisions to simulated field dispatches:

```text
Farmer Profile
      ↓
Forecast & Calibration
      ↓
Decision Engine
      ↓
Validated Agronomic Rule
      ↓
Farmer Message (Advisory Layer)
      ↓
Alert Eligibility & Consent Gate
      ↓
Channel Selection & Severity Policy
      ↓
Mock Communication Providers
      ↓
Delivery Simulation & Fallback Handling
      ↓
Alert Audit Log
      ↓
Officer Dashboard / Audit Interface
```

The objective is to demonstrate and audit how Meghvani delivers localized agronomic advisories across diverse communication channels after eventual deployment, while maintaining strict safety invariants and zero risk of unauthorized or unverified messages reaching actual farmers.

---

## 2. Architecture

The communication simulation subsystem is located at `backend/app/communication/` and interfaces seamlessly with existing databases, advisory models, and frontends without duplicate models:

- **Router**: [`AlertRouter`](file:///backend/app/communication/alert_router.py) coordinates farmer validation, consent gating, channel selection, duplicate suppression, mock provider invocation, fallback resolution, and audit logging.
- **Mock Providers**:
  - [`BaseMockProvider`](file:///backend/app/communication/providers/base.py) defines standard signature and deterministic testing hooks (`force_failure`).
  - [`MockSMSProvider`](file:///backend/app/communication/providers/mock_sms.py) generates `MOCK-SMS-...` dispatches.
  - [`MockWhatsAppProvider`](file:///backend/app/communication/providers/mock_whatsapp.py) generates `MOCK-WA-...` dispatches.
  - [`MockVoiceProvider`](file:///backend/app/communication/providers/mock_voice.py) generates `MOCK-VOICE-...` simulated calls.
- **Database Model**: Extended [`AlertLog`](file:///backend/app/models/alert_log.py) with structured metadata: `crop_id`, `decision`, `severity`, `message_type`, `language`, `provider`, `fallback_used`, `fallback_channel`, `reason`, `external_dispatch`.
- **API Endpoints**:
  - `POST /api/alerts/preview`: Generates a message and routing preview without simulation or logging.
  - `POST /api/alerts/simulate`: Executes end-to-end simulation for a farmer or block, returning simulated results with `external_dispatch: false`.
  - `GET /api/alerts/history`: Provides officer-facing audit logs with query filters and masked phone numbers.

---

## 3. Consent Flow

Before generating or simulating any dispatch, the `AlertRouter` executes an uncompromising consent gate:

```text
Check 1: Does farmer exist in the database?
Check 2: Is farmer active (active == True)?
Check 3: Has the farmer given explicit consent (consent == True)?
Check 4: Is a valid phone number registered?
Check 5: Is a registered crop specified?
Check 6: Is the block available?
Check 7: Is the preferred language supported or safely fallbacked?
```

- If `consent == False`: Returns `COMMUNICATION_NOT_AUTHORIZED` with status `BLOCKED_NO_CONSENT`. No communication is dispatched or queued.
- If `active == False`: Returns status `BLOCKED_INACTIVE_FARMER`.
- If phone is missing: Returns status `BLOCKED_MISSING_PHONE`.
- Safety and consent rules strictly supersede individual farmer channel preferences.

---

## 4. Alert Routing

Alert routing is decoupled from external delivery mechanisms and the core decision engine. The router inspects:
1. **Advisory Decision**: `SOW_NOW`, `SOW_PART_NOW`, or `WAIT`.
2. **Rule Status**: Only rules with status `VALIDATED` can generate farmer alerts.
3. **Severity Level**: `INFO`, `IMPORTANT`, or `HIGH`.
4. **Farmer Preference**: Channels requested by the farmer (`SMS`, `WHATSAPP`, `VOICE`, `ALL`).

The router determines:
- Primary channel(s)
- Fallback channel (default: `SMS`)
- Formatted localized message
- Dispatch execution order

---

## 5. Severity Policy

The prototype alert severity levels represent operational prototype policies (`PROTOTYPE_ALERT_POLICY`) and do NOT claim to be official government disaster thresholds:

| Severity Level | Prototype Definition | Primary Channel Allocation |
| :--- | :--- | :--- |
| **`INFO`** | Routine advisory / normal status updates | `SMS` |
| **`IMPORTANT`** | Meaningful meteorological change requiring attention | `SMS` + `WHATSAPP` |
| **`HIGH`** | High-risk situation requiring urgent operational attention | `VOICE` + `SMS` |

---

## 6. Channel Policy & Routing

- **INFO**: Routed via `SMS`.
- **IMPORTANT**: Multi-channel broadcast routed via `SMS` and `WHATSAPP`.
- **HIGH**: Urgent multi-channel broadcast routed via `VOICE` (simulated outbound IVR call) and `SMS`.
- **Farmer Preference**: If a farmer specifies a preference (e.g., `WHATSAPP`), the router prioritizes that channel for routine advisories while honoring multi-channel safety mandates for `HIGH` severity.

---

## 7. Mock Providers

Mock providers simulate external telecom and messaging gateways without any network socket, API request, or credential:

- Always return `"external_dispatch": false`.
- Generate distinct simulated identifiers:
  - `MockSMSProvider`: `MOCK-SMS-{uuid}`
  - `MockWhatsAppProvider`: `MOCK-WA-{uuid}`
  - `MockVoiceProvider`: `MOCK-VOICE-{uuid}`
- Support controlled testing through `force_failure=True` to deterministically verify fallback resilience.

Example simulated response:
```json
{
  "provider": "mock_sms",
  "status": "SIMULATED_SENT",
  "provider_message_id": "MOCK-SMS-095a89e6",
  "external_dispatch": false,
  "attempted_channel": "SMS"
}
```

---

## 8. Fallback Mechanism

When a primary delivery channel encounters a simulated failure, the router activates an automatic fallback pathway:

```text
Voice Simulated Failure  ──►  SMS Fallback  ──►  FALLBACK_USED
WhatsApp Simulated Failure ──► SMS Fallback ──►  FALLBACK_USED
```

- When the fallback channel succeeds, the alert log status is recorded as `FALLBACK_USED` with `fallback_channel = "SMS"` and `fallback_used = True`.
- Alerts are never silently discarded if any channel fails.

---

## 9. Duplicate Suppression

To prevent alert fatigue and redundant dispatches:
- The router checks recent alert logs for the same farmer, block, crop, and decision.
- A configurable cooldown period (prototype: **24 hours**) is enforced.
- If a matching alert was logged within the cooldown period:
  - Return code: `DUPLICATE_SUPPRESSED`
  - Status: `DUPLICATE_SUPPRESSED`
  - No redundant simulated dispatch occurs.

---

## 10. Alert Logging

All simulation events are persisted to the `alert_logs` table via SQLAlchemy:

- `id`: Unique alert ID
- `farmer_id`: Target farmer
- `block_id`: Geographic block
- `crop_id`: Target crop
- `decision`: Prototype decision (`SOW_NOW`, `SOW_PART_NOW`, `WAIT`)
- `severity`: Alert severity (`INFO`, `IMPORTANT`, `HIGH`)
- `message_type`: Message category / rule ID
- `language`: Advisory language (`en`, `hi`, `mr`)
- `channel`: Primary channel used
- `status`: Simulated delivery status (`SIMULATED_SENT`, `FALLBACK_USED`, `SIMULATED_FAILED`, `BLOCKED_*`)
- `provider`: Provider identifier (`mock_sms`, `mock_whatsapp`, `mock_voice`)
- `provider_message_id`: Mock tracking ID
- `fallback_used`: Boolean indicating fallback activation
- `fallback_channel`: Name of fallback channel if used
- `reason`: Explanatory operational log
- `external_dispatch`: Constrained to `False`
- `created_at`: Timestamp

---

## 11. Officer Alert Dashboard (Alert Center)

The frontend **Alert Center** (`/alerts`) provides agricultural and administrative officers with complete visibility and audit capabilities:

### Metric Summary Cards
1. **Alerts Generated**: Total alerts created/attempted.
2. **Simulated Success**: Dispatches completed via primary channels (`SIMULATED_SENT`).
3. **Simulated Failures**: Dispatches failing across all attempted channels (`SIMULATED_FAILED`).
4. **Consent Blocked**: Invocations stopped by missing consent or inactive profiles (`BLOCKED_NO_CONSENT`).
5. **No Validated Rule**: Dispatches blocked due to non-validated or missing agronomic rules (`BLOCKED_NO_VALIDATED_RULE`).
6. **Duplicate Suppressed**: Dispatches suppressed within 24h cooldown (`DUPLICATE_SUPPRESSED`).

### Filterable Audit Table
- Filters by Status, Channel, Severity, and Farmer ID.
- Displays Time, Block, Crop, Decision, Severity, Channel, Simulated Status, and Fallback indicator.
- Phone numbers are masked for officer privacy (`******1234`).

### Detailed Inspection Modal
Clicking any alert displays:
- Masked phone number and farmer ID.
- Decision, risk status, and rule provenance (source institution, source publication, and Meghvani decision boundaries).
- Channel plan, provider response, and explicit prototype disclaimer.

---

## 12. Farmer Simulation Sandbox

The **Farmer Simulation Sandbox** allows operators and SIH evaluators to interactively simulate an end-to-end alert:

1. **Select Inputs**: Choose Farmer, Crop, Language (`Marathi`, `Hindi`, `English`), Severity (`INFO`, `IMPORTANT`, `HIGH`), and Channel Preference.
2. **Resilience & Failure Testing**: Toggle "Simulate Primary Channel Failure" to observe simulated Voice/WhatsApp failure followed by instant SMS fallback.
3. **Live 6-Stage Pipeline Trace**:
   - `Farmer & Consent`: Verified active with explicit consent.
   - `Forecast & Probability`: Calibrated model assessment.
   - `Agronomic Rule`: Validated institutional rule verification.
   - `Localized Advisory`: Formatted farmer message in selected language.
   - `Channel Routing`: Selected channels with fallback policy.
   - `Delivery Simulation`: Provider execution, mock IDs, and `external_dispatch: false`.

---

## 13. Privacy & Security

- **Phone Number Masking**: Full phone numbers are never returned in public or officer audit endpoints. The format `******1234` is enforced by both the router and the schemas.
- **PIN Privacy**: Farmer PINs are never included in alert messages, payloads, or database logs.
- **Zero Sensitive Exposure**: Personal identifying information is strictly limited to authorized administrative contexts.

---

## 14. Safety Invariants

Phase 6A strictly enforces the following architectural guardrails:

| Invariant | System Action | Result Status |
| :--- | :--- | :--- |
| **`NO CONSENT`** | Halt dispatch immediately | `BLOCKED_NO_CONSENT` / `COMMUNICATION_NOT_AUTHORIZED` |
| **`INACTIVE FARMER`** | Halt dispatch immediately | `BLOCKED_INACTIVE_FARMER` |
| **`NO FORECAST`** | Halt dispatch immediately | `BLOCKED_NO_FORECAST` |
| **`REVIEW_REQUIRED` RULE** | Withhold advisory message | `BLOCKED_NO_VALIDATED_RULE` |
| **`UNVALIDATED` RULE** | Withhold advisory message | `BLOCKED_NO_VALIDATED_RULE` |
| **`NO VALIDATED RULE`** | Withhold advisory message | `BLOCKED_NO_VALIDATED_RULE` |
| **`EXTERNAL DISPATCH`** | Never connect to network or telecom | `external_dispatch: false` ALWAYS |
| **`OPERATIONAL STATE`** | System remains in prototype mode | `is_operational: false` ALWAYS |

---

## 15. Current Limitations

1. **Simulated Dispatches**: All provider executions are mock stubs in memory. No SMS or WhatsApp packets leave the server.
2. **Prototype Cooldown**: Duplicate suppression uses a 24-hour heuristic window; dynamic agronomic event invalidation is not yet implemented.
3. **Prototype Geography**: Supported blocks and crop rules are limited to the Vidarbha prototype dataset (Kalmeshwar, Mohpa, etc., for Soybean, Cotton, and Pigeonpea).

---

## 16. Future Real-Provider Integration

When transitioning to operational field deployment (subsequent phases), the architecture supports seamless provider substitution:

1. Replace `MockSMSProvider` with a real SMS gateway implementation (e.g., CDAC mKisan gateway, Exotel, or telecom partner) adhering to the `BaseMockProvider` contract.
2. Replace `MockWhatsAppProvider` with an approved WhatsApp Business API client (Meta Cloud API).
3. Replace `MockVoiceProvider` with an IVR telecom provider supporting vernacular voice playback.
4. Set `is_operational = true` only after formal institutional authorization and telecom sandbox certification.
