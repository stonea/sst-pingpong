# sst-pingpong

This repository contains files implementing a 2-dimensional ping-pong simulation and the scripts necessary to do scaling evaluation and profiling of the simulation. The simulation code was prepared by Andy Stone; the scaling and profiling evaluations by Brandon Neth.

To study SST’s scalability, we have developed a "ping pong” benchmark. The purpose of this benchmark is to study SST's performance when conducting a simulation that consists of large numbers of simple components.

Specifically, the "Ping Pong Simulation" adds two components to SST:

  - A simulator component whose only purpose is to manage the lifetime of the
    simulation (stop it after a set amount of simulated time has passed). And,
  - A Ponger component, this component connects to (up to) four adjacent ponger
    components to its north, south, west, and east.  When a ponger receives a
    message from its neighbor it will propagate it along.  If the ponger doesn't
    have a neighbor to propagate the message to it will "bounce" it back.

The ponger components can be arranged into a 1-dimensional grid of N components
that connect west-to-east or a 2D grid of NxN components.  The pongers are
preloaded with a set number of "ball" messages.

To run, invoke SST with the `ponger.py` script.  The `ponger.py` script takes
the following parameters (each take an integer argument):

- `--N` -- Size of the grid (defaults to 10)
- `--timeToRun` -- How long to run the simulation (in seconds; defaults to 200)
- `--numDims` -- Either 1 or 2 to specify dimensionality (defaults to 2)
- `--edgeDelay` -- How long it takes to propogate a message from one ponger to the next in simulated seconds (defaults to 50)
- `--artificialWork` -- When processing a ponger message conduct a meaningless loop that does a multiplication operation on a number for a set number of times. This is useful for studying scalability, where increasing this value can look at the impact of messages taking more or less time to conduct.

Additionally the user must choose exactly one of the following to set the initial placement of balls:
- `--corners` -- place balls in the corners of the 1D or 2D grid.
- `--random` -- randomly place balls in the grid such that no ponger has more than 1 ball
- `--randomOverlap` -- randomly place balls in the grid (where a single component may have more than one ball)
- `--wavefront` -- add balls along the perimeter of the grid (only works on 2d sim)

There is also a `--verbose` that if passed prints debugging information.
