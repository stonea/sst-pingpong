#!/bin/bash
#
#
set -e
set -x
nodeCount=$1
tasksPerNode=$2
threadCount=$3
sideLength=$4
ballCount=$5
timeStepCount=$6

suffix=${nodeCount}_${tasksPerNode}_${threadCount}_${sideLength}_${ballCount}_${timeStepCount}
measurementsDir=measurements_$suffix
databaseDir=database_$suffix

srun -N $nodeCount --cpus-per-task=$threadCount  --ntasks-per-node=$tasksPerNode \
  hpcrun -o $measurementsDir -- sst -n $threadCount ../pingpong.py -- \
  --numDims 2 --N $sideLength --random $ballCount --timeToRun $timeStepCount

hpcstruct $measurementsDir
hpcprof -o $databaseDir $measurementsDir


