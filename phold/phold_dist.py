import sst
import argparse

my_rank     = sst.getMyMPIRank()
num_ranks   = sst.getMPIRankCount()
num_threads = sst.getThreadCount()

parser = argparse.ArgumentParser(
  prog='PHOLD',
  description='Run a simulation of the PHOLD benchmark.')

parser.add_argument('--N', type=int, default=10, help='Height of grid (number of rows)')
parser.add_argument('--M', type=int, default=10, help='Width of grid (number of columns)')
parser.add_argument('--timeToRun', type=str, default='1000ns', help='Time to run the simulation')
parser.add_argument("--linkDelay", type=str, default="1ns", help="Delay for each link")
parser.add_argument('--numRings', type=int, default=1, help='Number of rings of neighbors to connect to each component')
parser.add_argument('--eventDensity', type=float, default=0.1, help="How many events to transmit per component.")
parser.add_argument('--exponentMultiplier', type=float, default=1.0, help="Multiplier for exponential distribution of event generation")
parser.add_argument('--nodeType', type=str, default='phold.Node', help='Type of node to create (default: phold.Node)')
args = parser.parse_args()


def row_to_rank(i):
  if i < 0 or i >= args.N:
    raise ValueError(f"Row index {i} is out of bounds for N={args.N}")
  # Calculate the rank based on the row index
  return min(i // rows_per_rank, num_ranks - 1)



rows_per_rank = args.N // num_ranks

comps = []


# Create grid of components for my rank
my_row_start = my_rank * rows_per_rank
my_row_end = my_row_start + rows_per_rank #exclusive
if my_rank == num_ranks - 1:  # Last rank gets the rest
  my_row_end = args.N



for i in range(my_row_start, my_row_end):
  row = []
  for j in range(args.M):
    comp = sst.Component(f"comp_{i}_{j}", args.nodeType)
    comp.addParams({
      "numRings": args.numRings,
      "i": i,
      "j": j,
      'colCount': args.M,
      "rowCount": args.N,
      "timeToRun": args.timeToRun,
      "multiplier": args.exponentMultiplier,
      "eventDensity": args.eventDensity
    })

    comp.setRank(row_to_rank(i))
    row.append(comp)
  comps.append(row)

low_rows = []

# Create low ghost components
low_ghost_start = max(0,my_row_start - args.numRings)
low_ghost_end = my_row_start
for i in range(low_ghost_start, low_ghost_end):
  row = []
  for j in range(args.M):
    comp = sst.Component(f"comp_{i}_{j}", args.nodeType)
    comp.addParams({
      "numRings": args.numRings,
      "i": i,
      "j": j,
      'colCount': args.M,
      "rowCount": args.N,
      "timeToRun": args.timeToRun,
      "multiplier": args.exponentMultiplier,
      "eventDensity": args.eventDensity
    })
    comp.setRank(row_to_rank(i))
    row.append(comp)
  low_rows.append(row)
comps = low_rows + comps

# Create high ghost components
high_ghost_start = my_row_end
high_ghost_end = min(args.N, my_row_end + args.numRings)
for i in range(high_ghost_start, high_ghost_end):
  row = []
  for j in range(args.M):
    comp = sst.Component(f"comp_{i}_{j}", args.nodeType)
    comp.addParams({
      "numRings": args.numRings,
      "i": i,
      "j": j,
      'colCount': args.M,
      "rowCount": args.N,
      "timeToRun": args.timeToRun,
      "multiplier": args.exponentMultiplier,
      "eventDensity": args.eventDensity
    })
    comp.setRank(row_to_rank(i))

    row.append(comp)
  comps.append(row)




def port_num(i,j,i2,j2, num_rings):
  side_length = (num_rings * 2 + 1)
  di = i-i2
  dj = j-j2
  ip = num_rings - di
  jp = num_rings - dj
  return ip * side_length + jp
 
linkCount = 0

def connect_upwards(local_i, local_j, num_rings):
  global linkCount
  my_idx = ((num_rings * 2 + 1) ** 2 - 1) // 2 # port number for self connect
  high_idx = (num_rings * 2 + 1) ** 2 - 1 # port number for highest connect

  for neighbor_ring_idx in range(my_idx, high_idx + 1):
    # My indices within the stencil
    my_ring_i = my_idx // (num_rings * 2 + 1)
    my_ring_j = my_idx % (num_rings * 2 + 1)

    # The indices of the neighbor component within the stencil
    neighbor_ring_i = neighbor_ring_idx // (num_rings * 2 + 1)
    neighbor_ring_j = neighbor_ring_idx % (num_rings * 2 + 1)

    # The local indices of the neighbor component
    neighbor_i = local_i + neighbor_ring_i - my_ring_i
    neighbor_j = local_j + neighbor_ring_j - my_ring_j

    if neighbor_i < 0 or neighbor_i >= len(comps) or neighbor_j < 0 or neighbor_j >= args.M:
      continue
    
    port1 = port_num(local_i, local_j, neighbor_i, neighbor_j, num_rings)
    port2 = port_num(neighbor_i, neighbor_j, local_i, local_j, num_rings)

    my_global_i = low_ghost_start + local_i
    my_global_j = local_j

    neighbor_global_i = low_ghost_start + neighbor_i
    neighbor_global_j = neighbor_j

    # Only need the links that connect to a component that lives on this rank
    if row_to_rank(my_global_i) != my_rank and row_to_rank(neighbor_global_i) != my_rank:
      continue
  
    link_name = f"link_{my_global_i}_{my_global_j}_to_{neighbor_global_i}_{neighbor_global_j}"
    link = sst.Link(link_name)
    link.connect((comps[local_i][local_j], f"port{port1}", args.linkDelay), 
                 (comps[neighbor_i][neighbor_j], f"port{port2}", args.linkDelay))
    if port1 == port2:
      linkCount += 1
    else:
      linkCount += 2

    


                                           

for local_i in range(len(comps)):
  for local_j in range(args.M):
    connect_upwards(local_i, local_j, args.numRings)

print("Created %d links" % linkCount)