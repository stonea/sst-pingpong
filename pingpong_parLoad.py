# This version of ping pong is meant to be run using sst with
# --parallel-load=SINGLE.  For --random and --randomOverlap ball placement we
# put a (roughly) even number of randomly place balls in each rank. Excess
# balls are placed on the final rank.

import sst, time
import argparse, random

startTime = time.time()

parser = argparse.ArgumentParser(
  prog='SSTPingPong',
  description='Run a simulation consisting of several components arranged in a 1D or 2D grid that send messages back and forth')
parser.add_argument('--N',              type=int, default=10)
parser.add_argument('--numDims',        type=int, choices=[1,2], default=2)
parser.add_argument('--timeToRun',      type=int, default=200)
parser.add_argument('--edgeDelay',      type=int, default=50)
parser.add_argument('--artificialWork', type=int, default=0)
parser.add_argument('--verbose',        default=False, action='store_true')
parser.add_argument('--printTime',      default=False, action='store_true')
group = parser.add_mutually_exclusive_group(required=True)
group.add_argument('--corners',         default=False, action='store_true')
group.add_argument('--random',          type=int, default=-1)
group.add_argument('--randomOverlap',   type=int, default=-1)
group.add_argument('--wavefront',       default=False, action='store_true')
args = parser.parse_args()

# -----------------------------------------------------------------------------

def oppositeDir(direction):
  opposites = {'north': 'south', 'south': 'north', 'west' : 'east', 'east' : 'west'}
  return opposites[direction]

numLinks = 0
def link(x,y, ponger1, ponger2, direction):
  global numLinks
  if args.verbose:
    print("on %d connect " % myRank, ponger1.getFullName(), direction, "--", ponger2.getFullName(), oppositeDir(direction))
  linkName = "link_%d_%d_%s" % (x,y,direction)

  sst.Link(linkName).connect( (ponger1, "%sPort" % direction, "%is" % args.edgeDelay), (ponger2, "%sPort" % oppositeDir(direction), "%is" % args.edgeDelay) )

# -----------------------------------------------------------------------------

myRank   = sst.getMyMPIRank()
numRanks = sst.getMPIRankCount()

def warnIfNotDivisibleByNumRanks(random):
  if random != -1 and random % numRanks != 0:
    print("WARNING:")
    print("Number of balls to randomly placed is not evenly divisible by number of ranks ")
    print("the final rank will have %d more balls than every other one." % (random % numRanks))
if myRank == 0:
  warnIfNotDivisibleByNumRanks(args.random)
  warnIfNotDivisibleByNumRanks(args.randomOverlap)

if myRank == 0:
  ballGen = sst.Component("sim", "pingpong.simulator")
  ballGen.addParams({"timeToRun"      : args.timeToRun,
                     "verbose"        : args.verbose,
                     "artificialWork" : args.artificialWork,

                     "numberOfPongers" : args.N}
                    )

  ballGen.setRank(0)

print("NUM RANKS = ", numRanks, " MY RANK = ", myRank)

pingPongers = {}
ballsHeadingNorthAt = {}
ballsHeadingSouthAt = {}
ballsHeadingWestAt  = {}
ballsHeadingEastAt  = {}

rowsPerRank  = int(args.N / numRanks)
rankRowStart = myRank * rowsPerRank
rankRowEnd   = args.N if myRank == numRanks-1 else rankRowStart + rowsPerRank
numComponentsOwnedByRank = (rankRowEnd - rankRowStart) * args.N;

NW_PONGER = 0
NE_PONGER = args.N-1
SW_PONGER = args.N * (args.N-1)
SE_PONGER = (args.N * args.N) - 1

if args.corners:
  if args.numDims == 1:
      ballsHeadingSouthAt[0] = 1
      ballsHeadingNorthAt[args.N-1] = 1
  else:
      assert(args.numDims == 2)
      ballsHeadingEastAt[SW_PONGER] = 1
      ballsHeadingWestAt[SE_PONGER] = 1
      ballsHeadingSouthAt[NW_PONGER] = 1
      ballsHeadingSouthAt[NE_PONGER] = 1
      ballsHeadingNorthAt[SW_PONGER] = 1
      ballsHeadingNorthAt[SE_PONGER] = 1
elif args.random != -1:
  if args.numDims == 1:
    print("--random does not currently work with numDims=1. Use --randomOverlap.")
    exit(1)
  numBalls = args.random / numRanks
  if myRank == numRanks-1:
    numBalls += args.random % numRanks
  sample = random.sample(range(numComponentsOwnedByRank), args.random)
  for r in sample:
    loc = rankRowStart * args.N + r
    direction = random.randint(0,3)
    if direction   == 0: ballsHeadingNorthAt[loc] = 1
    elif direction == 1: ballsHeadingSouthAt[loc] = 1
    elif direction == 2: ballsHeadingWestAt[loc]  = 1
    elif direction == 3: ballsHeadingEastAt[loc]  = 1
elif args.randomOverlap != -1:
  numBalls = int(args.randomOverlap / numRanks)
  if myRank == numRanks-1:
    numBalls += args.randomOverlap % numRanks
  for _ in range(numBalls):
    if args.numDims == 1:
      r = random.randint(0, (rankRowEnd - rankRowStart))
      loc = (rankRowStart * args.N) + (r * args.N)
    else:
      r = random.randint(0, numComponentsOwnedByRank - 1)
      loc = rankRowStart * args.N + r
    direction = random.randint(0,3)
    if direction   == 0: ballsHeadingNorthAt[loc] = 1
    elif direction == 1: ballsHeadingSouthAt[loc] = 1
    elif direction == 2: ballsHeadingWestAt[loc]  = 1
    elif direction == 3: ballsHeadingEastAt[loc]  = 1
elif args.wavefront:
  if args.numDims == 1:
    print("--wavefront does not currently work with numDims=1. Use --randomOverlap.")
    exit(1)
    if(myRank == 0):
      for i in range(0,args.N):
        ballsHeadingSouthAt[i] = 1
    if(myRank == numRanks-1):
      for i in range(0,args.N):
        ballsHeadingNorthAt[args.N*(args.N-1)+i] = 1
    for i in range(rankRowStart, rankRowEnd):
      ballsHeadingEastAt[i*args.N] = 1
      ballsHeadingWestAt[(i+1)*args.N-1] = 1
else:
  print("Unknown ball placement configuration")
  exit(1)

if args.verbose:
  print("Initial balls on rank %d --" % myRank)
  for i in range(0,args.N):
    for j in [0] if args.numDims == 1 else range(0,args.N):
      me = i * args.N + j;
      if me in ballsHeadingEastAt:  print("%5i %4i %4i %s" % (me, i, j, "east"))
      if me in ballsHeadingWestAt:  print("%5i %4i %4i %s" % (me, i, j, "west"))
      if me in ballsHeadingSouthAt: print("%5i %4i %4i %s" % (me, i, j, "south"))
      if me in ballsHeadingNorthAt: print("%5i %4i %4i %s" % (me, i, j, "north"))

def makePonger(i,j,rank):
  me = i * args.N + j;
  ponger = sst.Component("pong_%i_%i" % (i,j), "pingpong.ponger")
  ponger.addParams({
    "ballsHeadingNorth": ballsHeadingNorthAt.get(me, 0),
    "ballsHeadingSouth": ballsHeadingSouthAt.get(me, 0),
    "ballsHeadingWest":  ballsHeadingWestAt.get(me, 0),
    "ballsHeadingEast":  ballsHeadingEastAt.get(me, 0)})
  ponger.setRank(rank)
  pingPongers[me] = ponger;

# top row of "ghost" pongers
if myRank > 0:
  i = rankRowStart-1
  for j in [0] if args.numDims == 1 else range(0,args.N):
    makePonger(i,j,myRank-1)

# pongers owned by this rank
for i in range(rankRowStart,rankRowEnd):
  for j in [0] if args.numDims == 1 else range(0,args.N):
    makePonger(i,j,myRank)

# bottom row of "ghost" pongers
if myRank < numRanks-1:
  i = rankRowEnd
  for j in [0] if args.numDims == 1 else range(0,args.N):
    makePonger(i,j,myRank+1)

# i = row, j = col, (0,0) = north west corner
# Note this loop won't create the east/westward links on of the final row of
# "ghost" pongers but those aren't necessary.
for i in range(max(0,rankRowStart-1),rankRowEnd):
  for j in [0] if args.numDims == 1 else range(0,args.N):
    me = i * args.N + j;
    neighborS = me + args.N
    neighborE = me + 1

    connectS = i < args.N-1
    connectE = j < args.N-1 and args.numDims > 1 and i >= rankRowStart

    if connectS:
      link(i,j, pingPongers[me], pingPongers[neighborS], "south")
    if connectE:
      link(i,j, pingPongers[me], pingPongers[neighborE], "east")

endTime = time.time()
elapsedTime = endTime - startTime
if args.printTime:
  print("Elapsed time on rank %i is %f secs" % (myRank, elapsedTime))
