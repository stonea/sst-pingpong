#!/bin/bash
#
#
nodeCount=$1
tasksPerNode=$2
threadCount=$3
sideLength=$4
ballCount=$5
timeStepCount=$6

tmpOut=`mktemp`
 srun -N $nodeCount --cpus-per-task=$threadCount  --ntasks-per-node=$tasksPerNode \
  sst --print-timing-info=true -n $threadCount ../pingpong.py -- \
  --numDims 2 --random --N $sideLength --numBalls $ballCount --timeToRun $timeStepCount > $tmpOut
 grep "Build time:" $tmpOut | awk '{print $3}'
 grep "Run loop time:" $tmpOut | awk '{print $4}'
rm $tmpOut


