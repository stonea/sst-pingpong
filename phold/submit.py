import math
import argparse
import itertools
import subprocess
import os
import random

working_dir = os.getcwd()
script_dir = os.path.dirname(os.path.realpath(__file__))

def int_list(value):
  try:
    return [int(x) for x in value.split()]
  except ValueError:
    raise argparse.ArgumentTypeError(f"Invalid list of integers: '{value}'")
  
def float_list(value):
  try:
    return [float(x) for x in value.split()]
  except ValueError:
    raise argparse.ArgumentTypeError(f"Invalid list of floats: '{value}'")

def parse_arguments():
  parser = argparse.ArgumentParser(description="Submit PHOLD benchmark jobs.")

  parser.add_argument('--node_counts', '--node-counts', type=int_list, help="List of node counts to use for the benchmark, e.g., '4 8 16'", required=True)

  parser.add_argument('--widths', '--width', type=int_list, help="List of widths to use for the benchmark, e.g., '100 200 250'", default=None)
  parser.add_argument('--components_per_node', '--components-per-node',  type=int_list, default=None, help="List of components-per-node values to use for the simulation. This is used to calculate widths.")
  parser.add_argument('--heights', '--height', type=int_list, help="List of heights to use for the benchmark, e.g., '100 200 250'. The grid is distributed over this dimension.", required=True)
  parser.add_argument('--event_densities', '--event-densities', '--event-density', type=float_list, help="List of event densities to use for the benchmark, e.g., '0.1 0.5 10'", required=True)
  parser.add_argument('--times_to_run', '--times-to-run', '--time-to-run',type=int_list, help="List of times to run the benchmark, in nanoseconds, e.g., '1 1000 2500'", required=True)
  parser.add_argument('--ring_sizes', '--ring-sizes', '--ring-size', type=int_list, default=[1], help="How many rings of neighboring components each component should connect to, e.g., '1 2 4'. Default is [1].")
  parser.add_argument('--small_payloads', '--small-payloads', '--small-payload', type=int_list, default=[8], help="List of small payload sizes in bytes, e.g., '8 16 32'. Default is [8].")
  parser.add_argument('--large_payloads', '--large-payloads', '--large-payload', type=int_list, default=[1024], help="List of large payload sizes in bytes, e.g., '1024 2048 4096'. Default is [1024].")
  parser.add_argument('--large_event_fractions', '--large-event-fractions', '--large-event-fraction', type=float_list, default=[0.0], help="List of fractions of large events, e.g., '0.1 0.2 0.5'. Default is [0.1].")
  parser.add_argument('--dry_run', '--dry-run', action='store_true', help="If set, only print the commands that would be run without executing them.")
  parser.add_argument('--name', type=str, default="phold", help="(Optional) Name of the benchmark job prepended to output files.")

  # Weak scaling is used to indicate that the combinations of height and width are the "per-node" shape.
  # With a weak scaling run, if we vary the height, we are varying the per-node component count.
  # Sometimes, we want to run weak scaling where the per-node component count is fixed, the height varies, but the width varies.
  # In such a circumstance, we would want to have the per-node component count be used to dynamically calculate the necessary widths.
  # Or maybe, we want to say "the first width is the value that calculates the per-node component count. Vary widths as the height changes to maintain the per-node component count."

  parser.add_argument('--weak_scaling', '--weak', '--weak-scaling', action='store_true', help="If set, use weak scaling. The height will be multiplied by the node count to maintain the per-node linking.")
  parser.add_argument('--stochastic', type=int, help="If set, treat the arguments to this script as integer constants or range bounds, \
                      rather than lists of values. The value of this variable is the number of points in the resulting space to sample.")
  args = parser.parse_args()
  assert(args.widths is not None or args.components_per_node is not None), "Either --width or --components-per-node must be specified."
  return args


def calculate_grid_shapes(args):
  shapes = []
  if not args.weak_scaling and args.components_per_node is None:
    return list(itertools.product(args.widths, args.heights, args.node_counts))
  elif args.components_per_node is None:
    for per_node_width, per_node_height, node_count in itertools.product(args.widths, args.heights, args.node_counts):
      shapes.append((per_node_width, per_node_height * node_count, node_count))
  
  elif not args.weak_scaling:
    for per_node_component_count, grid_height, node_count in itertools.product(args.components_per_node, args.heights, args.node_counts):
      component_count = node_count * per_node_component_count
      grid_width = math.ceil(component_count / grid_height)
      shapes.append((grid_width, grid_height, node_count))
  else:
    # We are weak scaling and using a per-node component count.
    for per_node_component_count, per_node_height, node_count in itertools.product(args.components_per_node, args.heights, args.node_counts):
      component_count = node_count * per_node_component_count
      grid_height = per_node_height * node_count
      grid_width = math.ceil(component_count / grid_height)
      shapes.append((grid_width, grid_height, node_count))
  return shapes


if __name__ == "__main__":
  args = parse_arguments()

  os.chdir(script_dir)
  subprocess.run("make", shell=True, check=True)
  os.chdir(working_dir)

  if args.stochastic:
    
    # Turn the single values into ranges with a single element
    if len(args.node_counts) == 1:
      args.node_counts = [args.node_counts[0]] * 2
    if len(args.widths) == 1:
      args.widths = [args.widths[0]] * 2
    if len(args.heights) == 1:
      args.heights = [args.heights[0]] * 2
    if len(args.event_densities) == 1:
      args.event_densities = [args.event_densities[0]] * 2
    if len(args.ring_sizes) == 1:
      args.ring_sizes = [args.ring_sizes[0]] * 2
    if len(args.times_to_run) == 1:
      args.times_to_run = [args.times_to_run[0]] * 2
    if len(args.small_payloads) == 1:
      args.small_payloads = [args.small_payloads[0]] * 2
    if len(args.large_payloads) == 1:
      args.large_payloads = [args.large_payloads[0]] * 2
    if len(args.large_event_fractions) == 1:
      args.large_event_fractions = [args.large_event_fractions[0]] * 2
    
    shape_parameters = []
    non_shape_parameters = []
    for i in range(args.stochastic):
      density = round(random.uniform(*args.event_densities), 2)
      non_shape_point = (density, random.randint(*args.ring_sizes), random.randint(*args.times_to_run), random.randint(*args.small_payloads),
              random.randint(*args.large_payloads), random.uniform(*args.large_event_fractions))
      shape_point = (random.randint(*args.node_counts), random.randint(*args.widths), random.randint(*args.heights))
      shape_parameters.append(shape_point)
      non_shape_parameters.append(non_shape_point)

  else:
    shape_parameters = calculate_grid_shapes(args)
    non_shape_parameters = list(itertools.product(args.event_densities, args.ring_sizes, args.times_to_run,
                                        args.small_payloads, args.large_payloads, args.large_event_fractions))

  print("Shapes: ", shape_parameters)
  for (width, height, node_count) in shape_parameters:
    for (event_density, ring_size, time_to_run, small_payload, large_payload, large_event_fraction) in non_shape_parameters:
      output_file = f"{args.name}_{node_count}_{width}_{height}_{event_density}_{ring_size}_{time_to_run}_{small_payload}_{large_payload}_{large_event_fraction}"
      sbatch_portion = f"sbatch -N {node_count} -o {output_file}.out"
      command = f"{sbatch_portion} {script_dir}/dispatch.sh {node_count} {width} {height} {event_density} {ring_size} {time_to_run} {small_payload} {large_payload} {large_event_fraction} {output_file}"
      print(command)
      if not args.dry_run:
        print(f"Running: {command}")
        subprocess.run(command, shell=True, check=True)
      