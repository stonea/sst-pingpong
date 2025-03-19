import os
import sys

def decompose_filename(filename_no_extension):
    pieces = filename_no_extension.split("_")
    # It always starts with the node count, tasks per node, thread count, and message pattern
    nodes,tasks,threads,pattern = pieces[0:4]
    pieces = pieces[4:]
    message_count = -1
    # Message count is present if the pattern is 'random' or randomOverlap'
    if pattern in ['random', 'randomOverlap']:
        message_count = pieces[0]
        pieces = pieces[1:]
    # Message count is 2^dims if the pattern is 'corners'
    elif pattern == 'corners':
        message_count = 2 ** int(pieces[0])
    
    # After the comms material is the dimensions, side length, steps, verbosity, and input method
    dims,side_length,steps,verbosity,input_method = pieces[0:5]
    pieces = pieces[5:]

    if len(pieces) > 0:
        # We have an extra piece, which is the hpctoolkit flag(s), but we don't need to report those
        pass
    return {
        'Node Count' : nodes,
        'Tasks Per Node' : tasks,
        'Thread Count' : threads,
        'Dimensions' : dims,
        'Side Length' : side_length,
        'Message Pattern' : pattern,
        'Message Count' : message_count,
        'Step Count' : steps,
        'Input Method' : input_method
    }

def read_values(filename):
    with open(filename, 'r') as file:

        values = [line.strip() for line in file if line.strip()]
        if values[0] == 'Failure':
            raise ValueError("SST run reported failure")
        build_time = values[0]
        run_time = values[1]
        local_memory_usage = values[2]
        global_memory_usage = values[3]
        return {
            'Build Time' : build_time,
            'Run Time' : run_time,
            'Local Memory Usage' : local_memory_usage,
            'Global Memory Usage' : global_memory_usage
        }

outfile = 'times.csv' if len(sys.argv) < 2 else sys.argv[1]
data = []


for filename in os.listdir('.'):
    if filename.endswith('.time'):
        try:
            config_map = decompose_filename(filename[:-5])
            value_map = read_values(filename)
            config_map.update(value_map)
            data.append(config_map)
        except ValueError as e:
            print(f'Skipping invalid file: {filename}. Error message: ', e)
        except IndexError:
            print(f'Skipping possibly empty file: {filename}')
    
with open(outfile, 'w') as f:
    entry = data[0]
    f.write(','.join(entry.keys()) + "\n")
    for entry in data:
        f.write(','.join(map(str, entry.values())) + "\n")

print("Wrote to ", outfile)