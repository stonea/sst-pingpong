#!/bin/bash
#
# Arguments are quoted strings representing the node counts, thread counts, sst element counts, and ball counts.
#
set -e
# Check if there are exactly four arguments
if [ "$#" -ne 6 ]; then
    echo "Error: Six arguments are required."
    echo "Usage: $0 <nodeCounts> <tasksPerNodeCounts> <threadCounts> <sideLengths> <timeStepCounts> <Communication pattern and messageCounts>"
    exit 1
fi

# Assign arguments to variables
nodeCounts=$1
tasksPerNodeCounts=$2
threadCounts=$3
sideLengths=$4
timeStepCounts=$5
patternAndMessageCounts=$6
pattern=`echo $patternAndMessageCounts | awk '{print $1}'`
messageCounts=`echo $patternAndMessageCounts | awk '{ $1=""; print substr($0,2) }'`


if [[ "$pattern" = "random" || "$pattern" = "randomOverlap" ]]; then
  if [[ "$messageCounts" = "" ]]; then
    echo "Error: Message counts must be provided for random patterns"
    exit 1
  fi
elif [[ "$pattern" = "corner" || "$pattern" = "wavefront" ]]; then
  if [[ "$messageCounts" != "" ]]; then
    echo "Error: Message counts must not be provided for corner and wavefront patterns"
    exit 1
  fi
  messageCounts="1"
else 
  echo "Error: Invalid pattern: '$pattern'"
  exit 1
fi



# Print the values (optional)
echo "nodeCounts: $nodeCounts"
echo "tasksPerNodeCounts: $tasksPerNodeCounts"
echo "threadCounts: $threadCounts"
echo "sideLengths: $sideLengths"
echo "timeStepCounts: $timeStepCounts"
echo "pattern: $pattern"
echo "messageCounts: $messageCounts"


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
            outfile=${nodeCount}_${tasksPerNode}_${threadCount}_${sideLength}_${timeStepCount}_${pattern}_${messageCount}.time
            sbatch -N $nodeCount --cpus-per-task $threadCount --ntasks-per-node $tasksPerNode -o $outfile scaling.sh $nodeCount $tasksPerNode $threadCount $sideLength $timeStepCount "$pattern $messageCount"
          done
        done
      done
    done
  done
done
