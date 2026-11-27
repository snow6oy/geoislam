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

      self entries are a dict of coordinates k: p1, p2
      points are stored in shapely format

      OUPUT
      svgdata()
      ouput format is a list of entries as shapely linestrings
  '''
  pp  = pprint.PrettyPrinter(indent=2)

  def __init__(self):
    self.points = dict()

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

    print(f'{len(args)=} {args}')
    print(f'{ln1} {ln2}')
    '''
    ln1, ln2, p1, p2, p3, p4 = self.linestrings(*args)
    ln1r = rotate(ln1, 180, origin=p1)
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
    ''' package object content for SvgModel.render()
    '''
    svgdata = list()
    for p in self.points:
      svgdata.append(LineString((self.points[p]))) 
      #self.pp.pprint(f'{p} {self.points[p]}')
    return svgdata

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

  def explode(self, A, inner):
    ''' expand a star point (A-H)
        map to inner outer and compass points
    '''
    compass = (
      dict.fromkeys(['CA', 'CE', 'EG', 'GH'], 'nwsw')
      | dict.fromkeys(['AC', 'AB', 'EC', 'BD'], 'nwne')
      | dict.fromkeys(['BA', 'DB', 'FD', 'FH'], 'nese')
      | dict.fromkeys(['GE', 'DF', 'HG', 'HF'], 'swse')
    ) 
    a  = A.lower()
    i  = inner.index(a)
    aa = list()
    AA = list()
    stop = len(inner)
    for j in range(1, stop):
      max_i   = stop - j
      inner_i = i + j if i < max_i else i - max_i
      aa.append(inner[inner_i])
      AA.append(inner[inner_i].upper())
  
    c1 = AA[6] + A
    c1 = compass[c1]
    c2 = A + AA[6]
    c2 = compass[c2]
    return aa, AA, c1, c2

  def compute(self):
    ''' build configuration to construct lines
    '''
    conf  = dict()
    outer = list('ABDFHGEC')
    inner = list('abdfhgec')
    for K in outer:
      a, A, c1, c2 = self.explode(K, inner)
      k = K.lower()
      i = inner.index(k)
      conf[K] = dict()
      conf[K]['points'] = list()
      ''' lookup table - very handy
      [print(z, y, end=(' '), flush=True) for y, z in enumerate(a)]
      print() 
      '''
      if K in ['A']: 
        conf[K]['points'].append([True, k+a[4], K+A[6], k, a[4], K, A[6]])
        conf[K]['points'].append([True, k+a[2], K+A[6], k, a[2], K, A[6]])
      elif K in ['C']: 
        conf[K]['points'].append([True, k+a[2], K+A[6], k, a[2], K, A[6]])
        conf[K]['points'].append([True, k+a[4], K+A[6], k, a[4], K, A[6]])
      elif K in ['D', 'E', 'H']: 
        conf[K]['points'].append([True, k+a[4], A[6]+K, k, a[4], A[6], K])
        conf[K]['points'].append([True, k+a[2], A[6]+K, k, a[2], A[6], K])
      else: 
        conf[K]['points'].append([True, k+a[2], A[6]+K, k, a[2], A[6], K])
        conf[K]['points'].append([True, k+a[4], A[6]+K, k, a[4], A[6], K])
      
      conf[K]['points'].append([False, k+a[4], a[5]+a[0], a[5], a[0]])
      conf[K]['points'].append([False, k+a[2], a[6]+a[1], a[6], a[1]])
      if K in ['F', 'C']: 
        conf[K]['points'].append([True, A[6]+K, c1, K, A[6], c1[:2], c1[2:]])
        conf[K]['points'].append([False, A[6]+K, k+a[4]])
        conf[K]['points'].append([True, K+A[6], c2, A[6], K, c2[:2], c2[2:]])
        conf[K]['points'].append([False, K+A[6], k+a[2]])
      else:
        conf[K]['points'].append([True, A[6]+K, c1, A[6], K, c1[:2], c1[2:]])
        conf[K]['points'].append([False, A[6]+K, k+a[2]])
        conf[K]['points'].append([True, K+A[6], c2, K, A[6], c2[:2], c2[2:]])
        conf[K]['points'].append([False, K+A[6], k+a[4]])
      ''' rings
      pairs = (a[0]+a[3], a[0]+a[5]), (k+a[2], a[0]+a[5]), (k+a[4], k+a[2])
      conf[K]['rings'] = (a[0]+a[3], k+a[4], pairs)
      '''
    return conf

  def dumpConf(self, conf, wantd=None):
    for K in conf:
      if wantd not in conf[K]: continue
      if wantd == 'points':
        [print(' '.join(p[1:])) for p in conf[K]['points']]
      elif wantd == 'rings':
        r = conf[K]['rings']
        argstr = ' '.join(r[2][0] + r[2][1] + r[2][2])
        print(f'{K} {r[0]} {r[1]} {argstr}')
  
'''
the
end
'''
