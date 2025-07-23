import sys, os, argparse, random

sys.path.append(os.environ['AHP_PATH'])
from ahp_graph.Device import *
from ahp_graph.DeviceGraph import *
from ahp_graph.SSTGraph import *

try:
  import sst  # type: ignore[import]
  SST = True
except:
  SST = False

parser = argparse.ArgumentParser(
  prog='GameOfLife',
  description="Conway's Game-Of-Life")
parser.add_argument('--N',               type=int, default=10)
parser.add_argument('--prob',            type=int, default=30)
parser.add_argument('--stop-at',         default="10")
parser.add_argument('--onDemandMode',    default=False, action='store_true')
parser.add_argument('--postOnlyIfAlive', default=False, action='store_true')
parser.add_argument('--verbose',         default=False, action='store_true')
args = parser.parse_args()
cellType = "gol.onDemandCell" if args.onDemandMode else "gol.cell"

if SST:
  sst.setProgramOption("stop-at", args.stop_at)
  myRank = sst.getMyMPIRank()
  numRanks = sst.getMPIRankCount()
else:
  myRank = 0
  numRanks = 1

# -----------------------------------------------------------------------------

class cell(Device):
  """Cell device"""
  library = cellType
  portinfo = PortInfo()
  portinfo.add("nwPort", "GolEvent")
  portinfo.add("nPort",  "GolEvent")
  portinfo.add("nePort", "GolEvent")
  portinfo.add("wPort",  "GolEvent")
  portinfo.add("ePort",  "GolEvent")
  portinfo.add("swPort", "GolEvent")
  portinfo.add("sPort",  "GolEvent")
  portinfo.add("sePort", "GolEvent")

  attr : dict[str, bool] = {
    "isAlive": True,
    "postIfDead": True,
    "shouldReport": False
  }


class board(Device):
  """Assembly of game-of-life board (allocated to one partition)"""
  portinfo = PortInfo()
  portinfo.add('northBorder_nw', 'GolEvent', limit=args.N-1)
  portinfo.add('northBorder_n',  'GolEvent', limit=args.N)
  portinfo.add('northBorder_ne', 'GolEvent', limit=args.N-1)
  portinfo.add('southBorder_sw', 'GolEvent', limit=args.N-1)
  portinfo.add('southBorder_s',  'GolEvent', limit=args.N)
  portinfo.add('southBorder_se', 'GolEvent', limit=args.N-1)

  def expand(self, graph : DeviceGraph) -> None:
    print(f"On ({myRank}) expand {self.name}")

    cells = {}
    for i in range(0, args.N):
      cells[i] = {}
      for j in range(0, args.N):
        rval = random.randint(0,100)
        c = cell(f"cell_{i}_{j}")
        c.attr['isAlive'] = rval <= args.prob
        c.attr['shouldReport'] = args.verbose
        c.attr['postIfDead']   = not args.postOnlyIfAlive
        cells[i][j] = c

    for i in range(0, args.N):
      for j in range(0, args.N):
        if i > 0 and j > 0:
          graph.link(cells[i][j].nwPort, cells[i-1][j-1].sePort, "1s")
        if i > 0:
          graph.link(cells[i][j].nPort,  cells[i-1][j  ].sPort,  "1s")
        if i > 0 and j < args.N-1:
          graph.link(cells[i][j].nePort, cells[i-1][j+1].swPort, "1s")
        if j > 0:
          graph.link(cells[i][j].wPort,  cells[i  ][j-1].ePort,  "1s")

    for j in range(0, args.N):
      if j < args.N-1:
        graph.link(cells[args.N-1][j].sePort, self.southBorder_se(j))
      graph.link(cells[args.N-1][j].sPort, self.southBorder_s(j))
      if j > 0:
        graph.link(cells[args.N-1][j].swPort, self.southBorder_sw(j-1))

      if j < args.N-1:
        graph.link(cells[0][j].nePort, self.northBorder_ne(j))
      graph.link(cells[0][j].nPort, self.northBorder_n(j))
      if j > 0:
        graph.link(cells[0][j].nwPort, self.northBorder_nw(j-1))


def architecture(numBoards) -> DeviceGraph:
  graph = DeviceGraph()
  boards = dict()

  for i in range(numBoards):
    boards[i] = board(f"board{i}")
    boards[i].set_partition(i)
    graph.add(boards[i])

  for i in range(numBoards):
    for j in range(args.N):
      if i > 0:
        graph.link(boards[i-1].southBorder_s(j),  boards[i].northBorder_n(j),  '1s')
        if j < args.N - 1:
          graph.link(boards[i-1].southBorder_sw(j), boards[i].northBorder_ne(j), '1s')
          graph.link(boards[i-1].southBorder_se(j), boards[i].northBorder_nw(j), '1s')

  return graph

# -----------------------------------------------------------------------------

graph = architecture(numRanks)
sstgraph = SSTGraph(graph)

if SST:
  sstgraph.build(numRanks)
