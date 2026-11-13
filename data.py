"""Curated travel data. Hotels/places/airlines are real; prices are INDICATIVE (approx. INR, 2025-26)
and vary with season. Swap this module for Amadeus/Booking/Google Places calls for live prices."""
CITIES = ["Bengaluru", "Delhi", "Mumbai"]
DESTINATIONS = ["Goa", "Jaipur", "Manali"]

# approx. round-trip economy fare per person (INR) on the cheapest carrier
BASE_FARE = {
    ("Bengaluru", "Goa"): 7500, ("Bengaluru", "Jaipur"): 12000, ("Bengaluru", "Manali"): 16000,
    ("Delhi", "Goa"): 11000, ("Delhi", "Jaipur"): 6500, ("Delhi", "Manali"): 9500,
    ("Mumbai", "Goa"): 6500, ("Mumbai", "Jaipur"): 9000, ("Mumbai", "Manali"): 15000,
}
AIRLINES = [("IndiGo", 1.00), ("Akasa Air", 0.95), ("Air India Express", 0.98), ("SpiceJet", 0.93), ("Air India", 1.15)]
AIRPORT = {"Goa": "Goa (GOX/GOI)", "Jaipur": "Jaipur (JAI)", "Manali": "Kullu-Manali Bhuntar (KUU) / Chandigarh (IXC)"}

# (name, nightly rate per room INR, approx lat, approx lng) - real hotels, indicative prices, approximate map pins
HOTELS = {
    "Goa": {
        "budget": [("Zostel Goa (Anjuna)", 2200, 15.5736, 73.7407), ("goSTOPS Goa (Baga)", 2000, 15.5560, 73.7550), ("Hotel Mandovi (Panaji)", 3000, 15.4989, 73.8278)],
        "medium": [("Novotel Goa Candolim", 6500, 15.5170, 73.7620), ("Fairfield by Marriott Goa Benaulim", 7500, 15.2650, 73.9230), ("ibis Styles Goa Calangute", 4500, 15.5440, 73.7640)],
        "luxury": [("Grand Hyatt Goa", 14000, 15.4570, 73.8590), ("Taj Fort Aguada Resort & Spa", 22000, 15.4960, 73.7740), ("W Goa (Vagator)", 25000, 15.6020, 73.7350)],
    },
    "Jaipur": {
        "budget": [("Zostel Jaipur", 2000, 26.9300, 75.7900), ("Moustache Hostel Jaipur", 1800, 26.9170, 75.7880), ("Hotel Pearl Palace", 2500, 26.9140, 75.7910)],
        "medium": [("Hotel Clarks Amer", 6500, 26.8760, 75.8130), ("ITC Rajputana", 9000, 26.9080, 75.7910), ("Hotel Arya Niwas", 4500, 26.9120, 75.8050)],
        "luxury": [("Rambagh Palace", 45000, 26.8990, 75.8040), ("Taj Jai Mahal Palace", 15000, 26.9087, 75.7952), ("Fairmont Jaipur", 17000, 26.9740, 75.8520)],
    },
    "Manali": {
        "budget": [("Zostel Manali", 1800, 32.2590, 77.1760), ("The Hosteller Manali", 1700, 32.2610, 77.1770), ("goSTOPS Manali", 1900, 32.2430, 77.1890)],
        "medium": [("Snow Valley Resorts", 5500, 32.2410, 77.1900), ("Hotel Mountain Face", 4500, 32.2420, 77.1870), ("Apple Country Resort", 5000, 32.2400, 77.1830)],
        "luxury": [("The Himalayan", 10000, 32.2470, 77.1800), ("Span Resort & Spa", 11000, 32.2880, 77.1690), ("Manuallaya Resort Spa", 9500, 32.2410, 77.1840)],
    },
}
# (name, entry/activity cost per person INR, category, must_see, approx lat, approx lng, note)
# Real places; costs/prices are indicative. Food places cost 0 here because meals are covered by the daily food budget.
CATEGORIES = ["sightseeing", "culture", "beach", "park", "food", "shopping", "adventure", "nightlife"]
PLACES = {
    "Goa": [
        ("Baga Beach", 0, "beach", True, 15.5553, 73.7517, "Lively beach with water sports"),
        ("Basilica of Bom Jesus", 0, "culture", True, 15.5009, 73.9116, "UNESCO-listed church in Old Goa"),
        ("Fort Aguada", 0, "sightseeing", True, 15.4927, 73.7733, "17th-century Portuguese fort and lighthouse"),
        ("Chapora Fort", 0, "sightseeing", False, 15.6050, 73.7360, "Hilltop fort, good for sunset"),
        ("Dudhsagar Falls (jeep + entry)", 1000, "park", False, 15.3144, 74.3143, "Waterfall inside Mollem forest, jeep safari"),
        ("Salim Ali Bird Sanctuary", 50, "park", False, 15.5160, 73.9060, "Mangrove bird sanctuary on Chorao Island"),
        ("Anjuna Beach", 0, "beach", False, 15.5740, 73.7370, "Cliff-side beach with cafes"),
        ("Fontainhas (Latin Quarter)", 0, "culture", False, 15.4960, 73.8300, "Colourful Portuguese-era lanes in Panaji"),
        ("Britto's (Baga)", 0, "food", False, 15.5545, 73.7520, "Goan seafood on the beach, about Rs 700-1000 per person"),
        ("Souza Lobo (Calangute)", 0, "food", False, 15.5430, 73.7550, "Classic Goan seafood, about Rs 700-1000 per person"),
        ("Mum's Kitchen (Panaji)", 0, "food", False, 15.4940, 73.8260, "Traditional Goan thali and curries, about Rs 800-1200 per person"),
        ("Gunpowder (Assagao)", 0, "food", False, 15.5870, 73.7630, "Coastal South-Indian food in a garden, about Rs 800-1200 per person"),
        ("Arpora Saturday Night Market", 0, "shopping", False, 15.5640, 73.7790, "Seasonal night market with food stalls"),
        ("Tito's Lane (Baga)", 0, "nightlife", False, 15.5540, 73.7530, "Famous clubbing street"),
    ],
    "Jaipur": [
        ("Amber Fort", 500, "sightseeing", True, 26.9855, 75.8513, "Hill fort-palace, go early"),
        ("City Palace", 200, "culture", True, 26.9258, 75.8236, "Royal palace and museum"),
        ("Hawa Mahal", 50, "sightseeing", True, 26.9239, 75.8267, "Palace of Winds facade"),
        ("Jantar Mantar", 50, "culture", False, 26.9247, 75.8246, "18th-century astronomical observatory"),
        ("Nahargarh Fort", 50, "sightseeing", False, 26.9373, 75.8155, "City views at sunset"),
        ("Jal Mahal", 0, "sightseeing", False, 26.9535, 75.8460, "Palace in the middle of Man Sagar lake"),
        ("Albert Hall Museum", 40, "culture", False, 26.9118, 75.8190, "State museum in an Indo-Saracenic building"),
        ("Ram Niwas Garden", 10, "park", False, 26.9140, 75.8190, "Large city garden next to Albert Hall"),
        ("Sisodia Rani Garden", 50, "park", False, 26.8940, 75.8480, "Terraced Mughal-style garden and palace"),
        ("Laxmi Misthan Bhandar (LMB)", 0, "food", False, 26.9190, 75.8270, "Rajasthani sweets and thali, about Rs 400-700 per person"),
        ("Rawat Mishthan Bhandar", 0, "food", False, 26.9190, 75.7890, "Famous pyaaz kachori, about Rs 100-250 per person"),
        ("Chokhi Dhani", 0, "food", False, 26.7850, 75.8300, "Village-style Rajasthani dinner, about Rs 900-1200 per person"),
        ("Tapri Central", 0, "food", False, 26.9070, 75.8040, "Chai and snacks cafe, about Rs 300-500 per person"),
        ("Johari Bazaar", 0, "shopping", False, 26.9190, 75.8250, "Jewellery and textile market"),
    ],
    "Manali": [
        ("Solang Valley", 500, "adventure", True, 32.3160, 77.1590, "Paragliding, zorbing, skiing in winter (activities extra)"),
        ("Hadimba Temple", 0, "culture", True, 32.2480, 77.1800, "Cedar-forest temple"),
        ("Old Manali", 0, "sightseeing", True, 32.2590, 77.1790, "Riverside lanes and cafes"),
        ("Atal Tunnel & Sissu", 300, "sightseeing", False, 32.4830, 77.1270, "Long tunnel and Sissu valley"),
        ("Rohtang Pass (permit + taxi share)", 1500, "adventure", False, 32.3716, 77.2466, "Permit needed, closed in winter"),
        ("Van Vihar National Park", 20, "park", False, 32.2440, 77.1870, "Deodar park in the town"),
        ("Jogini Waterfalls (trek)", 0, "park", False, 32.2780, 77.1990, "Short trek from Vashisht"),
        ("Vashisht Hot Springs", 0, "culture", False, 32.2650, 77.1890, "Hot springs and temple"),
        ("Mall Road", 0, "shopping", False, 32.2410, 77.1890, "Shops and street food"),
        ("Johnson's Cafe (Old Manali)", 0, "food", False, 32.2570, 77.1790, "Trout and continental food, about Rs 800-1200 per person"),
        ("Cafe 1947 (Old Manali)", 0, "food", False, 32.2610, 77.1780, "Riverside cafe, about Rs 500-900 per person"),
        ("Chopsticks Restaurant", 0, "food", False, 32.2420, 77.1890, "Tibetan and Chinese food, about Rs 400-700 per person"),
        ("Lazy Dog Lounge (Old Manali)", 0, "nightlife", False, 32.2600, 77.1780, "Lounge bar"),
    ],
}
