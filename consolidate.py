import os
import sys

outfile = 'times.csv' if len(sys.argv) < 2 else sys.argv[1]
data = []


for filename in os.listdir('.'):
    if filename.endswith('.time'):
        try:
            pieces = filename[:-5].split("_")
            if pieces[-1] == 'hpctoolkit':
                pieces.pop()
            print(pieces)
            nodes,tasks,threads,pattern = pieces[0:4]
            dims,side_length,steps,verbosity,input_method = pieces[-5:]
            message_count = -1
            if pattern == 'random' or pattern == 'randomOverlap':
                message_count = pieces[4]
            elif pattern == 'corners':
                message_count = 2 ** int(dims)
            with open(filename, 'r') as file:
                values = [line.strip() for line in file if line.strip()]
                build_time = values[0]
                run_time = values[1]
                local_memory_usage = values[2]
                global_memory_usage = values[3]
            data.append({
                'Node Count' : nodes,
                'Tasks Per Node' : tasks,
                'Thread Count' : threads,
                'Dimensions' : dims,
                'Side Length' : side_length,
                'Message Pattern' : pattern,
                'Message Count' : message_count,
                'Step Count' : steps,
                'Input Method' : input_method,
                'Build Time' : build_time,
                'Run Time' : run_time,
                'Local Memory Usage' : local_memory_usage,
                'Global Memory Usage' : global_memory_usage
            })
        except ValueError:
            print(f'Skipping invalid file: {filename}')
        except IndexError:
            print(f'Skipping possibly empty file: {filename}')
    
with open(outfile, 'w') as f:
    entry = data[0]
    f.write(','.join(entry.keys()) + "\n")
    for entry in data:
        f.write(','.join(map(str, entry.values())) + "\n")

print("Wrote to ", outfile)