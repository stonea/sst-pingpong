This directory contains code for a PHOLD benchmark implemented using SST. 

Some notes / assumptions:
- Base delays on links are in nanoseconds (ns). 
- For different timestep increment functions, we input the multipliers, means, and ranges in terms of ns. In the C++ code, they are treated in picoseconds to allow for the small variability.
- All components need their own RNG, which should be seeded with their IDs. This ensures that parallel runs can still have correctness comparisons across different thread and rank counts.
- Event density times total component count should be a whole number. This ensures correct distribution of the events and the correct density.