#!/bin/bash
# SST Scaling
set -x
scriptDir="$(dirname "$(scontrol show job "$SLURM_JOB_ID" | awk -F= '/Command=/{print $2}')")"
echo "$scriptDir"
nodeCount=$1
ranksPerNode=$2
threadsPerRank=$3
commConfig=$4
dimCount=$5
sideLength=$6
timeStepCount=$7
edgeDelay=$8
verbosity=$9
inputMethod=${10}
withToolkit=${11}
prefix=${12}

tmpOut=${prefix}.tmp
timeFile=${prefix}.time
rm $timeFile
touch $timeFile

inputFlags=""
simFlags="--numDims $dimCount --N $sideLength --timeToRun $timeStepCount --$commConfig --edgeDelay=$edgeDelay"
if [[ "$inputMethod" == "json" ]]; then
  echo "Generating JSON input file..."
  ${scriptDir}/json-generator/jsonGenerator --rankCount $nodeCount --threadsPerRank $threadsPerRank --sideLength $sideLength --timeToRun $timeStepCount --edgeDelay=$edgeDelay --outputPrefix=$prefix --$commConfig --numDims $dimCount
  inputFlags="--parallel-load=MULTI ${prefix}.json"
elif [[ "$inputMethod" == "parallelPython" ]]; then
  inputFlags="--parallel-load=SINGLE ${scriptDir}/pingpong_parLoad.py"
else 
  inputFlags="${scriptDir}/pingpong.py"
fi

srunPortion="srun -N $nodeCount --ntasks-per-node=$ranksPerNode --cpus-per-task=$threadsPerRank"


sstVerbose=""
if [[ "$verbosity" == "1" ]]; then
  sstVerbose="--verbose"
  simFlags="$simFlags"
fi
sstPortion="sst $sstVerbose -n $threadsPerRank --print-timing-info=true $inputFlags -- $simFlags"


measurementsDir=measurements_$prefix
databaseDir=database_$prefix
hpcPortion=" "
if [[ "$withToolkit" != "None" ]]; then
  echo "Running with hpctoolkit..."
  spack load hpctoolkit
  hpcPortion="hpcrun -o $measurementsDir $withToolkit --"
fi


$srunPortion $hpcPortion $sstPortion > $tmpOut

if [[ $? -ne 0 ]]; then
  echo "Failure" > $timeFile
  if [[ "$inputMethod" == "json" ]]; then
    rm ${prefix}*.json
  fi
  exit 1
fi

grep "Build time:" $tmpOut | awk '{print $3}' > $timeFile
grep "Run stage Time:" $tmpOut | awk '{print $4}' >> $timeFile
grep "Max Resident Set Size:" $tmpOut | awk -F': *' '{print $2}' >> $timeFile
grep "Approx. Global Max RSS Size:" $tmpOut | awk -F': *' '{print $2}' >> $timeFile


if [[ "$withToolkit" != "None" ]]; then
  hpcstruct -c hpcstruct_cache $measurementsDir
  hpcprof -o $databaseDir $measurementsDir
fi


if [[ "$inputMethod" == "json" ]]; then
  rm ${prefix}*.json
fi
