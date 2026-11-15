import unittest
import pprint
from shapely.geometry import LinearRing, LineString, MultiLineString
from shapely.affinity import rotate
from share import SvgModel, Line
from six import SixStar

class Test(unittest.TestCase):

  pp = pprint.PrettyPrinter(indent=2)

  def setUp(self):
    filename     = self.id().split('.')
    self.svgfile = f'{filename[1]}_{filename[3]}'

  def test_a(self, hw=20, f='N'):
    ''' two triangles
    '''
    star6   = SixStar(hw)
    svg     = SvgModel(hw)
    points  = star6.fromCircle(facing=f)
    triangl = star6.twoTriangles(points)
    svg.render(self.svgfile, triangl)

  def test_b(self): self.test_a(hw=40)
  def test_q(self): self.test_a(f='E')

  def test_c(self, f='N'):
    ''' visual petal test

    A, B, C, D, E, F = triangl
    a, b, c, d, e, f = hxgn
    '''
    hw      = 24
    star6   = SixStar(hw)
    svg     = SvgModel(hw, stroke_width=1)
    triangl = star6.fromCircle(facing=f)
    t1, t2  = star6.twoTriangles(triangl)
    # svg.render(self.svgfile, [t1, t2])
    hxgn    = star6.hexagonPoints(t1, t2)
    edge    = star6.drawEdge(triangl, hxgn, facing=f)
    #self.pp.pprint(edge)
    svg.render(self.svgfile, [edge])

  def test_r(self): self.test_c(f='E')

  def test_d(self, pos='inner', f='N'):
    ''' visual test of inner and outer hexagons
    '''
    hw      = 20
    star6   = SixStar(hw)
    svg     = SvgModel(hw)
    triangl = star6.fromCircle(facing=f)
    t1, t2  = star6.twoTriangles(triangl)
    #if   pos == 'inner': h = star6.hexagonPoints(t1, t2, facing=f)
    #elif pos == 'outer': h = star6.hexagonPointsOuter(t1, t2, facing=f)
    hxpt    = star6.hexagonPoints(t1, t2, pos=pos)
    hexagon = star6.hexagon(hxpt, pos=pos, facing=f)
    #self.pp.pprint(hexagon)
    svg.render(self.svgfile, [hexagon])

  def test_p(self): self.test_d(pos='outer', f='E')
  def test_s(self): self.test_d(pos='inner', f='E')

  def test_e(self):
    ''' meander one petal from test triangle
    '''
    m2 = Line()
    hw  = 24
    hf  = 24 / 2 # half
    mid = (hf, hf)
    svg = SvgModel(hw, stroke_width=.5)
    # create 3 line strings to simulate a petal
    l1, l2, l3 = m2.fakePetal(hw) 
    stripes    = list()
    ls         = m2.meanderTriangle(hf, l1, l2, l3)
    stripes.append(ls)
    svg.render('six_test_e', stripes)

  def test_f(self, hw=24):
    ''' hexagon points
    '''
    star6   = SixStar(hw)
    triangl = star6.fromCircle()
    nt, st  = star6.twoTriangles(triangl)
    h       = star6.hexagonPoints(nt, st)
    dim     = 'hw' + str(hw)
    #self.pp.pprint(h)
    #print(dim, h[0].x)
    data = { 'hw24': 9, 'hw56': 20 }
    if dim in data: 
      x = round(h[0].x)
      #print(x, data[dim])
      self.assertEqual(x, data[dim])

  def test_g(self): 
    self.test_f(hw=56)

  def test_h(self, pair_index=0):
    ''' meander a petal pair
    '''
    hw      = 36
    pairs   = ((0, 3), (1, 4), (2, 5))
    i, j    = pairs[pair_index]
    svg     = SvgModel(hw, stroke_width=.5)
    star6   = SixStar(hw, stroke_width=.5)
    triangl = star6.fromCircle()
    t1, t2  = star6.twoTriangles(triangl)
    hexagon = star6.hexagonPoints(t1, t2)
    petals  = star6.petalLines(triangl, hexagon)
    opposites = list()
    opposites.append(petals[i])
    opposites.append(petals[j])
    ls         = star6.drawPetals(opposites)
    stripes    = list()
    stripes.append(ls)
    svg.render('six_test_h', ls)

  def test_l(self): self.test_h(pair_index=1)
  def test_m(self): self.test_h(pair_index=2)

  def test_i(self):
    ''' meander 6 petals
    '''
    hw      = 80
    svg     = SvgModel(hw, stroke_width=.5)
    star6   = SixStar(hw, stroke_width=.5)
    triangl = star6.fromCircle()
    t1, t2  = star6.twoTriangles(triangl)
    hexagon = star6.hexagonPoints(t1, t2)
    petals  = star6.petalLines(triangl, hexagon)
    #self.pp.pprint(petals)
    ls      = star6.drawPetals(petals)
    stripes = list()
    stripes.append(ls)
    svg.render(self.svgfile, ls)

  def test_j(self):
    ''' meander hexagon
        to see how the boundary intersects with the grid
        with inkscape change stroke colour of hexagon

    a, b, c, d, e, f = hxpt
    guidelines       = (
      ((c, a), (c, e), (a, e)),
      ((a, b), (e, f), (a, e)),
      ((b, d), (f, d), (b, f))
    )
    self.pp.pprint(guidelines)
    '''
    hw      = 20
    swd     = 1
    svg     = SvgModel(hw, stroke_width=swd)
    star6   = SixStar(hw)
    triangl = star6.fromCircle()
    nt, st  = star6.twoTriangles(triangl)
    hxpt    = star6.hexagonPoints(nt, st)
    hexagon = star6.hexagon(hxpt)
    #self.pp.pprint(hxpt)
    g1, g2, _ = star6.guidelinesXy(hexagon)
    stripes   = star6.grid(g1, g2, gap=swd)
    stripes.append(hexagon)
    svg.render('six_test_j', stripes)

  def test_k(self, f='N'): 
    ''' draw hexagon as line string
    '''
    hw      = 30
    svg     = SvgModel(hw, stroke_width=.5)
    star6   = SixStar(hw)
    triangl = star6.fromCircle(facing=f)
    nt, st  = star6.twoTriangles(triangl)
    hxpt    = star6.hexagonPoints(nt, st)
    hexagon = star6.hexagon(hxpt, facing=f)
    ''' lnstr   = hexagon
    self.pp.pprint(grid)
    '''
    gl1, gl2, facing = star6.guidelinesXy(hexagon)
    grid    = star6.grid(gl1, gl2)
    lnstr   = star6.meanderShape(hexagon, grid, facing)
    svg.render(self.svgfile, [lnstr])

  def test_t(self): self.test_k(f='E')

  def test_n(self):
    ''' same as test_e but using Line.meanderShape
    '''
    m2 = Line()
    hw  = 24
    hf  = 24 / 2 # half
    mid = (hf, hf)
    svg = SvgModel(hw, stroke_width=.5)
    lrg = m2.fakePetal(hw, geom=LinearRing())

    stripes          = list()
    gl1, gl2, facing = m2.guidelinesXy(lrg)
    grid             = m2.grid(gl1, gl2)
    line             = m2.meanderShape(lrg, grid, facing)

    stripes.append(line)
    svg.render('six_test_n', stripes)

  def test_o(self, f='N'):
    ''' visual petal test two axis meander
    '''
    hw      = 20
    star6   = SixStar(hw, stroke_width=.5)
    svg     = SvgModel(hw, stroke_width=.5)
    triangl = star6.fromCircle(facing=f)
    t1, t2  = star6.twoTriangles(triangl)
    hexagon = star6.hexagonPoints(t1, t2)
    plines  = star6.petalLines(triangl, hexagon, facing=f)
    petals  = star6.drawPetalsTwoAxis(plines)
    svg.render(self.svgfile, petals)

  def test_u(self): self.test_o(f='E')
'''
the
end
'''
