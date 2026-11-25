import pprint
from itertools import combinations
from shapely.geometry import Point, LineString, LinearRing
from shapely.affinity import rotate
from share import CompassPoints

class LineHacker:
  ''' line string store and transformer

      INPUTS
      inner and outer points from shape
      box coords from share.compass

      TRANSFORMER
      make a line longer() or shorter()
      required args: target, control
      optional args: start/end line points for above
      if no points given, then transform self 
      use target and control references to self to fetch points
      when points are given, use them to create/update self entries

      self entries are a dict k: p1, p2
      points are stored in shapely format

      use put(tuple) to create entries when no transform needed

      OUPUT
      svgdata()
      ouput format is a list of entries as shapely linestrings

      collections(refs)
      from a given collection of line refs
      return a linear ring for meander
  '''
  pp  = pprint.PrettyPrinter(indent=2)

  def __init__(self):
    self.points = dict()
    self.rings  = dict()

  # inputs example: target, control, p1, p2, p3, p4
  def longer(self, *args):
    ''' given four points double the length of target line
        and find where it touches control line
        create a new line that fills the gap

                * p3
                |
        *---*===* p5
        p2  p1  |
                * p4

    print(f'{target=} {control=} {len(points)=}')
    '''
    ln1, ln2, p1, p2, p3, p4 = self.linestrings(*args)
    ln1r = rotate(ln1, 180, origin=p1)
    #pp.pprint(ln1r)
    p5   = ln1r.intersection(ln2)
    if p2.is_empty or p5.is_empty:
      raise ValueError(f'''no intersect: 
{ln1r=} 
{ln2=}''')
    else:
      target = args[0]
      self.points[target] = (p2, p5)

  #def shorter(self, p1, p2, reverse=False):
  def shorter(self, *args):
    ''' split a line where it intersects the other
    '''
    l1, l2, *points = self.linestrings(*args)
    #self.pp.pprint(l2)
    p2 = l1.intersection(l2, grid_size=1)
    if p2.is_empty:
      raise ValueError(f'''no intersect: 
{l1=} 
{l2=}''')
    else:
      target = args[0]
      coord  = list(l1.coords)[1]
      p1     = Point(coord)
      self.points[target] = (p1, p2)

  def svgdata(self):
    svgdata = list()
    for p in self.points:
      svgdata.append(LineString((self.points[p]))) 
      #self.pp.pprint(f'{p} {self.points[p]}')
    '''
    for r in self.rings:
      lr = LinearRing(self.rings[r])
      if lr.is_valid: 
        svgdata.append(lr)
      else:
        raise TypeError(f'{r} is not a valid ring')
    '''
    return svgdata

  #def addToRings(self, name, touches, crosses, last=None):
  def addToRings(self, k, p0, *args):
    '''
    self.pp.pprint(points)
    print(self.points[t2])
    points.append(self.points[t2][0]) # <POINT (32 3.882)>
    #points.append(self.points[t1][0]) # <POINT (25 1)>
      print(f"{c1} and {c2} ")
    #self.pp.pprint(points)
    '''
    one, two, crosses = args
    p1 = self.points[one][0] 
    p2 = self.points[two][0] 
    #print(f'{name}: {p0} {one}: {p1} {two}: {p2} {len(crosses)}')

    points = list()
    points.append(p0) # <POINT (25 1)>
    points.append(p1) # <POINT (32 3.882)>
    for coords in crosses:
      c1, c2 = coords
      l1 = LineString(self.points[c1])
      l2 = LineString(self.points[c2])
      pt = l1.intersection(l2, grid_size=1)
      if pt.geom_type == 'Point': points.append(pt)
      else                      : raise TypeError(pt.geom_type)
    points.append(p2) # last point in ring
    self.rings[k] = points

  def linestrings(self, target, control, *points):
    ''' create linestrings from input or self
    '''
    if len(points) == 4: 
      p1, p2, p3, p4 = points
    elif len(points) == 2: 
      p1, p2 = self.points[target]
      p3, p4 = points
      #print(p1, p2, p3, p4)
    elif target in self.points and control in self.points:
      p1, p2 = self.points[target]
      p3, p4 = self.points[control]
    elif target in self.points: raise TypeError(f'{control} not found')
    elif control in self.points: raise TypeError(f'{target} not found')
    else:
      raise TypeError(f'{target} {control} {len(points)} expected 2 or 4')
    ln1 = LineString((p1, p2))
    ln2 = LineString((p3, p4))
    return ln1, ln2, p1, p2, p3, p4

  def _put(self, k, p1, p2):
    if isinstance(p1, tuple):
      self.points[k] = (Point(p1), Point(p2))

  def _pointToRing(self, *collectn, last=tuple()):
    print(collectn)
    points = list()
    seen   = set()
    coords = {k: self.points[k] for k in collectn}
    # copy of self.points to maintain order
    '''
    coords = dict() 
    a = list()
    [a.append(self.points[k]) for k in collectn]
    for k in collectn:
      print(k)
      coords[k] = self.points[k] 
    print(coords.keys())
    self.pp.pprint(coords)
    print()
    '''
    ''' coords is sorted on input order or a-z ?
        18 3 is missing coord ag[0]
      wantd = k1 in collectn and k2 in collectn
      if not wantd: continue
    '''
    # Compare every key-value pair with every other pair once
    for (k1, c1), (k2, c2) in combinations(coords.items(), 2):
      #print(f'{k1} {k2}')
      l1 = LineString(c1) 
      l2 = LineString(c2) 
      if l1.touches(l2):
        print(f"{k1} and {k2} touch")
        p1, p2 = c1[0], c2[0] # first point of each line coordinate
        if p1 not in seen:
          points.append(p1)
          seen.add(p1)
          self.pp.pprint(p1)
        if p2 not in seen:
          points.append(p2)
          seen.add(p2)
          self.pp.pprint(p2)
      elif l1.intersects(l2):
        pt = l1.intersection(l2, grid_size=1)
        points.append(pt)
        print(f"{k1} and {k2} cross")
        self.pp.pprint(pt)
    #points.append(coords['ag'][0])
    points.append(last)
    #points = set(points)
    #sp     = sorted(points, key=lambda p: p.y)
    lr = LinearRing(points)
    if not lr.is_valid: 
      print('invalid')
      self.pp.pprint(points)
    return lr

'''
the
end
'''
