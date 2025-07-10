#!/bin/bash
set -x
scriptDir="$(dirname "$(scontrol show job "$SLURM_JOB_ID" | awk -F= '/Command=/{print $2}')")"
echo "$scriptDir"

nodeCount=$1
width=$2
height=$3
eventDensity=$4
timeToRun=$5
prefix=$6

tmpFile=${prefix}.tmp
timeFile=${prefix}.time
outFile=${prefix}.err
outDir=${prefix}_dir
rm $timeFile
touch $timeFile

simFlags="--N $width --M $height --eventDensity $eventDensity --timeToRun ${timeToRun}ns"

sstFlags="--print-timing-info=true --parallel-load=SINGLE ${scriptDir}/phold_dist.py"

srunPortion="srun -N $nodeCount" 


mkdir $outDir
cd $outDir

$srunPortion sst $sstFlags -- $simFlags 1> $tmpFile 2> $outFile

grep "Build time:" $tmpFile | awk '{print $3}' > $timeFile
grep "Run stage Time:" $tmpFile | awk '{print $4}' >> $timeFile
grep "Max Resident Set Size:" $tmpFile | awk -F': *' '{print $2}' >> $timeFile
grep "Approx. Global Max RSS Size:" $tmpFile | awk -F': *' '{print $2}' >> $timeFile


cd -