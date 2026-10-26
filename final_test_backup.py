from scipy.stats import pearsonr, spearmanr, kendalltau
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from json import loads
import numpy as np
import time
from nltk.corpus import wordnet as wn

from api_utils import get_sentence_lemmas, build_tree_from_concepts, get_concept_data
from similarity import compute_similarity
from dataset_utils import load_dataset
from final_split import stratified_split
from tree_loader import load_enhanced_tree


CONFIGS = [
    {
        'matching': 'one_to_many',
        'word_agg': 'max',
        'sentence_agg': 'max',
        'direction': 'symmetric',
        'similarity_type': 'wupalmer',
        'power': 'power1',
        'index_weight_type': 'prime',
        'power_scope': 'local',
        'tree_type': 'wn'
    },
    {
        'matching': 'one_to_many',
        'word_agg': 'max',
        'sentence_agg': 'max',
        'direction': 'symmetric',
        'similarity_type': 'spath',
        'power': 'power1',
        'index_weight_type': 'prime',
        'power_scope': 'local',
        'tree_type': 'cd_basic'
    },
    {
        'matching': 'one_to_many',
        'word_agg': 'max',
        'sentence_agg': 'max',
        'direction': 'symmetric',
        'similarity_type': 'spath',
        'power': 'power1',
        'index_weight_type': 'prime',
        'power_scope': 'local',
        'tree_type': 'cd_llm'
    },
    {
        'matching': 'one_to_many',
        'word_agg': 'max',
        'sentence_agg': 'avg',
        'direction': 'symmetric',
        'similarity_type': 'wupalmer',
        'power': 'power2',
        'index_weight_type': None,
        'power_scope': 'local',
        'tree_type': 'wn'
    },
    {
        'matching': 'one_to_many',
        'word_agg': 'max',
        'sentence_agg': 'avg',
        'direction': 'symmetric',
        'similarity_type': 'wupalmer',
        'power': 'power7',
        'index_weight_type': None,
        'power_scope': 'local',
        'tree_type': 'cd_basic'
    },
    {
        'matching': 'one_to_many',
        'word_agg': 'max',
        'sentence_agg': 'max',
        'direction': 'symmetric',
        'similarity_type': 'wupalmer',
        'power': 'power7',
        'index_weight_type': 'prime',
        'power_scope': 'local',
        'tree_type': 'cd_llm'
    }
]


def has_entry_wn(lemmas):
    """Check if any lemma has a WordNet entry for Slovak."""
    for lemma in lemmas:
        synsets = wn.synsets(lemma, lang='slk')
        if synsets:
            return True
    return False


def has_entry_cd(lemmas):
    """Check if any lemma has a Conceptual Dictionary entry."""
    for lemma in lemmas:
        data = get_concept_data(lemma)
        if data.get('has_record', False):
            return True
    return False


def categorize_pair(veta1, veta2, tree_type):
    """Categorize sentence pair based on resource coverage.
    Returns: 1 (both have entries), 2 (one has entry), 3 (neither has entry)"""
    lemmas1 = get_sentence_lemmas(veta1)
    lemmas2 = get_sentence_lemmas(veta2)

    if tree_type == 'wn':
        has1 = has_entry_wn(lemmas1)
        has2 = has_entry_wn(lemmas2)
    else:
        has1 = has_entry_cd(lemmas1)
        has2 = has_entry_cd(lemmas2)

    if has1 and has2:
        return 1
    elif has1 or has2:
        return 2
    else:
        return 3


def compute_metrics(human_scores, model_scores):
    """Compute all metrics for given scores."""
    if not human_scores:
        return {
            'Pearson': None,
            'Spearman': None,
            'Kendall Tau': None,
            'MAE': None,
            'MSE': None,
            'RMSE': None,
            'MAPE': None,
            'R2': None,
            'count': 0
        }

    scaled_model_scores = [1 + s * 4 for s in model_scores]

    return {
        'Pearson': float(pearsonr(human_scores, model_scores)[0]),
        'Spearman': float(spearmanr(human_scores, model_scores)[0]),
        'Kendall Tau': float(kendalltau(human_scores, model_scores)[0]),
        'MAE': float(mean_absolute_error(human_scores, scaled_model_scores)),
        'MSE': float(mean_squared_error(human_scores, scaled_model_scores)),
        'RMSE': float(np.sqrt(mean_squared_error(human_scores, scaled_model_scores))),
        'MAPE': float(np.mean(np.abs((np.array(human_scores) - np.array(scaled_model_scores)) / np.array(human_scores))) * 100),
        'R2': float(r2_score(human_scores, scaled_model_scores)),
        'count': len(human_scores)
    }


dataset = load_dataset('sick_sk.txt')
train_data, test_data = stratified_split(dataset)

all_results = []

for config in CONFIGS:
    # Categorize all test pairs first
    categories = {1: [], 2: [], 3: []}

    print(f"Categorizing {len(test_data)} pairs for config: {config['tree_type']}...")
    for veta1, veta2, skore in test_data:
        cat = categorize_pair(veta1, veta2, config['tree_type'])
        categories[cat].append((veta1, veta2, skore))

    print(f"  Category 1 (both have entries): {len(categories[1])}")
    print(f"  Category 2 (one has entry): {len(categories[2])}")
    print(f"  Category 3 (neither has entry): {len(categories[3])}")

    config_results = {
        'config': config,
        'categories': {}
    }

    # Process each category
    for cat_id in [1, 2, 3, 'all']:
        if cat_id == 'all':
            pairs = test_data
        else:
            pairs = categories[cat_id]

        human_scores = []
        model_scores = []
        row_times = []

        config_start_time = time.time()

        for i, (veta1, veta2, skore) in enumerate(pairs):
            print(f"  Cat {cat_id}: {i}/{len(pairs)}")

            row_start_time = time.time()

            lemmas1 = get_sentence_lemmas(veta1)
            lemmas2 = get_sentence_lemmas(veta2)

            lemmas = list(set(lemmas1 + lemmas2))
            lemmas_key = ' '.join(sorted(lemmas))

            root = build_tree_from_concepts(lemmas)

            if 'cd_enhanced_' in config['tree_type']:
                root = load_enhanced_tree(root, lemmas_key, config['tree_type'])

            sim = compute_similarity(
                lemmas1,
                lemmas2,
                root,
                matching=config['matching'],
                word_agg=config['word_agg'],
                sentence_agg=config['sentence_agg'],
                direction=config['direction'],
                similarity_type=config['similarity_type'],
                power=config['power'],
                index_weight_type=config['index_weight_type'],
                power_scope=config['power_scope'],
                tree_type=config['tree_type']
            )

            model_scores.append(sim)
            human_scores.append(skore)
            row_times.append(time.time() - row_start_time)

        config_total_time = time.time() - config_start_time

        row_times_np = np.array(row_times) if row_times else np.array([0])
        time_stats = {
            'min_time': float(row_times_np.min()),
            'max_time': float(row_times_np.max()),
            'avg_time': float(row_times_np.mean()),
            'total_time': config_total_time
        }

        metrics = compute_metrics(human_scores, model_scores)
        metrics['row_times'] = row_times
        metrics['time_stats'] = time_stats

        config_results['categories'][f'category_{cat_id}'] = metrics

    all_results.append(config_results)

# Print summary
for result in all_results:
    config = result['config']
    print(f"\nConfig: {config}")
    for cat_name, metrics in result['categories'].items():
        print(f"  {cat_name}:")
        for name, value in metrics.items():
            if name not in ('row_times', 'time_stats'):
                print(f"    {name}: {value}")

# Save to JSON
output_data = {'results': all_results}
import json
with open('final_test_results.json', 'w', encoding='utf-8') as f:
    json.dump(output_data, f, indent=4, ensure_ascii=False)