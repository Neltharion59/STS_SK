import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import mannwhitneyu
from scipy.stats import pearsonr, spearmanr, kendalltau

from sklearn.metrics import mean_absolute_error
from sklearn.metrics import mean_squared_error
from sklearn.metrics import r2_score
from json import loads

import numpy as np

from api_utils import get_sentence_lemmas
from api_utils import build_tree_from_concepts

from similarity import compute_similarity

from dataset_utils import load_dataset
from final_split import stratified_split

def load_sklep_dataset(filepath='sklep.json'):
    """Load SKLEP dataset from JSON file."""
    data = []
    with open(filepath, "r", encoding="utf-8-sig") as f:
        for line in f:
            entry = loads(line.strip())
            data.append((
                entry["sentence1"],
                entry["sentence2"],
                float(entry["similarity_score"])
            ))
    return data


dataset = load_dataset("sick_sk.txt")
train_data, test_data = stratified_split(dataset)
#test_data = load_sklep_dataset()

df = pd.read_csv("pearson_results_final_final.csv", sep=";")

filter_options = {
    'power': [{'equal': True, 'value':'power1'}, {'equal': False, 'value':'power1'}],
    'tree_type': [{'equal': True, 'value':'wn'}, {'equal': True, 'value':'cd_basic'}, {'equal': True, 'value':'cd_enhanced_basic'}]
}

table_lines = []

for power in filter_options['power']:
    for tree_type in filter_options['tree_type']:
        row = df[
            (df["power"] == power['value'] if power['equal'] else df["power"] != power['value'] ) &
            (df["tree_type"] == tree_type['value'] )
        ].loc[
            lambda x: x["pearson"].idxmax()
        ]

        human_scores = []
        model_scores = []

        for i, (veta1, veta2, skore) in enumerate(test_data):

            print(f"{i}/{len(test_data)}")

            lemmas1 = get_sentence_lemmas(veta1)
            lemmas2 = get_sentence_lemmas(veta2)

            root = build_tree_from_concepts(
                list(set(lemmas1 + lemmas2))
            )

            sim = compute_similarity(
                lemmas1,
                lemmas2,
                root,
                matching=row["matching"],
                word_agg=row["word_agg"],
                sentence_agg=row["sentence_agg"],
                direction=row["direction"],
                similarity_type=row["similarity_type"],
                power=row["power"],
                index_weight_type=row["index_weight"] if row["index_weight"]!='none' else None,
                power_scope=row["power_scope"],
                tree_type=row['tree_type']
            )

            model_scores.append(sim)
            human_scores.append(skore)

        scaled_model_scores = [1 + s * 4 for s in model_scores]

        pearson = pearsonr(human_scores, model_scores)[0]
        spearman = spearmanr(human_scores, model_scores)[0]
        kendall = kendalltau(human_scores, model_scores)[0]

        mae = mean_absolute_error(human_scores, scaled_model_scores)

        mse = mean_squared_error(human_scores, scaled_model_scores)
        rmse = np.sqrt(mse)

        mape = np.mean(
            np.abs(
                (np.array(human_scores) - np.array(scaled_model_scores))
                / np.array(human_scores)
            )
        ) * 100

        r2 = r2_score(human_scores, scaled_model_scores)

        print("Pearson:", pearson)
        print("Spearman:", spearman)
        print("Kendall Tau:", kendall)

        print("MAE:", mae)
        print("MSE:", mse)
        print("RMSE:", rmse)
        print("MAPE:", mape)

        print("R2:", r2)

        pearson = round(pearson, 2)
        spearman = round(spearman, 2)
        kendall = round(kendall, 2)
        mae = round(mae, 2)
        mse = round(mse, 2)

        table_lines.append(f'{row['tree_type']},{row['power']} & {pearson} & {spearman} & {kendall} & {mae} & {mse}')


for line in table_lines:
    print(line)