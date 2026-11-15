import pprint
import xml.etree.ElementTree as ET
from shapely import transform
from shapely.geometry import Polygon

class SvgModel:

  def __init__(self, clen, stroke_width=1):
    self.border = 0
    self.unit   = 'mm'
    self.gridsz = (clen, clen)
    #if stroke_width == .5: clen *= 2 # scale to simulate pen width
    self.viewbx = (clen, clen)  
    self.clen   = clen          # for SVG comment
    self.swd    = stroke_width

  def render(self, model, shapes):
    self.setSvgHeader()
    elem    = 'polyline'
    uniqid  = 1 # xml elements must have unique IDs
    style   = f'fill:none;stroke:#000;stroke-width:{self.swd}'

    g = ET.SubElement(self.root, f"{self.ns}g", id=str(uniqid))
    g.set('style', style)  # 'fill:#FFF;stroke:#000;stroke-width:1'
    ''' create an SVG document
    '''
    for shape in shapes: # a list of LineStrings
      #print(shape.geom_type)
      uniqid += 1
      p       = ET.SubElement(g, f"{self.ns}{elem}", id=str(uniqid))
      coords  = list(shape.coords)
      points  = str()
      for c in coords:
        coord = ','.join(map(str, c))
        points += f"{coord} "
        p.set("points", points.strip())

    self.write(f'tmp/{model}.svg')

  def setSvgHeader(self):
    ''' start the markup
    '''
    ET.register_namespace('',"http://www.w3.org/2000/svg")
    w, h = self.gridsz
    W, H = self.viewbx
    unit = self.unit
    b    = self.border
    root = ET.fromstring(f'''
    <svg 
      xmlns="http://www.w3.org/2000/svg" 
      viewBox="0 0 {W} {H}" 
      width="{w}{unit}" height="{h}{unit}"
      style="border: {b}{unit} solid #000000;"></svg>
    ''')
    # transform="scale(1)" has not effect ?
    comment = ET.Comment(f' cell length: {self.clen}')
    root.insert(0, comment)  # 0 is the index where comment is inserted
    #ET.dump(root)
    self.ns = '{http://www.w3.org/2000/svg}'
    self.root = root

  def write(self, svgfile):
    tree = ET.ElementTree(self.root)
    ET.indent(tree, level=0)
    tree.write(svgfile)

'''
the
end
'''
