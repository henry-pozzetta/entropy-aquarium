# run.py
from data_streams.synthetic_stream import synthetic_stream
from entropy_core.entropy_engine import EntropyEngine
from frames.eeframe_generator import make_aquarium_eeframe

def main():
    engine = EntropyEngine(window=128, bins=32, dt=0.1)
    for ts, val in synthetic_stream(dt=0.1):
        out = engine.step(val)
        if out is None:
            continue
        H, dH, ddH = out
        frame = make_aquarium_eeframe(H, dH, ddH, source_label="Synthetic")
        # For now, print a compact line; later, push to WebSocket/visualizer
        print(f"H={H:.3f} dH={dH:+.3f} ddH={ddH:+.3f} "
              f"mag={frame['arrow_magnitude']:.3f} "
              f"heading=({frame['arrow_heading_deg']['azimuth']:.1f}°,"
              f"{frame['arrow_heading_deg']['elevation']:.1f}°)")

if __name__ == "__main__":
    main()

