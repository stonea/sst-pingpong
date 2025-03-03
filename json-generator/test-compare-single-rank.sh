#!/bin/bash

# This script compares the output of the json-generator with the output of an sst run
# This version of the script uses a single rank but does tests with multiple threads

# We can't really do the random or randomOverlap ones, because the random generators are different
# and the output will be different.  We can do the wavefront and corners ones, though.
sideLength=19
edgeDelay=29

prefix=${sideLength}_${edgeDelay}_${numThreads}
for numThreads in 1 2 3 7 18; do
  referenceOutput="${prefix}_reference.json"
  sst -n $numThreads --output-json=$referenceOutput --parallel-output=true ../pingpong.py -- \
    --numDims 2 --N $sideLength --edgeDelay $edgeDelay --timeToRun 100 --wavefront
done