#!/bin/bash

# Test DMA Prompt Script
# This script runs the DMA prompt test and displays the results

echo "Running DMA Prompt Test..."
cd "$(dirname "$0")"
python3 test_dma_prompt.py

if [ $? -eq 0 ]; then
    echo "Test completed successfully!"
    echo "Check dma_test_results.json for detailed results"
    
    # Display a summary of the results
    if [ -f dma_test_results.json ]; then
        total=$(grep -o '"total": [0-9]*' dma_test_results.json | awk '{print $2}')
        passed=$(grep -o '"passed": [0-9]*' dma_test_results.json | awk '{print $2}')
        failed=$(grep -o '"failed": [0-9]*' dma_test_results.json | awk '{print $2}')
        
        echo "Summary: $passed/$total tests passed, $failed failed"
        
        # Show failed test cases
        if [ $failed -gt 0 ]; then
            echo "Failed test cases:"
            python3 -c "
import json
with open('dma_test_results.json', 'r') as f:
    data = json.load(f)
    for detail in data['details']:
        if not detail['validation']['valid']:
            print(f\"- '{detail['test_case']}': {detail['validation']['reason']}\")
            print(f\"  Response: {detail['response']}\")
            print()
"
        fi
    fi
else
    echo "Test failed to run properly"
fi
