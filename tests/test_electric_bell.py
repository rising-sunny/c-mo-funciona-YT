import json
from pathlib import Path
import unittest
from bell_physics import quantities,simulate,prepare,display_state
from bell_graphics import project

CONFIG=Path(__file__).resolve().parents[1]/'episodes/electric_bell.json'


class BellTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.c=json.loads(CONFIG.read_text());cls.p=cls.c['physics'];cls.prepared=prepare(cls.c)

 def test_self_interruption_and_repeated_strikes(self):
  events=self.prepared[1]
  first=[e['type'] for e in events[:9]]
  self.assertEqual(first,['open','strike','close']*3)
  self.assertGreater(sum(e['type']=='strike' for e in events),10)

 def test_motion_respects_gap_and_current_bounds(self):
  rows=self.prepared[0];q=quantities(self.p)
  self.assertTrue(all(0<=r['x']<=self.p['stroke_m'] for r in rows))
  self.assertTrue(all(self.p['initial_gap_m']-r['x']>0 for r in rows))
  self.assertTrue(all(0<=r['current']<=q['steady_current_a']*1.01 for r in rows))

 def test_open_contact_current_decays_instead_of_vanishing(self):
  rows=self.prepared[0];i=next(i for i,r in enumerate(rows) if not r['closed'])
  self.assertGreater(rows[i]['current'],.1)
  self.assertLess(rows[i+50]['current'],rows[i]['current']*.02)

 def test_spring_always_restores(self):
  for r in self.prepared[0][::75]:
   self.assertAlmostEqual(r['spring_force'],self.p['spring_n_m']*r['x'])

 def test_story_shows_opening_and_reclosing(self):
  contact=[display_state(11+i*.05,self.c,self.prepared)['closed'] for i in range(80)]
  spring=[display_state(19+i*.05,self.c,self.prepared)['closed'] for i in range(80)]
  self.assertIn(True,contact);self.assertIn(False,contact)
  self.assertIn(True,spring);self.assertIn(False,spring)

 def test_invalid_stroke_rejected(self):
  with self.assertRaises(ValueError):quantities(dict(self.p,stroke_m=.007))
