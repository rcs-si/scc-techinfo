# scc-techinfo
SCC Technical Summary  
Authors: Ryan Gilbert


---

# SCC Tech Info  

## Overview  
This project provides a Python script for processing cluster node data, allowing users to filter and display relevant hardware information. The script is executed via the Bash wrapper script `scc-techinfo`, which passes all arguments to the Python script.

## Features  
- Filters SCC cluster nodes based on CPU cores, memory, GPUs, and other hardware attributes.  
- Parses system information from predefined commands.  
- Displays results in a tabulated format for easy reading.  

## Usage  
Run the Bash script with desired options:  
```bash
scc-techinfo [options]
```  

### Available Options  
See ./scc-techinfo --help for options

### Examples  

1. **List all nodes with at least 32 CPU cores and 128GB memory**  
   ```bash
   scc-techinfo -c=32 -m=128
   ```

2. **Filter nodes with NVIDIA A100 GPUs and at least 2 GPUs available (not in use)**  
   ```bash
   scc-techinfo -g=A100 -j=2
   ```

3. **Find the first 5 nodes with at least 10 GPUs**  
   ```bash
   scc-techinfo -n=10 -r=5
   ```

## Notes  
- The `scc-techinfo` script acts as a wrapper to execute the Python script with all arguments.  
- If no matching nodes are found, the script will notify the user.  


---

# Tech Summary Table for Webpage

To generate a current version for the tech summary webpage, run:
```bash
python3 capturenew.py
``` 
This uses the /projectnb/rcsmetrics/nodes/data/nodes.csv file.  

The result of this script is the data.js file containing an array for the table page.