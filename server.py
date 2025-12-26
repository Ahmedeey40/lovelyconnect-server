import asyncio, websockets, json, random

rooms = {} # {room_id: {host: ws, members: {ws: {name, muted}}, limit: 8}}

async def handler(ws):
    current_room = None
    try:
        async for msg in ws:
            d = json.loads(msg)
            m_type = d.get("type")

            if m_type == "create_team":
                rid = d["room"]
                rooms[rid] = {"host": ws, "members": {ws: {"muted": False}}, "limit": d["limit"]}
                current_room = rid
                await ws.send(json.dumps({"type": "joined", "role": "admin"}))

            elif m_type == "join_team":
                rid = d["room"]
                if rid in rooms and len(rooms[rid]["members"]) < rooms[rid]["limit"]:
                    rooms[rid]["members"][ws] = {"muted": False}
                    current_room = rid
                    await ws.send(json.dumps({"type": "joined", "role": "member"}))
                else:
                    await ws.send(json.dumps({"type": "error", "msg": "Qolka waa buuxaa ama ma jiro"}))

            elif m_type in ["mute_request", "kick_request", "sticker", "draw", "offer", "answer", "ice"]:
                if current_room in rooms:
                    for client in rooms[current_room]["members"]:
                        if client != ws: await client.send(msg)
    finally:
        if current_room in rooms:
            del rooms[current_room]["members"][ws]
            if not rooms[current_room]["members"]: del rooms[current_room]

asyncio.run(websockets.serve(handler, "0.0.0.0", 10000))
