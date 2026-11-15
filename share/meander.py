import pprint
from shapely.geometry import (
  Point, LineString, LinearRing, MultiLineString, MultiPoint
)
from shapely.affinity import rotate
from shapely.ops import linemerge

class Line:
  ''' all new version with unlimited precision
  '''
  pp = pprint.PrettyPrinter(indent=2)

  def meanderTriangle(self, half, *lines):
    ''' from three sides of a triangle
        return a meandered linestring
    '''
    l1, l2, l3 = lines
    #[print(f'len {l.length}') for l in lines]
    #print()
    mid        = (half, half)
    points     = list()
    l3m        = l3.interpolate(l3.length / 2) # midpooint as Point
    #print(l3m)
    l4         = LineString((l3m, mid))
    stop       = round(l4.length) + 2 # round up and zero-based
    #for i in range(0, stop, gap):
    for i in range(0, stop):
      interval = half - i
      p1 = l1.interpolate(l1.length - i)
      p2 = l2.interpolate(l2.length - i)
      if i % 2: # odd for meander logic 
        #print(f'{i} {interval} {p1} {p2}')
        points.append(p1)
        points.append(p2)
      else:
        #print(f'{i} {interval} {p2} {p1}')
        points.append(p2)
        points.append(p1)
    return LineString(points)

  def meanderShape(self, shape, grid, facing):
    ''' meander using boundary and bounds
    '''
    #print(f'{shape=} {facing} {grid[0]=}')
    meander_points = list()
    for i, linestr in enumerate(grid):
      point = shape.intersection(linestr)
      #print(f'{i=} {point.geom_type}')
      if point.geom_type == 'LineString': # eight produces linestrings
        pair  = [Point(c) for c in point.coords]
        point = MultiPoint(pair)
        #print(f'{point} {pair}')
      if point.geom_type == 'MultiPoint':
        pair = [p for p in point.geoms]
        if len(pair) != 2: raise ValueError(
          f'wrong number of points in MultiPoint: {len(pair)} '
        )
        ''' shapely geoms can come in any order :/
        '''
        if   facing == 'N': sp = sorted(pair, key=lambda p: p.y)
        elif facing == 'E': sp = sorted(pair, key=lambda p: p.x)
        else:               raise ValueError()
        #print(f'{round(sp[0].x)} {round(sp[0].y)}')
        #print(f'{round(sp[1].x)} {round(sp[1].y)}')
        if i % 2: # odd
          meander_points.append(sp[0])
          meander_points.append(sp[1])
        else:
          meander_points.append(sp[1])
          meander_points.append(sp[0])
      elif point.geom_type == 'Point':
        meander_points.append(point)
      else:
        raise TypeError(f'{point.geom_type=} unexpected')
    #self.pp.pprint(meander_points)
    meander_line = LineString((meander_points))
    return meander_line

  def grid(self, pl1, pl2, gap=1):
    ''' create a grid from two parallel lines
        evenly distribute gap over the length
    '''
    grid = list()
    ok   = (pl1.length == pl2.length)
    if not ok: raise ValueError('lines not equal')
    stop = int(pl1.length * (1 / gap)) # use the recipricol 
    dist = pl1.length                  # decimals for points
    ''' diff was supposed to evenly distribute gap 
        but not visible and buggy
    diff = (dist % stop) / stop 
    gap += diff
    print(f'{diff=}')
    print(f'{gap=} {stop=} len {dist}')
    '''
    for i in range(stop + 1):
      counter = i * gap
      p1   = pl1.interpolate(dist - counter)
      p2   = pl2.interpolate(dist - counter)
      #print(f'{i=} {counter=} {p1=} {p2=}')
      grid.append(LineString((p1, p2)))
    #print(f'{len(grid)=}')
    return grid

  def guidelinesXy(self, lring):
    ''' generate two parallel lines
    '''
    x, y, X, Y = lring.bounds
    #print(f'x {round(x, 2)} y {round(y, 2)} X {round(X, 2)} Y {round(Y, 2)}')
    xln = LineString(((x, y), (X, y)))
    yln = LineString(((x, y), (x, Y)))

    if xln.length >= yln.length:
      facing = 'N'
      line_1 = xln
      line_2 = LineString(((x, Y), (X, Y)))
    else:
      facing     = 'E'
      line_1 = yln
      line_2 = LineString(((X, y), (X, Y)))
    return line_1, line_2, facing

  def fakePetal(self, hw, geom=LineString()):
    ''' fake petal for testing shapely.rotate
        return 3 line strings or linear ring
    '''
    hf  = hw / 2 # half
    mid = (hf, hf)
    # create 3 line strings to simulate a petal
    a   = (0, hf)
    l1  = LineString((mid, a))
    l2  = rotate(l1, 60, origin=mid)
    l3  = rotate(l1, 300, origin=a)
    if geom.geom_type == 'LineString':
      return l1, l2, l3
    else:
      l2swap = list(l2.coords)
      l2     = LineString([l2swap[1], l2swap[0]])
      linestrings = [l1, l2, l3]
      multiline   = MultiLineString(linestrings)
      singleline  = linemerge(multiline)
      if singleline.geom_type == 'LineString':
        lr = LinearRing(singleline.coords)
      else:
        raise TypeError(linestrings)
      return lr


  ''' copied from recurrink because the new meander
      only supports perpendicular lines
      and EightStar uses these to generate mirrored lines

      and multiple inheritance across packages seems as bad as copying
  '''
  def collectPoints(self, guidelines, facing=None):
    ''' collect the points intersecting the shape
        gridwalk the bounding box and collect Points() touching the guidelines
        grouped by the guidelines
    '''

    points  = []
    for i, gl in enumerate(list(guidelines.geoms)):
      #print(f'{gl.length} {gl}')
      points.append([])          # template
      (start_x, stop_x, step_x,  # facing is only for triangles
       start_y, stop_y, step_y) = self.orderGrid(gl, facing)
      for y in range(start_y, stop_y, step_y):
        for x in range(start_x, stop_x, step_x):
          pt = Point(x, y)
          if gl.intersects(pt):   # collect the points on the guideline
            points[i].append((x,y))
    #self.pp.pprint(points[0])
    return points

  def orderGrid(self, guideline, facing=None):
    ''' private method to simplify collectPoints()
        calculate the grid order by converting LineString
        into parameters for iteration
    '''
    start, stop      = list(guideline.coords)
    start_x, start_y = [int(xy) for xy in start]
    stop_x, stop_y   = [int(xy) for xy in stop]
    step_x           = -1 if start_x > stop_x else 1
    step_y           = -1 if start_y > stop_y else 1
    stop_x          += step_x
    stop_y          += step_y
    #print(start_x, stop_x, step_x, start_y, stop_y, step_y)
    return start_x, stop_x, step_x, start_y, stop_y, step_y

  def makeStripes(self, points):
    ''' collapse a 2dim array of points into a single LineString
    '''
    #self.pp.pprint(points)
    sorted_points = []
    outer         = len(points)
    inner         = len(points[0])
    # print(f'{outer=} {inner=}')
    for i in range(inner):
      if i % 2:  # odd
        start, stop, step = outer - 1, -1, -1
      else:      # even
        start, stop, step = 0, outer, 1
      for o in range(start, stop, step):
          #print(f'|{points[o][i]}| ', end='', flush=True) 
        sorted_points.append(points[o][i])
      #print()
    return LineString(sorted_points)

  def _grid(self, pl1, pl2):
    ''' create a grid from two parallel lines
    '''
    grid = list()
    gap  = 1
    ok   = (pl1.length == pl2.length)
    if not ok: raise ValueError('lines not equal')
    ''' evenly distribute gap over the length
    '''
    stop = int(pl1.length) # round down
    diff = (pl1.length % stop) / stop 
    gap += diff
    print(f'{gap=} {stop=} len {pl1.length} {diff=}')
    for i in range(stop + 1):
      p1   = pl1.interpolate(pl1.length - i)
      p2   = pl2.interpolate(pl2.length - i)
      print(f'{i=} {p1=} {p2=}')
      grid.append(LineString((p1, p2)))
    print(f'{len(grid)=}')
    return grid

'''
the
end
'''
