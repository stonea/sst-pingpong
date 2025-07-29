# Lists the runs in the current directory that did not finish sucessfully

import os


failures = []
for filename in os.listdir('.'):
    if filename.endswith('.time'):
        with open(filename) as f:
            contents = f.read()
            if 'Failure' in contents:
                failures += [filename]
#print sorted
print("Failures: ", len(failures))
for failure in sorted(failures):
    print(failure)


running = []
for filename in os.listdir('.'):
    if filename.endswith('.time'):
        with open(filename) as f:
            contents = f.read()
            if contents == "":
                running += [filename]
#print sorted
print("Still Running: ", len(running))
for run in sorted(running):
    print(run)
