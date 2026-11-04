# The Physics Within — procedural physics videos

Independent project for English physics Shorts, covering mechanisms and expandable to electromagnetism, fluids and other physical processes. Visuals are generated entirely
with Blender Python; FFmpeg adds English captions and encodes H.264. No generated
AI images/video, paid services, or changes to MathRelaxing. No automatic posting.

## Current deliverable

A 22-second vertical **visual prototype**, not a finished editorial Short:
recognizable cast bench vise with swivel base, mounting bolts, replaceable grip
plates, continuous threaded screw and rounded T-handle. Six camera shots, using eased perspective orbits and push-ins:

| Time | Shot | Purpose |
| --- | --- | --- |
| 0–3.5 s | Orbit and push-in on the complete vise | Recognize the tool |
| 3.5–6 s | Isolated grip insert macro | Crosshatching and fixing screw details |
| 6–10 s | Orbiting screw/nut cutaway | See screw lead and the fixed nut |
| 10–14 s | Push-in around the handle | Applied force and torque direction |
| 14–19 s | Descending/rotating jaw close-up | Watch the gap close |
| 19–22 s | Orbiting pull-back | Hold first contact and reveal the assembly |

The movement runs continuously across camera cuts. The English captions, shot
headings and details have reserved header/footer panels. Revision 4 adds a locally synthesized English narration and matching subtitles. No music yet.

Blender 4.3.2 and FFmpeg 7.1.5 are available in this environment. The standard
library handles orchestration, configuration, physics and dry-run packaging.
The Workbench renderer makes CPU previews inexpensive; lighting/material polish
and a longer educational script are future steps.

```bash
cd /workspace/mecanismos-3d
python pipeline.py doctor
python -m unittest discover -s tests -v
python pipeline.py render --preview
python youtube_upload.py output/bench_vise/preview/upload.json
```

The render produces `scene.blend`, PNG frames, English `captions.srt`, `video.mp4`,
`poster.png`, a frozen `episode.json`, `render.log`, and a hash-checked `upload.json`.
Preview: 450×800, 16 fps. Final preset: 1080×1920, 24 fps:

```bash
python pipeline.py render
```

The final render will cost more CPU time; it has not been run as part of bootstrap.
Each render replaces only that episode/profile's frames and derived output.
Frame images are retained for inspection. Remove output directories manually when
no longer needed. Workbench is used for both profiles; resolution does not imply
final visual polish.

## Episode model

`episodes/bench_vise.json` is the editable source of timing, captions, title,
description, dimensions, physical parameters and intended YouTube channel ID.
The `shots` list also controls camera position, target, scale, dolly, timing and
shot labels; `contact_time` fixes when the continuous approach stops.
`camera_motion.py` computes a smooth perspective path with `orbit_deg`,
`rise_deg`, `end_scale`, and `target_shift`. Camera distance is derived from
vertical framing and a fixed 50 mm lens. Motion easing affects only the camera;
mechanical motion and screw lead remain unchanged.
`scene.py` currently implements **only the bench vise**; another mechanism needs a
new geometry/motion implementation, not merely a change of title.

Model assumptions: kinematic animation, a rigid workpiece and a single-start
screw. Lead is 4 mm/revolution; four turns give 16 mm of travel. The handle radius
is 0.065 m; a perpendicular 20 N hand force would give 1.3 N m. The arrow is
schematic and not scaled in newtons. The mechanism stops at first contact,
without simulating elastic loading or actual clamping force. The work-balance
calculation in the package is ideal, without friction: `F = 2*pi*torque/lead`.
It must not be interpreted as a measured or realistic force. The preview does
not simulate post-contact clamping or visualize reaction forces. A cyan arc
shows torque direction in the handle detail.
Technical equations should be checked against technical sources before release.

## Upload preparation and limits

`youtube_upload.py upload.json` is an offline **dry-run**. It needs no Google
libraries or credentials, checks the video SHA-256 and prints the exact request
body. The upload adapter has not been tested against the live YouTube API.

To connect later:

1. Create/identify the new channel and record its exact `UC...` channel ID in the
   episode configuration. Do not reuse MathRelaxing's credentials or channel.
2. Enable YouTube Data API v3 in your Google Cloud project and provision an OAuth
   desktop client. Obtain an authorized-user token **for this channel** with
   `youtube.upload` and `youtube.readonly` scopes through an OAuth consent flow.
   OAuth onboarding is not implemented in this starter. Store secrets outside the
   repository and do not send tokens through chat. Service accounts do not replace
   a channel owner's OAuth consent for normal YouTube uploads.
3. Enable the necessary network destinations in the environment configuration:
   typically `www.googleapis.com`, `youtube.googleapis.com`, `oauth2.googleapis.com`,
   and `accounts.google.com` for initial consent. Current policy excludes these.
   Confirm actual required upload destinations when connecting.
4. Install the optional dependencies in a virtual environment:
   `python -m venv .venv`, then
   `.venv/bin/pip install -r requirements-youtube.txt`.
5. Render a final version, inspect the video and metadata, and set
   `status` to `approved` in its `upload.json` only after review.
6. Once the user authorizes uploading, run with the approved token file path:

```bash
YOUTUBE_TOKEN_FILE=/secure/path/new-channel-token.json \
  .venv/bin/python youtube_upload.py output/bench_vise/final/upload.json --execute
```

The adapter verifies the OAuth identity's channel before uploading. It rejects
previews and unapproved packages, forces **private** visibility, and writes an
`upload-started.json` marker before sending media. A successful response writes
`upload-receipt.json`. If interrupted, it refuses an automatic retry: inspect the
channel first to avoid duplicates. Session resumption across process restarts,
a scheduler, automatic retries, token persistence, public publishing and a daily
queue are not implemented. Uploading in private is still an external action and
has not been executed here.

## Next production steps

Review this technical preview, improve composition and explanatory overlays,
choose narration/audio, expand the script with a verified physical explanation,
then render a final pilot. Connect and test private upload only after the new
channel, OAuth consent and network access are ready. Daily scheduling comes after
that pilot is validated.

Confirmed decisions: English on-screen text, bench-vise pilot, narration deferred.
The user confirmed the new channel has not been created yet.

## Reviewing revisions 3 and 4

The initial 12-second video is preserved in `output/bench_vise/archive-v1/`.
Revision 2 is preserved in `output/bench_vise/archive-v2/`.
The current rendered preview is `output/bench_vise/preview/video.mp4` and the
stable revision-specific copy is `output/bench_vise/preview/bench_vise_v3.mp4`.
The model now also includes crosshatched gripping plates, screw head slots,
cast strengthening ribs, a raised nameplate, bearing rings, and a screw witness
mark. The insert macro is an explicitly isolated detail view, not an exploded
mechanical simulation.
Reassemble captions/panels without repeating the Blender render:

```bash
python pipeline.py assemble --preview
```

This also exports `bench_vise_v<revision>.mp4` and one `shot-<name>.png` per camera.
To verify actual baked geometry and camera switching:

```bash
blender --background output/bench_vise/preview/scene.blend --python-exit-code 1 \
  --python tests/verify_blender_scene.py
```

The artifact check measures jaw contact against the workpiece, rejects
penetration or reopening, and checks every camera cut, perspective path motion and cutaway visibility.

## Narration, subtitles and physical expressions (revision 4)

The current video is `output/bench_vise/preview/bench_vise_v4.mp4`: the same
22-second procedural sequence with a synthetic US English female voice,
verbatim subtitles burned into the footer, a selectable English subtitle track,
and a separate `captions.srt`. Equations replace the large top heading only
when relevant; they do not overlap the spoken subtitles.

- Screw close-up: `Δx = L·θ/(2π)`, then one revolution gives 4 mm.
- Handle close-up: `τ = r·F` for perpendicular force, then 1.3 N·m.
- Jaw closure: `Δx = n·L`, with 16 mm total travel across four turns.

The `narration.segments` and `equations` lists in the episode JSON control
wording/timing. Voice synthesis measures each phrase's actual waveform duration
and generates subtitle cues from it. Revision 4 uses the voice's natural speed
for all six phrases. Narration and equations are checked for overlapping cues.
The SRT is phrase-aligned, not word-level forced alignment.

Dependencies are isolated in `.venv`, pinned in `requirements-voice.txt`.
The downloaded model is excluded from source control. See `VOICE_MODEL_CARD.md`
and `voice-model-provenance.json` for source, supplied model card and hashes.
Setup on another machine needs the pinned packages and extracted model:

```bash
python -m venv .venv
.venv/bin/pip install -r requirements-voice.txt
mkdir -p models
curl --fail --location \
  https://github.com/k2-fsa/sherpa-onnx/releases/download/tts-models/vits-piper-en_US-ljspeech-high.tar.bz2 \
  --output models/ljspeech.tar.bz2
# Verify the SHA-256 against voice-model-provenance.json before extracting.
tar -xjf models/ljspeech.tar.bz2 -C models
python pipeline.py narrate --preview
python pipeline.py assemble --preview
```

`render` automatically generates narration after rendering when the episode has a
narration section. Existing frames can be reused with `narrate` then `assemble`.
The model runs locally after download; no paid voice service or API key is used.
The final mix is 48 kHz, normalized toward -16 LUFS with a -1.5 dB true-peak
target, then encoded to AAC. `narration.json` records phrase durations and tempo.
`transcript.txt`, `narration.srt`, and `narration.wav` are exported for review.

## Separate physical lighting/material study

`material_study.py` adds Cycles surface shaders, small procedural surface bumps,
paint coating, a procedural hardwood bench and three area lights to a saved scene.
It renders two still images in `output/bench_vise/material-study/`.
This study has **not** replaced the renderer in the full revision-4 video.
The system Blender build lacks OpenImageDenoise; the study therefore uses
128 CPU samples without denoising and can retain visible grain.

```bash
blender --background --threads 4 output/bench_vise/preview/scene.blend \
  --python-exit-code 1 --python material_study.py -- \
  --output output/bench_vise/material-study
```

Revision 3 is preserved in `output/bench_vise/archive-v3/` and its original
revision-specific video file. No upload has been executed.

## Revision 5: flat vectors, expressive voice and short-form captions

`output/bench_vise/preview/bench_vise_v5.mp4` combines all three changes.

- Annotations: thin, antialiased vectors drawn with Pillow over the rendered
  mechanism. Blender exports the camera-projected application point, axis,
  tangent and torque-plane arc per frame. Force is cyan, torque amber and
  the radius dashed grey; widths and label sizes are constant in pixels.
  Force-arrow length remains schematic, not a newton scale. The force vector
  begins at the handle contact point and follows the projected tangent.
- Narration: Kokoro en v0.19, af_bella, with conversational phrasing and short
  pauses. The contact exclamation spans t=19 s, matching mechanical contact.
  No voice cloning or paid synthesis API is used. See the supplied Apache 2.0
  license and model provenance files.
- Captions: bold uppercase blocks of up to three words, black outline and
  yellow active-word emphasis. Groups respect punctuation and avoid trailing
  single words where possible. The selectable SRT remains phrase-based.
  Within-phrase word highlights use syllable-weight timing estimates, **not
  forced alignment**; they need a timing pass if frame-exact karaoke is required.

Graphics dependencies are pinned in `requirements-graphics.txt`. Install them in
whichever Python environment runs `pipeline.py`. For the new voice, extract the
Kokoro archive under `models/kokoro-en-v0_19/`; the older LJSpeech model remains a
fallback. Model locations and speaker ID are in the episode configuration.

A complete fresh `render` hides the mesh arrows, generates the narration,
exports Blender anchors, composites the flat annotations, then assembles the
short-form captions. Reassembling existing frames uses the already composited
annotations; do not apply the vector compositor repeatedly to annotated frames.
`export_arrow_study.py --render` renders only the clean handle shot when comparing
the annotation styles without rebuilding the complete sequence.

The original 3D-arrow excerpt and the flat-arrow prototype are retained in
`output/bench_vise/arrow-study/`. Revision 4's video, voice, SRT and original
handle frames are preserved in `output/bench_vise/archive-v4/`.
The physical lighting study remains separate from the complete video.

## Revision 6: complete 1080×1920 / 60 fps Short with licensed background music

The final preset now uses 60 fps, 22 seconds and 1320 natively rendered Blender
frames. Workbench FXAA is used for this complete render; the Cycles material study
remains separate. The preview profile is retained for inexpensive iteration.
Camera motion, procedural kinematics, flat annotations and short-form subtitles
are all evaluated at the selected profile's native frame rate.

Background track: **Monkeys Spinning Monkeys**, Kevin MacLeod (incompetech.com).
The official Godot demo credits identify it under **CC BY 3.0**:
https://github.com/godotengine/godot-demo-projects/blob/master/audio/audio_effects/README.md#music

The source file, source README snapshot, credit and SHA-256 provenance are in
`assets/music/`. The attribution and modification notice are included in the
YouTube description and exported as `MUSIC_CREDITS.txt`. The recording is excerpted,
faded and ducked beneath narration. This is a license-backed reuse choice, not a
guarantee about a platform's automated Content ID decisions.

`mix_audio.py` normalizes the music bed toward -26 LUFS, ducks it from the voice
signal, then targets a -16 LUFS master and -1.5 dB true peak. Fade-in is 0.35 s,
fade-out 1.2 s. The 48 kHz stereo WAV mix is saved as `soundtrack.wav` and its meter
report as `audio-mix.json`. `assemble` automatically uses the mixed soundtrack
when the episode contains a music configuration.

```bash
python pipeline.py render
```

The final output is `output/bench_vise/final/video.mp4` with a revision-specific
copy, full resolution subtitles, narration, music, formulas and flat annotations.
No upload or publication is performed by this command. Packaging validates the
encoded frame rate and requires the track credit in the upload description.
Caption overlays are cached against their measured voice cues and output profile.

## Checked-in deliveries

- Completed 1080p60 Short and subtitles: `deliverables/bench-vise/`.
- YouTube brand kit: `branding/the-physics-within/`.
- Facebook brand kit: `branding/the-physics-within/facebook/`.

Voice model weights, virtual environments and intermediate render frames are
excluded from Git. Model provenance and setup instructions are preserved above.
