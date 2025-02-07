import subprocess
import argparse

# Define command line arguments
parser = argparse.ArgumentParser(description="Process cluster node data.")
parser.add_argument("-c", "--cores", type=int, help="Filter rows by minimum number of cores")
parser.add_argument("-m", "--memory", type=int, help="Filter rows by minimum memory (GB)")
parser.add_argument("-g", "--gpu_type", type=str, help="Filter rows by GPU type")
parser.add_argument("-p", "--processor_type", type=str, help="Filter rows by processor type")
parser.add_argument("-s", "--sockets", type=int, help="Filter rows by minimum number of sockets")
parser.add_argument("-d", "--disk", type=int, help="Filter rows by minimum disk space")
parser.add_argument("-x", "--scratch", type=int, help="Filter rows by minimum scratch space")
parser.add_argument("-e", "--eth_speed", type=int, help="Filter rows by minimum Ethernet speed")
parser.add_argument("-i", "--ib_speed", type=int, help="Filter rows by minimum InfiniBand speed")
parser.add_argument("-n", "--gpus", type=int, help="Filter rows by minimum number of GPUs")
parser.add_argument("-f", "--flag", help="Filter rows by flag field (S or B)")
parser.add_argument("-b", "--extra_batch", type=str, help="Filter rows by extra batch info")
parser.add_argument("-r", "--rows", type=int, default=10, help="Number of rows to display (default: 10)")
args = parser.parse_args()

# Define the command to run
command = "cat /usr/local/sge/scv/nodes/master"

# Run the command and capture output
result = subprocess.run(command, shell=True, capture_output=True, text=True)
output = result.stdout

# Parse the output
lines = output.splitlines()
data = []

# Extract only relevant lines (skip comments and blank lines)
for line in lines:
    if line.strip().startswith("#") or not line.strip():
        continue
    parts = line.split()
    if len(parts) >= 11:  # Ensure minimum required columns are present
        data.append(parts)

# Define column headers based on the format in the file
headers = [
    "host", "processor_type", "sockets", "cores", "memory", "disk", "scratch", 
    "eth_speed", "ib_speed", "gpu_type", "gpus", "flag", "extra_batch"
]

# Apply filters efficiently
filtered_data = []
for row in data:
    if args.flag and row[11] != args.flag:
        continue
    if args.cores and int(row[3]) < args.cores:
        continue
    if args.memory and int(row[4]) < args.memory:
        continue
    if args.gpu_type and row[9].lower() != args.gpu_type.lower():
        continue
    if args.processor_type and row[1].lower() != args.processor_type.lower():
        continue
    if args.sockets and int(row[2]) < args.sockets:
        continue
    if args.disk and int(row[5]) < args.disk:
        continue
    if args.scratch and int(row[6]) < args.scratch:
        continue
    if args.eth_speed and int(row[7]) < args.eth_speed:
        continue
    if args.ib_speed and int(row[8]) < args.ib_speed:
        continue
    if args.gpus and int(row[10]) < args.gpus:
        continue
    if args.extra_batch and args.extra_batch.lower() not in row[12].lower():
        continue
    filtered_data.append(row)

# Print formatted table output
def print_table(data, headers, num_rows):
    from tabulate import tabulate
    print(tabulate(data[:num_rows], headers=headers, tablefmt="grid"))

if len(filtered_data):
    print_table(filtered_data, headers[:len(filtered_data[0])], args.rows)
    print(f"There are a total of {len(filtered_data)} matching nodes.")
else:
    print("No matching nodes that fit your requirements!")
