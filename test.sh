#!/bin/bash

# Number of times each test is repeated
REPEAT_COUNT=5

# Define test cases (each test is a different set of arguments)
declare -a TEST_CASES=(
    "./scc-techinfo -c 32 -m 128"
    "./scc-techinfo -g A100 -n 2"
    "./scc-techinfo -s 2 -d 500 -x 100"
    "./scc-techinfo -p Gold-6242 -e 10 -i 40"
    "./scc-techinfo -r 5 --fast"
    "./scc-techinfo -c 16 -m 64 -p AMD -g A40"
    "./scc-techinfo -a 10 -j 2"
    "./scc-techinfo -r 100"
    "./scc-techinfo -r 100 --fast"
)

# Function to run a command multiple times and compute average runtime
run_test() {
    local cmd="$1"
    local total_time=0

    echo "Running: $cmd"
    
    for ((i=1; i<=REPEAT_COUNT; i++)); do
        start_time=$(date +%s.%N)  # Start timer
        eval "$cmd" >/dev/null 2>&1  # Run command silently
        end_time=$(date +%s.%N)  # End timer

        # Calculate elapsed time
        elapsed=$(echo "$end_time - $start_time" | bc)
        total_time=$(echo "$total_time + $elapsed" | bc)
    done

    # Calculate and print the average time
    avg_time=$(echo "scale=3; $total_time / $REPEAT_COUNT" | bc)
    echo "Average time: ${avg_time}s"
    echo "----------------------------------"
}

# Run all test cases
for test in "${TEST_CASES[@]}"; do
    run_test "$test"
done
