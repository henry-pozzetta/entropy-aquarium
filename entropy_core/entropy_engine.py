# entropy_engine.py
import numpy as np
from collections import deque

class EntropyEngine:
    def __init__(self, window=128, bins=32, dt=0.1):
        self.window = window
        self.bins = bins
        self.dt = dt
        self.buf = deque(maxlen=window)
        self.prev_H = None
        self.prev_dH = None

    def _entropy01(self, arr):
        # Histogram → probabilities → normalized Shannon entropy in [0,1]
        hist, _ = np.histogram(arr, bins=self.bins, range=(0.0, 1.0))
        probs = hist / hist.sum() if hist.sum() else np.zeros_like(hist, dtype=float)
        nz = probs[probs > 0]
        H = -(nz * np.log2(nz)).sum()
        Hmax = np.log2(self.bins) if self.bins > 1 else 1.0
        return H / Hmax if Hmax else 0.0

    def step(self, x):
        self.buf.append(x)
        if len(self.buf) < max(8, self.window // 4):
            return None  # warmup
        H = self._entropy01(np.fromiter(self.buf, dtype=float))

        # finite differences with simple smoothing
        if self.prev_H is None:
            dH = 0.0
            ddH = 0.0
        else:
            dH = (H - self.prev_H) / self.dt
            if self.prev_dH is None:
                ddH = 0.0
            else:
                ddH = (dH - self.prev_dH) / self.dt

        self.prev_dH, self.prev_H = dH, H
        return H, dH, ddH

