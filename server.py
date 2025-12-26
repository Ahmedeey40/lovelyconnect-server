import asyncio
import websockets
import json
import random

# Waxaan u habaynay inaan aqoonsanno qof walba ws-kiisa
clients = {} # {code: [ws1, ws2]}

def generate_code():
    return str(random.randint(100000, 999999))

async def handler(ws):
    current_code = None
    try:
        async for msg in ws:
            data = json.loads(msg)
            m_type = data.get("type")

            # 1. Sameynta Code cusub
            if m_type == "create":
                # Haddii uu hore code u lahaa, ka saar kii hore
                if current_code in clients:
                    del clients[current_code]
                
                current_code = generate_code()
                clients[current_code] = [ws]
                await ws.send(json.dumps({"type": "code", "code": current_code}))

            # 2. Ku biirista code jira
            elif m_type == "join":
                code = data.get("code")
                if code in clients:
                    current_code = code
                    # Haddii uu qof kale horay ugu jiray, la soco
                    if ws not in clients[current_code]:
                        clients[current_code].append(ws)
                    
                    # Ogeysii qofka koowaad (Host-ka) in qof rabo inuu ku soo biiro
                    await clients[current_code][0].send(json.dumps({"type": "request"}))
                else:
                    await ws.send(json.dumps({"type": "error", "message": "Code-kan ma jiro!"}))

            # 3. Isu gudbinta xogta (WebRTC Signaling & Chat)
            elif m_type in ["offer", "answer", "ice", "accept", "draw", "msg", "clear"]:
                if current_code in clients:
                    # U dir fariinta qofka kale ee isla code-ka kula jira
                    for client in clients[current_code]:
                        if client != ws and client.open:
                            await client.send(msg)

    except websockets.exceptions.ConnectionClosed:
        print("Xiriir ayaa go'ay")
    finally:
        # Marka uu qofka ka baxo, nadiifi clients-ka
        if current_code in clients:
            if ws in clients[current_code]:
                clients[current_code].remove(ws)
            if not clients[current_code]:
                del clients[current_code]

async def main():
    # Dekedda 10000 waa mida Render inta badan isticmaalo
    async with websockets.serve(handler, "0.0.0.0", 10000):
        print("LovelyConnect Server is running on port 10000...")
        await asyncio.Future()  # Si joogto ah u shaqee

if name == "main":
    asyncio.run(main())
