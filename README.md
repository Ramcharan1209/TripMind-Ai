# TripMind AI

LLM travel planner: flights, hotels, places, day-wise route maps and an under / perfect / over budget verdict.

**Flow:** Browser -> FastAPI orchestrator -> **A2A** agents (Flight, Hotel, Places, Budget) -> **MCP** server (travel tools).
The **LLM** (Gemini free API by default) reads your preferences (food, parks, beaches, shopping...), chooses the flight, hotels
and matching places, plans the day-wise route and writes the final plan. Code validates every LLM answer (ids must exist) and
recalculates the budget from the places actually chosen.

## Run (Windows)
1. Extract the zip somewhere simple, e.g. `C:\TripMind` (right-click > Extract All).
2. Get a free Gemini key: https://aistudio.google.com/apikey
3. Double-click `EDIT_KEY.bat` (creates the `.env` file for you), replace `your-api-key-here` with your key, save.
   Your `.env` is never overwritten when you update the project files.
4. Double-click `CHECK_LLM.bat` (first run needs START.bat once) - it tells you if the key/model work.
5. Double-click `START.bat`. The browser opens at http://127.0.0.1:8000.

To use OpenRouter or another OpenAI-compatible API, change the 3 lines in `.env` (examples inside the file).

## Notes
- Hotels, airlines and places are real; prices are **indicative estimates** in `data.py`, not live quotes.
- Never share your `.env` file or key.
