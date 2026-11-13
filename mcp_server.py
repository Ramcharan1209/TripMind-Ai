"""MCP server: exposes travel data as tools (streamable HTTP on :9100/mcp)."""
import logging
from mcp.server.fastmcp import FastMCP
import data

mcp = FastMCP("tripmind-travel-data", host="127.0.0.1", port=9100, log_level="ERROR")
logging.getLogger("mcp.server.streamable_http").setLevel(logging.CRITICAL)  # hides harmless session-close noise

@mcp.tool()
def search_flights(origin: str, destination: str, travelers: int) -> dict:
    """Round-trip economy flight options with indicative fares (INR)."""
    base = data.BASE_FARE.get((origin, destination))
    if base is None:
        return {"error": f"No route data for {origin} -> {destination}"}
    opts = [{"airline": a, "per_person": round(base * m / 50) * 50, "total": round(base * m / 50) * 50 * travelers}
            for a, m in data.AIRLINES]
    return {"airport": data.AIRPORT[destination], "options": sorted(opts, key=lambda o: o["total"])}

@mcp.tool()
def search_hotels(destination: str) -> dict:
    """Real hotels grouped by tier (budget/medium/luxury) with indicative nightly room rates (INR)."""
    h = data.HOTELS.get(destination)
    if not h:
        return {"error": f"No hotel data for {destination}"}
    return {t: [{"name": n, "per_night": p, "lat": la, "lng": lo} for n, p, la, lo in v] for t, v in h.items()}

@mcp.tool()
def get_places(destination: str) -> dict:
    """Places to visit with per-person entry/activity cost and coordinates."""
    p = data.PLACES.get(destination)
    if not p:
        return {"error": f"No places for {destination}"}
    return {"places": [{"name": n, "cost_pp": c, "cat": cat, "must": mu, "lat": la, "lng": lo, "note": nt} for n, c, cat, mu, la, lo, nt in p]}

if __name__ == "__main__":
    mcp.run(transport="streamable-http")
