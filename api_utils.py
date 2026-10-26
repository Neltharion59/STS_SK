import requests, json, time, os
from tree import Node

token = None
missing_lemmas = set()

try:
    with open("concept_cache.json", "r", encoding = "utf-8-sig") as f:
        concept_cache = json.load(f)

except FileNotFoundError:
    concept_cache = {}

try:
    with open("lemma_cache.json", "r", encoding = "utf-8-sig") as f:
        lemma_cache = json.load(f)
        
except FileNotFoundError:
    lemma_cache = {}

try:
    with open("caches/endpoint_caches/cache_extractor.json", "r", encoding = "utf-8-sig") as f:
        extractor_cache = json.load(f)
except FileNotFoundError:
    extractor_cache = {}

try:
    with open("caches/endpoint_caches/cache_concept.json", "r", encoding = "utf-8-sig") as f:
        concept_endpoint_cache = json.load(f)
except FileNotFoundError:
    concept_endpoint_cache = {}

missing_lemmas = set()

try:
    with open("missing_lemmas.csv", "r", encoding="utf-8-sig") as f:
        next(f)  
        for line in f:
            idx, lemma = line.strip().split(",", 1)
            missing_lemmas.add(lemma)
except FileNotFoundError:
    with open("missing_lemmas.csv", "w", encoding="utf-8-sig") as f:
        f.write("idx,lemma\n")
        f.flush()
        os.fsync(f.fileno())
    

def get_token():
    global token

    if token is not None:
        return token

    endpoint = "https://pojmy.kinit.sk/api/auth"

    with open("udaje.txt", "r") as file:
        line = file.readline()
        info = line.split(' ')
        email = info[0]
        password = ' '.join(info[1:])

    logindata = {"email": email, "password": password}

    response = requests.post(endpoint, data=logindata)

    data = response.json()

    token = data.get("token")

    return token

def extract_lemmas(sentence):
    # Check if raw response is cached
    if sentence in extractor_cache:
        extractor_data = extractor_cache[sentence]
    else:
        # Make API call
        extractor_url = "https://pojmy.kinit.sk/api/extractor"
        extractor_headers = {"Authorization": f"Bearer {get_token()}"}
        extractor_params = {"text": sentence}
        extractor_response = requests.get(extractor_url, params=extractor_params, headers=extractor_headers, timeout = 10)

        try:
            extractor_data = extractor_response.json()
        except:
            return []
        
        # Cache the raw response
        extractor_cache[sentence] = extractor_data
        with open("caches/endpoint_caches/cache_extractor.json", "w", encoding="utf-8-sig") as f:
            json.dump(extractor_cache, f, ensure_ascii=False, indent=2)
            f.flush()
            os.fsync(f.fileno())
    
    # Process the response to extract lemmas
    lemmas = [record['lemma'] for record in extractor_data['results'] if record['lemma'] is not None]
    
    return lemmas

def get_sentence_lemmas(sentence):
    if sentence not in lemma_cache:
        lemma_cache[sentence] = extract_lemmas(sentence)

        with open("lemma_cache.json", "w", encoding="utf-8-sig") as f:
            json.dump(lemma_cache, f, ensure_ascii=False, indent=2)
            f.flush()
            os.fsync(f.fileno())

    return lemma_cache[sentence]

def parse_concept_response(data, concepts_dict, lemma):   

    main_lemma = lemma   

    if main_lemma not in concepts_dict:
        concepts_dict[main_lemma] = Node(main_lemma)

    children = []
    for word in data["results"].get("synonymum", []):     
        if word["lemma"] not in children:
            children.append(word["lemma"])
            
    for child in children:   
        if child not in concepts_dict:
            concepts_dict[child] = Node(child)
        concepts_dict[main_lemma].add_child(concepts_dict[child])

    return concepts_dict[main_lemma]

def build_tree_from_concepts(lemmas):        

    lemma_namespaces = dict(choose_namespace(lemmas))

    root = Node("root")
    concepts_dict = {"root": root}

    for lemma in lemmas:
        if lemma in concepts_dict:  
            continue

        data = {"results": {"synonymum": []}} 
        concept_info = get_concept_data(lemma)
        synonyms = concept_info["synonyms"]
        for syn in synonyms:
            data["results"]["synonymum"].append({"lemma": syn})

        node = parse_concept_response(data, concepts_dict, lemma)
        if not node:
            continue

        ns = lemma_namespaces.get(lemma, "Nezaradené")

        if ns not in concepts_dict:
            concepts_dict[ns] = Node(ns)
            root.add_child(concepts_dict[ns])

        if node not in concepts_dict[ns].children:
            concepts_dict[ns].add_child(node)

    return root

def get_concept_data(lemma):
    if lemma in concept_cache:
        return concept_cache[lemma]

    # Check if raw API response is cached
    if lemma in concept_endpoint_cache:
        data = concept_endpoint_cache[lemma]
    else:
        # Make API call with rate limiting
        time.sleep(0.5)

        endpoint = "https://pojmy.kinit.sk/api/concept"
        headers = {"Authorization": f"Bearer {get_token()}"}
        params = {"lemma": lemma}

        response = requests.get(endpoint, params=params, headers=headers)
        data = response.json()
        
        # Cache the raw response
        concept_endpoint_cache[lemma] = data
        with open("caches/endpoint_caches/cache_concept.json", "w", encoding="utf-8-sig") as f:
            json.dump(concept_endpoint_cache, f, ensure_ascii=False, indent=2)
            f.flush()
            os.fsync(f.fileno())

    results = data.get("results", {})

    if not isinstance(results, dict):
        results = {}

    syn_list = []

    if isinstance(results, dict):
        for word in results.get("synonymum", []):
            lemma_syn = word.get("lemma")
            if lemma_syn and lemma_syn not in syn_list:
                syn_list.append(lemma_syn)

    has_record = isinstance(results, dict) and len(results) > 0

    if not has_record and lemma not in missing_lemmas:
        with open("missing_lemmas.csv", "a", encoding="utf-8-sig") as f:
            f.write(f"{len(missing_lemmas)},{lemma}\n")
            f.flush()
            os.fsync(f.fileno())

        missing_lemmas.add(lemma)

    namespace = None

    type_data = results.get("typeOf", [])
    if type_data:
        namespace = type_data[0].get("namespace")

    if not namespace:
        syn_data = results.get("synonymum", [])
        if syn_data:
            namespace = syn_data[0].get("namespace")

    if namespace:
        namespace = namespace.split("/")[0].strip()
    else:
        namespace = "Nezaradené"

    concept_cache[lemma] = {
        "synonyms": syn_list,
        "namespace": namespace,
        "has_record": has_record
    }
    
    # Write concept cache to disk
    with open("concept_cache.json", "w", encoding="utf-8-sig") as f:
        json.dump(concept_cache, f, ensure_ascii=False, indent=2)
        f.flush()
        os.fsync(f.fileno())

    return concept_cache[lemma]

def get_terms_for_word(word):
    # Check if raw API response is cached
    if word in concept_endpoint_cache:
        data = concept_endpoint_cache[word]
    else:
        # Make API call
        concept_url = "https://pojmy.kinit.sk/api/concept"
        headers = {"Authorization": f"Bearer {get_token()}"}
        params = {"lemma": word}
        response = requests.get(concept_url, params=params, headers=headers)
        data = response.json()
        
        # Cache the raw response
        concept_endpoint_cache[word] = data
        with open("caches/endpoint_caches/cache_concept.json", "w", encoding="utf-8-sig") as f:
            json.dump(concept_endpoint_cache, f, ensure_ascii=False, indent=2)
            f.flush()
            os.fsync(f.fileno())

    results = data.get("results", {})

    if not isinstance(results, dict):
        results = {}

    words = []

    for relation in ["typeOf", "synonymum"]:
        for item in results.get(relation, []):
            lemma_str = item.get("lemma")
 
            if lemma_str and lemma_str != word and lemma_str not in words:
                words.append(lemma_str)
                
    return words

def choose_namespace(lemmas):
    return [(w, get_concept_data(w)["namespace"]) for w in lemmas]

def merge_sets(word1,word2):
    set1 = set(get_terms_for_word(word1))
    set2 = set(get_terms_for_word(word2))

    set1.add(word1)
    set1.add(word2)
    set2.add(word2)
    set2.add(word1)

    return set1, set2

