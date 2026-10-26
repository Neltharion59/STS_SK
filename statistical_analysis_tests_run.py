import pandas as pd
from statistical_analysis_tests_lib import sort_by_categorical, analyze_all_columns

df = pd.read_csv("pearson_results_final_final.csv", sep=";")
df, _ = sort_by_categorical(df)
all_results, comparison_lines = analyze_all_columns(df)