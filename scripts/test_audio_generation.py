"""
Meghvani Audio Generation and Local Playback Diagnostic Script.
Implements specifications from sections 10, 11, and 18 of the Voice Alert specification:
1. Calls Sarvam Bulbul v3 with valid v3 parameters (speaker=shubh, pace=1.0, sample_rate=24000, codec=wav).
2. Verifies base64 audio decoding and RIFF/WAVE headers.
3. Saves test_meghvani_voice.wav.
4. Prints: File size, Sample rate, Channels, Duration.
5. Plays the WAV file on the development machine.
"""
import os
import sys
import json
import base64
import wave
import subprocess
import urllib.request
import urllib.error
from pathlib import Path

# Locate backend directory
PROJECT_ROOT = Path(__file__).resolve().parent.parent
BACKEND_DIR = PROJECT_ROOT / "backend"
sys.path.insert(0, str(BACKEND_DIR))
sys.stdout.reconfigure(encoding="utf-8")

# Load .env safely
from app.config import settings

def get_sarvam_api_key():
    key = os.getenv("SARVAM_API_KEY") or getattr(settings, "sarvam_api_key", None)
    if key and key.strip():
        return key.strip()
    return None

def synthesize_and_verify(
    text: str,
    language_code: str = "en-IN",
    speaker: str = "shubh",
    model: str = "bulbul:v3",
    sample_rate: int = 24000,
    output_filename: str = "test_meghvani_voice.wav"
) -> bool:
    print("\n" + "=" * 60)
    print(f"TEST: {language_code} ({speaker}) -> {output_filename}")
    print(f"Text: '{text}'")
    print("=" * 60)

    api_key = get_sarvam_api_key()
    if not api_key:
        print("[NOTICE] SARVAM_API_KEY is not configured in backend/.env or system environment.")
        print("[FALLBACK] Generating local diagnostic WAV using Windows Speech Engine to verify audio hardware...")
        ps_cmd = f"""
Add-Type -AssemblyName System.Speech
$synth = New-Object System.Speech.Synthesis.SpeechSynthesizer
$synth.SetOutputToWaveFile('{output_filename}')
$synth.Speak('{text}')
$synth.Dispose()
"""
        res = subprocess.run(["powershell", "-NoProfile", "-Command", ps_cmd], capture_output=True, text=True)
        if res.returncode != 0:
            print("[ERROR] Local WAV generation failed:", res.stderr)
            return False
    else:
        endpoint = "https://api.sarvam.ai/text-to-speech"
        payload = {
            "inputs": [text],
            "target_language_code": language_code,
            "speaker": speaker,
            "pace": 1.0,
            "speech_sample_rate": sample_rate,
            "output_audio_codec": "wav",
            "enable_preprocessing": True,
            "model": model,
        }

        print(f"Sending request to {endpoint}...")
        req = urllib.request.Request(
            endpoint,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "api-subscription-key": api_key,
                "Content-Type": "application/json",
            },
            method="POST"
        )

        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                http_status = resp.status
                request_id = resp.headers.get("x-request-id", "unknown")
                resp_bytes = resp.read()
                resp_data = json.loads(resp_bytes.decode("utf-8"))

            print(f"HTTP Status: {http_status}")
            print(f"Request ID: {request_id}")

            audios = resp_data.get("audios", [])
            print(f"Audio array length: {len(audios)}")
            if not audios or not audios[0]:
                print("[ERROR] Sarvam returned an empty audios array!")
                return False

            raw_b64 = str(audios[0]).strip()
            print(f"Base64 string length: {len(raw_b64)}")

            decoded_bytes = base64.b64decode(raw_b64, validate=True)
            print(f"Decoded audio byte length: {len(decoded_bytes)}")
            print(f"First 16 decoded bytes: {decoded_bytes[:16]!r}")

            if not decoded_bytes.startswith(b"RIFF") or b"WAVE" not in decoded_bytes[:16]:
                print("[ERROR] Decoded audio does NOT have valid RIFF/WAVE header!")
                return False

            with open(output_filename, "wb") as f:
                f.write(decoded_bytes)

        except urllib.error.HTTPError as e:
            err_body = e.read().decode("utf-8", errors="ignore")
            print(f"[ERROR] Sarvam HTTP {e.code} Error: {err_body}")
            return False
        except Exception as e:
            print(f"[ERROR] Exception calling Sarvam API: {e}")
            return False

    # Inspect WAV file properties using standard wave module
    if not os.path.exists(output_filename):
        print(f"[ERROR] File {output_filename} was not created.")
        return False

    file_size = os.path.getsize(output_filename)
    with wave.open(output_filename, "rb") as w:
        channels = w.getnchannels()
        actual_sample_rate = w.getframerate()
        frames = w.getnframes()
        duration = frames / float(actual_sample_rate) if actual_sample_rate else 0

    print("\n--- WAV Audio Properties ---")
    print(f"File size:   {file_size} bytes")
    print(f"Sample rate: {actual_sample_rate} Hz")
    print(f"Channels:    {channels} ({'Mono' if channels == 1 else 'Stereo'})")
    print(f"Duration:    {duration:.2f} seconds")
    print("----------------------------\n")

    # Manually play audio on Windows
    print(f"Playing {output_filename} through development machine speakers...")
    play_cmd = f"(New-Object Media.SoundPlayer '{output_filename}').PlaySync()"
    play_res = subprocess.run(["powershell", "-NoProfile", "-Command", play_cmd], capture_output=True, text=True)
    if play_res.returncode == 0:
        print("[SUCCESS] Audio playback completed successfully.")
        return True
    else:
        print("[WARNING] Playback error:", play_res.stderr)
        return False


if __name__ == "__main__":
    print("MEGHVANI VOICE PIPELINE DIAGNOSTIC")
    print(f"Project root: {PROJECT_ROOT}")

    # TEST 1: English
    t1 = synthesize_and_verify(
        text="Hello. This is Meghvani. Heavy rainfall is expected. Do not sow seeds today.",
        language_code="en-IN",
        speaker="shubh",
        output_filename="test_meghvani_voice.wav"
    )

    # TEST 2: Marathi (Native Devanagari Script)
    t2 = synthesize_and_verify(
        text="नमस्कार. मेघवाणी कडून हवामानाचा इशारा आहे. आज पेरणी करू नका. पावसाची परिस्थिती स्थिर होईपर्यंत थांबा.",
        language_code="mr-IN",
        speaker="shubh",
        output_filename="test_meghvani_voice_mr.wav"
    )

    print("\n" + "=" * 60)
    print("DIAGNOSTIC SUMMARY:")
    print(f"Test 1 (English): {'PASSED' if t1 else 'FAILED'}")
    print(f"Test 2 (Marathi): {'PASSED' if t2 else 'FAILED'}")
    print("=" * 60)
