# scc-techinfo
SCC Technical Summary  
Authors: Ryan Gilbert


### Master file:
/usr/local/sge/scv/nodes/master  

"flag" field:
- s - shared nodes  
- b - buyin nodes  


### Additional commands that might be useful:

- `qhost -q`  - list of nodes with information about number of cores and memory used
- `qconf -sq <qname>` - list of policies for a queue


Make file executable: `chmod +x scc-techinfo`


