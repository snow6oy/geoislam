class Args:

  def __init__(self, args):
    ''' sixfhni six fill hexagon north inner
        sixspe2 six stroke petals east 2
    '''
    self.ok  = True
    self.hw  = 20
    self.swd = 1
    self.render = str() # default: fill 
    self.shape  = str() # default: petals
    self.facing = 'N'
    self.io     = 'inner' # io only works with shape:hexagon
    self.numax  = 2 # number of axis only works with shape:petals

    if len(args) == 2:
      self.svgfile = str(args[1])
    elif len(args) == 3:
      self.svgfile = str(args[1])
      self.hw      = int(args[2])
    elif len(args) == 4:
      self.svgfile = str(args[1])
      self.hw      = int(args[2])
      self.swd     = float(args[3])
    elif len(args) == 5:
      self.svgfile = str(args[1])
      self.hw      = int(args[2])
      self.swd     = float(args[3])
      self.render  = str(args[4])
    elif len(args) == 6:
      self.svgfile = str(args[1])
      self.hw      = int(args[2])
      self.swd     = float(args[3])
      self.render  = str(args[4])
      self.shape   = str(args[5])
    elif len(args) == 7:
      self.svgfile = str(args[1])
      self.hw      = int(args[2])
      self.swd     = float(args[3])
      self.render  = str(args[4])
      self.shape   = str(args[5])
      if self.render == 'fill' and self.shape == 'petals':
        self.numax  = int(args[6])
      else: self.facing = str(args[6])
    elif len(args) == 8:
      self.svgfile = str(args[1])
      self.hw      = int(args[2])
      self.swd     = float(args[3])
      self.render  = str(args[4])
      self.shape   = str(args[5])
      self.facing  = str(args[6])
      self.io      = str(args[7])
    else:
      self.ok = False
      self.usage(args[0], len(args))

  def usage(self, me, num):
    print(f'''
wrong number of arguments: {num}

usage: {me} 
  hw:int 
  swd:float 
  render:stroke|fill* 
  shape:hexagon|petals*
  numax:3|2*
  facing:E|N*
  position:outer|inner*
''')

  def printArgs(self):
    print(f'''{self.svgfile=} 
{self.hw=} 
{self.swd=} 
{self.shape=} 
{self.render=} 
{self.numax=} 
{self.facing=} 
{self.io=}''')

