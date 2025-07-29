This directory contains files for running weak scaling evaluation on the ping pong simulation. Please read the README for the strong scaling evaluation first, as the scripts here use the same syntax.

There is some slight complication to doing weak scaling evaluation for this simulation. First, we need to scale all parts of the computation, meaning we need to scale both the number of components and the number of messages. Second, because the simulation takes the side length as an argument, we need to do some calculations to correctly scale. Finally, because we'll be taking some square roots, these values are rounded to their nearest whole value. 

Base simulation: 128x128 components, 512 messages per node.
Performing the necessary multiplications and square rooting, we get the following component grids for different node counts:
```
1: 128x128
2: 181x181
4: 256x256
8: 362x362
16: 512x512
32: 724x724
64: 1024x1024
128: 1448x1448
256: 2048x2048
```

For message count, we multiply the node count by 512, no rounding needed.

The following submit commands gather data for a simple weak scaling evaluation of node count:
```simple weak scaling
./submit.sh 1 1 1 128 512 100000
./submit.sh 2 1 1 181 1024 100000
./submit.sh 4 1 1 256 2048 100000
./submit.sh 8 1 1 362 4096 100000
./submit.sh 16 1 1 512 8192 100000
./submit.sh 32 1 1 724 16384 100000
./submit.sh 64 1 1 1024 32768 100000
./submit.sh 128 1 1 1448 65536 100000
./submit.sh 256 1 1 2048 131072 100000
```

You can also collect performance data and vary the oversubscription

```weak scaling, varying oversubscription
./submit.sh 1 "1 2 4 8 16 32" 1 128 512 100000
./submit.sh 2 "1 2 4 8 16 32" 1 181 1024 100000
./submit.sh 4 "1 2 4 8 16 32" 1 256 2048 100000
./submit.sh 8 "1 2 4 8 16 32" 1 362 4096 100000
./submit.sh 16 "1 2 4 8 16 32" 1 512 8192 100000
./submit.sh 32 "1 2 4 8 16 32" 1 724 16384 100000
./submit.sh 64 "1 2 4 8 16 32" 1 1024 32768 100000
./submit.sh 128 "1 2 4 8 16 32" 1 1448 65536 100000
./submit.sh 256 "1 2 4 8 16 32" 1 2048 131072 100000
```

Or the thread count
```weak scaling, varying thread count
./submit.sh 1 1 "1 2 4 8 16 32" 128 512 100000
./submit.sh 2 1 "1 2 4 8 16 32" 181 1024 100000
./submit.sh 4 1 "1 2 4 8 16 32" 256 2048 100000
./submit.sh 8 1 "1 2 4 8 16 32" 362 4096 100000
./submit.sh 16 1 "1 2 4 8 16 32" 512 8192 100000
./submit.sh 32 1 "1 2 4 8 16 32" 724 16384 100000
./submit.sh 64 1 "1 2 4 8 16 32" 1024 32768 100000
./submit.sh 128 1 "1 2 4 8 16 32" 1448 65536 100000
./submit.sh 256 1 "1 2 4 8 16 32" 2048 131072 100000
```

Use the `consolidate.py` and `plots.py` files as in the strong scaling evaluation.

