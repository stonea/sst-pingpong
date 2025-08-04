This directory contains scripts related to performing profiling of the ping pong simulation using HPCToolkit.

You will need to install HPCToolkit on your own. This is incredibly simple if you have spack:
```
spack install hpctoolkit
spack load hpctoolkit
```

If you don't have spack, get spack. It will take a while to install with spack. It will take you longer to install from source

## Step 1: Rebuilt SST

We need to build SST with debugging information. We'll do this by setting two environment variables:
```
export CFLAGS="-g -O3"
export CXXFLAGS="-g -O3"
```

From the `sst-core` directory:
```
./configure --prefix=`pwd`/install MPICC=`which mpicc` MPICXX=`which mpicxx`
```
You should see the following near the end of the configure output, which confirms that the debugging flag (`-g`) will be used:
```
 C Compiler Options : -g -O3 -Wall -Wextra
                  C++ Compiler Options : -g -O3 -std=c++17 -Wall -Wextra
```

Then, again from the `sst-core` directory:
```
make -j8
make install
```

Next, we'll do the same for `sst-elements`. From the `sst-elements` base directory:
```
./configure --prefix=`pwd`/install --with-sst-core=$HOME/mysst/sst-core/install
make -j8
make install
```

Finally, we need to build our simulation elements. From the base directory of this repository:
```
make clean
make
```

## Step 2: Collect Profiling Information and Attribute

Now you can use the `./submit.sh` script to run the simulation, gather profiling information, gather program structure information, and attribute program execution time to parts of the program. The syntax is the same as the strong and weak scaling evaluations. 

The `./submit.sh` script will generate `database_*` directories. You can use `hpcviewer` to investigate the performance of your simulations.

Weak scaling evaluation:
```
./submit.sh 1 1 1 512 2621 100000
./submit.sh 4 1 1 1024 10485 100000
./submit.sh 16 1 1 2048 41943 100000
./submit.sh 64 1 1 4096 167772 100000
./submit.sh 256 1 1 8192 671088 100000
```