import json
import csv

with open('final_test_results.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Find config with power1 and tree_type cd_basic
target_config = None
for result in data['results']:
    config = result['config']
    if config.get('power') == 'power1' and config.get('tree_type') == 'cd_basic':
        target_config = result
        break

if not target_config:
    print("Config not found!")
    exit(1)

print(f"Found config: {target_config['config']}")

# Category order
category_order = ['neither_has_entry', 'one_has_entry', 'both_have_entries', 'all_pairs']

# Metrics to compare
metrics_to_compare = ['Pearson', 'Spearman', 'Kendall Tau', 'MAE', 'MSE']

# Write CSV
with open('config_comparison.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f, delimiter=';')
    writer.writerow(['Category', 'Count'] + metrics_to_compare)

    for cat_name in category_order:
        if cat_name in target_config['categories']:
            metrics = target_config['categories'][cat_name]
            row = [cat_name, metrics.get('count', 0)]
            for m in metrics_to_compare:
                val = metrics.get(m)
                row.append(f"{val:.6f}" if val is not None else 'N/A')
            writer.writerow(row)

print("CSV written to config_comparison.csv")

# Generate LaTeX table
latex_lines = []
latex_lines.append(r"\begin{table*}[htbp]")
latex_lines.append(r"\centering")
latex_lines.append(r"\caption{Comparison of metrics across categories for config: power1, cd\_basic, spath, one\_to\_many}")
latex_lines.append(r"\label{tab:config_comparison}")
latex_lines.append(r"\begin{tabular}{|l|c|c|c|c|c|c|}")
latex_lines.append(r"\hline")
latex_lines.append("Category & Count & Pearson & Spearman & Kendall Tau & MAE & MSE \\\\")
latex_lines.append(r"\hline")

for cat_name in category_order:
    if cat_name in target_config['categories']:
        metrics = target_config['categories'][cat_name]
        count = metrics.get('count', 0)
        
        def fmt(val):
            if val is None or (isinstance(val, float) and (val != val)):  # NaN check
                return "N/A"
            return f"{val:.2f}"
        
        row = [
            cat_name.replace('_', ' ').title(),
            str(count),
            fmt(metrics.get('Pearson')),
            fmt(metrics.get('Spearman')),
            fmt(metrics.get('Kendall Tau')),
            fmt(metrics.get('MAE')),
            fmt(metrics.get('MSE'))
        ]
        latex_lines.append(" & ".join(row) + r" \\")
        latex_lines.append(r"\hline")

latex_lines.append(r"\end{tabular}")
latex_lines.append(r"\end{table*}")

latex_output = "\n".join(latex_lines)

with open('config_comparison.tex', 'w', encoding='utf-8') as f:
    f.write(latex_output)

print("LaTeX table written to config_comparison.tex")
print("\n" + latex_output)

# Also print to console
for cat_name in category_order:
    if cat_name in target_config['categories']:
        metrics = target_config['categories'][cat_name]
        print(f"\n{cat_name} (count: {metrics.get('count', 0)}):")
        for m in metrics_to_compare:
            val = metrics.get(m)
            print(f"  {m}: {val:.6f}" if val is not None else f"  {m}: N/A")