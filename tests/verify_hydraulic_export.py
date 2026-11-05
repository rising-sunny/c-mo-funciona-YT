"""Final-artifact verification for the hydraulic episode."""
from pathlib import Path
from fractions import Fraction
import json
import subprocess
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from pipeline import digest
root=Path(__file__).resolve().parents[1];out=root/'output/hydraulic_syringes/final'
c=json.loads((out/'episode.json').read_text())
p=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(out/'video.mp4')]))
v=next(s for s in p['streams'] if s['codec_type']=='video');a=next(s for s in p['streams'] if s['codec_type']=='audio')
assert (v['width'],v['height'])==(1080,1920)
assert Fraction(v['r_frame_rate'])==Fraction(v['avg_frame_rate'])==60
assert int(v['nb_frames'])==1680 and len(list((out/'frames').glob('*.png')))==1680
assert abs(float(p['format']['duration'])-28)<.02
assert a['sample_rate']=='48000' and a['channels']==2
assert any(s['codec_type']=='subtitle' for s in p['streams'])
assert (out/'captions.srt').read_text()==(out/'narration.srt').read_text()
assert len(json.loads((out/'narration.json').read_text())['cues'])==7
assert len(json.loads((out/'hydraulic-anchors.json').read_text())['frames'])==1680
assert len(list((out/'hydraulic-overlays').glob('*.png')))==1680
m=json.loads((out/'upload.json').read_text())
assert m['physics']['output_force_n']==40 and m['physics']['output_stroke_m']==.02
assert m['physics']['input_work_j']==m['physics']['output_work_j']==.8
assert not m['preview'] and m['status']=='awaiting_review'
assert m['sha256']==digest(out/'video.mp4')==digest(out/'hydraulic_syringes_v1.mp4')
assert c['music']['credit'].strip() in c['description']
assert c['music']['title'] in p['format']['tags']['comment']
print('PASS: hydraulic Short, native 1080p60 / 1680 frames, 28 s, stereo mix, captions, overlays, ideal-force/work metadata, credits and hash')
