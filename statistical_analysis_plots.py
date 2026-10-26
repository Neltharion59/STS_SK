import pandas as pd
import matplotlib.pyplot as plt
from statistical_analysis_tests_lib import (
    get_pearson_vectors_by_column,
    pairwise_statistical_tests,
    format_comparison_line,
)

df = pd.read_csv("pearson_results_final_final.csv", sep=";")

for param in "similarity_type;matching;word_agg;sentence_agg;direction;power;index_weight;power_scope;tree_type".split(';'):
    vectors = get_pearson_vectors_by_column(df, param)
    results, sorted_items = pairwise_statistical_tests(vectors)
    
    order = [str(item[0]) for item in sorted_items]
    df[param] = pd.Categorical(df[param], categories=order, ordered=True)
    df_sorted = df.sort_values(param)
    
    plt.figure(figsize=(10, 6))
    bp = df_sorted.boxplot(column="pearson", by=param, return_type='axes')
    ax = bp if hasattr(bp, 'annotate') else plt.gca()
    plt.suptitle("")
    
    # Add significance symbols between tick labels at x-label level
    tick_labels = [str(item[0]) for item in sorted_items]
    for i in range(len(tick_labels) - 1):
        name1 = tick_labels[i]
        name2 = tick_labels[i + 1]
        key = f"{name1} vs {name2}"
        res = results.get(key, {"a >> b": False})
        symbol = " >> " if res.get("a >> b", False) else " > "
        # Position between tick marks aligned with x-tick labels
        ax.annotate(symbol, xy=(i + 1.5, -0.02), xycoords=('data', 'axes fraction'),
                    ha='center', va='top', fontsize=11, fontweight='bold')
    
    plt.xlabel(param)
    plt.ylabel("Pearson score")
    plt.tight_layout()
    plt.savefig(f"plots/boxplot_{param}.eps")
    plt.close()

print("All boxplots saved to plots/")
