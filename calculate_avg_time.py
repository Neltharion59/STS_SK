import json
import numpy as np

with open('final_test_results.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

all_row_times = []

for result in data['results']:
    for cat_name, metrics in result['categories'].items():
        row_times = metrics.get('row_times', [])
        all_row_times.extend(row_times)

all_times = np.array(all_row_times)

print(f"Total entries: {len(all_times)}")
print(f"Min time: {all_times.min():.4f}s")
print(f"Max time: {all_times.max():.4f}s")
print(f"Avg time: {all_times.mean():.4f}s")
print(f"Std time: {all_times.std():.4f}s")