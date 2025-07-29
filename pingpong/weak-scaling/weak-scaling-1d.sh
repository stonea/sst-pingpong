#/bin/bash
#
# This script automates the process of calculating weak scaling problem sizes for 1D problems. 
# It supports evaluating scaling over MPI ranks, MPI oversubscription, and threads, and combinations thereof.
# Arguments:
# - The number of components for the base problem size (1 node, 1 rank per node, 1 thread per rank)
# - The number of messages to send per time step for the base problem size
# - Quoted string of the number of nodes to run with
# - Quoted string of the number of ranks per node to run with
# - Quoted string of the number of threads per rank to run with
# - Quoted string of the number of time steps to run
# - Quoted string of the number of 

# Check for the correct number of arguments
if [ "$#" -ne 6 ]; then
    echo "Usage: $0 <base component count> <base messages> <nodes> <ranks> <threads> <time steps>"
    exit 1
fi

# Extract the arguments
baseComponents=$1
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
            # Submit the job
            ./submit-1d.sh $node $rank $thread $components $messages $timeSteps
          done
        done
    done
done
