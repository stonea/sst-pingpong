import sst
import argparse, random

parser = argparse.ArgumentParser(
  prog='GameOfLife',
  description="Conway's Game-Of-Life")
parser.add_argument('--N',            type=int, default=10)
parser.add_argument('--M',            type=int, default=-1)
parser.add_argument('--prob',         type=int, default=30)
parser.add_argument('--stop-at',      default="5s")
parser.add_argument('--onDemandMode', default=False, action='store_true')
args = parser.parse_args()

sst.setProgramOption("stop-at", args.stop_at)

myRank = sst.getMyMPIRank()
numRanks = sst.getMPIRankCount()
cellType = "gol.onDemandCell" if args.onDemandMode else "gol.cell"

if args.M == -1:
  args.M = args.N

# We do a block-row partitioning of the game board.  Because the number of rows
# might not be divisible my the number of MPI ranks we will have ranks 0
# through (args.M%numRanks) have (args.M / numRanks + 1) rows # and all
# subsequent ranks will have (args.M / numRanks).  IOW we evenly divide as best
# we can, and then add an extra row to the first (args.M%numRanks) to get us to
# our desired game board size.
#
# myRowStart and myRowEnd produce na inclusive range (IOW this rank owns row
# 'myRowEnd'). 
myRowStart = int(args.M / numRanks) * myRank + min(myRank, args.M % numRanks)
myRowEnd   = myRowStart + int(args.M / numRanks) - 1
if myRank < args.M % numRanks:
  myRowEnd += 1

# -----------------------------------------------------------------------------
cells = {}
links = set()

def createLink(srcRow, srcCol, offRow, offCol, srcPort, tgtPort):
  tgtRow = srcRow + offRow
  tgtCol = srcCol + offCol

  # Don't create a link that would go off the board
  if tgtRow < 0 or tgtCol < 0 or tgtRow >= args.M or tgtCol >= args.N:
    return

  # Don't create a link to a component that has not been made
  if (srcRow not in cells) or (tgtRow not in cells):
    return

  srcComp = cells[srcRow][srcCol]
  tgtComp = cells[tgtRow][tgtCol]

  # We want to 'normalize' link names so that a link that goes from component
  # 'x' to 'y' and a link that goes from component 'y' to 'x' will have the
  # same name.
  minRow = min( (srcRow,srcCol), (tgtRow,tgtCol) )[0]
  minCol = min( (srcRow,srcCol), (tgtRow,tgtCol) )[1]
  maxRow = max( (srcRow,srcCol), (tgtRow,tgtCol) )[0]
  maxCol = max( (srcRow,srcCol), (tgtRow,tgtCol) )[1]
  name = "link_%i_%i__%i_%i" % (minRow,minCol,maxRow,maxCol)

  # Avoid making duplicate links
  if not name in links:
    sst.Link(name).connect( (srcComp, srcPort, "1s"), (tgtComp, tgtPort, "1s") )
    links.add(name)

# -----------------------------------------------------------------------------

# First create the portion of the game board this rank is responsible for as
# well as one row below and above what this rank is responsible for (so that we
# can connect to it).
for row in range(max(0,myRowStart-1), min(args.M,myRowEnd+2)):
  cells[row] = {}
  for col in range(0, args.N):
    cell = sst.Component("cell_%i_%i" % (row,col), cellType)
    cells[row][col] = cell
    if row < myRowStart:
      cell.setRank(myRank-1)
    elif row > myRowEnd:
      cell.setRank(myRank+1)
    else:
      cell.setRank(myRank)
      rval = random.randint(0,100)
      cell.addParams({"isAlive": rval <= args.prob})

# Create links for all components owned by this rank
for row in range(max(0,myRowStart), min(args.M,myRowEnd+1)):
  for col in range(0, args.N):
    createLink(row, col, -1, -1, "nwPort", "sePort" )
    createLink(row, col, -1,  0, "nPort",  "sPort"  )
    createLink(row, col, -1,  1, "nePort", "swPort" )
    createLink(row, col,  0, -1, "wPort",  "ePort"  )
    createLink(row, col,  0,  1, "ePort",  "wPort"  )
    createLink(row, col,  1, -1, "swPort", "nePort" )
    createLink(row, col,  1,  0, "sPort",  "nPort"  )
    createLink(row, col,  1,  1, "sePort", "nwPort" )
