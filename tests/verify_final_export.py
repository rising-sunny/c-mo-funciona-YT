"""Validate the final 60 fps artifact, source sequence, audio and music attribution."""
import json
import math
import subprocess
import sys
from pathlib import Path
from fractions import Fraction
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from pipeline import digest

root=Path(__file__).resolve().parents[1]
out=root/'output/bench_vise/final'
c=json.loads((out/'episode.json').read_text())
video=out/'video.mp4'
p=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(video)]))
v=next(s for s in p['streams'] if s['codec_type']=='video')
a=next(s for s in p['streams'] if s['codec_type']=='audio')
assert (v['width'],v['height'])==(1080,1920)
assert Fraction(v['r_frame_rate'])==60 and Fraction(v['avg_frame_rate'])==60
assert int(v['nb_frames'])==1320
assert abs(float(p['format']['duration'])-22)<.02
assert a['sample_rate']=='48000' and a['channels']==2
assert any(s['codec_type']=='subtitle' for s in p['streams'])
frames=sorted((out/'frames').glob('*.png'))
assert len(frames)==1320
assert len({digest(out/'frames'/f'{i:04}.png') for i in range(650,656)})==6
cues=json.loads((out/'narration.json').read_text())['segments']
assert len(cues)==8 and cues[6]['start']<=19<=cues[6]['actual_end']
assert (out/'captions.srt').read_text()==(out/'narration.srt').read_text()
assert c['music']['credit'].strip() in c['description']
assert c['music']['title'] in p['format']['tags']['comment']
assert c['music']['license_url'] in (out/'MUSIC_CREDITS.txt').read_text()
manifest=json.loads((out/'upload.json').read_text())
assert not manifest['preview'] and manifest['status']=='awaiting_review'
assert manifest['sha256']==digest(video)
assert digest(out/'bench_vise_v6.mp4')==digest(video)
print('PASS: 1080×1920, native 1320 frames / 60 fps, 22 s, stereo mix, captions, music credit, contact timing and package integrity')
