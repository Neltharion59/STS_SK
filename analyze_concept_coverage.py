import json
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

    # WordNet check
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

def analyze_sentence(sentence, sentence_lemmas):
    words = sentence.split()
    return [analyze_word(word, sentence_lemmas) for word in words]

def main():
    dataset = load_dataset("sick_sk.txt")
    print(f"Loaded {len(dataset)} sentence pairs")

    all_pairs = []
    stats = {
        "total_words": 0,
        "words_with_lemma": 0,
        "words_with_concept_entry": 0,
        "words_with_category": 0,
        "words_with_synonyms": 0,
        "words_with_wn_entry": 0,
        "total_lemmas_found": 0,
        "unique_lemmas_with_entry": set(),
        "unique_lemmas_with_category": set(),
        "unique_lemmas_with_synonyms": set(),
        "unique_lemmas_with_wn": set(),
        "sentence_word_counts": 0,
        "sentence_lemma_counts": 0,
        "sentence_category_counts": 0,
        "sentence_synonym_counts": 0,
        "sentence_wn_counts": 0,
        "sentence_pct_lemma": 0.0,
        "sentence_pct_category": 0.0,
        "sentence_pct_synonyms": 0.0,
        "sentence_pct_wn": 0.0,
        "sentence_count": 0,
        "unique_words_per_sentence": [],
        "unique_lemmas_per_sentence": [],
        "unique_categories_per_sentence": [],
        "unique_synonyms_per_sentence": [],
        "unique_wn_per_sentence": [],
        "unique_pct_lemma_per_sentence": [],
        "unique_pct_category_per_sentence": [],
        "unique_pct_synonyms_per_sentence": [],
        "unique_pct_wn_per_sentence": [],
        "unique_lemma_total": 0,
        "unique_category_total": 0,
        "unique_synonym_total": 0,
        "unique_wn_total": 0,
        "unique_words_total": 0,
    }

    for i, (sent1, sent2, score) in enumerate(dataset):
        lemmas1 = lemma_cache.get(sent1, [])
        lemmas2 = lemma_cache.get(sent2, [])

        words1 = analyze_sentence(sent1, lemmas1)
        words2 = analyze_sentence(sent2, lemmas2)

        for w in words1 + words2:
            stats["total_words"] += 1
            if w["has_lemma"]:
                stats["words_with_lemma"] += 1
                stats["total_lemmas_found"] += 1
            if w["has_concept_entry"]:
                stats["words_with_concept_entry"] += 1
                stats["unique_lemmas_with_entry"].add(w["lemma"])
            if w["has_category"]:
                stats["words_with_category"] += 1
                stats["unique_lemmas_with_category"].add(w["lemma"])
            if w["has_synonyms"]:
                stats["words_with_synonyms"] += 1
                stats["unique_lemmas_with_synonyms"].add(w["lemma"])
            if w["has_wn_entry"]:
                stats["words_with_wn_entry"] += 1
                stats["unique_lemmas_with_wn"].add(w["lemma"])

        for sent_words in [words1, words2]:
            sent_total = len(sent_words)
            sent_lemmas = sum(1 for w in sent_words if w["has_lemma"])
            sent_cats = sum(1 for w in sent_words if w["has_category"])
            sent_syns = sum(1 for w in sent_words if w["has_synonyms"])
            sent_wn = sum(1 for w in sent_words if w["has_wn_entry"])
            
            stats["sentence_word_counts"] += sent_total
            stats["sentence_lemma_counts"] += sent_lemmas
            stats["sentence_category_counts"] += sent_cats
            stats["sentence_synonym_counts"] += sent_syns
            stats["sentence_wn_counts"] += sent_wn
            stats["sentence_pct_lemma"] += (sent_lemmas / sent_total * 100) if sent_total > 0 else 0
            stats["sentence_pct_category"] += (sent_cats / sent_total * 100) if sent_total > 0 else 0
            stats["sentence_pct_synonyms"] += (sent_syns / sent_total * 100) if sent_total > 0 else 0
            stats["sentence_pct_wn"] += (sent_wn / sent_total * 100) if sent_total > 0 else 0
            stats["sentence_count"] += 1

            seen_words = set()
            seen_lemmas = set()
            seen_categories = set()
            seen_synonym_lemmas = set()
            seen_wn_lemmas = set()
            
            for w in sent_words:
                word_lower = w["word"].lower()
                if word_lower not in seen_words:
                    seen_words.add(word_lower)
                    if w["has_lemma"]:
                        seen_lemmas.add(w["lemma"].lower())
                    if w["has_category"]:
                        seen_categories.add(w["lemma"].lower())
                    if w["has_synonyms"]:
                        seen_synonym_lemmas.add(w["lemma"].lower())
                    if w["has_wn_entry"]:
                        seen_wn_lemmas.add(w["lemma"].lower())
            
            unique_total = len(seen_words)
            unique_lemmas = len(seen_lemmas)
            unique_cats = len(seen_categories)
            unique_syns = len(seen_synonym_lemmas)
            unique_wn = len(seen_wn_lemmas)
            
            stats["unique_words_total"] += unique_total
            stats["unique_lemma_total"] += unique_lemmas
            stats["unique_category_total"] += unique_cats
            stats["unique_synonym_total"] += unique_syns
            stats["unique_wn_total"] += unique_wn
            
            stats["unique_words_per_sentence"].append(unique_total)
            stats["unique_lemmas_per_sentence"].append(unique_lemmas)
            stats["unique_categories_per_sentence"].append(unique_cats)
            stats["unique_synonyms_per_sentence"].append(unique_syns)
            stats["unique_wn_per_sentence"].append(unique_wn)
            stats["unique_pct_lemma_per_sentence"].append((unique_lemmas / unique_total * 100) if unique_total > 0 else 0)
            stats["unique_pct_category_per_sentence"].append((unique_cats / unique_total * 100) if unique_total > 0 else 0)
            stats["unique_pct_synonyms_per_sentence"].append((unique_syns / unique_total * 100) if unique_total > 0 else 0)
            stats["unique_pct_wn_per_sentence"].append((unique_wn / unique_total * 100) if unique_total > 0 else 0)

        all_pairs.append({
            "sentence1": sent1,
            "sentence2": sent2,
            "score": score,
            "words1": words1,
            "words2": words2
        })

        if (i + 1) % 1000 == 0:
            print(f"Processed {i + 1}/{len(dataset)} pairs")

    print("\n=== STATISTICS ===")
    print(f"Total sentence pairs: {len(dataset)}")
    print(f"Total words analyzed: {stats['total_words']}")
    print(f"Words with lemma: {stats['words_with_lemma']} ({stats['words_with_lemma']/stats['total_words']*100:.1f}%)")
    print(f"Words with concept cache entry: {stats['words_with_concept_entry']} ({stats['words_with_concept_entry']/stats['total_words']*100:.1f}%)")
    print(f"Words with category (namespace): {stats['words_with_category']} ({stats['words_with_category']/stats['total_words']*100:.1f}%)")
    print(f"Words with synonyms: {stats['words_with_synonyms']} ({stats['words_with_synonyms']/stats['total_words']*100:.1f}%)")
    print(f"Words with WordNet entry: {stats['words_with_wn_entry']} ({stats['words_with_wn_entry']/stats['total_words']*100:.1f}%)")
    
    if stats['words_with_lemma'] > 0:
        print(f"\n--- CONDITIONAL (among words WITH lemma) ---")
        print(f"Words with concept entry: {stats['words_with_concept_entry']} ({stats['words_with_concept_entry']/stats['words_with_lemma']*100:.1f}%)")
        print(f"Words with category: {stats['words_with_category']} ({stats['words_with_category']/stats['words_with_lemma']*100:.1f}%)")
        print(f"Words with synonyms: {stats['words_with_synonyms']} ({stats['words_with_synonyms']/stats['words_with_lemma']*100:.1f}%)")
        print(f"Words with WordNet entry: {stats['words_with_wn_entry']} ({stats['words_with_wn_entry']/stats['words_with_lemma']*100:.1f}%)")

    print(f"\nUnique lemmas with concept entry: {len(stats['unique_lemmas_with_entry'])}")
    print(f"Unique lemmas with category: {len(stats['unique_lemmas_with_category'])}")
    print(f"Unique lemmas with synonyms: {len(stats['unique_lemmas_with_synonyms'])}")
    print(f"Unique lemmas with WordNet entry: {len(stats['unique_lemmas_with_wn'])}")

    all_seen_words = set()
    all_seen_lemmas = set()
    all_seen_categories = set()
    all_seen_synonym_lemmas = set()
    all_seen_wn_lemmas = set()
    
    for pair in all_pairs:
        for w in pair['words1'] + pair['words2']:
            word_lower = w["word"].lower()
            if word_lower not in all_seen_words:
                all_seen_words.add(word_lower)
                if w["has_lemma"]:
                    all_seen_lemmas.add(w["lemma"].lower())
                if w["has_category"]:
                    all_seen_categories.add(w["lemma"].lower())
                if w["has_synonyms"]:
                    all_seen_synonym_lemmas.add(w["lemma"].lower())
                if w["has_wn_entry"]:
                    all_seen_wn_lemmas.add(w["lemma"].lower())
    
    print(f"\n--- GLOBAL UNIQUE WORD STATISTICS (across dataset) ---")
    print(f"Unique word forms in dataset: {len(all_seen_words)}")
    print(f"Unique word forms with lemma: {len(all_seen_lemmas)} ({len(all_seen_lemmas)/len(all_seen_words)*100:.1f}%)")
    print(f"Unique word forms with category: {len(all_seen_categories)} ({len(all_seen_categories)/len(all_seen_words)*100:.1f}%)")
    print(f"Unique word forms with synonyms: {len(all_seen_synonym_lemmas)} ({len(all_seen_synonym_lemmas)/len(all_seen_words)*100:.1f}%)")
    print(f"Unique word forms with WordNet entry: {len(all_seen_wn_lemmas)} ({len(all_seen_wn_lemmas)/len(all_seen_words)*100:.1f}%)")

    print(f"\n--- PER-SENTENCE STATISTICS (ALL WORDS) ---")
    total_sentences = stats['sentence_count']
    if total_sentences > 0:
        avg_words = stats['sentence_word_counts'] / total_sentences
        avg_lemmas = stats['sentence_lemma_counts'] / total_sentences
        avg_categories = stats['sentence_category_counts'] / total_sentences
        avg_synonyms = stats['sentence_synonym_counts'] / total_sentences
        avg_wn = stats['sentence_wn_counts'] / total_sentences
        
        avg_pct_lemma = stats['sentence_pct_lemma'] / total_sentences
        avg_pct_category = stats['sentence_pct_category'] / total_sentences
        avg_pct_synonyms = stats['sentence_pct_synonyms'] / total_sentences
        avg_pct_wn = stats['sentence_pct_wn'] / total_sentences
        
        print(f"Sentences analyzed: {total_sentences}")
        print(f"Avg words per sentence: {avg_words:.1f}")
        print(f"Avg words with lemma per sentence: {avg_lemmas:.1f} ({avg_pct_lemma:.1f}%)")
        print(f"Avg words with category per sentence: {avg_categories:.1f} ({avg_pct_category:.1f}%)")
        print(f"Avg words with synonyms per sentence: {avg_synonyms:.1f} ({avg_pct_synonyms:.1f}%)")
        print(f"Avg words with WordNet entry per sentence: {avg_wn:.1f} ({avg_pct_wn:.1f}%)")

    print(f"\n--- PER-SENTENCE STATISTICS (UNIQUE WORDS) ---")
    if total_sentences > 0:
        avg_unique_words = stats['unique_words_total'] / total_sentences
        avg_unique_lemmas = stats['unique_lemma_total'] / total_sentences
        avg_unique_cats = stats['unique_category_total'] / total_sentences
        avg_unique_syns = stats['unique_synonym_total'] / total_sentences
        avg_unique_wn = stats['unique_wn_total'] / total_sentences
        
        avg_unique_pct_lemma = sum(stats['unique_pct_lemma_per_sentence']) / total_sentences
        avg_unique_pct_category = sum(stats['unique_pct_category_per_sentence']) / total_sentences
        avg_unique_pct_synonyms = sum(stats['unique_pct_synonyms_per_sentence']) / total_sentences
        avg_unique_pct_wn = sum(stats['unique_pct_wn_per_sentence']) / total_sentences
        
        print(f"Sentences analyzed: {total_sentences}")
        print(f"Avg unique words per sentence: {avg_unique_words:.1f}")
        print(f"Avg unique words with lemma per sentence: {avg_unique_lemmas:.1f} ({avg_unique_pct_lemma:.1f}%)")
        print(f"Avg unique words with category per sentence: {avg_unique_cats:.1f} ({avg_unique_pct_category:.1f}%)")
        print(f"Avg unique words with synonyms per sentence: {avg_unique_syns:.1f} ({avg_unique_pct_synonyms:.1f}%)")
        print(f"Avg unique words with WordNet entry per sentence: {avg_unique_wn:.1f} ({avg_unique_pct_wn:.1f}%)")

    print("\n=== SAMPLE OUTPUT (first 3 pairs) ===")
    for i, pair in enumerate(all_pairs[:3]):
        print(f"\nPair {i+1} (score: {pair['score']}):")
        print(f"  Sentence 1: {pair['sentence1']}")
        for w in pair['words1']:
            status = []
            if w["has_lemma"]: status.append(f"lemma={w['lemma']}")
            if w["has_concept_entry"]: status.append("concept_entry=yes")
            if w["has_category"]: status.append(f"category={w['category']}")
            if w["has_synonyms"]: status.append(f"synonyms={w['synonym_count']}")
            status_str = " | ".join(status) if status else "no lemma match"
            print(f"    {w['word']}: {status_str}")
        print(f"  Sentence 2: {pair['sentence2']}")
        for w in pair['words2']:
            status = []
            if w["has_lemma"]: status.append(f"lemma={w['lemma']}")
            if w["has_concept_entry"]: status.append("concept_entry=yes")
            if w["has_category"]: status.append(f"category={w['category']}")
            if w["has_synonyms"]: status.append(f"synonyms={w['synonym_count']}")
            status_str = " | ".join(status) if status else "no lemma match"
            print(f"    {w['word']}: {status_str}")

    output_file = "concept_coverage_analysis.json"
    serializable_pairs = []
    for pair in all_pairs:
        serializable_pairs.append({
            "sentence1": pair["sentence1"],
            "sentence2": pair["sentence2"],
            "score": pair["score"],
            "words1": [{k: v for k, v in w.items() if k != "synonyms"} for w in pair["words1"]],
            "words2": [{k: v for k, v in w.items() if k != "synonyms"} for w in pair["words2"]],
        })
    
    with open(output_file, "w", encoding="utf-8-sig") as f:
        json.dump(serializable_pairs, f, ensure_ascii=False, indent=2)
    print(f"\nSaved analysis to {output_file}")

    return all_pairs

if __name__ == "__main__":
    data = main()