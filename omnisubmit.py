import argparse

def int_list(value):
    try:
        return [int(x) for x in value.split()]
    except ValueError:
        raise argparse.ArgumentTypeError(f"Invalid list of integers: '{value}'")
def parse_arguments():
    parser = argparse.ArgumentParser(description="Submit Slurm jobs to evaluate SST.")

    # Required lists of integers
    parser.add_argument(
        "node_counts", 
        type=int_list, 
        help="List of node counts to use (e.g., '1 2 4 8')."
    )
    parser.add_argument(
        "ranks_per_node", 
        type=int_list, 
        help="List of MPI ranks per node to use (e.g., '1 2 4')."
    )
    parser.add_argument(
        "threads_per_rank", 
        type=int_list, 
        help="List of threads per MPI rank to use (e.g., '1 2')."
    )

    # Problem size arguments (required)
    parser.add_argument(
        "--dimensions", 
        type=int, 
        required=True, 
        help="Number of dimensions for the problem (e.g., '2')."
    )
    parser.add_argument(
        "--side-length", "--side-lengths",
        type=int_list, 
        nargs='+', 
        required=True, 
        dest="side_lengths",
        help="List of side lengths of the grid (e.g., '128 256')."
    )

    # Communication pattern arguments
    pattern_group = parser.add_mutually_exclusive_group(required=True)
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
        type=int,
        metavar="COUNT",
        help="Use the random communication pattern with a specified count."
    )
    pattern_group.add_argument(
        "--random-overlap",
        type=int,
        metavar="COUNT",
        help="Use the randomOverlap communication pattern with a specified count."
    )

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
    # Input method argument
    parser.add_argument(
        "--input-method",
        type=input_type_list,
        required=True,
        help="Input method to use (options: 'python', 'parallelPython', 'json')."
    )

    return parser.parse_args()

if __name__ == "__main__":
    args = parse_arguments()
    print(f"Node counts: {args.node_counts}")
    print(f"Ranks per node: {args.ranks_per_node}")
    print(f"Threads per rank: {args.threads_per_rank}")
    print(f"Dimensions: {args.dimensions}")
    print(f"Side lengths: {args.side_lengths}")
    if args.corners:
        print("Using corners communication pattern")
    if args.wavefront:
        print("Using wavefront communication pattern")
    if args.random is not None:
        print(f"Using random communication pattern with count: {args.random}")
    if args.random_overlap is not None:
        print(f"Using randomOverlap communication pattern with count: {args.random_overlap}")
    print(f"Input method: {args.input_method}")