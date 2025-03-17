# Lists the runs in the current directory that did not finish sucessfully

import os

print("Failures: ")
for filename in os.listdir('.'):
    if filename.endswith('.time'):
        with open(filename) as f:
            contents = f.read()
            if 'Failure' in contents:
                print(filename)


print("Still Running: ")
for filename in os.listdir('.'):
    if filename.endswith('.time'):
        with open(filename) as f:
            contents = f.read()
            if contents == "":
                print(filename)
