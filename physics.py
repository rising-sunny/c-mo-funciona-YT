"""SI units. Ideal work balance, NOT a dynamic/contact simulation."""
import math


def quantities(p):
    if any(not math.isfinite(p[k]) or p[k] <= 0 for k in
           ('lead_m', 'handle_radius_m', 'hand_force_n', 'turns')):
        raise ValueError('Physical parameters must be finite and positive')
    torque = p['handle_radius_m'] * p['hand_force_n']
    return {'torque_nm': torque,
            'ideal_axial_force_n': 2 * math.pi * torque / p['lead_m'],
            'travel_m': p['lead_m'] * p['turns']}


def motion(progress, p):
    """Approach ends at first contact; no penetration or post-contact rotation."""
    progress = max(0.0, min(1.0, progress))
    angle = progress * p['turns'] * 2 * math.pi
    return angle, angle / (2 * math.pi) * p['lead_m']


def episode_progress(time_s, config):
    """Single approach across all camera cuts; holds when first contact is reached."""
    return max(0.0, min(1.0, time_s / config['contact_time']))
