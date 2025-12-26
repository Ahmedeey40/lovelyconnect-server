import asyncio, websockets, json, random

clients = {}

def gen():
    return str(random.randint(100000,999999))

async def handler(ws):
    code=None
    async for msg in ws:
        d=json.loads(msg)

        if d["type"]=="create":
            code=gen()
            clients[code]=[ws]
            await ws.send(json.dumps({"type":"code","code":code}))

        elif d["type"]=="join":
            code=d["code"]
            if code in clients:
                clients[code].append(ws)
                await clients[code][0].send(json.dumps({"type":"request"}))

        elif d["type"] in ["offer","answer","ice","accept"]:
            for c in clients.get(code,[]):
                if c!=ws:
                    await c.send(msg)

asyncio.run(websockets.serve(handler,"0.0.0.0",10000))
