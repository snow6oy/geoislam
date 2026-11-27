import pprint
import unittest
from shapely.geometry import Point
from share import CompassPoints, LineHacker
from eb200db import conf

class Test(unittest.TestCase):

  pp = pprint.PrettyPrinter(indent=2)

  def setUp(self):
    self.lh  = LineHacker()
    self.cp  = CompassPoints()

  def test_a(self):
    n, e, s, w, ne, se, nw, sw, mid = self.cp.points(20, 1)[2:]
    before = Point((10, 10))
    self.lh.longer('MNW', 'SWSE', Point(mid), Point(nw), Point(sw), Point(se))
    after = self.lh.svgdata()[0]
    self.assertNotEqual(before, after)

  def test_d(self):
    pass

  def test_c(self):
    n, e, s, w, ne, se, nw, sw, mid = self.cp.points(20, 1)[2:]
    self.lh.shorter('NWSE', 'SWNE', Point(nw), Point(se), Point(sw), Point(ne))
    # TODO test what happen

  def test_b(self):
    ''' LineHacker.shorter receives its args from explode()
        explode needs to calculate based on petal
        Petals BFGC must swap a2, a4 
    '''
    candidate = self.lh.compute()
    for K in list(conf.db):
      for i, rule in enumerate(conf.db[K]['points']):
        #print(f'{K}', end=(''), flush=True)
        for k in range(len(rule)):
          target = candidate[K]['points'][i][k]
          #print(f' {rule[k]} {target}|', end=(' '), flush=True)
          self.assertEqual(rule[k], target)
        #print()

  def test_e(self):
    ''' rings
    move test to t.eb200 once eb200 converts from script to class

    candidate = self.lh.compute()
    for K in list(conf.db):
      if 'rings' not in conf.db[K]: continue
      print(f'{K}', end=(''), flush=True)
      for i, k in enumerate(conf.db[K]['rings'][:2]):
        target = candidate[K]['rings'][i]
        print(f' {k} {target}|', end=(' '), flush=True)
      for a, b in enumerate(conf.db[K]['rings'][2]):
        c = candidate[K]['rings'][2][a]
        print(' '.join(b), end=(','), flush=True)
        print(' '.join(c), end=('|'), flush=True)
        #self.assertEqual(rule[k], target)
      print()
    '''
''' 
the
end
'''
