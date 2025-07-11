import math
import argparse
import itertools
import subprocess
import os

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

  parser.add_argument('--widths', '--width', type=int_list, help="List of widths to use for the benchmark, e.g., '100 200 250'", required=True)
  parser.add_argument('--heights', '--height', type=int_list, help="List of heights to use for the benchmark, e.g., '100 200 250'. The grid is distributed over this dimension.", required=True)
  parser.add_argument('--event_densities', '--event-densities', type=float_list, help="List of event densities to use for the benchmark, e.g., '0.1 0.5 10'", required=True)
  parser.add_argument('--times_to_run', '--times-to-run',type=int_list, help="List of times to run the benchmark, in nanoseconds, e.g., '1 1000 2500'", required=True)
  parser.add_argument('--ring_sizes', '--ring-sizes' , type=int_list, default=[1], help="How many rings of neighboring components each component should connect to, e.g., '1 2 4'. Default is [1].")
  parser.add_argument('--dry-run' , action='store_true', help="If set, only print the commands that would be run without executing them.")
  parser.add_argument('--name', type=str, default="phold", help="(Optional) Name of the benchmark job prepended to output files.")
  parser.add_argument('--weak_scaling', '--weak', '--weak-scaling', action='store_true', help="If set, use weak scaling. The height will be multiplied by the node count to maintain the per-node linking.")

  args = parser.parse_args()
  return args


if __name__ == "__main__":
  args = parse_arguments()

  os.chdir(script_dir)
  subprocess.run("make", shell=True, check=True)
  os.chdir(working_dir)


  for (node_count, width, height, event_density, ring_size, time_to_run) in itertools.product(args.node_counts, args.widths, args.heights, args.event_densities, args.ring_sizes, args.times_to_run):
      if args.weak_scaling:
        height *= node_count
      
      output_file = f"{args.name}_{node_count}_{width}_{height}_{event_density}_{ring_size}_{time_to_run}"
      sbatch_portion = f"sbatch -N {node_count} -o {output_file}.out"
      command = f"{sbatch_portion} {script_dir}/dispatch.sh {node_count} {width} {height} {event_density} {ring_size} {time_to_run} {output_file}"
      print(command)
      if not args.dry_run:
        print(f"Running: {command}")
        subprocess.run(command, shell=True, check=True)
      