import subprocess
import argparse
import pandas as pd
import json

# Parse command line arguments
parser = argparse.ArgumentParser(
    prog="scc-techinfo",
    description="Query and display cluster node data."
)
parser.add_argument("-w", "--node", type=str)
parser.add_argument("-c", "--cores", type=int)
parser.add_argument("-m", "--memory", type=int)
parser.add_argument("-g", "--gpu_type", type=str)
parser.add_argument("-p", "--processor_type", type=str)
parser.add_argument("-s", "--sockets", type=int)
parser.add_argument("-d", "--disk", type=int)
parser.add_argument("-x", "--scratch", type=int)
parser.add_argument("-e", "--eth_speed", type=int)
parser.add_argument("-i", "--ib_speed", type=int)
parser.add_argument("-n", "--gpus", type=int)
parser.add_argument("-f", "--flag", type=str)
parser.add_argument("-b", "--extra_batch", type=str)
parser.add_argument("-r", "--rows", type=int, default=10)
parser.add_argument("--fast", action="store_true")
args = parser.parse_args()

# Get raw data from shell commands
command_nodes = "cat /usr/local/sge/scv/nodes/master"
command_gpus = "qgpus -v"

result_nodes = subprocess.run(command_nodes, shell=True, capture_output=True, text=True)
result_gpus = subprocess.run(command_gpus, shell=True, capture_output=True, text=True)

# Parse node file
node_headers = [
    "host", "processor_type", "sockets", "cores", "memory", "disk", "scratch",
    "eth_speed", "ib_speed", "gpu_type", "gpus", "flag", "extra_batch"
]
node_rows = []
for line in result_nodes.stdout.splitlines():
    line = line.strip()
    if not line or line.startswith("#"):
        continue
    cols = line.split()
    if len(cols) == 12:
        cols.append("") # pad if extra_batch missing
    if len(cols) == 13:
        node_rows.append(cols)

nodes_df = pd.DataFrame(node_rows, columns=node_headers)

# Parse GPU info table
gpu_header_line = None
gpu_rows = []
for line in result_gpus.stdout.splitlines():
    line = line.strip()
    if not line:
        continue
    if "host" in line and "gpu_type" in line:
        gpu_header_line = line
        gpu_headers = line.split()
        continue
    if gpu_header_line and "-"*5 in line:
        continue
    elif gpu_header_line:
        fields = line.split()
        if len(fields) == len(gpu_headers):
            gpu_rows.append(fields)

if gpu_rows:
    gpus_df = pd.DataFrame(gpu_rows, columns=gpu_headers)
else:
    gpus_df = pd.DataFrame([], columns=['host'])

# Merge GPU info into nodes_df (if needed for persistent fields)
df = nodes_df.merge(gpus_df, on='host', how='left', suffixes=('', '_gpu'))

# Filters (no avail columns)
filt = pd.Series([True] * len(df))

if args.node:
    filt = filt & (df["host"] == args.node)
if args.flag:
    filt = filt & (df["flag"] == args.flag)
if args.cores:
    filt = filt & (df["cores"].astype(int) >= args.cores)
if args.memory:
    filt = filt & (df["memory"].astype(int) >= args.memory)
if args.gpu_type:
    filt = filt & (df["gpu_type"].str.lower() == args.gpu_type.lower())
if args.processor_type:
    filt = filt & (df["processor_type"].str.lower() == args.processor_type.lower())
if args.sockets:
    filt = filt & (df["sockets"].astype(int) >= args.sockets)
if args.disk:
    filt = filt & (df["disk"].astype(int) >= args.disk)
if args.scratch:
    filt = filt & (df["scratch"].astype(int) >= args.scratch)
if args.eth_speed:
    filt = filt & (df["eth_speed"].astype(int) >= args.eth_speed)
if args.ib_speed:
    filt = filt & (df["ib_speed"].astype(int) >= args.ib_speed)
if args.gpus:
    filt = filt & (df["gpus"].astype(int) >= args.gpus)
if args.extra_batch:
    filt = filt & (df["extra_batch"].str.contains(args.extra_batch, case=False, na=False))

filtered = df[filt].copy()

# Specify grouping columns
group_cols = [
    'processor_type', 'cores', 'memory', 'gpu_type', 'gpus', 'flag'
]

grouped = (
    filtered
    .groupby(group_cols)
    .agg(
        quantity=('host', 'count'),
        hostnames=('host', lambda x: sorted(list(x))) # optional: collect sorted list of hostnames per group
    )
    .reset_index()
)

# For export, you'll probably only want to show quantity
# If you want hostnames for debugging, keep that too!
output_cols = group_cols + ['quantity', 'hostnames'] # add 'hostnames' if you want that to be exported as well
export_data = grouped[output_cols].values.tolist()

# Save in JS display order: [hostnames, processor_type, cores, memory, gpu_type, gpus, flag]
export_data = grouped.apply(
    lambda row: [row['hostnames'], row['processor_type'], row['cores'], row['memory'], row['gpu_type'], row['gpus'], row['flag']],
    axis=1
).tolist()

with open("output_grouped.json", 'w') as outfile:
    json.dump(export_data, outfile, indent=2)

# Print preview table
print(grouped[output_cols].head(args.rows).to_markdown())

if not args.fast:
    print(f"There are a total of {len(filtered)} matching nodes.")
    print(f"There are {len(grouped)} unique configurations (groups).")