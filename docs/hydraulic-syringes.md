# Hydraulic syringes — episode 2

A 28-second English Short with seven dynamic shots, two cutaway syringe barrels,
a connecting hose, an output load, local expressive narration, short-form
captions, physical expressions, camera-anchored force arrows and licensed music.
Final preset: 1080×1920, native 60 fps. No upload is performed.

## Physical model

| Parameter | Input | Output |
| --- | --- | --- |
| Piston area | 5 cm² | 20 cm² |
| Force | 10 N | 40 N |
| Full stroke | 80 mm | 20 mm |
| Displaced volume | 40 mL | 40 mL |
| Ideal work | 0.8 J | 0.8 J |

The area ratio is four; the radius ratio is two. Added (gauge) pressure is
20 kPa in the simplified model. Both liquid chamber meshes change volume using
the same displaced volume. The output plunger and its load move together.
Hose markings are schematic flow cues, not a particle or CFD simulation.

Assumptions: quasi-static motion, incompressible air-free liquid, no leakage,
friction, piston weight, tube losses or hydrostatic head corrections. The two
piston faces can be at different heights in the drawing, so neglect of height
is explicitly stated in the video footer and description. Actual forces would
include gravity head, seal friction and other losses.

## Reference checked

OpenStax, *College Physics*, “Pascal’s Principle”, source module m42193:
https://github.com/openstax/osbooks-college-physics-bundle/blob/main/modules/m42193/index.cnxml

The chapter explicitly derives F1/A1 = F2/A2 for equal heights with negligible
friction, and explains the inverse force/distance relationship and conservation
of work. Its height condition is the reason the simplification is called out.
This episode uses original narration and procedural visuals; no textbook images
or passages are reproduced in the video.

## Reproduce

```bash
python pipeline.py render --episode episodes/hydraulic_syringes.json --preview
python pipeline.py render --episode episodes/hydraulic_syringes.json
```

`hydraulic_scene.py` builds geometry, bakes coupled motion and projects anchors.
`hydraulic_graphics.py` draws a separate transparent annotation sequence.
`hydraulics.py` is the independent SI model. The existing pipeline supplies
narration, captions, equations, music ducking, attribution and MP4 packaging.

```bash
python -m unittest discover -s tests -v
blender --background output/hydraulic_syringes/final/scene.blend \
  --python-exit-code 1 --python tests/verify_hydraulic_scene.py
```

The geometry check measures the baked chamber volumes and piston translations,
checks the wet piston faces and verifies all seven camera cuts. Narrated word
highlights remain estimated within measured phrase timings, as in episode 1.
