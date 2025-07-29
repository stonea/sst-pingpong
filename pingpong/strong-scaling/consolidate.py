import os
import pandas as pd
import sys

outfile = 'times.csv' if len(sys.argv) < 2 else sys.argv[1]
data = []



for filename in os.listdir('.'):
    if filename.endswith('.time'):
        # Try to split and remove the extension
        try:
            base_name = filename[:-5]
            node,task,thread,element,message,step = map(int, base_name.split('_'))

            with open(filename, 'r') as file:
                times = [float(line.strip()) for line in file if line.strip()]
                build_time = times[0]
                run_time = times[1]
            data.append({
                'Node Count' : node,
                'Tasks Per Node' : task,
                'Thread Count' : thread,
                'Side Length' : element,
                'Message Count' : message,
                'Step Count' : step,
                'Build Time' : build_time,
                'Run Time' : run_time
            })
        except ValueError:
            print(f'Skipping invalid file: {filename}')
        except IndexError:
            print(f'Skipping possibly empty file: {filename}')

df = pd.DataFrame(data)


df.to_csv(outfile, index=False)
print("Wrote to ", outfile)
