"""Relaciones físicas puras (SI). Sin dependencias de Blender: testeables y reutilizables en guion y render."""
import math


def torque(r: float, force: float, theta: float = math.pi / 2) -> float:
    """τ = r·F·sen(θ); con fuerza perpendicular (θ=90°) τ = r·F."""
    return r * force * math.sin(theta)


def lead_advance(lead: float, turns: float) -> float:
    """Avance axial Δx = L·n (L = avance por vuelta; = paso en rosca de una entrada)."""
    return lead * turns


def ideal_axial_force(tau: float, lead: float) -> float:
    """Modelo ideal sin pérdidas: 2π·τ = F·L  →  F = 2π·τ / L."""
    return 2 * math.pi * tau / lead


def smoothstep(x: float) -> float:
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


def lerp(a, b, k):
    return a + (b - a) * k
