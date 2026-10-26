import json
import csv
from collections import Counter, defaultdict
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

def main():
    dataset = load_dataset("sick_sk.txt")
    
    word_total_counts = Counter()
    word_sentence_counts = Counter()
    word_per_sentence_counts = defaultdict(list)
    
    word_lemma_map = {}
    word_cd_map = {}
    word_category_map = {}
    word_synonym_map = {}
    word_wn_map = {}

    total_words = 0
    total_sentences = 0

    for sent1, sent2, score in dataset:
        lemmas1 = lemma_cache.get(sent1, [])
        lemmas2 = lemma_cache.get(sent2, [])

        words1 = sent1.split()
        words2 = sent2.split()

        for sent_words, sent_lemmas in [(words1, lemmas1), (words2, lemmas2)]:
            total_sentences += 1
            seen_in_sentence = set()
            
            for word in sent_words:
                word_lower = word.lower()
                word_total_counts[word_lower] += 1
                total_words += 1
                
                if word_lower not in seen_in_sentence:
                    word_sentence_counts[word_lower] += 1
                    seen_in_sentence.add(word_lower)
                
                if word_lower not in word_lemma_map:
                    analysis = analyze_word(word, sent_lemmas)
                    word_lemma_map[word_lower] = analysis["lemma"]
                    word_cd_map[word_lower] = analysis["has_concept_entry"]
                    word_category_map[word_lower] = analysis["has_category"]
                    word_category_map[word_lower] = analysis["category"] if analysis["has_category"] else ""
                    word_synonym_map[word_lower] = analysis["has_synonyms"]
                    word_synonym_count_map = {}
                    word_synonym_count_map[word_lower] = analysis["synonym_count"]
                    word_wn_map[word_lower] = analysis["has_wn_entry"]
                    word_wn_synset_count = {}
                    word_wn_synset_count[word_lower] = analysis["wn_synset_count"]

            for word_lower in seen_in_sentence:
                word_per_sentence_counts[word_lower].append(1)

    rows = []
    for word, total_count in word_total_counts.most_common():
        sentence_count = word_sentence_counts[word]
        pct_of_total = round(total_count / total_words * 100, 4)
        pct_of_sentences = round(sentence_count / total_sentences * 100, 2)
        avg_per_sentence = round(total_count / sentence_count, 2) if sentence_count > 0 else 0
        avg_per_sentence_pct = round(avg_per_sentence / (total_words / total_sentences) * 100, 2) if total_words > 0 else 0
        
        lemma = word_lemma_map.get(word, "")
        has_lemma = bool(lemma)
        has_cd = word_cd_map.get(word, False)
        has_cat = word_category_map.get(word, False)
        category = word_category_map.get(word, "")
        has_syn = word_synonym_map.get(word, False)
        syn_count = word_synonym_count_map.get(word, 0) if 'word_synonym_count_map' in locals() else 0
        has_wn = word_wn_map.get(word, False)
        wn_count = word_wn_synset_count.get(word, 0) if 'word_wn_synset_count' in locals() else 0

        rows.append({
            "word": word,
            "total_occurrences": total_count,
            "pct_of_total_words": pct_of_total,
            "sentences_containing": sentence_count,
            "pct_of_sentences": pct_of_sentences,
            "avg_occurrences_per_sentence": avg_per_sentence,
            "avg_occurrences_per_sentence_pct": avg_per_sentence_pct,
            "lemma": lemma,
            "has_lemma": has_lemma,
            "has_concept_entry": has_cd,
            "has_category": has_cat,
            "category": category,
            "has_synonyms": has_syn,
            "synonym_count": syn_count,
            "has_wn_entry": has_wn,
            "wn_synset_count": wn_count
        })

    with open("word_occurrence_grid.csv", "w", newline="", encoding="utf-8-sig") as f:
        fieldnames = list(rows[0].keys())
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=";")
        writer.writeheader()
        writer.writerows(rows)

    print(f"Saved {len(rows)} unique words to word_occurrence_grid.csv")
    print(f"Total words in dataset: {total_words}")
    print(f"Total sentences: {total_sentences}")
    print(f"Unique word forms: {len(word_total_counts)}")

    # Also create a summary by frequency bins
    freq_bins = {
        "1": 0, "2-5": 0, "6-10": 0, "11-50": 0, "51-100": 0, "101-500": 0, "501+": 0
    }
    for word, count in word_total_counts.items():
        if count == 1:
            freq_bins["1"] += 1
        elif count <= 5:
            freq_bins["2-5"] += 1
        elif count <= 10:
            freq_bins["6-10"] += 1
        elif count <= 50:
            freq_bins["11-50"] += 1
        elif count <= 100:
            freq_bins["51-100"] += 1
        elif count <= 500:
            freq_bins["101-500"] += 1
        else:
            freq_bins["501+"] += 1

    summary_rows = []
    for bin_name, count in freq_bins.items():
        words_in_bin = [w for w, c in word_total_counts.items() 
                       if (bin_name == "1" and c == 1) or
                          (bin_name == "2-5" and 2 <= c <= 5) or
                          (bin_name == "6-10" and 6 <= c <= 10) or
                          (bin_name == "11-50" and 11 <= c <= 50) or
                          (bin_name == "51-100" and 51 <= c <= 100) or
                          (bin_name == "101-500" and 101 <= c <= 500) or
                          (bin_name == "501+" and c > 500)]
        total_occ = sum(word_total_counts[w] for w in words_in_bin)
        with_lemma = sum(1 for w in words_in_bin if word_lemma_map.get(w))
        with_cd = sum(1 for w in words_in_bin if word_cd_map.get(w, False))
        with_cat = sum(1 for w in words_in_bin if word_category_map.get(w, False))
        with_syn = sum(1 for w in words_in_bin if word_synonym_map.get(w, False))
        with_wn = sum(1 for w in words_in_bin if word_wn_map.get(w, False))
        
        summary_rows.append({
            "frequency_bin": bin_name,
            "unique_words": count,
            "total_occurrences": total_occ,
            "pct_of_unique_words": round(count / len(word_total_counts) * 100, 1),
            "pct_of_total_occurrences": round(total_occ / total_words * 100, 1),
            "words_with_lemma": with_lemma,
            "pct_with_lemma": round(with_lemma / count * 100, 1) if count > 0 else 0,
            "words_with_cd_entry": with_cd,
            "pct_with_cd_entry": round(with_cd / count * 100, 1) if count > 0 else 0,
            "words_with_category": with_cat,
            "pct_with_category": round(with_cat / count * 100, 1) if count > 0 else 0,
            "words_with_synonyms": with_syn,
            "pct_with_synonyms": round(with_syn / count * 100, 1) if count > 0 else 0,
            "words_with_wn_entry": with_wn,
            "pct_with_wn_entry": round(with_wn / count * 100, 1) if count > 0 else 0,
        })

    with open("word_frequency_bins.csv", "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=list(summary_rows[0].keys()), delimiter=";")
        writer.writeheader()
        writer.writerows(summary_rows)

    print(f"Saved frequency bin summary to word_frequency_bins.csv")

if __name__ == "__main__":
    main()