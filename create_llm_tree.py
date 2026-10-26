from dataset_utils import load_dataset, stratified_split
from api_utils import get_sentence_lemmas, build_tree_from_concepts
from json import loads, dumps
from dotenv import dotenv_values

import requests, time, os, copy
from datetime import datetime

config = dotenv_values(".env")

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

def load_sick_dataset():
    dataset = load_dataset("sick_sk.txt")
    train_data, test_data = stratified_split(dataset)

    return train_data + test_data

def flatten(xss):
    return [x for xs in xss for x in xs]

def load_enhanced_tree_terms(root, lemmas_key):
    basic_tree = root.tree_to_text()
    enhancements = loaded_enhanced_trees_basic[lemmas_key]
    edges = set(basic_tree.split('\n') + enhancements.split('\n'))
    edges = sorted([edge for edge in edges if len(edge) > 0])

    terms = sorted(list(set(flatten([edge.split(' - ') for edge in edges]))))
    if 'root' in terms:
        terms.remove('root')
    terms_string = ','.join(terms)
    return terms_string

def make_prompt(couple, lemmas_key, tree_variant_name, prompt_template):
    if tree_variant_name == 'basic':
        prompt = prompt_template.format(INPUT_PAIRS = ' - '.join(couple))
    elif tree_variant_name == 'subsumer':
        terms_string = load_enhanced_tree_terms(root, lemmas_key)
        prompt = copy.deepcopy(prompt_template)
        prompt[-1]["content"].format(WORDS_COMMA_SEPARATED = root.tree_to_text())
    return prompt

def query_llm(prompt):
    """
    Query LLM with robust two-tier retry mechanism.
    
    Implements retry pattern from RETRY_LOGIC_PATTERN.md:
    - Inner loop: 5 quick attempts with 3-second delays
    - Outer loop: 6 extended cycles with 5-minute delays
    - Total capacity: Up to 30 attempts over ~25 minutes
    
    Args:
        prompt: The prompt to send to the LLM
        
    Returns:
        LLM response content or None if all retries exhausted
    """
    headers = {
        "Authorization": f"Bearer {config['LITELLM_API_KEY']}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": config['MODEL_NAME'],
        "messages": [
            {
                "role": "user",
                "content": prompt,
                "cache_control": {
                    "type": "ephemeral"
                }
            }
        ],
        "temperature": 0.7,
    }
    
    # Retry configuration
    max_5min_retries = 6
    max_inner_attempts = 5
    short_delay = 3
    long_delay = 60
    
    retry_cycle = 0
    
    # OUTER LOOP: Extended recovery cycles
    while retry_cycle < max_5min_retries:
        
        # INNER LOOP: Quick successive retries
        for attempt in range(1, max_inner_attempts + 1):
            try:
                r = requests.post(
                    f"{config['LITELLM_BASE_URL']}/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=int(config.get('MODEL_TIMEOUT', '900'))
                )
                
                r.raise_for_status()
                data = r.json()
                result = data["choices"][0]["message"]["content"]

                # SUCCESS: Return immediately
                return result
                
            except Exception as e:
                # LOG: Record the failure
                print(f"{datetime.now()} LLM request failed "
                      f"(attempt {attempt}/{max_inner_attempts}, "
                      f"cycle {retry_cycle + 1}/{max_5min_retries}): {e}")
                
                # DECISION POINT: Inner retry or outer cycle?
                if attempt < max_inner_attempts:
                    # Still have inner attempts left
                    time.sleep(short_delay)
                    continue  # Try again after short delay
                else:
                    # All inner attempts exhausted
                    retry_cycle += 1
                    
                    if retry_cycle < max_5min_retries:
                        # Start new cycle after long delay
                        print(f"{datetime.now()} All {max_inner_attempts} retry attempts failed. "
                              f"Sleeping for {long_delay}s before trying again "
                              f"(cycle {retry_cycle}/{max_5min_retries})...")
                        time.sleep(long_delay)
                        break  # Exit inner loop to restart outer loop
                    else:
                        # All cycles exhausted
                        print(f"{datetime.now()} Maximum retry cycles "
                              f"({max_5min_retries}) reached. Giving up.")
                        return None
    
    # Fallback: Should not reach here, but return None if we do
    return None

datasets = [
    {
        'name': 'sick',
        'data': load_sick_dataset()
    },
    {
        'name': 'sklep',
        'data': load_sklep_dataset()
    }
]

def get_prompt_from_file(file_name):
    with open(f'prompts/{file_name}', "r", encoding="utf-8-sig") as f:
        prompt_template = f.read()
    return prompt_template

tree_variants = {
    'basic': get_prompt_from_file('make_tree_v3.md'),
    'subsumer': get_prompt_from_file('make_tree_with_common_denominators.md')
}


def create_trees(tree_variant_name):
    try:
        with open(f'trees_raw_{tree_variant_name}.json', "r", encoding="utf-8-sig") as f:
            print('Found existing trees')
            enhanced_trees = loads(f.read())
    except FileNotFoundError:
        print('Creating trees from scratch')
        enhanced_trees = {}

    for dataset in datasets:
        for i, (veta1, veta2, skore) in enumerate(dataset['data']):
            print(f"{tree_variant_name} {dataset['name']} {i}/{len(dataset['data'])}")

            lemmas1 = get_sentence_lemmas(veta1)
            lemmas2 = get_sentence_lemmas(veta2)

            lemmas = list(set(lemmas1 + lemmas2))
            lemmas_key = ' '.join(sorted(lemmas))

            root = build_tree_from_concepts(lemmas)
            couples = [couple for couple in sorted(root.tree_to_couples()) if couple[0]!='root']
            for couple in couples:
                    couple_key = '-'.join(couple)
                    if couple_key not in enhanced_trees:
                        prompt = make_prompt(couple, lemmas_key, tree_variant_name, tree_variants[tree_variant_name])
                        tree_raw = query_llm(prompt)
                        
                        if tree_raw is None:
                            print(f"Failed to get LLM response for lemmas: {couple_key}")
                            print("Skipping this entry and continuing...")
                            continue
                        
                        enhanced_trees[couple_key] = tree_raw

                        with open(f'trees_raw_{tree_variant_name}.json', "w+", encoding="utf-8-sig") as f:
                            f.write(dumps(enhanced_trees, indent=4))
                            f.flush()
                            os.fsync(f.fileno())

loaded_enhanced_trees_basic = {}
for tree_variant_name in tree_variants:
    if tree_variant_name == 'subsumer':
        with open(f'trees_raw_basic.json', "r", encoding="utf-8-sig") as f:
            loaded_enhanced_trees_basic = loads(f.read())
    create_trees(tree_variant_name)

        