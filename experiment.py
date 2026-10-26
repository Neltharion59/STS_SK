import json, os
from datetime import datetime
from itertools import product

from api_utils import get_sentence_lemmas
from api_utils import build_tree_from_concepts

from similarity import compute_similarity

from dataset_utils import load_dataset
from final_split import stratified_split

from tree_loader import load_enhanced_tree



dataset = load_dataset("sick_sk.txt")
train_data, test_data = stratified_split(dataset)

matchings = ["one_to_many", "all_to_all", "element_wise"]
word_aggs = ["max", "avg", "min"]
sentence_aggs = ["max", "avg", "min"]
directions = ["single", "symmetric"]
powers = ["power1", "power2", "power7", "power13", "power101"]
index_weights = [None, "linear", "prime", "exponential"]
similarity_types = ["wupalmer", "spath", "lch"]
power_scopes = ["local", "global"]
tree_types = ["cd_basic", "wn", "cd_enhanced_basic"]#, "cd_enhanced_subsumer"]

configs = []

for similarity_type, matching, direction, power, index_w, power_scope, tree_type in product(
        similarity_types, matchings, directions, powers, index_weights, power_scopes, tree_types):

    if matching == "one_to_many":
        for word_agg, sentence_agg in product(word_aggs, sentence_aggs):
            configs.append((similarity_type, matching, word_agg, sentence_agg, direction, power, index_w, power_scope, tree_type))
    else:
        for sentence_agg in sentence_aggs:
            configs.append((similarity_type, matching, None, sentence_agg, direction, power, index_w, power_scope, tree_type))

human_scores = []
results = [[] for _ in configs]

try:
    with open("experiment_scores_final_final.json", "r", encoding="utf-8") as f:
        file_raw = f.read()
        file_json = json.loads(file_raw)
        human_scores = file_json['human']
        results = file_json['results']
except FileNotFoundError:
    pass

for i, (veta1, veta2, skore) in enumerate(train_data):
    skip = False
    if i < len(human_scores):
        skip = True

    print(f"{datetime.now()} {i}/{len(train_data)} ... {'Skipping' if skip else 'Calculating'}")

    if skip:
        continue

    lemmas1 = get_sentence_lemmas(veta1)
    lemmas2 = get_sentence_lemmas(veta2)

    lemmas = list(set(lemmas1 + lemmas2))
    lemmas_key = ' '.join(sorted(lemmas))

    for j, config in enumerate(configs):
        similarity_type, matching, word_agg, sentence_agg, direction, power, index_w, power_scope,tree_type = config
        
        root = build_tree_from_concepts(lemmas)
        if "cd_enhanced_" in tree_type:
            root = load_enhanced_tree(root, lemmas_key, tree_type)

        sim = compute_similarity(
            lemmas1,
            lemmas2,
            root,
            matching,
            word_agg,
            sentence_agg,
            direction,
            similarity_type=similarity_type,
            power=power,
            index_weight_type=index_w,
            power_scope = power_scope,
            tree_type = tree_type
        )

        results[j].append(sim)

    human_scores.append(skore)

    with open("experiment_scores_final_final.json", "w+", encoding="utf-8") as f:
        json.dump({
            "human": human_scores,
            "results": results,
            "configs": configs
        }, f, indent=2)
        f.flush()
        os.fsync(f.fileno())

