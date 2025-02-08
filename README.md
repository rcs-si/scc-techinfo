# scc-techinfo
SCC Technical Summary  
Authors: Ryan Gilbert

Here is a **README.md** file for your script and accompanying Bash wrapper (`scc-techinfo`):

---

# SCC Tech Info  

## Overview  
This project provides a Python script for processing cluster node data, allowing users to filter and display relevant hardware information. The script is executed via the Bash wrapper script `scc-techinfo`, which passes all arguments to the Python script.

## Features  
- Filters SCC cluster nodes based on CPU cores, memory, GPUs, and other hardware attributes.  
- Parses system information from predefined commands.  
- Supports fast filtering to limit results quickly.  
- Displays results in a tabulated format for easy reading.  

## Usage  
Run the Bash script with desired options:  
```bash
scc-techinfo [options]
```  

### Available Options  
| Option | Description |
|--------|-------------|
| `-c, --cores` | Minimum number of CPU cores |
| `-m, --memory` | Minimum memory in GB |
| `-g, --gpu_type` | Filter by GPU type |
| `-p, --processor_type` | Filter by processor type |
| `-s, --sockets` | Minimum number of CPU sockets |
| `-d, --disk` | Minimum disk space (GB) |
| `-x, --scratch` | Minimum scratch space (GB) |
| `-e, --eth_speed` | Minimum Ethernet speed (Gbps) |
| `-i, --ib_speed` | Minimum InfiniBand speed (Gbps) |
| `-n, --gpus` | Minimum number of GPUs |
| `-f, --flag` | Filter by shared/buy in flag (S or B) |
| `-b, --extra_batch` | Filter by extra batch information |
| `-a, --avail_cpu` | Minimum available CPUs |
| `-j, --avail_gpu` | Minimum available GPUs |
| `-r, --rows` | Number of rows to display (default: 10) |
| `--fast` | Stop filtering once the requested number of rows is found |

### Examples  

1. **List all nodes with at least 32 CPU cores and 128GB memory**  
   ```bash
   scc-techinfo -c=32 -m=128
   ```

2. **Filter nodes with NVIDIA A100 GPUs and at least 2 GPUs available (not in use)**  
   ```bash
   scc-techinfo -g=A100 -j=2
   ```

3. **Quickly find the first 5 nodes with at least 10 GPUs**  
   ```bash
   scc-techinfo -n=10 -r=5 --fast
   ```

## Notes  
- The `scc-techinfo` script acts as a wrapper to execute the Python script with all arguments.  
- If no matching nodes are found, the script will notify the user.  
- Using `--fast` can slightly improve performance by stopping filtering early.  





---
# notes from first proj. meeting:

### Master file:
/usr/local/sge/scv/nodes/master  

"flag" field:
- s - shared nodes  
- b - buyin nodes  


### Additional commands that might be useful:

- `qhost -q`  - list of nodes with information about number of cores and memory used
- `qconf -sq <qname>` - list of policies for a queue


Make file executable: `chmod +x scc-techinfo`


