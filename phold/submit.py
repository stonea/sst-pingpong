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

  parser.add_argument('--node_counts', type=int_list, help="List of node counts to use for the benchmark, e.g., '4 8 16'", required=True)

  parser.add_argument('--widths', type=int_list, help="List of widths to use for the benchmark, e.g., '100 200 250'", required=True)
  parser.add_argument('--heights', type=int_list, help="List of heights to use for the benchmark, e.g., '100 200 250'", required=True)
  parser.add_argument('--event_densities', type=float_list, help="List of event densities to use for the benchmark, e.g., '0.1 0.5 10'", required=True)
  parser.add_argument('--times_to_run', type=int_list, help="List of times to run the benchmark, in nanoseconds, e.g., '1 1000 2500'", required=True)
  
  parser.add_argument('--dry-run' , action='store_true', help="If set, only print the commands that would be run without executing them.")
  parser.add_argument('--name', type=str,help="(Optional) Name of the benchmark job prepended to output files.")

  args = parser.parse_args()
  return args


if __name__ == "__main__":
  args = parse_arguments()

  os.chdir(script_dir)
  subprocess.run("make", shell=True, check=True)
  os.chdir(working_dir)

  for node_count in args.node_counts:
    for width, height, event_density, time_to_run in itertools.product(args.widths, args.heights, args.event_densities, args.times_to_run):
      if args.name:
        output_file = f"{args.name}_{node_count}_{width}_{height}_{event_density}_{time_to_run}"
      else:
        output_file = f"{node_count}_{width}_{height}_{event_density}_{time_to_run}"

      sbatch_portion = f"sbatch -N {node_count} -o {output_file}.out"
      command = f"{sbatch_portion} {script_dir}/dispatch.sh {node_count} {width} {height} {event_density} {time_to_run} {output_file}"
      print(command)
      if not args.dry_run:
        print(f"Running: {command}")
        subprocess.run(command, shell=True, check=True)