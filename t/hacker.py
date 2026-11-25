import pprint
import unittest
from shapely.geometry import Point
from share import CompassPoints, LineHacker

class Test(unittest.TestCase):

  pp = pprint.PrettyPrinter(indent=2)

  def setUp(self):
    self.lh  = LineHacker()
    self.cp  = CompassPoints()

  def test_a(self):
    expected = Point((10, 10))
    n, e, s, w, ne, se, nw, sw, mid = self.cp.points(20, 1)[2:]

    self.lh.put('MNW', mid, nw)
    self.assertEqual(expected, self.lh.points['MNW'][0])
    
    before = self.lh.svgdata()[0]
    self.lh.longer('MNW', 'SWSE', Point(mid), Point(nw), Point(sw), Point(se))
    after = self.lh.svgdata()[0]
    self.assertNotEqual(before, after)

  def test_b(self):
    self.lh.put('z', None, None) # silently fail
    self.assertFalse('z' in self.lh.points)

  def test_c(self):
    n, e, s, w, ne, se, nw, sw, mid = self.cp.points(20, 1)[2:]
    self.lh.shorter('NWSE', 'SWNE', Point(nw), Point(se), Point(sw), Point(ne))
    # TODO test what happen

  def test_d(self):
    ''' make a linear ring from
        CA AB ag af bh be
    to_draw = [ 
      (True,  'ag', 'AC', a, g, A, C),
      (True,  'af', 'AC', a, f, A, C),
      (False, 'ag', 'eb', e, b),
      (False, 'af', 'cd', c, d),
      (True,  'CA', 'nwsw', C, A, nw, sw),
      (False, 'CA', 'af'),
      (True,  'AC', 'nwne', A, C, nw, ne),
      (False, 'AC', 'ag'),
    
      (True,  'bh', 'AB', b, h, A, B),
      (True,  'be', 'AB', b, e, A, B),
      (False, 'bh', 'af', a, f),
      (False, 'be', 'cd', c, d),
      (True,  'AB', 'nwne', A, B, nw, ne),
      (False, 'AB', 'bh'),
      (True,  'BA', 'nese', B, A, ne, se),
      (False, 'BA', 'be')
    ]
    for td in to_draw:
      longer, target, control, *points = td
      #print(f'{target=} {control=} {len(points)}')
      if longer: self.lh.longer(target, control, *points)
      else:      self.lh.shorter(target, control, *points)
    self.pp.pprinnt(self.lines)
    ''' 
