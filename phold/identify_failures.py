import sys

failure_file = sys.argv[1] if len(sys.argv) > 1 else 'failures.txt'

with open(failure_file, 'r') as f:
  failures = f.read().splitlines()

for failure in failures:
  print(f"Failure: {failure}")
  (name, node_count, width, height, event_density, ring_size, time_to_run, small_payload, large_payload, large_event_fraction, dir) = failure.split('_')
  print(f"  Name: {name}")
  print(f"  Node Count: {node_count}")
  print(f"  Width: {width}")
  print(f"  Height: {height}")
  print(f"  Event Density: {event_density}")
  print(f"  Ring Size: {ring_size}")
  print(f"  Time to Run: {time_to_run}")
  print(f"  Small Payload: {small_payload}")
  print(f"  Large Payload: {large_payload}")
  print(f"  Large Event Fraction: {large_event_fraction}")
  
