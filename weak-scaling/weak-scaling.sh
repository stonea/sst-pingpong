#/bin/bash
#
# This script automates the process of calculating weak scaling problem sizes. 
# It supports evaluating scaling over MPI ranks, MPI oversubscription, and threads, and combinations thereof.
# Arguments:
# - The number of components to use for the base problem size (1 node, 1 rank per node, 1 thread per rank)
# - The number of messages to send per time step for the base problem size
# - Quoted string of the number of nodes to run with
# - Quoted string of the number of ranks per node to run with
# - Quoted string of the number of threads per rank to run with
# - Quoted string of the time steps to run with

# Check for the correct number of arguments
if [ "$#" -ne 6 ]; then
    echo "Usage: $0 <base components> <base messages> <nodes> <ranks> <threads> <time steps>"
    exit 1
fi

# Extract the arguments
base_components=$1
base_messages=$2
nodes=$3
ranks=$4
threads=$5
time_steps=$6

for node in $nodes; do
    for rank in $ranks; do
        for thread in $threads; do
          for time_step in $time_steps; do
            # Calculate the number of components for this configuration
            components=$(($base_components * $node * $rank * $thread))
            # Calculate the number of messages for this configuration
            messages=$(($base_messages * $node * $rank * $thread))
            # Calculate side length for the 2D grid of components
            side_length=$(echo "sqrt($components)" | bc)
            # Print the configuration
            echo "Components: $components, Messages: $messages, Side Length: $side_length, Nodes: $node, Ranks: $rank, Threads: $thread, Time Steps: $time_step"
            # Submit the job
            ./submit.sh $node $rank $thread $side_length $messages $time_step
          done
        done
    done
done