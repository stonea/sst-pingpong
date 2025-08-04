The files in this directory evaluate the strong scaling of the 2D pingpong simulation. The files are set up for running on SLURM clusters.

To submit jobs for an evaluation run, use the `./submit.sh` script. The arguments are as follows, and need to be quoted strings if there are multiple values.

```
./submit.sh <Node counts> <MPI ranks per node> <C++ threads per rank> <Side lengths for the 2D grid> <Number of messages to send per timestep> <How many timesteps to run>
```

The following command will submit jobs that allow analysis of strong scaling over node counts, running one MPI rank per node and one C++ thread per rank:
```
./submit.sh "1 2 4 8 16 32 64" 1 1 1024 1024 100000
```

The following will do the same for the strong scaling of MPI oversubscription:
```
./submit.sh 1 "1 2 4 8 16 32 64" 1 1024 1024 100000
```

After all submitted jobs are complete, use the `consolidate.py` script to combine all the timing information into a single `.csv` file. If you provide an argument to the script, it will use it as the output file name, otherwise it will write to `times.csv`.

Finally, use the `plots.py` script to generate plots showing the strong scaling. This script takes 2 arguments. First, the input `.csv` file that contains timing information. Second, the prefix to prepend to the generated plot file names. We suggest using the name of the system the run was performed on. So, if you wanted to compare the effects of node count on strong scaling on Frontier, you would run the following three commands:
```
./submit.sh "1 2 4 8 16 32 64 128" 1 1 1024 1024 100000
python3 consolidate.py frontier.csv
python3 plots.py frontier.csv frontier
```
