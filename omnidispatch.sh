#!/bin/bash
set -e
set -x

nodeCount=$1
ranksPerNode=$2
threadsPerRank=$3
commConfig=$4
dimCount=$5
sideLength=$6
timeStepCount=$7
verbosity=$8
inputMethod=$9
withToolkit=${10}
prefix=${11}

inputFlags=""
simFlags="--N $sideLength --timeToRun $timeStepCount --$commConfig"
if [[ "$inputMethod" == "json" ]]; then
  echo "Generating JSON input file..."
  ./json-generator/jsonGenerator --rankCount $nodeCount --threadsPerRank $threadsPerRank --sideLength $sideLength --timeToRun $timeStepCount --outputPrefix=$prefix --$commConfig
  inputFlags="--parallel-load ${prefix}.json"
elif [[ "$inputMethod" == "parallelPython" ]]; then
  inputFlags="--parallel-load=SINGLE pingpong_parLoad.py"
else 
  inputFlags="pingpong.py"
  simFlags="$simFlags --numDims $dimCount"
fi

srunPortion="srun -N $nodeCount --ntasks-per-node=$ranksPerNode --cpus-per-task=$threadsPerRank"

sstPortion="sst -n $threadsPerRank --print-timing-info=true $inputFlags -- $simFlags"
if [[ "$verbosity" == "1" ]]; then
  sstPortion=$sstPortion" --verbose"
fi

measurementsDir=measurements_$prefix
databaseDir=database_$prefix
hpcPortion=" "
if [[ "$withToolkit" == "1" ]]; then
  echo "Running with hpctoolkit..."
  spack load hpctoolkit
  hpcPortion="hpcrun -o $measurementsDir --"
fi

tmpOut=${prefix}.tmp
$srunPortion $hpcPortion $sstPortion > $tmpOut
timeFile=${prefix}.time
grep "Build time:" $tmpOut | awk '{print $3}' > $timeFile
grep "Run loop time:" $tmpOut | awk '{print $4}' >> $timeFile
grep "Max Resident Set Size:" $tmpOut | awk -F': *' '{print $2}' >> $timeFile
grep "Approx. Global Max RSS Size:" $tmpOut | awk -F': *' '{print $2}' >> $timeFile


if [[ "$withToolkit" == "1" ]]; then
  hpcstruct $measurementsDir
  hpcprof -o $databaseDir $measurementsDir
fi

