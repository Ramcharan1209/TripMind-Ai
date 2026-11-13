"""Deterministic, Decimal-safe budget math. The LLM never does the arithmetic."""
from decimal import Decimal as D
from math import ceil

DAILY_PP = {"budget": D(800), "medium": D(1600), "luxury": D(4000)}  # food + local transport / person / day
MISC = D("0.05")

def evaluate(flights, hotels, places, travelers, nights, budget, flight=None, hotels_choice=None):
    budget = D(str(budget))
    opt = next((o for o in flights["options"] if o["airline"] == flight), None) or min(flights["options"], key=lambda o: o["total"])
    flight_cost = D(opt["total"])
    attractions = sum(D(p["cost_pp"]) for p in places["places"]) * travelers
    rooms = ceil(travelers / 2)
    tiers = {}
    for tier in ("budget", "medium", "luxury"):
        hotel = next((h for h in hotels[tier] if h["name"] == (hotels_choice or {}).get(tier)), None) or min(hotels[tier], key=lambda h: h["per_night"])
        stay = D(hotel["per_night"]) * rooms * nights
        food = DAILY_PP[tier] * travelers * (nights + 1)
        sub = flight_cost + stay + food + attractions
        total = (sub * (1 + MISC)).quantize(D(1))
        ratio = total / budget if budget else D(0)
        verdict = "over" if total > budget else ("perfect" if ratio >= D("0.9") else "under")
        tiers[tier] = {
            "hotel": hotel["name"], "alt_hotels": [h["name"] for h in hotels[tier] if h["name"] != hotel["name"]],
            "rooms": rooms,
            "breakdown": {"flights": int(flight_cost), "hotel": int(stay), "food_local_transport": int(food),
                          "attractions": int(attractions), "misc_5pct": int(total - sub)},
            "total": int(total), "difference": int(budget - total), "verdict": verdict,
        }
    return {"flight_used": opt["airline"], "budget": int(budget), "nights": nights, "travelers": travelers, "tiers": tiers}
