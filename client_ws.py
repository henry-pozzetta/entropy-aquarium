import argparse
import asyncio
import json

import websockets


def parse_args():
    p = argparse.ArgumentParser(description="Entropy Aquarium WS client")
    p.add_argument("--url", default="ws://127.0.0.1:8765", help="WebSocket URL")
    p.add_argument("--source", choices=["synthetic", "weather", "stocks"], default=None,
                   help="Request a specific source after connect")
    p.add_argument("--frames", type=int, default=20, help="How many frames to print before exiting")
    return p.parse_args()


async def main():
    args = parse_args()
    async with websockets.connect(args.url) as ws:
        if args.source:
            await ws.send(json.dumps({"action": "switch", "source": args.source}))

        frames_seen = 0
        while frames_seen < args.frames:
            msg = await ws.recv()
            try:
                data = json.loads(msg)
            except Exception:
                print("NON-JSON:", msg)
                continue

            mtype = data.get("type")
            if mtype == "notice":
                print(f"[NOTICE] {data.get('message')} (source={data.get('source')})")
                continue
            if mtype != "frame":
                print("[UNKNOWN]", data)
                continue

            # Frame printing
            H, dH, ddH = data["arrow_vector"]
            mag = data["arrow_magnitude"]
            head = data["arrow_heading_deg"]
            az, el = head["azimuth"], head["elevation"]
            src = data.get("source", "?")

            print(
                f"EEFrame H={H:.3f} dH={dH:+.3f} ddH={ddH:+.3f} mag={mag:.3f} "
                f"heading=({az:.1f}°, {el:.1f}°) src={src}"
            )
            frames_seen += 1


if __name__ == "__main__":
    asyncio.run(main())
