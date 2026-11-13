"""LLM layer for any OpenAI-compatible API (Gemini free tier, OpenRouter, Ollama /v1, ...). Configure in .env."""
import asyncio, json, os
from pathlib import Path
from urllib.parse import urlparse
import httpx
from dotenv import load_dotenv

load_dotenv(Path(__file__).with_name(".env"))  # real environment variables win over .env

BASE = os.getenv("LLM_BASE_URL", "https://generativelanguage.googleapis.com/v1beta/openai").strip().rstrip("/")
API_KEY = os.getenv("LLM_API_KEY", "").strip()
MODEL = os.getenv("LLM_MODEL", "gemini-flash-latest").strip()
JSON_MODE = os.getenv("LLM_JSON_MODE", "true").strip().lower() != "false"
TIMEOUT = float(os.getenv("LLM_TIMEOUT", "45"))
TRUST_ENV = os.getenv("LLM_TRUST_ENV", "true").strip().lower() != "false"   # false = ignore Windows/system proxy settings
REASONING = os.getenv("LLM_REASONING_EFFORT", "low" if "googleapis" in BASE else "").strip().lower()
SITE_URL = os.getenv("LLM_SITE_URL", "").strip()
APP_NAME = os.getenv("LLM_APP_NAME", "TripMind AI").strip()

class LLMError(RuntimeError):
    pass

def _host(): return (urlparse(BASE).hostname or "").lower()
def _is_local(): return _host() in ("127.0.0.1", "localhost", "::1")
def _has_key(): return bool(API_KEY) and not API_KEY.lower().startswith("your-")
def configured() -> bool: return _has_key() or _is_local()

def label() -> str:
    h = _host()
    name = "gemini" if "googleapis" in h else "openrouter" if "openrouter" in h else "local" if _is_local() else h
    return f"{name}:{MODEL}"

def _explain(r: httpx.Response) -> str:
    body = r.text[:200].replace("\n", " ")
    hints = {401: "API key rejected - check LLM_API_KEY in .env", 403: "Access denied - check the API key and that the model is allowed",
             402: "No credits on this account", 404: "Model or URL not found - check LLM_MODEL and LLM_BASE_URL in .env",
             429: "Rate limit reached - wait a minute and try again"}
    return f"HTTP {r.status_code}: {hints.get(r.status_code, 'request failed')} ({body})"

async def chat(prompt: str, as_json: bool = False) -> str:
    if not configured():
        raise LLMError("LLM_API_KEY is empty. Open the .env file, paste your key and restart.")
    headers = {"Content-Type": "application/json"}
    if _has_key(): headers["Authorization"] = f"Bearer {API_KEY}"
    if SITE_URL: headers["HTTP-Referer"] = SITE_URL
    if APP_NAME: headers["X-Title"] = APP_NAME
    payload = {"model": MODEL, "temperature": 0.2, "messages": [{"role": "user", "content": prompt}]}
    if REASONING: payload["reasoning_effort"] = REASONING          # less "thinking" = much faster answers
    if as_json and JSON_MODE: payload["response_format"] = {"type": "json_object"}
    r, timeouts = None, 0
    async with httpx.AsyncClient(timeout=httpx.Timeout(TIMEOUT, connect=15), trust_env=TRUST_ENV) as c:
        for attempt in range(4):
            try:
                r = await c.post(f"{BASE}/chat/completions", json=payload, headers=headers)
            except httpx.TimeoutException:
                timeouts += 1
                if timeouts < 2: continue                           # one retry on a slow answer
                raise LLMError(f"The model did not answer within {TIMEOUT:.0f}s (twice). The free API may be busy or the model too slow. "
                               f"Try again in a minute, or choose a faster model in .env (run CHECK_LLM.bat to see the list).")
            except httpx.HTTPError as e:
                raise LLMError(f"Cannot reach {BASE} ({type(e).__name__}). Check your internet connection, VPN or firewall.")
            if r.status_code == 400:
                opt = next((k for k in ("reasoning_effort", "response_format") if k in payload), None)
                if opt: payload.pop(opt); continue                  # provider does not support this option: retry without it
            if r.status_code in (429, 500, 502, 503) and attempt < 3:
                await asyncio.sleep(3 * (attempt + 1)); continue    # rate limit / busy: wait and retry
            break
    if r is None or r.status_code >= 400:
        raise LLMError(_explain(r))
    try:
        return r.json()["choices"][0]["message"]["content"] or ""
    except Exception:
        raise LLMError(f"Unexpected reply from the API: {r.text[:150]}")

CHOOSE = """TASK=PLAN. You are the planner of a travel app. Choose ONLY from the options in DATA and refer to them by id.
If the budget is tight prefer cheaper options. Reply with ONLY JSON like:
{"flight": "F1", "hotels": {"budget": "H1", "medium": "H4", "luxury": "H7"},
 "days": [{"day": 1, "stops": ["P1", "P2", "P5"]}],
 "reasons": {"flight": "one sentence", "hotels": "one sentence", "route": "one sentence", "preferences": "one sentence"}}
PREFERENCES ARE IMPORTANT: read the user's preferences and pick places whose category matches them. If they ask for food,
include food places (at least one per day, a mix of local specialities). If they ask for parks or nature, include park places.
Same for beaches, shopping, culture, adventure and nightlife. Fill the remaining slots with must-see places.
Rules: hotel ids must match the tier they are listed under; use at most DAYS days and at most 4 places per day;
each place at most once; put places that are close (lat/lng) on the same day; in reasons.preferences say which places
satisfy the preferences (use place names).
DATA: PAYLOAD"""

NARRATE = """TASK=NARRATE. You are TripMind, a friendly travel assistant. Using ONLY the JSON below (never change or invent
numbers, hotels or places), write in plain text: 1) a 2-sentence budget verdict for the user's chosen tier and what the other
tiers mean, 2) a short day-wise itinerary following the 'route' (one line per stop; for food places say what to eat using the
note), 3) a line on how the user's preferences were covered, 4) three money-saving tips. Use simple words. No tables.
JSON: PAYLOAD"""

def _json(text: str) -> dict:
    t = text.strip()
    i, j = t.find("{"), t.rfind("}")
    if i != -1 and j > i:
        t = t[i:j + 1]
    return json.loads(t)

async def choose(payload: dict, days: int) -> dict:
    return _json(await chat(CHOOSE.replace("DAYS", str(days)).replace("PAYLOAD", json.dumps(payload)), as_json=True))

async def narrate(plan: dict) -> dict:
    keys = ("origin", "destination", "budget", "nights", "travelers", "chosen_tier", "tiers", "flight_used", "preferences")
    slim = {k: plan[k] for k in keys if k in plan}
    slim["route"] = [{"day": d["day"], "stops": [{"name": s["name"], "cat": s["cat"], "note": s["note"]} for s in d["stops"]]} for d in plan.get("route", [])]
    try:
        return {"text": (await chat(NARRATE.replace("PAYLOAD", json.dumps(slim)))).strip(), "source": label()}
    except Exception as e:
        t = plan["tiers"][plan["chosen_tier"]]
        names = [s["name"] for d in plan.get("route", []) for s in d["stops"]]
        return {"text": (f"[LLM unavailable: {e}] Template summary: your {plan['chosen_tier']} plan costs Rs {t['total']:,} vs "
                         f"budget Rs {plan['budget']:,} -> {t['verdict'].upper()}. Route: {', '.join(names)}."), "source": "template-fallback"}
