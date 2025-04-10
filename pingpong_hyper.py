# This version of ping pong is meant to be run using sst with
# --parallel-load=SINGLE.  For --random and --randomOverlap ball placement we
# put a (roughly) even number of randomly place balls in each rank. Excess
# balls are placed on the final rank.

import sst
import time, argparse, random

startTime = time.time()

parser = argparse.ArgumentParser(
  prog='SSTPingPong',
  description='Run a simulation consisting of several components arranged in a 1D or 2D grid that send messages back and forth')
parser.add_argument('--N',              type=int, default=2)
parser.add_argument('--timeToRun',      type=int, default=200)
parser.add_argument('--edgeDelay',      type=int, default=50)
parser.add_argument('--artificialWork', type=int, default=0)
parser.add_argument('--verbose',        default=False, action='store_true')
parser.add_argument('--dryRun',         type=int, default=-1)
group = parser.add_mutually_exclusive_group(required=True)
group.add_argument('--corners',         default=False, action='store_true')
group.add_argument('--random',          type=int, default=-1)
group.add_argument('--randomOverlap',   type=int, default=-1)
group.add_argument('--wavefront',       default=False, action='store_true')
args = parser.parse_args()

# -----------------------------------------------------------------------------

N = args.N
nGrids = N * 100
nHlPerPt = 100

if args.dryRun == -1:
  myRank   = sst.getMyMPIRank()
  numRanks = sst.getMPIRankCount()
else:
  myRank   = 0
  numRanks = args.dryRun

# -----------------------------------------------------------------------------

pongers = {}
numGhostPongers = 0
numNumGhostComponents = 0

def oppositeDir(direction):
  opposites = {'north': 'south', 'south': 'north', 'west' : 'east', 'east' : 'west'}
  return opposites[direction]

def pongerId(g,i,j):
  return g * (N*N) + i * N + j;

def pongerLoc(someId):
  gridNum = int(someId / (N*N))
  xyId = int(someId % (N*N));
  i = int(xyId / N)
  j = int(xyId % N)
  return (gridNum,i,j)

def ponger(g,i,j):
  global pongers, numGhostPongers, numNumGhostComponents 

  me = pongerId(g,i,j)
  if me in pongers:
    return pongers[me]

  ponger = None
  if args.dryRun == -1:
    ponger = sst.Component("p%i" % (me), "pingpong.hyperPonger")
  else:
    ponger = 1 # dummy value
  pongerRank = int(g / gridsPerRank)
  ponger.setRank(pongerRank)
  if pongerRank == myRank:
    ponger.addParams({"numBalls": 0})
  pongers[me] = ponger;

  isGhostPonger = int(g/gridsPerRank) != myRank
  if isGhostPonger:
    numGhostPongers += 1
  else:
    numNumGhostComponents += 1

  if args.verbose:
    print(f"Make ponger ({g},{i},{j}) on {int(g / gridsPerRank)} {'*' if ghostPonger else ' '}")
  return ponger

def hyperLink(g1,i1,j1, g2,i2,j2, port1Name, port2Name):
  id1 = pongerId(g1,i1,j1)
  id2 = pongerId(g2,i2,j2)
  minId = min(id1,id2)
  maxId = max(id1,id2)

  ponger1 = ponger(g1,i1,j1)
  ponger2 = ponger(g2,i2,j2)

  if args.verbose:
    print("Connect (%d,%d,%d) %s -- (%d,%d,%d) %s" % (g1,i1,j1,port1Name, g2,i2,j2,port2Name))

  linkName = "l%d_%d" % (minId, maxId)
  if args.dryRun != -1:
    sst.Link(linkName).connect( (ponger1, port1Name, "%is" % args.edgeDelay), (ponger2, port2Name, "%is" % args.edgeDelay) )

# -----------------------------------------------------------------------------

gridsPerRank = int(nGrids / numRanks)

if nGrids % numRanks != 0:
  print("nGrids (%d) not divisible by numRanks (%d) how about run with %d or %d compute nodes?" %
        (nGrids, numRanks, (nGrids / int(nGrids/numRanks)), (nGrids / (int(nGrids/numRanks)+1))))
  exit(1)

if myRank == 0:
  ballGen = sst.Component("sim", "pingpong.simulator")
  ballGen.addParams({"timeToRun"      : args.timeToRun,
                     "verbose"        : args.verbose,
                     "artificialWork" : args.artificialWork})
  ballGen.setRank(0)

firstGridOnRank = myRank * gridsPerRank
for g in range(firstGridOnRank, (myRank+1) * gridsPerRank):
  nextGridToConnect = int((nGrids - g + nHlPerPt - 1) % nGrids / nHlPerPt) * nHlPerPt

  for i in range(0,N):
    for j in range(0,N):
      ponger(g,i,j)

      if i+1 < N:
        hyperLink(g,i,j, g,i+1,j, "port_s", "port_n")
      if j+1 < N:
        hyperLink(g,i,j, g,i,j+1, "port_e", "port_w")

      for x in range(0,nHlPerPt):
        if nextGridToConnect > g or nextGridToConnect < firstGridOnRank:
          hyperLink(g,i,j, nextGridToConnect,i,j, "port_%d" % (x), "port_%d" % (g % nHlPerPt))
        nextGridToConnect = (nextGridToConnect + 1) % nGrids

print("Rank %3d nGrids=%8d numNonGhostComponents=%12d numGhostComponents=%14d" % (myRank, nGrids, numNumGhostComponents, numGhostPongers))
if(args.dryRun != -1):
  sys.exit(1)

endTime = time.time()
elapsedTime = endTime - startTime
print("Elapsed time on rank %i is %f secs" % (myRank, elapsedTime))
