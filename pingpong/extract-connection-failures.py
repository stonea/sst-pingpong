import sys
import os

# For each .out file in the current directory
for filename in os.listdir('.'):
    
    if filename.endswith('.out'):
        # Open the file
        with open(filename) as f:
            # Read the file line by line
            for line in f:
                if 'inet_connect:inet_connect: connect from' in line:
                    from_node = line.split(' ')[-7]
                    to_node = line.split(' ')[-5]
                    print(from_node, 'to', to_node)