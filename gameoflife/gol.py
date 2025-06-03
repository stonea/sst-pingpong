import sst
import argparse, random

parser = argparse.ArgumentParser(
  prog='GameOfLife',
  description="Conway's Game-Of-Life")
parser.add_argument('--N',       type=int, default=10)
parser.add_argument('--prob',    type=int, default=30)
parser.add_argument('--stop-at', default="5s")
args = parser.parse_args()

sst.setProgramOption("stop-at", args.stop_at)

myRank = sst.getMyMPIRank()
numRanks = sst.getMPIRankCount()

# ranks 0-(args.N%numRanks) will have args.N / numRanks + 1 rows
# and all subsequent ranks will have args.N / numRanks
myRowStart = int(args.N / numRanks) * myRank + min(myRank, args.N % numRanks)
myRowEnd   = myRowStart + int(args.N / numRanks) - 1
if myRank < args.N % numRanks:
  myRowEnd += 1

# -----------------------------------------------------------------------------
cells = {}
links = set()

def createLink(srcRow, srcCol, offRow, offCol, srcPort, tgtPort):
  tgtRow = srcRow + offRow
  tgtCol = srcCol + offCol
  if tgtRow < 0 or tgtCol < 0 or tgtRow >= args.N or tgtCol >= args.N:
    return
  if (srcRow not in cells) or (tgtRow not in cells):
    return

  srcComp = cells[srcRow][srcCol]
  tgtComp = cells[tgtRow][tgtCol]

  minRow = min( (srcRow,srcCol), (tgtRow,tgtCol) )[0]
  minCol = min( (srcRow,srcCol), (tgtRow,tgtCol) )[1]
  maxRow = max( (srcRow,srcCol), (tgtRow,tgtCol) )[0]
  maxCol = max( (srcRow,srcCol), (tgtRow,tgtCol) )[1]
  name = "link_%i_%i__%i_%i" % (minRow,minCol,maxRow,maxCol)

  if not name in links:
    sst.Link(name).connect( (srcComp, srcPort, "1s"), (tgtComp, tgtPort, "1s") )
    links.add(name)

# -----------------------------------------------------------------------------
r = random.randint(0, args.N * args.N - 1)
for row in range(max(0,myRowStart-1), min(args.N,myRowEnd+2)):
  cells[row] = {}
  for col in range(0, args.N):
    rval = random.randint(0,100)
    cell = sst.Component("cell_%i_%i" % (row,col), "gol.cell")
    cells[row][col] = cell
    if row < myRowStart:
      cell.setRank(myRank-1)
    elif row > myRowEnd:
      cell.setRank(myRank+1)
    else:
      cell.addParams({"isAlive": rval <= args.prob})
      cell.setRank(myRank)


for row in range(max(0,myRowStart-1), min(args.N,myRowEnd+2)):
  for col in range(0, args.N):
    createLink(row, col, -1, -1, "nwPort", "sePort" )
    createLink(row, col, -1,  0, "nPort",  "sPort"  )
    createLink(row, col, -1,  1, "nePort", "swPort" )
    createLink(row, col,  0, -1, "wPort",  "ePort"  )
    createLink(row, col,  0,  1, "ePort",  "wPort"  )
    createLink(row, col,  1, -1, "swPort", "nePort" )
    createLink(row, col,  1,  0, "sPort",  "nPort"  )
    createLink(row, col,  1,  1, "sePort", "nwPort" )



#r = random.randint(0, args.N * args.N - 1)
#for row in range(max(0,myRowStart-1), min(args.N,myRowEnd+2)):
#  cells[row] = {}
#  for col in range(0, args.N):
#    rval = random.randint(0,100)
#    cell = sst.Component("cell_%i_%i" % (row,col), "gol.cell")
#    cells[row][col] = cell
#
#    createLink(row, col,  0, -1, "wPort",  "ePort" )
#    createLink(row, col, -1, -1, "nwPort", "swPort")
#    createLink(row, col, -1,  0, "nPort",  "sPort" )
#    createLink(row, col, -1,  1, "nePort", "sePort")
