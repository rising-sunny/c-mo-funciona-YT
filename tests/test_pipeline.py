import json
import math
from pathlib import Path
import tempfile
import subprocess
import sys
import unittest
from physics import quantities, motion, episode_progress
from pipeline import load, digest
from youtube_upload import plan

CONFIG = Path(__file__).resolve().parents[1]/'episodes/bench_vise.json'


class PipelineTests(unittest.TestCase):
    def test_work_balance(self):
        p = load(CONFIG)['physics']
        q = quantities(p)
        self.assertAlmostEqual(2*math.pi*q['torque_nm'], q['ideal_axial_force_n']*p['lead_m'])

    def test_contact_clamps_motion(self):
        p = load(CONFIG)['physics']
        angle, travel = motion(2, p)
        self.assertAlmostEqual(travel, p['turns']*p['lead_m'])
        self.assertAlmostEqual(angle, p['turns']*2*math.pi)
        self.assertEqual(motion(-1, p), (0, 0))

    def test_camera_cuts_preserve_continuous_travel(self):
        c = load(CONFIG)
        previous = -1
        for t in [0, 4, 9, 14, 19, 21.99]:
            _, travel = motion(episode_progress(t, c), c['physics'])
            self.assertGreaterEqual(travel, previous)
            previous = travel
        self.assertEqual(episode_progress(c['contact_time'], c), 1)
        self.assertEqual(episode_progress(c['duration'], c), 1)

    def test_storyboard_gap_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            c = load(CONFIG)
            c['shots'][1]['start'] += .1
            path = Path(tmp)/'bad.json'
            path.write_text(json.dumps(c))
            with self.assertRaises(ValueError):
                load(path)

    def test_overlapping_narration_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            c=load(CONFIG)
            c['narration']['segments'][1]['start']=1
            path=Path(tmp)/'bad.json'
            path.write_text(json.dumps(c))
            with self.assertRaises(ValueError):
                load(path)

    def test_overlapping_equations_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            c=load(CONFIG)
            c['equations'][1]['start']=7
            path=Path(tmp)/'bad.json'
            path.write_text(json.dumps(c))
            with self.assertRaises(ValueError):
                load(path)

    def test_music_credit_and_source_integrity(self):
        c=load(CONFIG)
        if not c.get('music',{}).get('path'):
            self.skipTest('Episode has no licensed music')
        self.assertIn(c['music']['credit'].strip(),c['description'])
        self.assertEqual(digest(CONFIG.parents[1]/c['music']['path']),c['music']['sha256'])
        self.assertEqual(c['music']['license'],'CC BY 3.0')

    def test_bad_lead_rejected(self):
        p = dict(load(CONFIG)['physics'], lead_m=0)
        with self.assertRaises(ValueError):
            quantities(p)

    def test_upload_private_and_tamper_detection(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            video = root/'video.mp4'
            video.write_bytes(b'test')
            c = load(CONFIG)
            m = dict(c, video='video.mp4', sha256=digest(video), preview=True)
            manifest = root/'upload.json'
            manifest.write_text(json.dumps(m))
            self.assertEqual(plan(manifest)[2]['status']['privacyStatus'], 'private')
            m['status'] = 'awaiting_review'
            manifest.write_text(json.dumps(m))
            result = subprocess.run([sys.executable, str(CONFIG.parents[1]/'youtube_upload.py'),
                                     str(manifest), '--execute'], capture_output=True, text=True)
            self.assertEqual(result.returncode, 2)
            self.assertIn('final render', result.stderr)
            self.assertFalse((root/'upload-started.json').exists())
            video.write_bytes(b'changed')
            with self.assertRaises(ValueError):
                plan(manifest)


if __name__ == '__main__':
    unittest.main()
