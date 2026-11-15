import pprint
from shapely.geometry import Point, LineString, Polygon, LinearRing
from circle import Circle
from share import Line

class SixStar(Line): # inherit from Meander
  pp = pprint.PrettyPrinter(indent=2)

  def __init__(self, hw, stroke_width=1):
    self.hw  = hw           # height width of bounding square
    self.gap = stroke_width - .1 # control meander gap. avoid inkscape tinker

  def draw(self, a, centre=None):
    ''' orchestrate class functions and return data for svg render
    '''
    triangl = self.fromCircle(facing=a.facing, centre=centre)
    t1, t2  = self.twoTriangles(triangl)

    if a.shape == 'hexagon' and a.render == 'stroke':
      hxpt    = self.hexagonPoints(t1, t2, pos=a.io)
      linestr = self.hexagon(hxpt, pos=a.io, facing=a.facing)
      svgdata = [linestr]
    elif a.shape == 'hexagon': # render as fill by default
      hxpt    = self.hexagonPoints(t1, t2, pos=a.io)
      hexagon = self.hexagon(hxpt, pos=a.io, facing=a.facing)
      # facing is calculated from dimension, a.facing is a config param
      gl1, gl2, facing = self.guidelinesXy(hexagon)
      grid             = self.grid(gl1, gl2, gap=self.gap) 
      line             = self.meanderShape(hexagon, grid, facing)
      svgdata          = [line]
    elif a.render == 'stroke': # petals are the default shape
      hxgn    = self.hexagonPoints(t1, t2)
      lring   = self.drawEdge(triangl, hxgn, facing=a.facing)
      svgdata = [lring]
    else:
      hxpt    = self.hexagonPoints(t1, t2) # pos has to be inner
      petals  = self.petalLines(triangl, hxpt, facing=a.facing)
      svgdata = self.drawPetals(petals, axis=a.numax)

    return svgdata

  def drawPetals(self, petal_points, axis=2):
    ''' meander six petals
    '''
    if   axis == 2: return self.drawPetalsTwoAxis(petal_points)
    elif axis == 3: return self.drawPetalsThreeAxis(petal_points)
    else          : raise ValueError(f'{axis=} is not 2 or 3')

  def drawPetalsThreeAxis(self, petal_points):
    #self.pp.pprint(petal_points)
    hf    = self.hw / 2 # half
    mid   = (hf, hf)
    lines = list()
    for points in petal_points:
      #print(points)
      p1, p2, p3 = points
      #print(f'{p1=} {p2=} {p3=}')
      l1 = LineString(p1)
      l2 = LineString(p2)
      l3 = LineString(p3)
      ln = self.meanderTriangle(hf, l1, l2, l3)
      lines.append(ln)
    return lines

  def drawPetalsTwoAxis(self, plines):
    ''' the newer library meanders on two axis
        either N or E depending on dimensions
        then calls Line.meanderShape for each petal
    '''
    petals = list()
    for points in plines:
      p1, p2, p3 = points
      #print(f'{p1[0]} {p1[1]}')
      lring = LinearRing([p1[0], p1[1], p2[0], p2[1], p3[0], p3[1]])
      gl1, gl2, facing = self.guidelinesXy(lring)
      grid  = self.grid(gl1, gl2, gap=self.gap)
      petal = self.meanderShape(lring, grid, facing)
      petals.append(petal)

    return petals

  def drawEdge(self, triangl, hxgn, facing='N'):
    ''' six star stroke as linear ring
    '''
    if facing == 'E': return self.drawEdgeEast(triangl, hxgn)

    A, B, C, D, E, F = triangl
    a, b, c, d, e, f = hxgn

    e = LinearRing((
      (a.x, a.y),
      (A.x, A.y),
      (b.x, b.y),
      (C.x, C.y),
      (d.x, d.y),
      (E.x, E.y),
      (f.x, f.y),
      (F.x, F.y),
      (e.x, e.y),
      (D.x, D.y),
      (c.x, c.y),
      (B.x, B.y)
    ))
    return e

  def drawEdgeEast(self, triangl, hxgn):
    ''' six star stroke as linear ring
    '''
    A, B, C, D, E, F = triangl
    a, b, c, d, e, f = hxgn

    e = LinearRing((
      (A.x, A.y),
      (a.x, a.y),
      (B.x, B.y),
      (b.x, b.y),
      (D.x, D.y),
      (e.x, e.y),
      (F.x, F.y),
      (f.x, f.y),
      (E.x, E.y),
      (d.x, d.y),
      (C.x, C.y),
      (c.x, c.y)
    ))
    return e

  def hexagon(self, points, pos='inner', facing='N'):
    ''' hexagon points to linear ring

    print(f'{self.hw=} {pos=} {facing=}')
    self.pp.pprint(points)
    '''
    a, b, c, d, e, f = points
    hexgn = {
      'N': {
        'inner': LinearRing((a, b, d, f, e, c, a)),
        'outer': LinearRing((a, b, d, f, e, c, a))
      },
      'E': {
        'inner': LinearRing((a, b, e, f, d, c, a)), # why different ?
        'outer': LinearRing((a, b, d, f, e, c, a))
      }
    }
    return hexgn[facing][pos]

  ''' PRIVATE
  '''
  def fromCircle(self, facing='N', centre=None):
    ''' make a circle polygon with 3 points per quadrant 3 * 4 = 12
        extract six outer points from circle boundary
        points represent two triangles either N or E facing

     facing=N          facing=E
          A              A  B
        B   C          C      D
        D   E            E  F
          F
    '''
    c      = Circle()
    geom   = { 'size': 'medium' }
    radius = c.getRadius(geom['size'], self.hw, 0) # ignore self.swd
    if centre: x, y = centre
    else     : x, y = (self.hw / 2), (self.hw / 2)
    circle = Point(x, y).buffer(radius, quad_segs=3)
    #print(f'{self.hw} {X=} {x=} {Y=} {y=} {radius=} ')
    if facing == 'N':
      _, C, _, A, _, B, _, D, _, F, _, E, _ = list(circle.boundary.coords)
    elif facing == 'E':
      D, _, B, _, A, _, C, _, E, _, F, _, _ = list(circle.boundary.coords)
    else: raise ValueError(f'unknown direction {facing=}')
    #print(f''' {A=} {B=} {C=} {D=} {E=} {F=} ''')
    return (Point(A), Point(B), Point(C), Point(D), Point(E), Point(F))

  def twoTriangles(self, t):
    ''' convert triangle points into line strings
    '''
    A, B, C, D, E, F = t
    t1 = LineString((A, D, E, A))
    t2 = LineString((C, F, B, C))
    return t1, t2

  def hexagonPoints(self, t1, t2, pos='inner'):
    '''
    facing=E       facing=N
       a  b           a
     c      d       b   c
       e  f         d   e
                      f
    print(f'{self.hw=} {pos=}')
    self.pp.pprint(points)
    '''
    ok = t1.geom_type == 'LineString'
    if not ok: raise TypeError(f'{t1.geom_type} panic')

    if pos == 'outer':
      A, D, E, _ = list(t1.coords)
      C, F, B, _ = list(t2.coords)

      points = (Point(A), Point(B), Point(C), Point(D), Point(E), Point(F))

    elif pos == 'inner': 
      intersect = t1.intersection(t2)
      inner     = [list([pt.x, pt.y]) for pt in intersect.geoms]
      # change from random shapely sort order to coordinate order
      sip    = sorted(inner, key=lambda k: (k[1], k[0])) # sort on y then x
      points = [Point(p) for p in sip]
    return points

  def petalLines(self, triangl, hexagon, facing='N'):
    ''' create a linear ring for six petals

     facing=E
         A  B          a
       C      D      b   c
         E  F        d   e
                       f
    '''
    A, B, C, D, E, F = triangl
    a, b, c, d, e, f = hexagon
 
    if facing == 'N':
      petals = (
        ((A, b), (A, a), (b, a)),
        ((B, a), (B, c), (a, c)),
        ((e, D), (c, D), (c, e)),
        ((F, e), (F, f), (e, f)),
        ((E, f), (E, d), (f, d)),
        ((b, C), (d, C), (d, b)),
      )
    elif facing == 'E':
      petals = (
        ((A, c), (A, a), (c, a)),
        ((B, a), (B, b), (a, b)),
        ((e, D), (b, D), (b, e)),
        ((F, e), (F, f), (e, f)),
        ((E, f), (E, d), (f, d)),
        ((c, C), (d, C), (d, c)),
      )
    return petals

if __name__ == "__main__":
  ''' hw is the height and width of the cell in mm
      stroke width should be same as pen width e.g. 1 or .5
      may need to reduce swd in inkscape to see meander lines

      the old scale hack was 
      when .5 then SvgModel set: hw x 2 and scale at .5
      but we ignore that now :)

      see Makefile for inputs
  '''
  import sys
  from share import SvgModel, Args

  a = Args(sys.argv)
  if not a.ok: sys.exit()
  #print(f'''{sys.argv[0]} {a.svgfile=} {a.hw=} {a.swd=} {a.shape=} {a.render=} {a.numax=} {a.facing=} {a.io=}''')
  star6   = SixStar(a.hw, stroke_width=a.swd)
  svg     = SvgModel(a.hw, stroke_width=a.swd)
  svgdata = star6.draw(a)
  svg.render(a.svgfile, svgdata)
'''
the
end
'''
