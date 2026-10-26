import json
from scipy.stats import pearsonr
import csv

with open("experiment_scores_final_final.json", "r", encoding="utf-8-sig") as f:
    data = json.load(f)

human_scores = data["human"]
results = data["results"]
configs = data["configs"]

scores = []

for i in range(len(configs)):
    model_scores = results[i]
    r = pearsonr(human_scores, model_scores)[0]
    scores.append((i, r, configs[i]))

scores.sort(key=lambda x: x[1], reverse=True)


with open("pearson_results_final_final.csv", "w", newline="", encoding="utf-8-sig") as f:
    writer = csv.writer(f, delimiter=";")

    writer.writerow([
        "pearson",
        "similarity_type",
        "matching",
        "word_agg",
        "sentence_agg",
        "direction",
        "power",
        "index_weight",
        "power_scope",
        "tree_type"
    ])

    for i, r, config in scores:
        similarity_type, matching, word_agg, sentence_agg, direction, power, index_w, power_scope, tree_type = config

        if index_w is None:
            index_w = "none"

        writer.writerow([
            r,
            similarity_type,
            matching,
            word_agg,
            sentence_agg,
            direction,
            power,
            index_w,
            power_scope,
            tree_type
        ])



