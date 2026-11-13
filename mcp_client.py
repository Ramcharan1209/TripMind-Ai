import json
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

URL = "http://127.0.0.1:9100/mcp"

async def call_tool(name: str, args: dict) -> dict:
    async with streamablehttp_client(URL) as (r, w, _):
        async with ClientSession(r, w) as s:
            await s.initialize()
            res = await s.call_tool(name, args)
            return res.structuredContent or json.loads(res.content[0].text)
