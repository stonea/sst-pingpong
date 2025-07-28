import sys

filename1 = sys.argv[1]
filename2 = sys.argv[2]

# We need to show that the contents are the same upon sorting.

def read_file(filename):
  with open(filename, 'r') as file:
      lines = file.readlines()
  return [line.strip() for line in lines if line.strip()]

def compare_files(file1, file2):
  lines1 = read_file(file1)
  lines2 = read_file(file2)

  if len(lines1) != len(lines2):
    return False

  # Sort both lists of lines
  lines1.sort()
  lines2.sort()

  # Compare the sorted lists
  return lines1 == lines2

if __name__ == "__main__":
  if compare_files(filename1, filename2):
    print("The files are equivalent.")
  else:
    print("The files are not equivalent.")
    sys.exit(1)
