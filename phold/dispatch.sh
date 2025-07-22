#!/bin/bash
set -x
scriptDir="$(dirname "$(scontrol show job "$SLURM_JOB_ID" | awk -F= '/Command=/{print $2}')")"
echo "$scriptDir"

nodeCount=$1
threadCount=$2
width=$3
height=$4
eventDensity=$5
ringSize=$6
timeToRun=$7
smallPayload=$8
largePayload=$9
largeEventFraction=$10
prefix=${11}

tmpFile=${prefix}.tmp
timeFile=${prefix}.time
outFile=${prefix}.err
outDir=${prefix}_dir


simFlags="--N $height --M $width --eventDensity $eventDensity --timeToRun ${timeToRun}ns --numRings $ringSize --smallPayload $smallPayload --largePayload $largePayload --largeEventFraction $largeEventFraction"

sstFlags="--num-threads $threadCount --print-timing-info=true --parallel-load=SINGLE ${scriptDir}/phold_dist.py"

srunPortion="srun -N $nodeCount --cpus-per-task=$threadCount --ntasks-per-node=1" 


mkdir $outDir
cd $outDir
rm $timeFile
touch $timeFile
$srunPortion sst $sstFlags -- $simFlags 1> $tmpFile 2> $outFile

grep "Build time:" $tmpFile | awk '{print $3}' > $timeFile
grep "Run stage Time:" $tmpFile | awk '{print $4}' >> $timeFile
grep "Max Resident Set Size:" $tmpFile | awk -F': *' '{print $2}' >> $timeFile
grep "Approx. Global Max RSS Size:" $tmpFile | awk -F': *' '{print $2}' >> $timeFile


cd -