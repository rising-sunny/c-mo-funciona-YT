"""Validate the delivered native 60 fps bell explainer and independent graphic layers."""
from pathlib import Path
from fractions import Fraction
import json
import subprocess
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from pipeline import digest
out=Path(__file__).resolve().parents[1]/'output/electric_bell/final'
p=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(out/'video.mp4')]))
v=next(s for s in p['streams'] if s['codec_type']=='video');a=next(s for s in p['streams'] if s['codec_type']=='audio')
assert (v['width'],v['height'])==(1080,1920)
assert Fraction(v['r_frame_rate'])==Fraction(v['avg_frame_rate'])==60
assert int(v['nb_frames'])==1800 and len(list((out/'frames').glob('*.png')))==1800
assert abs(float(p['format']['duration'])-30)<.02
assert a['channels']==2 and a['sample_rate']=='48000'
assert any(s['codec_type']=='subtitle' for s in p['streams'])
assert (out/'captions.srt').read_text()==(out/'narration.srt').read_text()
assert len(json.loads((out/'narration.json').read_text())['cues'])==8
layers=json.loads((out/'bell-overlay-info.json').read_text())
assert layers['frames']==1800 and len(list((out/'bell-overlays').glob('*.png')))==1800
assert len(layers['displayed_impacts'])==9
sound=json.loads((out/'bell-sound-info.json').read_text())
assert sound['impacts']==9 and sound['peak']<.99
manifest=json.loads((out/'upload.json').read_text())
assert not manifest['preview'] and manifest['status']=='awaiting_review'
assert digest(out/'video.mp4')==manifest['sha256']==digest(out/'electric_bell_v1.mp4')
assert 'Kevin MacLeod' in p['format']['tags']['comment']
print('PASS: native 1080p60 / 1800 frames, 30 s, stereo mix, 8 voice phrases, independent 2D layers, 9 matched impact cues, credits and delivery hash')
