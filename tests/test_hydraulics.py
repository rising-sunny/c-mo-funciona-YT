import math
import unittest
from hydraulics import quantities,state

P={'input_area_m2':.0005,'output_area_m2':.002,'input_force_n':10,'input_stroke_m':.08}


class HydraulicTests(unittest.TestCase):
 def test_pascal_force(self):
  q=quantities(P)
  self.assertAlmostEqual(q['output_force_n'],40)
  self.assertAlmostEqual(P['input_force_n']/P['input_area_m2'],q['output_force_n']/P['output_area_m2'])

 def test_volume_conserved_through_motion(self):
  for t in [0,4,6,9,12,15,18,21,28]:
   st=state(t,P)
   self.assertAlmostEqual(P['input_area_m2']*st['input_displacement_m'],P['output_area_m2']*st['output_displacement_m'])

 def test_equal_work_not_free_energy(self):
  q=quantities(P)
  self.assertAlmostEqual(q['input_work_j'],.8)
  self.assertAlmostEqual(q['input_work_j'],q['output_work_j'])
  self.assertAlmostEqual(state(28,P)['output_displacement_m'],.02)

 def test_same_pistons_give_no_amplification(self):
  p=dict(P,output_area_m2=P['input_area_m2']);q=quantities(p)
  self.assertAlmostEqual(q['output_force_n'],P['input_force_n'])
  self.assertAlmostEqual(q['output_stroke_m'],P['input_stroke_m'])

 def test_invalid_area_rejected(self):
  for bad in [0,-1,float('nan'),float('inf')]:
   with self.assertRaises(ValueError):quantities(dict(P,input_area_m2=bad))
