import os
import pandas as pd
import sys

outfile = 'times.csv' if len(sys.argv) < 2 else sys.argv[1]
data = []



for filename in os.listdir('.'):
    if filename.endswith('_1d.time'):
        # Try to split and remove the extension
        try:
            base_name = filename[:-8]
            pieces = base_name.split('_')
            print(pieces)

            node,task,thread,element,message,step = pieces[0:6]
            if len(pieces) == 7:
                input_method = pieces[6]
            else:
                input_method='python'

            with open(filename, 'r') as file:
                values = [line.strip() for line in file if line.strip()]
                build_time = values[0]
                run_time = values[1]
                local_memory_usage = values[2]
                global_memory_usage = values[3]
            data.append({
                'Node Count' : node,
                'Tasks Per Node' : task,
                'Thread Count' : thread,
                'Component Count' : element,
                'Message Count' : message,
                'Step Count' : step,
                'Build Time' : build_time,
                'Run Time' : run_time,
                'Local Memory Usage' : local_memory_usage,
                'Global Memory Usage' : global_memory_usage,
                'Input Method' : input_method
            })
        except ValueError:
            print(f'Skipping invalid file: {filename}')
        except IndexError:
            print(f'Skipping possibly empty file: {filename}')

df = pd.DataFrame(data)


df.to_csv(outfile, index=False)
print("Wrote to ", outfile)
