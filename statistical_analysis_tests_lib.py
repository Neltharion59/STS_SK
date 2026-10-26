import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import shapiro, ttest_rel, wilcoxon, ttest_ind, mannwhitneyu, kstest
import numpy as np
from itertools import combinations

def is_normal(data, alpha=0.05):
    """
    Test whether a numeric vector is normally distributed.

    Returns:
        True  -> data is consistent with normality
        False -> data significantly deviates from normality
    """
    data = np.asarray(data)
    data = data[~np.isnan(data)]
    n = len(data)

    if n > 2000:
        # Kolmogorov-Smirnov test against normal distribution
        # Uses sample mean/std as reference parameters
        stat, p = kstest(data, 'norm', args=(data.mean(), data.std()))
    else:
        stat, p = shapiro(data)

    return p > alpha

def is_significantly_higher(a, b, alpha=0.05):
    """
    Tests whether sample a is higher than sample b.
    Uses paired test if same length, otherwise unpaired.
    """
    paired = len(a) == len(b)
    
    if paired:
        diffs = a - b
        normal = is_normal(diffs)
        test = ttest_rel if normal else wilcoxon
        test_name = "ttest_rel" if normal else "wilcoxon"
        stat, p = test(a, b, alternative="greater")
    else:
        # Unpaired: test differences of means
        normal_a = is_normal(a)
        normal_b = is_normal(b)
        if normal_a and normal_b:
            test = ttest_ind
            test_name = "ttest_ind"
        else:
            test = mannwhitneyu
            test_name = "mannwhitneyu"
        stat, p = test(a, b, alternative="greater")
    
    return p < alpha, float(p), test_name


def statistical_test(vec1, vec2):
    """Placeholder statistical test function. Accepts two numerical vectors."""
    test_result, p, test_name = is_significantly_higher(vec1, vec2)
    return {"a >> b": test_result, "pvalue": p, "test_name": test_name}


def get_pearson_vectors_by_column(df, column_name):
    """Get pearson vectors grouped by each unique value of column_name."""
    vectors = {}
    unique_vals = df[column_name].dropna().unique()
    for val in sorted(unique_vals, key=lambda x: str(x)):
        mask = df[column_name] == val
        vectors[val] = df.loc[mask, 'pearson'].values
    return vectors


def pairwise_statistical_tests(vectors_dict, test_func=statistical_test):
    """Run statistical test on neighboring pairs after sorting by median pearson descending."""
    sorted_items = sorted(vectors_dict.items(), key=lambda x: np.median(x[1]), reverse=True)
    results = {}
    for i in range(len(sorted_items) - 1):
        name1, vec1 = sorted_items[i]
        name2, vec2 = sorted_items[i + 1]
        key = f"{name1} vs {name2}"
        results[key] = test_func(vec1, vec2)
    return results, sorted_items


def format_comparison_line(sorted_items, results):
    """Create visual line: name1 > name2 >> name3 ..."""
    if not sorted_items:
        return ""
    
    parts = [str(sorted_items[0][0])]
    for i in range(len(sorted_items) - 1):
        name1 = sorted_items[i][0]
        name2 = sorted_items[i + 1][0]
        key = f"{name1} vs {name2}"
        res = results.get(key, {"a >> b": False})
        operator = " >> " if res.get("a >> b", False) else " > "
        parts.append(operator)
        parts.append(str(name2))
    return "".join(parts)

def sort_by_categorical(df):
    """Sort dataframe by all non-numeric columns for consistent pairing."""
    numeric_cols = df.select_dtypes(include='number').columns
    categorical_cols = [c for c in df.columns if c not in numeric_cols]
    return df.sort_values(by=categorical_cols).reset_index(drop=True), categorical_cols


def compare_columns(df, column_name):
    print("\n--- Testing get_pearson_vectors_by_column ---")
    vectors = get_pearson_vectors_by_column(df, column_name)
    for k, v in vectors.items():
        print(f"  {k}: n={len(v)}, median={np.median(v):.4f}")

    print("\n--- Testing pairwise_statistical_tests ---")
    results = pairwise_statistical_tests(vectors)
    for k, v in results.items():
        print(f"  {k}: {v}")

def analyze_all_columns(df, exclude_cols=('pearson',)):
    """Loop over all non-numerical columns and run statistical comparisons."""
    numeric_cols = df.select_dtypes(include='number').columns
    categorical_cols = [c for c in df.columns if c not in numeric_cols and c not in exclude_cols]
    
    comparison_lines = []

    all_results = {}
    for col in categorical_cols:
        print(f"\n{'='*60}")
        print(f"ANALYZING COLUMN: {col}")
        print(f"{'='*60}")
        
        vectors = get_pearson_vectors_by_column(df, col)
        for k, v in vectors.items():
            print(f"  {k}: n={len(v)}, median={np.median(v):.4f}")
        
        results, sorted_items = pairwise_statistical_tests(vectors)
        all_results[col] = {"results": results, "order": sorted_items}
        
        for k, v in results.items():
            print(f"  {k}: {v}")
        
        visual = format_comparison_line(sorted_items, results)
        print(f"  {visual}")
        comparison_lines.append(visual)
    
    return all_results, comparison_lines


df = pd.read_csv("pearson_results_final_final.csv", sep=";")

column_names = df.columns.tolist()

df, column_names_categorical = sort_by_categorical(df)

all_results, comparison_lines = analyze_all_columns(df)
