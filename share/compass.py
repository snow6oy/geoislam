class CompassPoints:

  def points(self, hw, swd, x=0, y=0):
    ''' set coordinates for the bounding box of a star 
    
      this is a fake version of recurrinnk.cell.build
      because that broke with relative import errors

      points(self, swd, hw):
    '''
    # TODO test swd and remove if possible
    if x % hw or y % hw: 
      raise ValueError(f'{x} {y} coordinates not a multiple of {hw=}')

    n    = tuple([x + hw / 2,   y + swd])
    e    = tuple([x + hw - swd, y + hw / 2])
    s    = tuple([x + hw / 2,   y + hw - swd])
    w    = tuple([x + swd,      y + hw / 2])
    se   = tuple([x + hw - swd, y + hw - swd])
    ne   = tuple([x + hw - swd, y + swd] )
    sw   = tuple([x + swd,      y + hw - swd])
    nw   = tuple([x + swd,      y + swd])
    mid  = tuple([x + hw / 2,   y + hw / 2])

    return  tuple([swd, hw, n, e, s, w, ne, se, nw, sw, mid])
