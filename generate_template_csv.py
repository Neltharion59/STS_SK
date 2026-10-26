import csv
from collections import Counter
from dataset_utils import load_dataset
from api_utils import lemma_cache, concept_cache

try:
    from nltk.corpus import wordnet as wn
    WN_AVAILABLE = True
except ImportError:
    WN_AVAILABLE = False

def analyze_word(word, sentence_lemmas):
    lemma = None
    has_lemma = False
    has_concept_entry = False
    has_category = False
    has_synonyms = False
    category = None
    synonyms = []

    for sent_lemma in sentence_lemmas:
        if sent_lemma.lower() == word.lower():
            lemma = sent_lemma
            has_lemma = True
            break

    if has_lemma and lemma in concept_cache:
        has_concept_entry = True
        entry = concept_cache[lemma]
        category = entry.get("namespace")
        if category and category != "Nezaradené":
            has_category = True
        synonyms = entry.get("synonyms", [])
        if synonyms:
            has_synonyms = True

    has_wn_entry = False
    wn_synset_count = 0
    if has_lemma and WN_AVAILABLE:
        synsets = wn.synsets(lemma, lang="slk")
        wn_synset_count = len(synsets)
        if wn_synset_count > 0:
            has_wn_entry = True

    return {
        "word": word,
        "lemma": lemma,
        "has_lemma": has_lemma,
        "has_concept_entry": has_concept_entry,
        "has_category": has_category,
        "category": category,
        "has_synonyms": has_synonyms,
        "synonyms": synonyms,
        "synonym_count": len(synonyms),
        "has_wn_entry": has_wn_entry,
        "wn_synset_count": wn_synset_count
    }

def read_metrics(csv_file):
    metrics = {}
    with open(csv_file, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f, delimiter=";")
        for row in reader:
            key = (row["metric_group"], row["metric"])
            metrics[key] = row["value"]
    return metrics

def get_val(metrics, group, metric, default="N/A"):
    return metrics.get((group, metric), default)

def compute_unique_given_lemma():
    """Compute absolute counts for unique words with category/synonyms given lemma"""
    dataset = load_dataset("sick_sk.txt")
    
    # Track unique word forms and their properties
    word_has_lemma = {}
    word_has_category = {}
    word_has_synonyms = {}
    word_has_cd_entry = {}
    
    for sent1, sent2, score in dataset:
        lemmas1 = lemma_cache.get(sent1, [])
        lemmas2 = lemma_cache.get(sent2, [])
        
        words1 = sent1.split()
        words2 = sent2.split()
        
        for sent_words, sent_lemmas in [(words1, lemmas1), (words2, lemmas2)]:
            for word in sent_words:
                word_lower = word.lower()
                if word_lower not in word_has_lemma:
                    analysis = analyze_word(word, sent_lemmas)
                    word_has_lemma[word_lower] = analysis["has_lemma"]
                    word_has_cd_entry[word_lower] = analysis["has_concept_entry"]
                    word_has_category[word_lower] = analysis["has_category"]
                    word_has_synonyms[word_lower] = analysis["has_synonyms"]
    
    # Count unique words with lemma
    unique_with_lemma = sum(1 for v in word_has_lemma.values() if v)
    
    # Count unique words with category given lemma
    unique_with_category_given_lemma = sum(1 for w, has_lemma in word_has_lemma.items() 
                                            if has_lemma and word_has_category.get(w, False))
    
    # Count unique words with synonyms given lemma
    unique_with_synonyms_given_lemma = sum(1 for w, has_lemma in word_has_lemma.items() 
                                            if has_lemma and word_has_synonyms.get(w, False))
    
    # Count unique words with CD entry given lemma (should equal unique_with_lemma since all lemmas have CD entry)
    unique_with_cd_given_lemma = sum(1 for w, has_lemma in word_has_lemma.items() 
                                      if has_lemma and word_has_cd_entry.get(w, False))
    
    return {
        "unique_with_lemma": unique_with_lemma,
        "unique_with_category_given_lemma": unique_with_category_given_lemma,
        "unique_with_synonyms_given_lemma": unique_with_synonyms_given_lemma,
        "unique_with_cd_given_lemma": unique_with_cd_given_lemma,
    }

def main():
    m = read_metrics("coverage_metrics_summary.csv")
    counts = compute_unique_given_lemma()

    rows = []

    # HEADER row
    rows.append({
        "metric": "HEADER",
        "conceptual_dictionary": "entries in conceptual dictionary (%)",
        "wordnet": "entries in wordnet (%)"
    })

    # unique words with entry
    cd_unique_entry = get_val(m, "unique_word_forms_global", "unique_word_forms_with_lemma")
    cd_unique_entry_pct = get_val(m, "unique_word_forms_global", "unique_word_forms_with_lemma_pct")
    wn_unique_entry = get_val(m, "unique_word_forms_global", "unique_word_forms_with_wn_entry")
    wn_unique_entry_pct = get_val(m, "unique_word_forms_global", "unique_word_forms_with_wn_entry_pct")
    
    rows.append({
        "metric": "unique words with entry",
        "conceptual_dictionary": f"{cd_unique_entry} ({cd_unique_entry_pct}%)",
        "wordnet": f"{wn_unique_entry} ({wn_unique_entry_pct}%)"
    })

    # total words in the dataset with entry (all tokens, not unique)
    cd_total_with_entry = get_val(m, "overall_all_words", "words_with_concept_entry")
    cd_total_with_entry_pct = get_val(m, "overall_all_words", "words_with_concept_entry_pct")
    wn_total_with_entry = get_val(m, "overall_all_words", "words_with_wn_entry")
    wn_total_with_entry_pct = get_val(m, "overall_all_words", "words_with_wn_entry_pct")
    
    rows.append({
        "metric": "total words in the dataset with entry",
        "conceptual_dictionary": f"{cd_total_with_entry} ({cd_total_with_entry_pct}%)",
        "wordnet": f"{wn_total_with_entry} ({wn_total_with_entry_pct}%)"
    })

    # entries per a sentence
    cd_avg_per_sent = get_val(m, "per_sentence_all_words", "avg_words_with_lemma_per_sentence")
    cd_avg_pct = get_val(m, "per_sentence_all_words", "avg_words_with_lemma_pct")
    wn_avg_per_sent = get_val(m, "per_sentence_all_words", "avg_words_with_wn_entry_per_sentence")
    wn_avg_pct = get_val(m, "per_sentence_all_words", "avg_words_with_wn_entry_pct")
    
    rows.append({
        "metric": "entries per a sentence",
        "conceptual_dictionary": f"avg {cd_avg_per_sent} ({cd_avg_pct}%)",
        "wordnet": f"avg {wn_avg_per_sent} ({wn_avg_pct}%)"
    })

    # ratio of sentence pairs with at least one entry in each sentence
    cd_pairs_both = get_val(m, "pair_hit_rates", "pairs_with_cd_entry_both")
    cd_pairs_both_pct = get_val(m, "pair_hit_rates", "pairs_with_cd_entry_both_pct")
    wn_pairs_both = get_val(m, "pair_hit_rates", "pairs_with_wn_entry_both")
    wn_pairs_both_pct = get_val(m, "pair_hit_rates", "pairs_with_wn_entry_both_pct")
    
    rows.append({
        "metric": "ratio of sentence pairs with at least one entry in each sentence",
        "conceptual_dictionary": f"{cd_pairs_both} ({cd_pairs_both_pct}%)",
        "wordnet": f"{wn_pairs_both} ({wn_pairs_both_pct}%)"
    })

    # ratio of sentence pairs with exactly one sentence without entry
    total_pairs = int(get_val(m, "pair_hit_rates", "pairs_total", "9840"))
    sent_total = int(get_val(m, "sentence_hit_rates", "sentences_total", "19680"))
    sent_with_cd = int(get_val(m, "sentence_hit_rates", "sentences_with_cd_entry", "16602"))
    sent_without_cd = sent_total - sent_with_cd
    
    p_none = sent_without_cd / sent_total
    expected_neither = round(p_none * p_none * total_pairs)
    pairs_at_least_one_cd = total_pairs - expected_neither
    pairs_exactly_one_cd = pairs_at_least_one_cd - int(cd_pairs_both)
    
    sent_with_wn = int(get_val(m, "sentence_hit_rates", "sentences_with_wn_entry", "15479"))
    sent_without_wn = sent_total - sent_with_wn
    p_none_wn = sent_without_wn / sent_total
    expected_neither_wn = round(p_none_wn * p_none_wn * total_pairs)
    pairs_at_least_one_wn = total_pairs - expected_neither_wn
    pairs_exactly_one_wn = pairs_at_least_one_wn - int(wn_pairs_both)
    
    rows.append({
        "metric": "ratio of sentence pairs with exactly one sentence without entry",
        "conceptual_dictionary": f"{pairs_exactly_one_cd} ({round(pairs_exactly_one_cd/total_pairs*100,1)}%)",
        "wordnet": f"{pairs_exactly_one_wn} ({round(pairs_exactly_one_wn/total_pairs*100,1)}%)"
    })

    # Separator
    rows.append({
        "metric": "\\hline",
        "conceptual_dictionary": "",
        "wordnet": ""
    })

    # unique words with a category
    cd_unique_cat = get_val(m, "unique_word_forms_global", "unique_word_forms_with_category")
    cd_unique_cat_pct = get_val(m, "unique_word_forms_global", "unique_word_forms_with_category_pct")
    rows.append({
        "metric": "unique words with a category",
        "conceptual_dictionary": f"{cd_unique_cat} ({cd_unique_cat_pct}%)",
        "wordnet": "N/A (no category in WordNet)"
    })

    # unique words with a category given lemma - use computed absolute count
    cd_cat_given_lemma_count = counts["unique_with_category_given_lemma"]
    cd_cat_given_lemma_pct = get_val(m, "conditional_given_lemma_unique_words", "category_given_lemma_pct")
    rows.append({
        "metric": "unique words with a category given lemma",
        "conceptual_dictionary": f"{cd_cat_given_lemma_count} ({cd_cat_given_lemma_pct}%)",
        "wordnet": "N/A (no category in WordNet)"
    })

    # unique words with synonyms
    cd_unique_syn = get_val(m, "unique_word_forms_global", "unique_word_forms_with_synonyms")
    cd_unique_syn_pct = get_val(m, "unique_word_forms_global", "unique_word_forms_with_synonyms_pct")
    rows.append({
        "metric": "unique words with synonyms",
        "conceptual_dictionary": f"{cd_unique_syn} ({cd_unique_syn_pct}%)",
        "wordnet": "N/A (synonyms via synsets not directly comparable)"
    })

    # unique words with synonyms given lemma - use computed absolute count
    cd_syn_given_lemma_count = counts["unique_with_synonyms_given_lemma"]
    cd_syn_given_lemma_pct = get_val(m, "conditional_given_lemma_unique_words", "synonyms_given_lemma_pct")
    rows.append({
        "metric": "unique words with synonyms given lemma",
        "conceptual_dictionary": f"{cd_syn_given_lemma_count} ({cd_syn_given_lemma_pct}%)",
        "wordnet": "N/A (synonyms via synsets not directly comparable)"
    })

    # Write output CSV
    with open("template_metrics_v2.csv", "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=["metric", "conceptual_dictionary", "wordnet"], delimiter=";")
        writer.writeheader()
        writer.writerows(rows)

    print("Saved template_metrics_v2.csv")
    print(f"Computed counts: {counts}")

if __name__ == "__main__":
    main()