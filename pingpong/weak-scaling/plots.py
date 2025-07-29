from plotnine import *

import pandas as pd
import sys
import itertools
#Check if the correct number of arguments are passed
if len(sys.argv) != 3:
    print("Usage: python3 plot.py <filename> <output prefix>")
    sys.exit(1)

# Load the data
filename = sys.argv[1]
unmelted_data = pd.read_csv(filename)

output_prefix = sys.argv[2]

unmelted_data['Total Time'] = unmelted_data['Build Time'] + unmelted_data['Run Time']

data = unmelted_data.melt(id_vars=['Side Length', 'Message Count', 'Thread Count', 'Node Count', 'Tasks Per Node', 'Step Count'], value_vars=['Total Time', 'Build Time', 'Run Time'], var_name='Time Type', value_name='Time')


# Add columns for elements per node and messages per node
data['Total Elements'] = data['Side Length'] ** 2
data['Elements Per Node'] = data['Total Elements'] / data['Node Count']
data['Messages Per Node'] = data['Message Count'] / data['Node Count']

# First, plot scaling for one MPI rank per node without additional threading or oversubscription
basic_data = data[(data['Tasks Per Node'] == 1) & (data['Thread Count'] == 1)]
basic_plot = ggplot(basic_data, aes(x='Node Count', y='Time', color='Time Type')) + geom_point() + geom_line() \
    + ggtitle("Weak Scaling, 1 MPI Rank per Node, 1 Thread per Rank.\n\n128x128 Elements and 512 Messages per Rank")

basic_plot.save(output_prefix + '_weak_basic.png')

# Plot, with different lines for thread counts
thread_data = data[data['Tasks Per Node'] == 1]
print(thread_data)
thread_plot = ggplot(thread_data, aes(x='Node Count', y='Time', color='Time Type')) + geom_point() + geom_line() \
    + facet_wrap('Thread Count') \
    + ggtitle("Weak Scaling, 1 MPI Rank per Node, Varying Threads per Rank.\n\n128x128 Elements and 512 Messages per Rank")
thread_plot.save(output_prefix + '_weak_threads.png')

# Plot, with different lines for tasks per node
task_data = data[data['Thread Count'] == 1]
task_plot = ggplot(task_data, aes(x='Node Count', y='Time', color='Time Type')) + geom_point() + geom_line() \
    + facet_wrap('Tasks Per Node') \
    + ggtitle("Weak Scaling, Varying MPI Ranks per Node, 1 Thread per Rank.\n\n128x128 Elements and 512 Messages per Rank")
task_plot.save(output_prefix + '_weak_tasks.png')

# Plot thread count with color for thread count and facet for time type
thread_data['ThreadCount'] = thread_data['Thread Count']
thread_plot2 = ggplot(thread_data, aes(x='Node Count', y='Time', color='factor(ThreadCount)')) + geom_point() + geom_line() \
    + facet_wrap('Time Type') \
    + ggtitle("Weak Scaling, 1 MPI Rank per Node, Varying Threads per Rank.\n\n128x128 Elements and 512 Messages per Rank")
thread_plot2.save(output_prefix + '_weak_threads2.png')

# Do the same with oversubscription
task_data['TasksPerNode'] = task_data['Tasks Per Node']
task_plot2 = ggplot(task_data, aes(x='Node Count', y='Time', color='factor(TasksPerNode)')) + geom_point() + geom_line() \
    + facet_wrap('Time Type') \
    + ggtitle("Weak Scaling, Varying MPI Ranks per Node, 1 Thread per Rank.\n\n128x128 Elements and 512 Messages per Rank")
task_plot2.save(output_prefix + '_weak_tasks2.png')