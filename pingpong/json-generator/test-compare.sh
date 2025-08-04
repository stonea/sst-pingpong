#!/bin/bash

# This script compares the output of the json-generator with the output of 
# an sst run.

# We can't really do the random or randomOverlap ones, because the random 
# generators are different and the output will be different.  We can do
# the wavefront and corners ones, though. We also need to do just threadCount=1
# to avoid mismatches of ordering between the threads


set -e
sideLength=8
edgeDelay=29
rankCounts="1 2 4 8"
threadCounts="1"

make jsonGenerator

for numRanks in $rankCounts; do
  for numThreads in $threadCounts; do
    prefix=${sideLength}_${edgeDelay}_${numRanks}_${numThreads}
    referenceOutput="${prefix}_reference.json"
    srun -N ${numRanks} sst -n $numThreads --output-json=$referenceOutput \
      --parallel-output=true ../pingpong.py -- \
      --numDims 2 --N $sideLength --edgeDelay $edgeDelay --timeToRun 100 \
      --wavefront --verbose > /dev/null
    
    generatedOutputPrefix="${prefix}_generated"
    ./jsonGenerator -nl1 --rankCount=$numRanks --threadsPerRank=$numThreads \
      --sideLength=$sideLength --edgeDelay=$edgeDelay --timeToRun=100 \
      --wavefront --outputPrefix=$generatedOutputPrefix \
      --printTimingInfo=false --verbose=true

    reference=$(srun -N ${numRanks} sst -n $numThreads --parallel-load $referenceOutput)
    generated=$(srun -N ${numRanks} sst -n $numThreads --parallel-load ${generatedOutputPrefix}.json)

    if [ "$reference" != "$generated" ]; then
      echo "Output for $prefix does not match"
      exit 1
    fi
  done
done