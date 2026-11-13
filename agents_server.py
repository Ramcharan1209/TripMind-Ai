"""A2A agents (Agent Cards + JSON-RPC message/send) on :9000. Data agents call the MCP server."""
from uuid import uuid4
from fastapi import FastAPI, Request
import uvicorn
from mcp_client import call_tool
import budget

BASE = "http://127.0.0.1:9000"

def make_agent(key, name, desc, handler):
    app = FastAPI()
    def card():
        return {"name": name, "description": desc, "url": f"{BASE}/{key}/", "version": "1.0.0",
                "protocolVersion": "0.3.0", "capabilities": {"streaming": False},
                "defaultInputModes": ["application/json"], "defaultOutputModes": ["application/json"],
                "skills": [{"id": key, "name": name, "description": desc, "tags": ["travel"]}]}
    app.get("/.well-known/agent-card.json")(card)
    app.get("/.well-known/agent.json")(card)

    @app.post("/")
    async def rpc(req: Request):
        body = await req.json()
        parts = body["params"]["message"]["parts"]
        inp = next(p["data"] for p in parts if p.get("kind") == "data")
        try:
            out = await handler(inp)
        except Exception as e:
            return {"jsonrpc": "2.0", "id": body.get("id"), "error": {"code": -32000, "message": f"{type(e).__name__}: {e}"}}
        return {"jsonrpc": "2.0", "id": body.get("id"),
                "result": {"kind": "message", "role": "agent", "messageId": str(uuid4()),
                           "parts": [{"kind": "data", "data": out}]}}
    return app

async def flight(i): return await call_tool("search_flights", {"origin": i["origin"], "destination": i["destination"], "travelers": i["travelers"]})
async def hotel(i): return await call_tool("search_hotels", {"destination": i["destination"]})
async def places(i): return await call_tool("get_places", {"destination": i["destination"]})
async def budg(i): return budget.evaluate(i["flights"], i["hotels"], i["places"], i["travelers"], i["nights"], i["budget"], i.get("flight"), i.get("hotels_choice"))

root = FastAPI()
root.mount("/flight", make_agent("flight", "Flight Agent", "Finds round-trip flight options via MCP", flight))
root.mount("/hotel", make_agent("hotel", "Hotel Agent", "Finds budget/medium/luxury hotels via MCP", hotel))
root.mount("/places", make_agent("places", "Places Agent", "Finds attractions and costs via MCP", places))
root.mount("/budget", make_agent("budget", "Budget Agent", "Computes costs and under/perfect/over verdict", budg))

if __name__ == "__main__":
    uvicorn.run(root, host="127.0.0.1", port=9000)
