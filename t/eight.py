import unittest
import pprint
from shapely.geometry import LinearRing, LineString, MultiLineString
from share import SvgModel, Line, CompassPoints
from eight import EightStar

class Test(unittest.TestCase):

  pp = pprint.PrettyPrinter(indent=2)

  def setUp(self):
    filename     = self.id().split('.')
    self.svgfile = f'{filename[1]}_{filename[3]}'

  def test_a(self):
    ''' octagon for visual test of SvgModel.render
    '''
    coords = tuple((
      (3, 1), (5, 1), 
      (5, 1), (7, 3),
      (7, 3), (7, 5),
      (7, 5), (5, 7),
      (5, 7), (3, 7),
      (3, 7), (1, 5),
      (1, 5), (1, 3),
      (1, 3)
    ))
    ring   = LinearRing(coords)
    svg    = SvgModel(20)
    svg.render('eight_test_a', [ring])

  def test_b(self):
    ''' test data to meander octagon
        note the naming of the A-H is different e.g. HA is named c 

            A  B
            ----
        H  /    \ C
           |    | 
        G  \    / D
            ----
            F  E
    '''
    HA = LineString(((1, 3), (3, 1)))
    GF = LineString(((1, 5), (3, 7)))
    AB = LineString(((3, 1), (5, 1)))
    FE = LineString(((3, 7), (5, 7)))
    BC = LineString(((5, 1), (7, 3)))
    ED = LineString(((5, 7), (7, 5)))

    guides = (
      MultiLineString([HA, GF]),
      MultiLineString([AB, FE]),
      MultiLineString([BC, ED])
    )

    drawn   = list()
    meander = Line()
    # code extracted from EightStar.drawOctogan()
    for guideln in guides:
      p1, p2  = meander.collectPoints(guideln)
      stripe  = meander.makeStripes([p1, p2])
      #print(list(stripe.coords))
      [drawn.append(c) for c in list(stripe.coords)]
    lstr = LineString(drawn)
    svg  = SvgModel(8, stroke_width=.5)
    svg.render('eight_test_b', [lstr])

  def test_c(self):
    ''' make an SVG of petals
    '''
    hw    = 56 # 24
    star8 = EightStar(hw)
    svg   = SvgModel(hw, stroke_width=.5)
    nw, se  = star8.fromCircle()
    polygn  = star8.polygonFromDiagonal(nw, se)
    petals  = star8.drawPetalsFourAxis(polygn)
    svg.render(self.svgfile, petals)

  def test_d(self):
    ''' use inkscape stroke colour to see where
        octagon boundary touches the grid
    '''
    hw      = 20
    swd     = 1
    svg     = SvgModel(hw, stroke_width=swd)
    star8   = EightStar(hw, stroke_width=swd)
    nw, se  = star8.fromCircle()
    polygn  = star8.polygonFromDiagonal(nw, se)
    ogpt    = star8.octagonPoints(polygn)
    octagon = star8.octagon(ogpt)
    stripes = list()
    g1, g2, _ = star8.guidelinesXy(octagon)
    stripes   = star8.grid(g1, g2, gap=swd)
    stripes.append(octagon)
    svg.render('eight_test_d', stripes)

  def test_e(self):
    ''' make an SVG of petals with meander v2
    '''
    hw    = 20
    star8 = EightStar(hw, stroke_width=.5)
    svg   = SvgModel(hw, stroke_width=.5)
    nw, se  = star8.fromCircle()
    polygn  = star8.polygonFromDiagonal(nw, se)
    petals  = star8.drawPetals(polygn)
    svg.render('eight_test_e', petals)

  def test_f(self, pos='inner', f='N'):
    ''' make SVGs for inner or outer octagons
        facing either N or E
    '''
    hw      = 20
    swd     = 1
    svg     = SvgModel(hw, stroke_width=swd)
    star8   = EightStar(hw, stroke_width=swd)
    shapes  = list()
    nw, se  = star8.fromCircle()
    polygn  = star8.polygonFromDiagonal(nw, se, facing=f)
    if pos == 'inner':
      inner   = star8.octagonPoints(polygn)
      octagon = star8.octagon(inner, facing=f)
      shapes.append(octagon)
    elif pos == 'outer':
      outer   = star8.octagonPoints(polygn, pos='outer')
      octagon = star8.octagon(outer, facing=f)
      shapes.append(octagon)
    svg.render(self.svgfile, shapes)

    '''
    self.pp.pprint(polygn)
    svg.render(self.svgfile, [sq, dd])
    sq, dd  = star8.polygonFromDiagonal(nw, se, facing='E')
    svg.render(self.svgfile, [sq.boundary, dd.boundary])
    '''

  def test_g(self): self.test_f(pos='outer')
  def test_h(self): self.test_f(pos='outer', f='E')
  def test_i(self): self.test_f(pos='inner', f='E')

  def test_j(self):
    cp     = CompassPoints()
    # expect coords at default start position xy 0 0
    coords = cp.points(10, 0)
    #self.pp.pprint(coords)
    north  = coords[2]
    self.assertEqual((5, 0), north)
    # shift right by 10
    coords = cp.points(10, 0, x=10, y=0)
    north  = coords[2]
    self.assertEqual((15, 0), north)

'''
the
end
'''
