from shapely.geometry import LineString, box, MultiLineString, LinearRing, Point
from shapely.affinity import rotate
from shapely.ops import unary_union
from circle import Circle
from share import CompassPoints, Line

class EightStar(Line): # inherit from Meander

  def __init__(self, hw, stroke_width=1):
    self.hw  = hw
    self.swd = stroke_width

  def draw(self, a):
    nw, se = self.fromCircle()
    polygn = self.polygonFromDiagonal(nw, se, facing=a.facing)

    if a.shape == 'octagon' and a.render == 'stroke':
      ogpt    = self.octagonPoints(polygn, pos=a.io)
      linestr = self.octagon(ogpt, facing=a.facing) 
      svgdata = [linestr]
    elif a.shape == 'octagon': # render as meander by default
      ogpt    = self.octagonPoints(polygn, pos=a.io)
      octagon = self.octagon(ogpt)
      gl1, gl2, facing = self.guidelinesXy(octagon)
      grid             = self.grid(gl1, gl2, gap=a.swd)
      line             = self.meanderShape(octagon, grid, facing)
      svgdata          = [line]
    elif a.render == 'stroke': # petals are the default shape
      inn      = self.octagonPoints(polygn)
      out      = self.octagonPoints(polygn, pos='outer')
      lring    = self.drawEdge(inn, out)
      svgdata  = [lring]
    else:
      svgdata = self.drawPetals(polygn, axis=a.numax)

    return svgdata

  def drawPetals(self, polygn, axis=2):
    ''' meander 8 petals with either meander v1 or v2
    '''
    if axis == 4: return self.drawPetalsFourAxis(polygn)
    else        : return self.drawPetalsTwoAxis(polygn)

  def drawPetalsFourAxis(self, polygn):
    ''' uses the original library to mirror petals on three axis
    '''
    lines      = list()

    for p in polygn.geoms:
      guideln = self.guidelines(p.boundary)
      p1, p2  = self.collectPoints(guideln)
      if len(p1) == len(p2):
        shape = self.makeStripes([p1, p2])
      else:
        raise ValueError(f'Uneven num of points: {len(p1)} is not {len(p2)}')
      if shape.geom_type == 'LineString':
        lines.append(shape)
      else: # fall back
        lines.append(p.boundary) 

    return lines

  def drawPetalsTwoAxis(self, polygn):
    ''' the newer library meanders on two axis
        either N or E depending on dimensions
        then calls Line.meanderShape for each petal
    '''
    petals = list()
    for p in polygn.boundary.geoms:
      lring            = LinearRing(list(p.coords))
      gl1, gl2, facing = self.guidelinesXy(lring)
      #print(gl1, gl2, facing)
      grid  = self.grid(gl1, gl2, gap=self.swd)
      petal = self.meanderShape(lring, grid, facing)
      petals.append(petal)

    return petals

  def drawEdge(self, inner_points, outer_points):
    ''' sort octagon points and return a ring
    '''
    a, b, c, d, e, f, g, h = inner_points
    A, B, C, D, E, F, G, H = outer_points
    #print(f'{a=} {b=} {c=} {d=} {e=} {f=} {g=} {h=}')
    #print(f'{A=} {B=} {C=} {D=} {E=} {F=} {G=} {H=}')
    edge = LinearRing((a, A, b, B, d, D, f, F, h, H, g, G, e, E, c, C))
    return edge

  def guidelines(self, boundary):
    ''' override meander.guidelines
    A -- C
    |    |
    B -- D

    print(f'{list(boundary.coords)}')
    '''
    a, b, c, d = list(boundary.coords)
    AB = LineString([a, b])
    DC = LineString([d, c])
    return MultiLineString([DC, AB])

  def octagon(self, points, facing='N'):
    ''' sort points according to position and facing

    outer              inner

    facing=N

           A           a   b
         C   B       c       d
       E       D     e       f
         G   F         g   h
           H

    facing=E

          A   B           a
        C       D       c   b
        E       F     e       d
          G   H         g   f
                          h
    print(f'{facing=}')
    self.pp.pprint(points)
    '''
    a, b, c, d, e, f, g, h = points
    if   facing == 'N': octgn = LinearRing((a, b, d, f, h, g, e, c))
    elif facing == 'E': octgn = LinearRing((a, d, g, h, f, e, c, b))
    return octgn

  def octagonPoints(self, polygn, pos='inner'):
    ''' gather boundary points from polygon
        return the inner and outer octogans

    print(f'{pos=}')
    self.pp.pprint(points)
    '''
    points = list()
    if pos == 'inner':
      for p in polygn.geoms:
        _, i, _, _ = list(p.boundary.coords)
        #print(f'{i=}')
        points.append(Point(i))
    elif pos == 'outer':
      for p in polygn.geoms:
        o, _, _, _ = list(p.boundary.coords)
        points.append(Point(o))
    # swap f and g
    points[5], points[6] = points[6], points[5]
    return points

  def fromCircle(self):
    ''' make a circle polygon and a diagonal NW -> SE
        return the points where the diagonal touches the circle
    '''
    c    = Circle()
    cp   = CompassPoints()
    grid = list(cp.points(self.hw, self.swd))
    geom = { 'size': 'medium' }
    plgn = c.paint(grid, geom)
    swd, hw, n, e, s, w, ne, se, nw, sw, mid = grid
    #print(f'{nw=} {se=} {n=} {s=} {c.name}')
    lstr = LineString([nw, se])  # north west to south east diagonal
    nwpt, sept = list(plgn.intersection(lstr).coords) # linestring with 2 points
    return nwpt, sept

  def polygonFromDiagonal(self, nwpt, sept, facing='N'):
    ''' create a polygon from two points
    '''
    square  = box(nwpt[0], nwpt[1], sept[0], sept[1])
    if facing == 'N':
      bx1 = square
      bx2 = rotate(square, 45, origin='center')
    elif facing == 'E':
      bx1 = rotate(square,  23, origin='center')
      bx2 = rotate(square, 337, origin='center')
    else: raise ValueError(f'where to {facing=} ?')

    diff1 = bx1.difference(bx2, grid_size=1) # return MultiPolygon
    diff2 = bx2.difference(bx1, grid_size=1) # return MultiPolygon
    polygn = unary_union([diff1, diff2])
    return polygn

if __name__ == "__main__":
  ''' hw is the height and width of the cell in mm
      stroke width should be same as pen width e.g. 1 or .5
  '''
  import sys
  from share import Args, SvgModel
  a = Args(sys.argv)
  if not a.ok: sys.exit()
  #print(f'''Inputs 
  #{sys.argv[0]} {a.svgfile=} {a.hw=} {a.swd=} {a.shape=} 
  #{a.render=} {a.numax=} {a.facing=} {a.io=}''')
  star8  = EightStar(a.hw, stroke_width=a.swd)
  svg    = SvgModel(a.hw, stroke_width=a.swd)
  svgdata = star8.draw(a)
  svg.render(a.svgfile, svgdata)
'''
the
end
'''
