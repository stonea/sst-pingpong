from plotnine import *
import humanfriendly

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

data = unmelted_data


# Add columns for elements per node and messages per node
data['Total Elements'] = data['Side Length'] ** 2
data['Elements Per Node'] = data['Total Elements'] / data['Node Count']
data['Messages Per Node'] = data['Message Count'] / data['Node Count']

print(data)

mpn = data['Messages Per Node'].unique()[1]
print(mpn)

d1 = data[data['Messages Per Node'] == mpn].copy(deep=True)

print(d1)

print(d1.columns)

print(d1['Global Memory Usage'])

d1['Global Memory Usage'] = d1['Global Memory Usage'].apply(humanfriendly.parse_size)
d1['Local Memory Usage'] = d1['Local Memory Usage'].apply(humanfriendly.parse_size)

p1 = ggplot(d1, aes(x='Node Count', y='Global Memory Usage', color='Input Method')) + geom_point() + geom_line()
p1.show()
p1 = ggplot(d1, aes(x='Node Count', y='Local Memory Usage', color='Input Method')) + geom_point() + geom_line()
p1.show()

p2 = ggplot(d1, aes(x='Node Count', y='Run Stage', color='Input Method')) + geom_point() + geom_line()
p2.show()

p3 = ggplot(d1, aes(x='Node Count', y='Build Time', color='Input Method')) + geom_point() + geom_line()
p3.show()

d1['Total Time'] = d1['Build Time'] + d1['Run Time']

p4 = ggplot(d1, aes(x='Node Count', y='Total Time', color='Input Method')) + geom_point() + geom_line()
p4.show()