# eeframe_generator.py
import math

def make_aquarium_eeframe(H, dH, ddH, source_label="Synthetic"):
    arrow_vector = [H, dH, ddH]
    magnitude = math.sqrt(H*H + dH*dH + ddH*ddH)
    az = math.degrees(math.atan2(dH, H)) if (H != 0 or dH != 0) else 0.0
    el = math.degrees(math.atan2(ddH, math.sqrt(H*H + dH*dH))) if (H != 0 or dH != 0 or ddH != 0) else 0.0
    opp = [-H, -dH, -ddH]
    # angle between vectors (arrow vs. opp): ideally ~180; handle zeros safely
    denom = magnitude * magnitude
    try:
        cosang = max(-1.0, min(1.0, (H*opp[0] + dH*opp[1] + ddH*opp[2]) / denom))
        offset = math.degrees(math.acos(cosang))
    except Exception:
        offset = 0.0
    return {
        "source": source_label,
        "arrow_vector": arrow_vector,
        "arrow_magnitude": magnitude,
        "arrow_heading_deg": {"azimuth": az, "elevation": el},
        "suggested_opp_vector": opp,
        "opp_angle_offset_deg": offset,
        "response_strategy_hint": "simple-reverse"
    }

