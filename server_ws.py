# server_ws.py
import asyncio
import json
import math
import random
from typing import Dict, Set

import websockets  # ensure installed in venv: pip install websockets

from entropy_core.entropy_engine import EntropyEngine
from frames.eeframe_generator import make_aquarium_eeframe


# ----------------------------- Stream Generators -----------------------------
# All streams here are async generators yielding a single float in [0,1].

async def stream_synthetic(dt: float = 0.1):
    t = 0.0
    phase = random.random()
    while True:
        val = 0.5 + 0.45 * math.sin(2 * math.pi * (t / 5.0 + phase))
        val += random.uniform(-0.05, 0.05)
        if random.random() < 0.02:  # rare chaos injection
            val = random.random()
        val = max(0.0, min(1.0, val))
        yield val
        await asyncio.sleep(dt)
        t += dt

async def stream_weather(dt: float = 0.5):
    # Placeholder: smooth, slower drift (swap with real API sampling later)
    t = 0.0
    while True:
        val = 0.45 + 0.2 * math.sin(t / 15.0) + random.uniform(-0.02, 0.02)
        val = max(0.0, min(1.0, val))
        yield val
        await asyncio.sleep(dt)
        t += dt

async def stream_stocks(dt: float = 0.2):
    # Placeholder: choppier movement with occasional spikes
    drift = 0.0
    while True:
        drift += random.uniform(-0.02, 0.02)
        drift = max(-0.3, min(0.3, drift))
        val = 0.5 + drift + random.uniform(-0.05, 0.05)
        if random.random() < 0.02:
            val = random.random()
        val = max(0.0, min(1.0, val))
        yield val
        await asyncio.sleep(dt)


STREAMS = {
    "synthetic": {"fn": stream_synthetic, "dt": 0.1},
    "weather":   {"fn": stream_weather,   "dt": 0.5},
    "stocks":    {"fn": stream_stocks,    "dt": 0.2},
}


# ------------------------------- Server Logic --------------------------------
class AquariumServer:
    def __init__(self):
        self.source: str = "synthetic"
        self.clients: Set[websockets.WebSocketServerProtocol] = set()
        self.epoch: int = 0  # increments whenever source changes
        self.broadcast_task: asyncio.Task | None = None

    def set_source(self, name: str) -> str:
        new_src = name if name in STREAMS else "synthetic"
        if new_src != self.source:
            self.source = new_src
            self.epoch += 1  # trigger broadcaster to restart with new stream
        return self.source

    async def start(self):
        # Ensure a broadcaster task is running
        if not self.broadcast_task or self.broadcast_task.done():
            self.broadcast_task = asyncio.create_task(self._broadcaster())

    async def handler(self, websocket: websockets.WebSocketServerProtocol):
        self.clients.add(websocket)
        try:
            # greet with current status
            await websocket.send(json.dumps({
                "type": "notice",
                "message": "connected",
                "source": self.source,
                "sources": list(STREAMS.keys()),
            }))

            # process incoming control messages
            async for raw in websocket:
                try:
                    data = json.loads(raw)
                except Exception:
                    continue
                if data.get("action") == "switch":
                    new_src = self.set_source(data.get("source", "synthetic"))
                    # notify all clients
                    await self._broadcast({
                        "type": "notice",
                        "message": f"switched to {new_src}",
                        "source": new_src,
                    })
        finally:
            self.clients.discard(websocket)

    async def _broadcaster(self):
        """Continuously produce frames for the active source and broadcast."""
        while True:
            epoch = self.epoch
            cfg = STREAMS.get(self.source, STREAMS["synthetic"])
            dt = cfg["dt"]
            gen = cfg["fn"](dt=dt)
            engine = EntropyEngine(window=128, bins=32, dt=dt)

            async for val in gen:
                # If the source changed, restart the loop with new stream/engine
                if epoch != self.epoch:
                    break

                out = engine.step(val)
                if out is None:
                    continue  # warmup

                H, dH, ddH = out
                frame = make_aquarium_eeframe(H, dH, ddH, source_label=self.source)
                frame.update({
                    "type": "frame",
                    "stats": {"bins": 32, "window": 128, "rate_hz": round(1.0 / dt, 2)},
                })
                await self._broadcast(frame)

    async def _broadcast(self, payload: Dict):
        if not self.clients:
            return
        msg = json.dumps(payload)
        dead = []
        for ws in self.clients:
            try:
                await ws.send(msg)
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.clients.discard(ws)


async def main():
    server = AquariumServer()
    await server.start()
    async with websockets.serve(server.handler, "127.0.0.1", 8765, ping_interval=20, ping_timeout=20):
        print("Aquarium WS server on ws://127.0.0.1:8765  (sources: synthetic | weather | stocks)")
        await asyncio.Future()  # run forever


if __name__ == "__main__":
    asyncio.run(main())
