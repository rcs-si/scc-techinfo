import subprocess
import argparse
from tabulate import tabulate
# potential import reductions?

# Define command line arguments
parser = argparse.ArgumentParser(
    prog="scc-techinfo",
    description="Query and display cluster node data.")
parser.add_argument("-w", "--node", type=str, help="Filter by node name")
parser.add_argument("-c", "--cores", type=int, help="Filter rows by minimum number of cores")
parser.add_argument("-m", "--memory", type=int, help="Filter rows by minimum memory (GB)")
parser.add_argument("-g", "--gpu_type", type=str, help="Filter rows by GPU type")
parser.add_argument("-p", "--processor_type", type=str, help="Filter rows by processor type")
parser.add_argument("-t", "--architecture_type", type=str, help="Filter rows by processor architecture type")
parser.add_argument("-s", "--sockets", type=int, help="Filter rows by minimum number of sockets")
parser.add_argument("-d", "--disk", type=int, help="Filter rows by minimum disk space")
parser.add_argument("-x", "--scratch", type=int, help="Filter rows by minimum scratch space")
parser.add_argument("-e", "--eth_speed", type=int, help="Filter rows by minimum Ethernet speed")
parser.add_argument("-i", "--ib_speed", type=int, help="Filter rows by minimum InfiniBand speed")
parser.add_argument("-n", "--gpus", type=int, help="Filter rows by minimum number of GPUs")
parser.add_argument("-f", "--flag", help="Filter rows by shared/buy in field (S or B)")
parser.add_argument("-b", "--extra_batch", type=str, help="Filter rows by extra batch info")
parser.add_argument("-a", "--avail_cpu", type=int, help="Filter rows by minimum available cpus")
parser.add_argument("-j", "--avail_gpu", type=int, help="Filter rows by minimum available gpus")
parser.add_argument("-q", "--queue", type=str, help="Filter rows by queue name")
parser.add_argument("-r", "--rows", type=int, default=20, help="Number of rows to display (default: 20)")
parser.add_argument("--all", action="store_true", help="Rather than specify count, display all matching nodes.")
parser.add_argument("--count", action="store_true", help="Display count of matching nodes, rather than the table.")
# parser.add_argument("--fast", action="store_true", help="Stops filtering once number of rows to display argument hit")
args = parser.parse_args()

# Define the command to run
command_nodes = "cat /usr/local/sge/scv/nodes/master"
command_gpus = "qgpus -v"
command_queues = "qhost -q"

# Run the commands and capture output
result_nodes = subprocess.run(command_nodes, shell=True, capture_output=True, text=True)
result_gpus = subprocess.run(command_gpus, shell=True, capture_output=True, text=True)
result_queues = subprocess.run(command_queues, shell=True, capture_output=True, text=True)

output_nodes = result_nodes.stdout
output_gpus = result_gpus.stdout
output_queues = result_queues.stdout

awk_script = r'''
BEGIN { OFS="," }

$0 ~ /^[^[:space:]]/ && $1 != "HOSTNAME" && $1 != "global" {
    if (have_host) print host, used
    host = $1
    used = 0
    have_host = 1
    next
}

$0 ~ /[0-9]+\/[0-9]+\/[0-9]+/ {
    match($0, /[0-9]+\/[0-9]+\/[0-9]+/, m)
    split(m[0], s, "/")
    used += s[2]
}

END {
    if (have_host) print host, used
}
'''

proc = subprocess.run(
    ["awk", awk_script],
    input=output_queues,
    text=True,
    capture_output=True,
    check=True,
)

# will be total - used
host_cpu_used = {}

for line in proc.stdout.strip().splitlines():
    host, used = line.split(",")
    host_cpu_used[host] = int(used)


# Parse the cluster node data
lines = output_nodes.splitlines()
data = []

for line in lines:
    if line.strip().startswith("#") or not line.strip():
        continue
    parts = line.split()
    if len(parts) >= 11:
        if len(parts) == 12:
            parts.append("") # if no extra_batch, makes formatting work with gpu info
        data.append(parts)

headers = [
    "host", "processor_type", "sockets", "cores", "memory", "disk", "scratch", 
    "eth_speed", "ib_speed", "gpu_type", "gpus", "flag", "extra_batch", "cpu_avail", "gpu_avail", "queues"
]

headers = [
    "Host", "Processor\nArchitecture", "Cores", "Memory\n(GB)", 
    "Eth\nSpeed", "IB\nSpeed", "GPU", "GPU\nCount", "(S)hared\n(B)uy in", "CPU\nAvail", "GPU\nAvail", "Queues"
]

# Parse GPU availability data
gpu_data = []
gpu_table_started = False
gpu_headers = []

gpu_lines = output_gpus.splitlines()
for line in gpu_lines:
    if "host" in line and "gpu_type" in line:
        gpu_headers = line.split()
        continue
    if "total" in line and "in_use" in line:
        gpu_table_started = 2
        continue
    if gpu_table_started:
        if gpu_table_started == 2: # skip dashes
            gpu_table_started = True
            continue
        parts = line.split()
        if len(parts) >= len(gpu_headers):
            gpu_data.append(parts)

# Convert GPU data into a dictionary for easy lookup
gpu_dict = {row[0]: row[1:] for row in gpu_data}  # host -> GPU details

# Get architecture from cpu name since used file does not contain arch
"""
awk '
BEGIN {
    FPAT = "([^,]+)|(\"[^\"]+\")"
    print "CPU_ARCH_MAP = {"
}
{
    cpu  = $2
    arch = $21

    gsub(/^"|"$/, "", cpu)
    gsub(/^"|"$/, "", arch)

    if (cpu != "" && arch != "" && !(cpu in seen)) {
        printf "    \"%s\": \"%s\",\n", cpu, arch
        seen[cpu] = 1
    }
}
END {
    print "}"
}
' /projectnb/rcsmetrics/nodes/data/nodes.csv
"""

CPU_ARCH_MAP = {
    "Gold-6242": "cascadelake",
    "E5-2407v2": "ivybridge",
    "7250": "knl",
    "E5-2680v4": "broadwell",
    "EPYC-7501": "naples",
    "EPYC-7702": "rome",
    "E5-2660v3": "haswell",
    "E7-4809v3": "haswell",
    "E7-8867v4": "broadwell",
    "E5-2670": "sandybridge",
    "E5-2650v2": "ivybridge",
    "E5-2680": "sandybridge",
    "Gold-6226R": "cascadelake",
    "Gold-5120": "skylake",
    "Gold-5118": "skylake",
    "Gold-6326": "icelake",
    "Gold-6132": "skylake",
    "Gold-6426Y": "sapphirerapids",
    "EPYC-7351": "naples",
    "E5-2620v3": "haswell",
    "E5-2620v4": "broadwell",
    "Platinum-8468": "sapphirerapids",
    "EPYC-7413": "milan",
    "EPYC-7302": "rome",
    "EPYC-9354": "genoa",
    "Platinum-8358": "icelake",
    "Gold-6526Y": "emeraldrapids",
    "EPYC-9124": "genoa",
    "EPYC-9135": "turin",
    "6737P": "graniterapids",
    "6517P": "graniterapids",
}

# Parse queue information
def parse_queue_info(output_queues):
    """Parse qhost -q output to extract hostname -> queues mapping"""
    lines = output_queues.splitlines()
    queue_dict = {}
    current_host = None
    
    for line in lines:
        if line.strip() == "" or line.startswith("-") or "HOSTNAME" in line:
            continue
            
        # Check if line starts with whitespace/tab (queue line) or not (hostname line)
        if line.startswith(('\t', ' ')):
            # This is a queue line (indented)
            if current_host:
                parts = line.strip().split()
                if parts:
                    queue_name = parts[0]
                    # Skip lines that are just queue status info (BIP, numbers, 'd', etc.)
                    # if not any(char.isdigit() for char in queue_name) and queue_name not in ['BIP', 'd']:
                    #     queue_dict[current_host].append(queue_name)
                    queue_dict[current_host].append(queue_name)
        else:
            # This is a hostname line (not indented)
            parts = line.split()
            if parts:
                current_host = parts[0]
                # Skip the global line and any other non-hostname entries
                if current_host != 'global':
                    queue_dict[current_host] = []
    
    return queue_dict

queue_dict = parse_queue_info(output_queues)

# Merge GPU info and queue info with node data
for row in data:
    host = row[0]
    
    # Add GPU info
    if host in gpu_dict:
        gpu_entry = gpu_dict[host]
        row.append(int(gpu_entry[3]) - int(gpu_entry[4]))
        row.append(int(gpu_entry[3]))
        row.append(int(gpu_entry[7]))
        row.append(int(gpu_entry[5]))
    else:
        # if no info from qgpus, filling with -1
        row.append(-1)
        row.append(-1)
        row.append(-1)
        row.append(-1)
    
    # Add queue info
    if host in queue_dict:
        # queues = ', '.join(queue_dict[host])
        queues = "\n".join(queue_dict[host])
        row.append(queues)
    else:
        row.append("")

# Apply filters efficiently
filtered_data = []
count = 0
for row in data:
    # if args.fast and count >= int(args.rows):
    #     break
    if args.node and row[0] != args.node:
        continue
    if args.flag and row[11] != args.flag.upper():
        continue
    if args.cores and int(row[3]) != args.cores:
        continue
    if args.memory and int(row[4]) < args.memory:
        continue
    if args.gpu_type and row[9].lower() != args.gpu_type.lower():
        continue
    if args.processor_type and row[1].lower() != args.processor_type.lower():
        continue
    if args.architecture_type and CPU_ARCH_MAP.get(row[1],"unknown") != args.architecture_type:
        continue
    if args.sockets and int(row[2]) != args.sockets:
        continue
    if args.disk and int(row[5]) < args.disk:
        continue
    if args.scratch and int(row[6]) < args.scratch:
        continue
    if args.eth_speed and int(row[7]) != args.eth_speed:
        continue
    if args.ib_speed and int(row[8]) != args.ib_speed:
        continue
    if args.gpus and int(row[10]) != args.gpus:
        continue
    if args.extra_batch and args.extra_batch.lower() not in row[12].lower():
        continue
    if args.avail_cpu and row[13] < args.avail_cpu:
        continue
    if args.avail_gpu and row[15] < args.avail_gpu:
        continue
    if args.queue and args.queue.lower() not in row[17].lower():
        continue

    count += 1
    host_cpu_used[row[0]]
    # format cpu/gpu avail to single col
    cpu_avail_formatted = ""
    gpu_avail_formatted = ""
    if row[13] != -1: # sometimes don't have info from qgpus
        cpu_avail_formatted = f"{row[13]} / {row[14]}"
    else:
        cpu_avail_formatted = f"{int(row[3])-host_cpu_used[row[0]]} / {int(row[3])}"
        
    if row[15] != -1:
        gpu_avail_formatted = f"{row[15]} / {row[16]}"
    
    # Create final row with formatted availability and queues
    final_row = row[:13] + [cpu_avail_formatted, gpu_avail_formatted, row[17]]
    
    # Replace CPU name with architecture
    final_row[1] = CPU_ARCH_MAP.get(final_row[1],"unknown")

    # Delete some rows:
    final_row.pop(2) # sockets
    final_row.pop(4) # disk
    final_row.pop(4) # scratch
    final_row.pop(9) # extra_batch

#     headers = [
#     "host", "processor_type", "sockets", "cores", "memory", "disk", "scratch", 
#     "eth_speed", "ib_speed", "gpu_type", "gpus", "flag", "extra_batch", "cpu_avail", "gpu_avail", "queues"
# ]

    filtered_data.append(final_row)

# Print formatted table output
def print_table(data, headers, num_rows):
    print(tabulate(data[:num_rows], headers=headers, tablefmt="grid"))

if len(filtered_data):
    if args.count:
        print(len(filtered_data))
    else:
        num_rows = len(filtered_data) if args.all else min(args.rows, len(filtered_data))
        if num_rows > 10:
            print_table(filtered_data[:num_rows] + [headers], headers, int(9e9) if args.all else args.rows + 1)
        else:
            print_table(filtered_data, headers, int(9e9) if args.all else args.rows)
        print(f"There are a total of {len(filtered_data)} matching nodes.")
else:
    print("No matching nodes that fit your requirements!")