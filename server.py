import asyncio, websockets, json

# Rooms structure: { "773834": { "host": ws, "users": {ws: {"name": "User1", "muted": False}} } }
rooms = {}

async def handler(ws):
    current_room = None
    try:
        async for msg in ws:
            data = json.loads(msg)
            m_type = data.get("type")

            if m_type == "join_room":
                room_id = data["room"]
                if room_id not in rooms:
                    rooms[room_id] = {"host": ws, "users": {}}
                
                if len(rooms[room_id]["users"]) >= 8:
                    await ws.send(json.dumps({"type": "error", "msg": "Qolku waa buuxaa (Max 8)"}))
                    continue

                rooms[room_id]["users"][ws] = {"muted": False}
                current_room = room_id
                
                # Ogeysii dadka kale
                for client in rooms[room_id]["users"]:
                    await client.send(json.dumps({"type": "user_joined", "count": len(rooms[room_id]["users"])}))

            elif m_type == "control": # Host-ka oo mute-gareynaya qof
                if rooms[current_room]["host"] == ws:
                    target_ws = data["target"] # Tani waxay u baahan tahay ID-yada ws
                    # ... logic-ga xakamaynta ...

            elif m_type in ["offer", "answer", "ice"]:
                # Isu gudbi WebRTC signaling-ka dadka qolka ku jira
                for client in rooms[current_room]["users"]:
                    if client != ws:
                        await client.send(msg)

    finally:
        if current_room in rooms:
            del rooms[current_room]["users"][ws]
            if not rooms[current_room]["users"]:
                del rooms[current_room]

asyncio.run(websockets.serve(handler, "0.0.0.0", 10000))
