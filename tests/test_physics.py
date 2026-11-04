import math
from mech import physics as ph


def test_torque_perpendicular():
    assert math.isclose(ph.torque(0.065, 20), 1.3)


def test_lead_advance_four_turns():
    assert math.isclose(ph.lead_advance(0.004, 4), 0.016)


def test_ideal_force_matches_energy_balance():
    tau, lead = 1.3, 0.004
    f = ph.ideal_axial_force(tau, lead)
    assert math.isclose(f * lead, 2 * math.pi * tau)  # trabajo por vuelta
    assert 2000 < f < 2100
