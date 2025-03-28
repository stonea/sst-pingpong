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

def parse_arguments():
    parser = argparse.ArgumentParser(description="Submit Slurm jobs to evaluate SST.")

    # Required scale arguments
    scale_group = parser.add_argument_group("Scale Options")
    scale_group.add_argument(
        "node_counts", 
        type=int_list, 
        help="List of node counts to use (e.g., '1 2 4 8')."
    )
    scale_group.add_argument(
        "ranks_per_node", 
        type=int_list, 
        help="List of MPI ranks per node to use (e.g., '1 2 4')."
    )
    scale_group.add_argument(
        "threads_per_rank", 
        type=int_list, 
        help="List of threads per MPI rank to use (e.g., '1 2')."
    )

    # Problem size arguments (required)
    grid_group = parser.add_argument_group("Grid Options")
    grid_group.add_argument(
        "--dimensions", 
        type=int_list,
        required=True, 
        help="Number(s) of dimensions to use (1 or 2 or '1 2' for both)."
    )
    grid_group.add_argument(
        "--side-length", "--side-lengths", "--sideLengths", "--sideLength",
        type=int_list, 
        dest="side_lengths",
        default="",
        help="List of side lengths of the grid (e.g., '128 256')."
    )
    grid_group.add_argument(
        "--component-counts", "--component-count", "--componentCounts", "--componentCount",
        type=int_list,
        dest="component_counts",
        default="",
        help="List of component counts to use for the simulation. Be careful to use square numbers when running 2D simulations."
        )

    # Communication pattern arguments
    pattern_group = parser.add_argument_group("Communication Pattern Options")
    pattern_group.add_argument(
        "--corners",
        action="store_true",
        help="Use the corners communication pattern."
    )
    pattern_group.add_argument(
        "--wavefront",
        action="store_true",
        help="Use the wavefront communication pattern."
    )
    pattern_group.add_argument(
        "--random",
        type=int_list,
        metavar="COUNT(S)",
        help="Use the random communication pattern with a specified count."
    )
    pattern_group.add_argument(
        "--random-overlap", "--randomOverlap",
        dest="random_overlap",
        type=int_list,
        metavar="COUNT(S)",
        help="Use the randomOverlap communication pattern with a specified count."
    )
    
    time_group = parser.add_argument_group("Time Options")
    time_group.add_argument(
        "--timestep-count", "--timestep-counts", "--time-to-run", "--times-to-run",
        dest="timestep_counts",
        type=int_list,
        help="List of timestep counts to use (e.g., '100 200').",
        default="1000"
    )
    time_group.add_argument("--edge-delay", '--edgeDelay', type=int, default=50, help="Edge delay between components. Default is 50.")

    sim_group = parser.add_argument_group("Other Simulation Options")
    # Input method argument
    def input_type_list(value):
        valid_inputs = ["python", "parallelPython", "json"]
        try:
            values = value.split()
            for v in values:
                if v not in valid_inputs:
                    raise ValueError
            return values
        except ValueError:
            raise argparse.ArgumentTypeError(f"Invalid list of strings: '{value}'")
    sim_group.add_argument(
        "--input-method",
        type=input_type_list,
        metavar="METHOD(S)",
        required=True,
        help="Input method to use (options: 'python', 'parallelPython', 'json'). This accepts a quoted, space-separated list of valid options as well. (e.g., --input-method 'python parallelPython')"
    )

    sim_group.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose simulation output."
    )

    experiment_group = parser.add_argument_group("Experiment Options")
    experiment_group.add_argument(
        "--hpctoolkit",
        nargs='?',
        const = '',
        default = None,
        help="Runs simulations with hpctoolkit, optionally passing the argument text as a flag to hpctoolkit. (e.g., --hpctoolkit='-e MEMLEAK')"
    )

    experiment_group.add_argument(
        "--weak-scaling",
        action='store_true',
        help="Run weak scaling evaluation. This treats all grid and \
              communication configurations as the configuration for \
              a 1-node, 1-rank, 1-thread run. It then runs the simulation \
              with scaled problem sizes of those base configurations."
    )

    experiment_group.add_argument(
        "--name",
        type=str,
        help="(Optional) Name of the experiment that is appended to the output files."
    )

    parser.add_argument(
        "--dry",
        action="store_true",
        help="Dry run (do not submit jobs)."
    )

    args = parser.parse_args()

    if args.side_lengths + args.component_counts == []:
        parser.error("At least one of --side-length or --component-counts must be provided.")

    return args

def print_args(args):
    print(f"Node counts: {args.node_counts}")
    print(f"Ranks per node: {args.ranks_per_node}")
    print(f"Threads per rank: {args.threads_per_rank}")
    print(f"Dimensions: {args.dimensions}")
    print(f"Side lengths: {args.side_lengths}")
    print(f"Component counts: {args.component_counts}")
    if args.corners:
        print("Using corners communication pattern")
    if args.wavefront:
        print("Using wavefront communication pattern")
    if args.random is not None:
        print(f"Using random communication pattern with count: {args.random}")
    if args.random_overlap is not None:
        print(f"Using randomOverlap communication pattern with count: {args.random_overlap}")
    print(f"Timestep counts: {args.timestep_counts}")
    print(f'Edge delay: {args.edge_delay}')
    print(f"Input method: {args.input_method}")
    if args.verbose:
        print("Verbose output enabled")
    if args.hpctoolkit != '0':
        print("Running simulations with hpctoolkit")
    if args.dry:
        print("Dry run enabled")
    if args.weak_scaling:
        print("Running weak scaling evaluation")
    if args.name:
        print(f"Experiment name: {args.name}")

def comm_configs_list(args):
    comm_pattern_args = []
    if args.corners:
        comm_pattern_args.append("corners")
    if args.wavefront:
        comm_pattern_args.append("wavefront")
    if args.random is not None:
        for count in args.random:
            comm_pattern_args.append(f"random {count}")
    if args.random_overlap is not None:
        for count in args.random_overlap:
            comm_pattern_args.append(f"randomOverlap {count}")
    return comm_pattern_args

def grid_config_lists(args):
    grid_configs = []
    # Configs for 1D simulations
    if 1 in args.dimensions:
        counts = args.component_counts + args.side_lengths
        for count in counts:
            config = (1,count)
            grid_configs.append(config)

    # Configs for 2D simulations
    if 2 in args.dimensions:
        for count in args.component_counts:
            side_length = int(math.sqrt(count))
            config = (2, side_length)
            grid_configs.append(config)
        for side_length in args.side_lengths:
            config = (2, side_length)
            grid_configs.append(config)
    
    return grid_configs
        


def submit_job(node_count, ranks_per_node, threads_per_rank, comm_config, grid_config, timestep_count, edge_delay, verbosity, input_method, with_toolkit, dry):
    #print(f"Submitting job with scale {node_count}x{ranks_per_node}x{threads_per_rank}, {comm_config}, {grid_config}, {side_length}, {timestep_count}, {input_method}")

    prefix=f"{node_count}_{ranks_per_node}_{threads_per_rank}"

    grid_prefix = f"{grid_config[0]}_{grid_config[1]}"
    comm_prefix = "_".join(comm_config.split())
    prefix = prefix + f"_{comm_prefix}_{grid_prefix}_{timestep_count}_{edge_delay}_{int(verbosity)}_{input_method}"
    if with_toolkit:
        prefix = prefix + "_hpctoolkit"
        if with_toolkit != '':
            prefix = prefix + "_" + with_toolkit.replace(' ', '_')
    if args.name:
        prefix = prefix + "_" + args.name
    outfile = prefix + ".out"


    script_path = os.path.join(script_dir, "omnidispatch.sh")

    sbatch_portion = f"sbatch -N {node_count} --cpus-per-task {threads_per_rank} --ntasks-per-node {ranks_per_node} -o {outfile}"
    arglist = f'{node_count} {ranks_per_node} {threads_per_rank} "{comm_config}" {grid_config[0]} {grid_config[1]} {timestep_count} {edge_delay} {int(verbosity)} {input_method} "{with_toolkit}" {prefix}'
    command = sbatch_portion + f" {script_path} " + arglist
    print(command)
    if not dry:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)

def scale_comms(comm_config, scale_config):
    if comm_config == "corners" or comm_config == "wavefront":
        return comm_config
    message_count = comm_config.split()[1]
    num_processes = scale_config[0] * scale_config[1] * scale_config[2]
    scaled_message_count = int(message_count) * num_processes
    return comm_config.split()[0] + " " + str(scaled_message_count)

def scale_grid(grid_config, scale_config):
    component_count = grid_config[1] ** grid_config[0]
    num_processes = scale_config[0] * scale_config[1] * scale_config[2]
    scaled_component_count = component_count * num_processes
    scaled_side_length = int(math.pow(scaled_component_count, 1/grid_config[0]))
    return (grid_config[0], scaled_side_length)

def run_weak_scaling(args, scale_configs, comm_configs, grid_configs):
    for comm_config in comm_configs:
        for grid_config in grid_configs:
            for scale_config in scale_configs:
                scaled_comms = scale_comms(comm_config, scale_config)
                scaled_grid = scale_grid(grid_config, scale_config)
                for timestep_count in args.timestep_counts:
                        for input_method in args.input_method:
                            submit_job(scale_config[0], scale_config[1], scale_config[2], scaled_comms, scaled_grid, timestep_count, args.edge_delay, args.verbose, input_method, args.hpctoolkit, args.dry)

if __name__ == "__main__":
    args = parse_arguments()
    print_args(args)
    
    scale_configs = list(itertools.product(args.node_counts, args.ranks_per_node, args.threads_per_rank))
    comm_configs = comm_configs_list(args)
    grid_configs = grid_config_lists(args)

    os.chdir(script_dir)
    subprocess.run("make", shell=True, check=True)
    os.chdir(working_dir)

    if args.weak_scaling:
        run_weak_scaling(args, scale_configs, comm_configs, grid_configs)
    else:
        for (node_count, ranks_per_node, threads_per_rank) in scale_configs:
            for comm_config in comm_configs:
                for grid_config in grid_configs:
                    for timestep_count in args.timestep_counts:
                        for input_method in args.input_method:
                            submit_job(node_count, ranks_per_node, threads_per_rank, comm_config, grid_config, timestep_count, args.edge_delay, args.verbose, input_method, args.hpctoolkit, args.dry)