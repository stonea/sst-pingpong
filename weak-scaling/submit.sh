#!/bin/bash
#
# Arguments are quoted strings representing the node counts, thread counts, sst element counts, and ball counts.
#
set -e
set -x
# Check if there are exactly four arguments
if [ "$#" -ne 6 ]; then
    echo "Error: Six arguments are required."
    echo "Usage: $0 <nodeCounts> <tasksPerNodeCounts> <threadCounts> <sideLengths>  <messageCounts (or 'wavefront' or 'corners')> <timeStepCounts> "
    exit 1
fi

# Assign arguments to variables
nodeCounts=$1
tasksPerNodeCounts=$2
threadCounts=$3
sideLengths=$4
messageCounts=$5
timeStepCounts=$6


# Print the values (optional)
echo "nodeCounts: $nodeCounts"
echo "tasksPerNodeCounts: $tasksPerNodeCounts"
echo "threadCounts: $threadCounts"
echo "sideLengths: $sideLengths"
echo "messageCounts: $messageCounts"
echo "timeStepCounts: $timeStepCounts"



echo "Making..."
pushd ..
make
popd 
for nodeCount in $nodeCounts; do
  for tasksPerNode in $tasksPerNodeCounts; do
    for threadCount in $threadCounts; do
      for sideLength in $sideLengths; do
        for messageCount in $messageCounts; do
          for timeStepCount in $timeStepCounts; do
            outfile=${nodeCount}_${tasksPerNode}_${threadCount}_${sideLength}_${messageCount}_${timeStepCount}.time
            sbatch -N $nodeCount --cpus-per-task $threadCount --ntasks-per-node $tasksPerNode -o $outfile scaling.sh $nodeCount $tasksPerNode $threadCount $sideLength $messageCount $timeStepCount
          done
        done
      done
    done
  done
done
