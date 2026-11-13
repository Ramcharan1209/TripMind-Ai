"""Orchestrator: A2A agents collect options, the LLM parses/chooses/plans, code validates and recalculates the budget."""
import asyncio, datetime as dt, httpx
from pathlib import Path
from math import ceil, hypot
from uuid import uuid4
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
import data, llm

A2A = "http://127.0.0.1:9000"
TIERS = ("budget", "medium", "luxury")
app = FastAPI(title="TripMind AI")

class PlanReq(BaseModel):
    origin: str
    destination: str
    start_date: dt.date
    end_date: dt.date
    travelers: int = Field(ge=1, le=20)
    budget: int = Field(gt=0)
    hotel_tier: str = "medium"
    preferences: str = ""

async def ask(agent: str, payload: dict) -> dict:
    body = {"jsonrpc": "2.0", "id": str(uuid4()), "method": "message/send",
            "params": {"message": {"kind": "message", "role": "user", "messageId": str(uuid4()),
                                   "parts": [{"kind": "data", "data": payload}]}}}
    try:
        async with httpx.AsyncClient(timeout=60) as c:
            r = await c.post(f"{A2A}/{agent}/", json=body)
            r.raise_for_status()
            j = r.json()
    except httpx.HTTPError:
        raise HTTPException(503, "Agent service not reachable. Close everything, run START.bat again and read the black window for errors.")
    if "error" in j:
        raise HTTPException(502, f"{agent} agent failed: {j['error']['message'][:200]}")
    return j["result"]["parts"][0]["data"]

CAT_WORDS = {
    "food": ["food", "eat", "restaurant", "cafe", "caf", "cuisine", "seafood", "thali", "dining", "breakfast", "lunch", "dinner", "snack", "sweet", "biryani", "street food"],
    "park": ["park", "garden", "nature", "wildlife", "waterfall", "lake", "bird", "green", "forest"],
    "beach": ["beach", "sea", "coast", "sand"],
    "shopping": ["shop", "market", "bazaar", "souvenir", "mall"],
    "culture": ["temple", "palace", "heritage", "history", "museum", "culture", "church", "historic"],
    "adventure": ["adventure", "trek", "sport", "paraglid", "ski", "raft", "thrill"],
    "nightlife": ["night", "party", "club", "bar", "pub", "lounge"],
    "sightseeing": ["sightseeing", "fort", "view", "sunset"],
}

def pref_cats(prefs):
    t = (prefs or "").lower()
    return {c for c, ws in CAT_WORDS.items() if any(w in t for w in ws)}

def select_places(places, prefs, days):
    """Rule-based fallback: places matching the preferences first, then must-see places."""
    cats = pref_cats(prefs)
    n = min(len(places), max(3, days * 3))
    ranked = sorted(places, key=lambda p: -((2 if p["cat"] in cats else 0) + (1 if p["must"] else 0)))
    return ranked[:n]

def build_route(places, days):
    pts, order = list(places), []
    order.append(pts.pop(0))
    while pts:
        last = order[-1]
        nxt = min(pts, key=lambda p: hypot(p["lat"] - last["lat"], p["lng"] - last["lng"]))
        pts.remove(nxt); order.append(nxt)
    days = max(1, min(days, len(order)))
    size = ceil(len(order) / days)
    chunks = [order[i * size:(i + 1) * size] for i in range(days)]
    return [{"day": i + 1, "stops": c} for i, c in enumerate(chunks) if c]

@app.get("/api/meta")
def meta(): return {"cities": data.CITIES, "destinations": data.DESTINATIONS}

@app.get("/api/health")
def health(): return {"llm": llm.label(), "configured": llm.configured()}

@app.post("/api/plan")
async def plan(q: PlanReq):
    nights = (q.end_date - q.start_date).days
    if nights < 1 or q.origin == q.destination or q.hotel_tier not in TIERS:
        raise HTTPException(400, "Check dates (at least 1 night), cities (from and to must differ) and hotel tier.")
    base = {"origin": q.origin, "destination": q.destination, "travelers": q.travelers}
    flights, hotels, places = await asyncio.gather(ask("flight", base), ask("hotel", base), ask("places", base))
    for x in (flights, hotels, places):
        if "error" in x: raise HTTPException(400, x["error"])
    selected = select_places(places["places"], q.preferences, nights + 1)
    result = await ask("budget", {"flights": flights, "hotels": hotels, "places": {"places": selected},
                                  "travelers": q.travelers, "nights": nights, "budget": q.budget})
    result.update(chosen_tier=q.hotel_tier, flights=flights, hotels=hotels, places=places["places"],
                  origin=q.origin, destination=q.destination, preferences=q.preferences,
                  price_note="Prices are indicative estimates, not live quotes.",
                  route=build_route(selected, nights + 1))
    return result

def _n(s): return str(s).strip().lower()

def validate_choice(raw, fid, hid, pid, hotels, nights, prefs):
    """Never trust the LLM blindly: ids/names must exist, otherwise fall back to cheapest / proximity plan."""
    notes = []
    tok = _n(raw.get("flight", ""))
    fl = next((a for k, a in fid.items() if _n(k) == tok or _n(a) == tok), None)
    if not fl:
        fl = next(iter(fid.values())); notes.append("flight choice invalid, cheapest used")
    hraw = raw.get("hotels") if isinstance(raw.get("hotels"), dict) else {}
    hch = {}
    for t in TIERS:
        tok = _n(hraw.get(t, ""))
        name = next((nm for k, (tt, nm) in hid.items() if tt == t and (_n(k) == tok or _n(nm) == tok)), None)
        if not name:
            name = min(hotels[t], key=lambda h: h["per_night"])["name"]; notes.append(f"{t} hotel choice invalid, cheapest used")
        hch[t] = name
    byname = {_n(p["name"]): p for p in pid.values()}
    used, days = set(), []
    for d in raw.get("days") if isinstance(raw.get("days"), list) else []:
        stops = []
        for s in (d.get("stops") if isinstance(d, dict) and isinstance(d.get("stops"), list) else []):
            p = next((pl for k, pl in pid.items() if _n(k) == _n(s)), None) or byname.get(_n(s))
            if p and p["name"] not in used:
                used.add(p["name"]); stops.append(p)
        if stops: days.append(stops[:4])
    days = days[:nights + 1]
    places = list(pid.values())
    if not days:
        notes.append("route invalid, preference-based route used")
        return fl, hch, build_route(select_places(places, prefs, nights + 1), nights + 1), notes
    return fl, hch, [{"day": i + 1, "stops": s} for i, s in enumerate(days)], notes

@app.post("/api/llm-plan")
async def llm_plan(plan: dict):
    nights = plan["nights"]
    fid = {f"F{i + 1}": o["airline"] for i, o in enumerate(plan["flights"]["options"])}
    hid, hpay, n = {}, {}, 1
    for t in TIERS:
        hpay[t] = []
        for h in plan["hotels"][t]:
            hid[f"H{n}"] = (t, h["name"])
            hpay[t].append({"id": f"H{n}", "name": h["name"], "per_night_inr": h["per_night"]}); n += 1
    pid = {f"P{i + 1}": p for i, p in enumerate(plan["places"])}
    payload = {"preferences": plan.get("preferences", ""), "budget_inr": plan["budget"], "travelers": plan["travelers"], "nights": nights,
               "flights": [{"id": f"F{i + 1}", "airline": o["airline"], "total_inr": o["total"]} for i, o in enumerate(plan["flights"]["options"])],
               "hotels": hpay,
               "places": [{"id": k, "name": p["name"], "category": p["cat"], "must_see": p["must"], "cost_pp": p["cost_pp"], "note": p["note"], "lat": p["lat"], "lng": p["lng"]} for k, p in pid.items()]}
    try:
        raw = await llm.choose(payload, nights + 1)
        if not isinstance(raw, dict): raise ValueError("answer was not a JSON object")
    except Exception as e:
        return {"tiers": plan["tiers"], "flight_used": plan.get("flight_used"), "route": plan["route"],
                "llm": {"ok": False, "error": f"{e}"[:250]}}
    fl, hch, route, notes = validate_choice(raw, fid, hid, pid, plan["hotels"], nights, plan.get("preferences", ""))
    res = await ask("budget", {"flights": plan["flights"], "hotels": plan["hotels"], "places": {"places": [p for d in route for p in d["stops"]]},
                               "travelers": plan["travelers"], "nights": nights, "budget": plan["budget"],
                               "flight": fl, "hotels_choice": hch})
    rs = raw.get("reasons") if isinstance(raw.get("reasons"), dict) else {}
    return {"tiers": res["tiers"], "flight_used": res["flight_used"], "route": route,
            "llm": {"ok": True, "source": llm.label(), "notes": notes,
                    "reasons": {k: str(rs.get(k, ""))[:300] for k in ("flight", "hotels", "route", "preferences")}}}

@app.post("/api/narrate")
async def narrate(plan: dict):
    return await llm.narrate(plan)

@app.get("/")
def index(): return FileResponse(Path(__file__).with_name("static").joinpath("index.html"))
