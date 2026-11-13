"""Tests your .env: network/proxy, then finds the fastest working model and can save it to .env."""
import asyncio, re, time
from pathlib import Path
import httpx, llm

ENV = Path(__file__).with_name(".env")
SKIP = ("image", "tts", "live", "audio", "embedding", "robotics", "computer", "native", "veo", "imagen", "gemma")

def hdr(): return {"Authorization": f"Bearer {llm.API_KEY}"} if llm._has_key() else {}

async def ping(model, trust_env, timeout=25.0, effort="low"):
    body = {"model": model, "temperature": 0.2, "messages": [{"role": "user", "content": "Reply with the single word OK."}]}
    if effort: body["reasoning_effort"] = effort
    t = time.time()
    try:
        async with httpx.AsyncClient(timeout=httpx.Timeout(timeout, connect=10), trust_env=trust_env) as c:
            r = await c.post(f"{llm.BASE}/chat/completions", json=body, headers=hdr())
            if r.status_code == 400 and effort:
                body.pop("reasoning_effort"); r = await c.post(f"{llm.BASE}/chat/completions", json=body, headers=hdr())
        return time.time() - t, ("OK" if r.status_code == 200 else f"HTTP {r.status_code}")
    except httpx.TimeoutException:
        return time.time() - t, "TIMEOUT"
    except Exception as e:
        return time.time() - t, type(e).__name__

def save(key, value):
    if not ENV.exists(): ENV.write_text(Path(__file__).with_name(".env.example").read_text())
    txt = ENV.read_text()
    new = f"{key}={value}"
    txt = re.sub(rf"(?m)^{key}=.*$", new, txt) if re.search(rf"(?m)^{key}=", txt) else txt.rstrip() + "\n" + new + "\n"
    ENV.write_text(txt); print(f"Saved to .env: {new}  (restart START.bat to use it)")

def ask(q):
    try: return input(q).strip().lower().startswith("y")
    except EOFError: return False

async def main():
    print(f"Base URL : {llm.BASE}\nModel    : {llm.MODEL}\nKey      : {'found' if llm._has_key() else 'MISSING' if not llm._is_local() else 'not needed (local)'}\n")
    if not llm.configured():
        print("Open the .env file (EDIT_KEY.bat), paste your API key after LLM_API_KEY= and run this again."); return
    print("STEP 1: network test with your configured model (up to 25s each)...")
    a, b = await asyncio.gather(ping(llm.MODEL, True), ping(llm.MODEL, False))
    print(f"  using system/proxy settings : {a[1]:8s} {a[0]:5.1f}s")
    print(f"  ignoring proxy (direct)     : {b[1]:8s} {b[0]:5.1f}s")
    trust = True
    if a[1] != "OK" and b[1] == "OK":
        print("  -> A proxy/VPN/firewall is slowing your normal connection. Direct works."); trust = False
        if ask("  Save LLM_TRUST_ENV=false to .env? (y/n): "): save("LLM_TRUST_ENV", "false")
    elif a[1] != "OK" and b[1] != "OK":
        print("  -> Both failed. Try another network (mobile hotspot), check the key, or the model name in STEP 2.")
    print("\nSTEP 2: testing flash models to find the fastest one...")
    try:
        r = httpx.get(f"{llm.BASE}/models", headers=hdr(), timeout=30, trust_env=trust)
        ids = [m.get("id", "").removeprefix("models/") for m in r.json().get("data", [])] if r.status_code == 200 else []
    except Exception as e:
        ids = []; print(f"  could not list models ({type(e).__name__})")
    cands = [i for i in ids if "flash" in i and not any(s in i for s in SKIP)][:8]
    if llm.MODEL not in cands: cands.insert(0, llm.MODEL)
    res = await asyncio.gather(*[ping(m, trust) for m in cands])
    rows = sorted(zip(cands, res), key=lambda x: (x[1][1] != "OK", x[1][0]))
    for m, (t, st) in rows: print(f"  {m:40s} {st:8s} {t:5.1f}s")
    ok = [(m, t) for m, (t, st) in rows if st == "OK"]
    if not ok:
        print("\nNo model answered. If you see HTTP 429, wait a minute (free-tier limit). If TIMEOUT everywhere, it's your network."); return
    best = ok[0][0]
    print(f"\nFastest working model: {best} ({ok[0][1]:.1f}s)")
    if best != llm.MODEL and ask(f"Save LLM_MODEL={best} to .env? (y/n): "): save("LLM_MODEL", best)
    print("\nDone. Use START.bat to run TripMind.")

asyncio.run(main())
