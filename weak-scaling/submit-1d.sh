#!/bin/bash
#
# Arguments are quoted strings representing the node counts, thread counts, sst element counts, and ball counts.
#
set -e
set -x
# Check if there are exactly four arguments
if [ "$#" -ne 6 ]; then
    echo "Error: Six arguments are required."
    echo "Usage: $0 <nodeCounts> <tasksPerNodeCounts> <threadCounts> <componentCounts>  <messageCounts (or 'wavefront' or 'corners')> <timeStepCounts> "
    exit 1
fi

# Assign arguments to variables
nodeCounts=$1
tasksPerNodeCounts=$2
threadCounts=$3
componentCounts=$4
messageCounts=$5
timeStepCounts=$6


# Print the values (optional)
echo "nodeCounts: $nodeCounts"
echo "tasksPerNodeCounts: $tasksPerNodeCounts"
echo "threadCounts: $threadCounts"
echo "componentCounts: $componentCounts"
echo "messageCounts: $messageCounts"
echo "timeStepCounts: $timeStepCounts"



echo "Making..."
pushd ..
make
popd 
for nodeCount in $nodeCounts; do
  for tasksPerNode in $tasksPerNodeCounts; do
    for threadCount in $threadCounts; do
      for componentCount in $componentCounts; do
        for messageCount in $messageCounts; do
          for timeStepCount in $timeStepCounts; do
            outfile=${nodeCount}_${tasksPerNode}_${threadCount}_${componentCount}_${messageCount}_${timeStepCount}_1d.time
            sbatch -N $nodeCount --cpus-per-task $threadCount --ntasks-per-node $tasksPerNode -o $outfile scaling-1d.sh $nodeCount $tasksPerNode $threadCount $componentCount $messageCount $timeStepCount
          done
        done
      done
    done
  done
done
