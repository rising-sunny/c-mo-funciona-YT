import unittest
from shorts_captions import word_cues


class CaptionTests(unittest.TestCase):
 def test_trailing_single_word_keeps_every_word(self):
  phrase='That’s hydraulics. Pretty clever, right?'
  rows=word_cues([(0,3,phrase)])
  self.assertEqual([r['words'][r['active']] for r in rows],phrase.split())
  self.assertTrue(all(1<=len(r['words'])<=3 for r in rows))
  self.assertAlmostEqual(rows[-1]['end'],3)

 def test_punctuation_and_short_clauses(self):
  phrase='More force. Less distance. No free energy.'
  rows=word_cues([(1,5,phrase)])
  self.assertEqual([r['words'][r['active']] for r in rows],phrase.split())
  self.assertTrue(all(a['end']<=b['start']+1e-9 for a,b in zip(rows,rows[1:])))
