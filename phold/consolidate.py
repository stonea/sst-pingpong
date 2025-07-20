import pandas as pd
import numpy as np
import sys
import os




def identify_result_dirs(experiment_name=None):
  """
  Identify directories containing result files.
  """
  result_dirs = []
  invalid_dirs = []
  for item in os.listdir('.'):
    if os.path.isdir(item) and item.endswith('_dir'):
      if experiment_name is not None and not item.startswith(experiment_name):
        continue  
      has_time_file = any(file.endswith('.time') for file in os.listdir(item))
      has_rank_files = any(file.startswith('rank') for file in os.listdir(item))

      if not has_time_file:
        invalid_dirs.append((item, "Missing .time file"))
      elif not has_rank_files:
        invalid_dirs.append((item, "Missing rank files"))
      else:
        result_dirs.append(item)
        
  return (result_dirs, invalid_dirs)


def extract_sync_data(result_dir):
  """
  Extract synchronization times from the result files in the given directory.
  """
  sync_files = []
  for file_name in os.listdir(result_dir):
    if file_name.startswith('rank'):
      sync_files.append(os.path.join(result_dir, file_name))
  sync_data = []
  for sync_file in sync_files:
    with open(sync_file, 'r') as f:
      lines = f.readlines()
      count_line = lines[-4]
      time_line = lines[-3]
      count = int(count_line.split(':')[1].strip())
      time = float(time_line.split(' ')[-2].strip())
      sync_data.append((count, time))

  sync_counts = [count for count, _ in sync_data]
  sync_times = [time for _, time in sync_data]

  sync_time_mean = np.mean(sync_times) if sync_times else None
  sync_time_std = np.std(sync_times) if sync_times else None
  sync_count_mean = np.mean(sync_counts) if sync_counts else None
  sync_count_std = np.std(sync_counts) if sync_counts else None
  sync_time_max = np.max(sync_times) if sync_times else None
  sync_time_min = np.min(sync_times) if sync_times else None
  sync_count_max = np.max(sync_counts) if sync_counts else None
  sync_count_min = np.min(sync_counts) if sync_counts else None


  return {
    'Sync Time Max (s)': sync_time_max,
    'Sync Time Min (s)': sync_time_min,
    'Sync Time Mean (s)': sync_time_mean,
    'Sync Time Std (s)': sync_time_std,
    'Sync Count Max': sync_count_max,
    'Sync Count Min': sync_count_min,
    'Sync Count Mean': sync_count_mean,
    'Sync Count Std': sync_count_std
  }


def extract_time_data(results_dir):
  """
  Extract build and run time data from the result files in the given directory.
  """
  time_files = []
  for file_name in os.listdir(results_dir):
    if file_name.endswith('.time'):
      path = os.path.join(results_dir, file_name)
      with open(path, 'r') as f:
        lines = f.readlines()
        build_time = float(lines[0].strip())
        run_time = float(lines[1].strip())
        return {
          'Build Time (s)': build_time,
          'Run Time (s)': run_time
        }

  return None

def extract_parameters(results_dir):
  """
  Extract parameters from the directory name.
  """
  results_dir = results_dir.split('/')[-1]  # Get the last part of the path
  parts = results_dir.split('_')
  if len(parts) < 5:
    raise ValueError("Directory name does not contain enough parts to extract parameters.")
  
  experiment_name = parts[0]
  node_count = int(parts[1])
  width = int(parts[2])
  height = int(parts[3])
  event_density = float(parts[4])
  ring_size = int(parts[5])
  time_to_run = int(parts[6])
  small_payload = int(parts[7])
  large_payload = int(parts[8])
  large_event_fraction = float(parts[9])

  return {
    'Experiment Name': experiment_name,
    'Node Count': node_count,
    'Width': width,
    'Height': height,
    'Event Density': event_density,
    'Ring Size': ring_size,
    'Time to Run (ns)': time_to_run,
    'Small Payload (bytes)': small_payload,
    'Large Payload (bytes)': large_payload,
    'Large Event Fraction': large_event_fraction
  }

failures = []
def extract_row(results_dir):
  global failures
  try:
    parameters = extract_parameters(results_dir)
    time_data = extract_time_data(results_dir)
    sync_data = extract_sync_data(results_dir)
  except:

    print(f"Error extracting data from {results_dir}. Skipping this directory.")
    failures += [results_dir]
    return None
  
  return parameters | time_data | sync_data


if __name__ == "__main__":
  if len(sys.argv) > 3 or len(sys.argv) < 2:
    print("Usage: python consolidate.py [output_file.csv] [optional experiment name to look for]")
    sys.exit(1)
  if len(sys.argv) == 3:
    experiment_name = sys.argv[2]
  else:
    experiment_name = None
  
  outfile = sys.argv[1]

  (result_dirs,invalid_dirs) = identify_result_dirs(experiment_name)
  for invalid_dir, reason in invalid_dirs:
    print(f"Skipping invalid directory {invalid_dir}: {reason}")

  data = [extract_row(result_dir) for result_dir in result_dirs]
  data = [d for d in data if d is not None]
  if len(data) == 0:
    print("No valid data found. Exiting.")
    sys.exit(0)
  with open(outfile, 'w') as f:
      entry = data[0]
      f.write(','.join(entry.keys()) + "\n")
      for entry in data:
          f.write(','.join(map(str, entry.values())) + "\n")
  
  if len(failures) > 0:
    with open('failures.txt', 'w') as f:
      for failure in failures:
        f.write(f"{failure}\n")

  print(f"Results consolidated into {outfile}.")
