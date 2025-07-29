#/bin/bash
#
# This script automates the process of calculating weak scaling problem sizes. 
# It supports evaluating scaling over MPI ranks, MPI oversubscription, and threads, and combinations thereof.
# Arguments:
# - The side length of the 2D grid for the base problem size (1 node, 1 rank per node, 1 thread per rank)
# - The number of messages to send per time step for the base problem size
# - Quoted string of the number of nodes to run with
# - Quoted string of the number of ranks per node to run with
# - Quoted string of the number of threads per rank to run with
# - Quoted string of the number of time steps to run
# - Quoted string of the number of 

# Check for the correct number of arguments
if [ "$#" -ne 6 ]; then
    echo "Usage: $0 <base side length> <base messages> <nodes> <ranks> <threads> <time steps>"
    exit 1
fi

# Extract the arguments
baseSideLengths=$1
baseComponents=$((baseSideLengths * $baseSideLengths))
baseMessages=$2
nodes=$3
ranks=$4
threads=$5
timeStep=$6

for node in $nodes; do
    for rank in $ranks; do
        for thread in $threads; do
          for timeSteps in $timeStep; do
            # Calculate the number of components for this configuration
            components=$(($baseComponents * $node * $rank * $thread))
            # Calculate the number of messages for this configuration
            messages=$(($baseMessages * $node * $rank * $thread))
            # Calculate side length for the 2D grid of components
            sideLength=$(echo "sqrt($components)" | bc)
            # Print the configuration
            echo "Components: $components, Messages: $messages, Side Length: $sideLength, Nodes: $node, Ranks: $rank, Threads: $thread, Time Steps: $timeSteps"
            # Submit the job
            ./submit.sh $node $rank $thread $sideLength $messages $timeSteps
          done
        done
    done
done
