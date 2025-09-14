import pandas as pd
import json

# load nodes data file
df = pd.read_csv("/projectnb/rcsmetrics/nodes/data/nodes.csv")

# keep only active nodes
df = df[df["netbox_status"] == "Active"]

# for figuring out cpu manual URL map
print(df['processor_type'].unique())

# scc-globus, not shown?
print(df[df['processor_type']=='E5-2407v2'])



# 112 groups on scc page, but this generates 118
df['gpu_type'] = df['gpu_type'].fillna('None')

# group by:
group_cols = [
    'processor_type', 'cores', 'memory','scratch','eth_speed', 'gpu_type', 'gpus', 'flag'
]


grouped = (
    df
    .groupby(group_cols)
    .agg(
        quantity=('host', 'count'),
        hostnames=('host', lambda x: sorted(list(x))) # optional: collect sorted list of hostnames per group
    )
    .reset_index()
)

cpu_display_map = {
    'Gold-6242': '<a href="https://ark.intel.com/content/www/us/en/ark/products/192440/intel-xeon-gold-6242-processor-22m-cache-2-80-ghz.html">Intel Gold 6242</a>',
    'E5-2407v2': 'Intel E5-2407v2',
    '7250': '<a href="https://www.intel.com/content/www/us/en/products/sku/94035/intel-xeon-phi-processor-7250-16gb-1-40-ghz-68-core/specifications.html?wapkw=xeon%20phi%207250">Intel Xeon Phi (Knights Landing) 7250</a>',
    'E5-2680v4': '<a href="https://www.intel.com/content/www/us/en/products/sku/91754/intel-xeon-processor-e52680-v4-35m-cache-2-40-ghz/specifications.html?wapkw=e5-2680%20v4">Intel Xeon E5-2680v4</a>',
    'EPYC-7501': 'AMD EPYC-7501',
    'EPYC-7702': 'AMD EPYC-7501',
    'E5-2670': '<a href="https://www.intel.com/content/www/us/en/products/sku/64595/intel-xeon-processor-e52670-20m-cache-2-60-ghz-8-00-gts-intel-qpi/specifications.html?wapkw=e5-2670">Intel Xeon E5-2670</a>',
    'E5-2650v2': '<a href="https://www.intel.com/content/www/us/en/products/sku/75269/intel-xeon-processor-e52650-v2-20m-cache-2-60-ghz/specifications.html?wapkw=xeon%20e5%202650%20v2">Intel Xeon E5-2650v2</a>',
    'E5-2660v3': '<a href="https://www.intel.com/content/www/us/en/products/sku/81706/intel-xeon-processor-e52660-v3-25m-cache-2-60-ghz/specifications.html?wapkw=e5-2660%20v3">Intel Xeon E5-2660v3</a>',
    'E7-4809v3': '<a href="https://www.intel.com/content/www/us/en/products/sku/84676/intel-xeon-processor-e74809-v3-20m-cache-2-00-ghz/specifications.html?wapkw=e7-4809%20">Intel Xeon E7-4809v3</a>',
    'E7-8867v4': '<a href="https://www.intel.com/content/www/us/en/products/sku/93804/intel-xeon-processor-e78867-v4-45m-cache-2-40-ghz/specifications.html?wapkw=e7-8867">Intel Xeon E7-8867v4</a>',
    'E5-2680': '<a href="https://www.intel.com/content/www/us/en/products/sku/64583/intel-xeon-processor-e52680-20m-cache-2-70-ghz-8-00-gts-intel-qpi/specifications.html?wapkw=e5-2680">Intel Xeon E5-2680</a>',
    'Gold-6226R': '<a href="https://ark.intel.com/content/www/us/en/ark/products/199347/intel-xeon-gold-6226r-processor-22m-cache-2-90-ghz.html">Intel Xeon Gold 6226R</a>',
    'Gold-5120': '<a href="https://ark.intel.com/content/www/us/en/ark/products/120474/intel-xeon-gold-5120-processor-19-25m-cache-2-20-ghz.html">Intel Xeon Gold 5120</a>',
    'Gold-5118': '<a href="https://ark.intel.com/content/www/us/en/ark/products/120473/intel-xeon-gold-5118-processor-16-5m-cache-2-30-ghz.html">Intel Xeon Gold 5118</a>',
    'Gold-6326': '<a href="https://www.intel.com/content/www/us/en/products/sku/215274/intel-xeon-gold-6326-processor-24m-cache-2-90-ghz/specifications.html">Intel Gold 6326</a>',
    'Gold-6132': '<a href="https://www.intel.com/content/www/us/en/products/sku/123541/intel-xeon-gold-6132-processor-19-25m-cache-2-60-ghz/specifications.html?wapkw=intel%20gold%206132">Intel Gold 6132</a>',
    'Gold-6426Y': '<a href="https://www.intel.com/content/www/us/en/products/sku/232377/intel-xeon-gold-6426y-processor-37-5m-cache-2-50-ghz/specifications.html">Intel Gold 6426Y</a>',
    'EPYC-7351': '<a href="https://www.amd.com/en/support/downloads/drivers.html/processors/epyc/epyc-7001-series/amd-epyc-7351.html">AMD Epyc 7351</a>',
    'E5-2620v3': '<a href="https://www.intel.com/content/www/us/en/products/sku/83352/intel-xeon-processor-e52620-v3-15m-cache-2-40-ghz/specifications.html?wapkw=e5-2620%20v3">Intel Xeon E5-2620v3</a>',
    'E5-2620v4': '<a href="https://www.intel.com/content/www/us/en/products/sku/92986/intel-xeon-processor-e52620-v4-20m-cache-2-10-ghz/specifications.html?wapkw=e5-2620%20v4">Intel Xeon E5-2620v4</a>',
    'Platinum-8468': '<a href="https://www.intel.com/content/www/us/en/products/sku/231735/intel-xeon-platinum-8468-processor-105m-cache-2-10-ghz/specifications.html">Intel Platinum 8468</a>',
    'EPYC-7413': '<a href="https://www.amd.com/en/products/processors/server/epyc/7003-series/amd-epyc-7413.html">AMD EPYC-7413</a>',
    'EPYC-7302': '<a href="https://www.amd.com/en/support/downloads/drivers.html/processors/epyc/epyc-7002-series/amd-epyc-7302.html">AMD EPYC-7302</a>',
    'EPYC-9354': '<a href="https://www.amd.com/en/products/processors/server/epyc/4th-generation-9004-and-8004-series/amd-epyc-9354.html">AMD EPYC 9354</a>',
    'Platinum-8358': '<a href="https://www.intel.com/content/www/us/en/products/sku/212282/intel-xeon-platinum-8358-processor-48m-cache-2-60-ghz/specifications.html">Intel Xeon Platinum 8358</a>',
    'Gold-6526Y': '<a href="https://www.intel.com/content/www/us/en/products/sku/237560/intel-xeon-gold-6526y-processor-37-5m-cache-2-80-ghz/specifications.html">Intel Gold 6526Y</a>',
    'EPYC-9124': '<a href="https://www.amd.com/en/products/processors/server/epyc/4th-generation-9004-and-8004-series/amd-epyc-9124.html">EPYC 9124</a>',
    'EPYC-9135': '<a href="https://www.amd.com/en/products/processors/server/epyc/9005-series/amd-epyc-9135.html">EPYC 9135</a>',
}

grouped['processor_type'] = grouped['processor_type'].map(cpu_display_map)

output_cols = group_cols + ['quantity', 'hostnames'] # add 'hostnames' if you want that to be exported as well
export_data = grouped[output_cols].values.tolist()

# Save in JS display order: [hostnames, processor_type, cores, memory, gpu_type, gpus, flag]
export_data = grouped.apply(
    lambda row: [row['hostnames'], row['processor_type'], row['cores'], row['memory'], row['gpu_type'], row['gpus'], row['flag']],
    axis=1
).tolist()

with open("new_output_grouped.json", 'w') as outfile:
    json.dump(export_data, outfile, indent=2)

# Print preview table
print(grouped[output_cols].head().to_markdown())