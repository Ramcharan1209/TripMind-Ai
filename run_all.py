"""Starts MCP server (9100), A2A agents (9000) and the web app (8000), waits until each is ready."""
import os, socket, subprocess, sys, time, webbrowser

os.chdir(os.path.dirname(os.path.abspath(__file__)))
procs = []

def up(port):
    with socket.socket() as s:
        s.settimeout(0.5)
        return s.connect_ex(("127.0.0.1", port)) == 0

def stop_all():
    for p in procs:
        if p.poll() is None: p.terminate()

def start(args, name, port):
    if up(port):
        print(f"ERROR: port {port} is already in use. Close the other TripMind window and try again."); stop_all(); sys.exit(1)
    p = subprocess.Popen([sys.executable] + args)
    procs.append(p)
    for _ in range(60):
        if p.poll() is not None:
            print(f"ERROR: {name} stopped while starting. Read the error above."); stop_all(); sys.exit(1)
        if up(port):
            print(f"  [ok] {name} (port {port})"); return
        time.sleep(0.5)
    print(f"ERROR: {name} did not start in time."); stop_all(); sys.exit(1)

print("Starting TripMind AI...")
start(["mcp_server.py"], "MCP server", 9100)
start(["agents_server.py"], "A2A agents", 9000)
start(["-m", "uvicorn", "app:app", "--port", "8000", "--log-level", "warning"], "Web app", 8000)
import llm
print(f"  LLM: {llm.label()}  " + ("(key found)" if llm.configured() else "(NO API KEY - open the .env file and paste your key)"))
print("\nTripMind is running at http://127.0.0.1:8000   (close this window or press Ctrl+C to stop)\n")
if not os.getenv("TRIPMIND_NO_BROWSER"):
    webbrowser.open("http://127.0.0.1:8000")
try:
    while all(p.poll() is None for p in procs):
        time.sleep(1)
except KeyboardInterrupt:
    pass
stop_all()
