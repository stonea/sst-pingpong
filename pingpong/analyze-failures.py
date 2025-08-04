import pandas as pd
import re
import sys

if len(sys.argv) < 2:
    print("Usage: python3 {} <filename>".format(sys.argv[0]))
    sys.exit(1)
filename = sys.argv[1]

tuples = []
with open(filename) as file:
    for line in file:
        if 'to' in line:
            tuples += [line.strip().split("to")]

froms = [t[0] for t in tuples]
tos = [t[-1] for t in tuples]

data = pd.DataFrame({'from': froms, 'to': tos})


# Define regex pattern to extract values
pattern = r"x(\d+)c(\d+)s(\d+)b(\d+)n(\d+)"

# Extract values using .str.extract()
data[['from x', 'from c', 'from s', 'from b', 'from n']] = data['from'].str.extract(pattern).astype(int)
data[['to x', 'to c', 'to s', 'to b', 'to n']] = data['to'].str.extract(pattern).astype(int)

data = data.sort_values('to')
print(data)

print('x: ', sum(data['from x'] - data['to x']))

print('c: ',sum(data['from c'] - data['to c']))

print('s: ', sum(data['from s'] - data['to s']))
print('b: ', data['from b'] - data['to b'])
print('n: ', data['from n'] - data['to n'])