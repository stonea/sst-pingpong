#!/bin/bash
#
#
nodeCount=$1
tasksPerNode=$2
threadCount=$3
sideLength=$4
timeStepCount=$5
patternAndMessageCount=$6

pattern=`echo $patternAndMessageCount | awk '{print $1}'`
messageCount=`echo $patternAndMessageCount | awk '{print $2}'`

commFlag="--$pattern"
if [[ "$pattern" = "random" || "$pattern" = "randomOverlap" ]]; then
  commFlag="--$pattern $messageCount"
fi

tmpOut=`mktemp`
 echo "srun -N $nodeCount --cpus-per-task=$threadCount  --ntasks-per-node=$tasksPerNode \
  sst --print-timing-info=true -n $threadCount ../pingpong.py -- \
  --numDims 2 --N $sideLength $commFlag --timeToRun $timeStepCount > $tmpOut"
 grep "Build time:" $tmpOut | awk '{print $3}'
 grep "Run loop time:" $tmpOut | awk '{print $4}'
rm $tmpOut


