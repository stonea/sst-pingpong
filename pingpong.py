import sst
import argparse, random

parser = argparse.ArgumentParser(
  prog='SSTPingPong',
  description='Run a simulation consisting of several components arranged in a 1D or 2D grid that send messages back and forth')
parser.add_argument('--timeToRun',  type=int, default=200)
parser.add_argument('--numDims',    type=int, default=1)
parser.add_argument('--N',          type=int, default=10)
parser.add_argument('--numBalls',   type=int, default=-1)
parser.add_argument('--edgeDelay',  type=int, default=50)
parser.add_argument('--random',     default=False, action='store_true')
parser.add_argument('--verbose',    default=False, action='store_true')
args = parser.parse_args()

if args.numBalls == -1 and args.numDims == 1:
  args.numBalls = 2
elif args.numBalls == -1 and args.numDims == 2:
  args.numBalls = 8

# -----------------------------------------------------------------------------

def oppositeDir(direction):
  opposites = {'north': 'south', 'south': 'north', 'west' : 'east', 'east' : 'west'}
  return opposites[direction]

numLinks = 0
def link(x, y, direction):
  global numLinks
  if args.verbose:
    print("connect ", x.getFullName(), direction, "--", y.getFullName(), oppositeDir(direction))
  sst.Link("link%i" % numLinks).connect( (x, "%sPort" % direction, "%ips" % args.edgeDelay), (y, "%sPort" % oppositeDir(direction), "%ips" % args.edgeDelay) )
  numLinks += 1

# -----------------------------------------------------------------------------

ballGen = sst.Component("sim", "pingpong.simulator")
ballGen.addParams({"timeToRun" : args.timeToRun})

pingPongers = []
ballsHeadingNorthAt = {}
ballsHeadingSouthAt = {}
ballsHeadingWestAt  = {}
ballsHeadingEastAt  = {}

NW_PONGER = 0
NE_PONGER = args.N-1
SW_PONGER = args.N * (args.N-1)
SE_PONGER = (args.N * args.N) - 1

# Assign balls in corners if we're not setting them randomly
if not args.random:
  if args.numBalls >= 1:
    ballsHeadingEastAt[NW_PONGER] = 1
  if args.numBalls >= 2:
    ballsHeadingWestAt[NE_PONGER] = 1
  if args.numDims > 1:
    if args.numBalls >= 3:
      ballsHeadingEastAt[SW_PONGER] = 1
    if args.numBalls >= 4:
      ballsHeadingWestAt[SE_PONGER] = 1
    if args.numBalls >= 5:
      ballsHeadingSouthAt[NW_PONGER] = 1
    if args.numBalls >= 6:
      ballsHeadingSouthAt[NE_PONGER] = 1
    if args.numBalls >= 7:
      ballsHeadingNorthAt[SW_PONGER] = 1
    if args.numBalls >= 8:
      ballsHeadingNorthAt[SE_PONGER] = 1
else:
  sample = random.sample(range(args.N * args.N), args.numBalls)
  for r in sample:
    direction = random.randint(0,3)
    if direction   == 0: ballsHeadingNorthAt[r] = 1
    elif direction == 1: ballsHeadingSouthAt[r] = 1
    elif direction == 2: ballsHeadingWestAt[r]  = 1
    elif direction == 3: ballsHeadingEastAt[r]  = 1

if args.verbose:
  print("Initial balls --")
  for i in [0] if args.numDims == 1 else range(0,args.N):
    for j in range(0,args.N):
      me = i * args.N + j;
      if me in ballsHeadingEastAt:  print("%5i %s" % (me, "east"))
      if me in ballsHeadingWestAt:  print("%5i %s" % (me, "west"))
      if me in ballsHeadingSouthAt: print("%5i %s" % (me, "south"))
      if me in ballsHeadingNorthAt: print("%5i %s" % (me, "north"))

for i in [0] if args.numDims == 1 else range(0,args.N):
  for j in range(0,args.N):
    me = i * args.N + j;
    ponger = sst.Component("pong_%i" % (me), "pingpong.ponger")
    ponger.addParams({
      "ballsHeadingNorth": ballsHeadingNorthAt.get(me, 0),
      "ballsHeadingSouth": ballsHeadingSouthAt.get(me, 0),
      "ballsHeadingWest":  ballsHeadingWestAt.get(me, 0),
      "ballsHeadingEast":  ballsHeadingEastAt.get(me, 0)})
    pingPongers.append(ponger);

# i = row, j = col, (0,0) = north west corner
for i in [0] if args.numDims == 1 else range(0,args.N):
  for j in range(0,args.N):
    me = i * args.N + j;
    neighborS = me + args.N
    neighborE = me + 1

    connectS = i < args.N-1 and args.numDims > 1
    connectE = j < args.N-1

    if connectS:
      link(pingPongers[me], pingPongers[neighborS], "south")
    if connectE:
      link(pingPongers[me], pingPongers[neighborE], "east")

