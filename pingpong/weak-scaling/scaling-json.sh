#!/bin/bash
#
#
set -e

nodeCount=$1
tasksPerNode=$2
threadCount=$3
sideLength=$4
messageCount=$5
timeStepCount=$6

if [[ "$messageCount" = "wavefront" || "$messageCount" = "corners" ]]; then
  commFlags="--$messageCount"
else
  commFlags="--random $messageCount"
fi

prefix=${nodeCount}_${tasksPerNode}_${threadCount}_${sideLength}_${messageCount}_${timeStepCount}
tmpOut=$prefix_json.out
jsonIn=$prefix.json
touch $tmpOut
 srun -N $nodeCount --cpus-per-task=$threadCount  --ntasks-per-node=$tasksPerNode \
  sst --print-timing-info=true -n $threadCount  --parallel-load $jsonIn -- \
  > $tmpOut
 grep "Build time:" $tmpOut | awk '{print $3}'
 grep "Run loop time:" $tmpOut | awk '{print $4}'
 grep "Max Resident Set Size:" $tmpOut | awk -F': *' '{print $2}'
 grep "Approx. Global Max RSS Size:" $tmpOut | awk -F': *' '{print $2}'
