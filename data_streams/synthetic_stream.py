# synthetic_stream.py
# Generates a bounded stream with occasional spikes/regime shifts
import math, random, time

def synthetic_stream(period_s=5.0, dt=0.1, noise=0.05, spike_prob=0.02):
    t = 0.0
    base = random.random()  # shift phase
    while True:
        # Smooth oscillation in [0,1]
        val = 0.5 + 0.45 * math.sin(2*math.pi*(t/period_s + base))
        val += random.uniform(-noise, noise)
        val = max(0.0, min(1.0, val))
        # Rare chaos injection
        if random.random() < spike_prob:
            val = random.random()
        yield time.time(), val
        time.sleep(dt)
        t += dt

