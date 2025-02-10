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

data['Step Count'] = data['Step Count'] / 50

basic_data = data[(data['Tasks Per Node'] == 1) & (data['Thread Count'] == 1)]
basic_plot = ggplot(basic_data, aes(x='Node Count', y='Time', color='Time Type')) + geom_point() + geom_line() \
    + ggtitle("Strong Scaling, 1 MPI Rank per Node, 1 Thread per Rank.\n\n1024x1024 Elements, 1024 Messages per time step, 2000 Time steps")
basic_plot.save(output_prefix + '_strong_basic.png')


thread_data = pd.DataFrame(data[data['Tasks Per Node'] == 1])
thread_plot = ggplot(thread_data, aes(x='Node Count', y='Time', color='Time Type')) + geom_point() + geom_line() \
    + facet_wrap('Thread Count',labeller='label_both') \
    + ggtitle("Strong Scaling, 1 MPI Rank per Node, Varying Threads per Rank") \
    + labs(subtitle="1024x1024 Elements, 1024 Messages per Time Step, 100000 Time Steps") \

thread_plot.save(output_prefix + '_strong_threads.png')

# Plot, with different lines for tasks per node
task_data = pd.DataFrame(data[data['Thread Count'] == 1])
task_plot = ggplot(task_data, aes(x='Node Count', y='Time', color='Time Type')) + geom_point() + geom_line() \
    + facet_wrap('Tasks Per Node',labeller='label_both') \
    + ggtitle("Strong Scaling, Varying MPI Ranks per Node, 1 Thread per Rank.\n\n1024x1024 Elements, 1024 Messages per Time Step, 100000 Time Steps")
task_plot.save(output_prefix + '_strong_tasks.png')

# Plot thread count with color for thread count and facet for time type
thread_data['ThreadCount'] = thread_data['Thread Count']
thread_plot2 = ggplot(thread_data, aes(x='Node Count', y='Time', color='factor(ThreadCount)')) + geom_point() + geom_line() \
    + facet_wrap('Time Type',labeller='label_both') \
    + ggtitle("Strong Scaling, 1 MPI Rank per Node, Varying Threads per Rank.\n\n1024x1024 Elements, 1024 Messages per Time Step, 100000 Time Steps")
thread_plot2.save(output_prefix + '_strong_threads2.png')

# Do the same with oversubscription
task_data['TasksPerNode'] = task_data['Tasks Per Node']
task_plot2 = ggplot(task_data, aes(x='Node Count', y='Time', color='factor(TasksPerNode)')) + geom_point() + geom_line() \
    + facet_wrap('Time Type',labeller='label_both') \
    + ggtitle("Strong Scaling, Varying MPI Ranks per Node, 1 Thread per Rank.\n\n1024x1024 Elements, 1024 Messages per Time Step, 100000 Time Steps")
task_plot2.save(output_prefix + '_strong_tasks2.png')