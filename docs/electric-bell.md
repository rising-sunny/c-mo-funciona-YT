# Electric bell — episode 3

A 30-second English explainer of a classic self-interrupting electromagnetic
bell. This is a make-and-break bell, not a claim that all modern doorbells use
this mechanism. Final preset: 1080×1920, native 60 fps, 1800 source frames.

## Causal story and timing

1. A broad introduction shows repeated ringing.
2. Holding the button connects the battery to the series circuit.
3. Current in the coil creates magnetic pull on the armature.
4. Armature motion opens the electrical contact.
5. Inductive current and pull decay; inertia completes the hammer strike.
6. The return spring pulls back and recloses the contact.
7. The cycle repeats while the button remains held.
8. The battery, not the spring or magnet alone, supplies each cycle's energy.

The detailed sequence replays one calculated cycle in expanded time. Shot timing
is deliberately nonuniform and is **not real-time footage**. Intro and closing
shots sample additional cycles. Impact cues and procedural audio follow the
same displayed event timeline, with no invented extra impacts at edit boundaries.

## Independent graphics — explicitly outside the Blender render

The base Blender scene contains only the mechanism and its physical wiring.
There are no force-arrow meshes, magnetic-field-line meshes, current particles,
callout labels or sound-wave meshes in the saved scene.

`bell_scene.py` exports body anchors and camera projection matrices as JSON.
`bell_graphics.py`, which does not import `bpy`, draws transparent 2D PNGs using
Pillow: force arrows, magnetic-field curves, current traces, the contact status,
the current meter and schematic impact waves. FFmpeg composites this sequence
after the 3D render. Typography, colour and line width can be changed without
rendering the mechanism again. The projection calculation is checked against
Blender's camera anchors.

The field lines are qualitative annotations, not the result of a field solver.
Their brightness follows the model current; there is no Tesla scale. The current
traces show conventional circuit direction, not electron drift speed. The spring
arrow points against deflection and the signed expression is `F_s = -k*x`.

## Lumped illustrative electromechanical model

`bell_physics.py` integrates a translating armature with a variable-inductance
coil and a linear return spring. It is **not a fitted model of a real product**.
Rendered winding count, contact mechanism and spring shape are schematic; effective
parameters are not inferred from visible material dimensions.

- Inductance: `L(x) = L_leak + C/(g0-x)`.
- Magnetic force for the linear model: `F_mag = 0.5*i^2*dL/dx`.
- Electrical equation: `V = R*i + L*di/dt + i*(dL/dx)*dx/dt` while supplied.
- Mechanical equation: `m*x'' = F_mag - k*x - b*x'`.
- A simple hysteretic contact opens and recloses at different displacements.
- Impact at the gong uses prescribed restitution; the pole gap stays positive.
- On opening, battery voltage is removed and a high effective resistance
  dissipates the inductive transient. This stands for an unshown arc/parasitic
  discharge path. Contact bounce, explicit arcing, magnetic saturation, eddy
  currents, ferromagnetic hysteresis, full field geometry and detailed gong
  deformation are omitted.

The model does not set coil current to zero instantaneously. Closed/open/strike
logic, air-gap clearance, spring attachment and gong contact are verified both
in Python and against the baked Blender artifact.

## References checked

OpenStax, *College Physics*, source modules:

- Magnetic fields and current, including the solenoid relation: https://github.com/openstax/osbooks-college-physics-bundle/blob/main/modules/m42382/index.cnxml
- Inductance and energy: https://github.com/openstax/osbooks-college-physics-bundle/blob/main/modules/m42420/index.cnxml
- RL switching transients: https://github.com/openstax/osbooks-college-physics-bundle/blob/main/modules/m42425/index.cnxml
- Hooke's restoring force: https://github.com/openstax/osbooks-college-physics-bundle/blob/main/modules/m42240/index.cnxml

No textbook artwork or wording is copied into the video. `B ∝ I` is explicitly
qualified by fixed geometry and operation before core saturation; it is not a
numeric field-strength claim for the moving device.

## Audio

Local Kokoro narration, the existing CC BY 3.0 background track with attribution,
and original procedural inharmonic gong modes. The sound is illustrative and
aligned to displayed impacts; it is not a recording or an acoustic FEM result.
`mix_audio.py` mixes the bell effects with narration and ducked background music.

## Reproduce

```bash
python pipeline.py render --episode episodes/electric_bell.json --preview
python pipeline.py render --episode episodes/electric_bell.json
python -m unittest discover -s tests -v
blender --background output/electric_bell/final/scene.blend \
  --python-exit-code 1 --python tests/verify_bell_scene.py
```

Voice weights, intermediate renders and software environments remain excluded
from Git. Nothing in these commands uploads to a media channel.
