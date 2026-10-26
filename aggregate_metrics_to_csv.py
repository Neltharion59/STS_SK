import json
import csv
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

def analyze_sentence(sentence, sentence_lemmas):
    words = sentence.split()
    return [analyze_word(word, sentence_lemmas) for word in words]

def main():
    dataset = load_dataset("sick_sk.txt")
    
    stats = {
        "total_words": 0,
        "words_with_lemma": 0,
        "words_with_concept_entry": 0,
        "words_with_category": 0,
        "words_with_synonyms": 0,
        "words_with_wn_entry": 0,
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
        "unique_words_total": 0,
        "unique_lemma_total": 0,
        "unique_category_total": 0,
        "unique_synonym_total": 0,
        "unique_wn_total": 0,
        "unique_pct_lemma_per_sentence": [],
        "unique_pct_category_per_sentence": [],
        "unique_pct_synonyms_per_sentence": [],
        "unique_pct_wn_per_sentence": [],
        "sentences_with_lemma": 0,
        "sentences_with_cd_entry": 0,
        "sentences_with_category": 0,
        "sentences_with_synonyms": 0,
        "sentences_with_wn_entry": 0,
        "sentences_with_cd_or_wn_entry": 0,
        "pairs_with_lemma_both": 0,
        "pairs_with_cd_entry_both": 0,
        "pairs_with_category_both": 0,
        "pairs_with_synonyms_both": 0,
        "pairs_with_wn_entry_both": 0,
        "pairs_with_cd_or_wn_both": 0,
    }

    all_seen_words = set()
    all_seen_lemmas = set()
    all_seen_categories = set()
    all_seen_synonym_lemmas = set()
    all_seen_wn_lemmas = set()

    for sent1, sent2, score in dataset:
        lemmas1 = lemma_cache.get(sent1, [])
        lemmas2 = lemma_cache.get(sent2, [])

        words1 = analyze_sentence(sent1, lemmas1)
        words2 = analyze_sentence(sent2, lemmas2)

        for w in words1 + words2:
            stats["total_words"] += 1
            if w["has_lemma"]:
                stats["words_with_lemma"] += 1
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

        sent1_lemmas = sum(1 for w in words1 if w["has_lemma"])
        sent1_cd = any(w["has_concept_entry"] for w in words1)
        sent1_cat = any(w["has_category"] for w in words1)
        sent1_syn = any(w["has_synonyms"] for w in words1)
        sent1_wn = any(w["has_wn_entry"] for w in words1)

        sent2_lemmas = sum(1 for w in words2 if w["has_lemma"])
        sent2_cd = any(w["has_concept_entry"] for w in words2)
        sent2_cat = any(w["has_category"] for w in words2)
        sent2_syn = any(w["has_synonyms"] for w in words2)
        sent2_wn = any(w["has_wn_entry"] for w in words2)

        for sent_words, sent_lemmas, sent_cd, sent_cat, sent_syn, sent_wn in [
            (words1, sent1_lemmas, sent1_cd, sent1_cat, sent1_syn, sent1_wn),
            (words2, sent2_lemmas, sent2_cd, sent2_cat, sent2_syn, sent2_wn),
        ]:
            sent_total = len(sent_words)
            sent_cats = sum(1 for w in sent_words if w["has_category"])
            sent_syns = sum(1 for w in sent_words if w["has_synonyms"])
            sent_wn_count = sum(1 for w in sent_words if w["has_wn_entry"])
            
            stats["sentence_word_counts"] += sent_total
            stats["sentence_lemma_counts"] += sent_lemmas
            stats["sentence_category_counts"] += sent_cats
            stats["sentence_synonym_counts"] += sent_syns
            stats["sentence_wn_counts"] += sent_wn_count
            stats["sentence_pct_lemma"] += (sent_lemmas / sent_total * 100) if sent_total > 0 else 0
            stats["sentence_pct_category"] += (sent_cats / sent_total * 100) if sent_total > 0 else 0
            stats["sentence_pct_synonyms"] += (sent_syns / sent_total * 100) if sent_total > 0 else 0
            stats["sentence_pct_wn"] += (sent_wn_count / sent_total * 100) if sent_total > 0 else 0
            stats["sentence_count"] += 1

            if sent_lemmas > 0:
                stats["sentences_with_lemma"] += 1
            if sent_cd:
                stats["sentences_with_cd_entry"] += 1
            if sent_cats > 0:
                stats["sentences_with_category"] += 1
            if sent_syns > 0:
                stats["sentences_with_synonyms"] += 1
            if sent_wn:
                stats["sentences_with_wn_entry"] += 1
            if sent_cd or sent_wn:
                stats["sentences_with_cd_or_wn_entry"] += 1

        # Pair-level metrics (both sentences must have hit)
        if sent1_lemmas > 0 and sent2_lemmas > 0:
            stats["pairs_with_lemma_both"] += 1
        if sent1_cd and sent2_cd:
            stats["pairs_with_cd_entry_both"] += 1
        if sent1_cat and sent2_cat:
            stats["pairs_with_category_both"] += 1
        if sent1_syn and sent2_syn:
            stats["pairs_with_synonyms_both"] += 1
        if sent1_wn and sent2_wn:
            stats["pairs_with_wn_entry_both"] += 1
        if (sent1_cd or sent1_wn) and (sent2_cd or sent2_wn):
            stats["pairs_with_cd_or_wn_both"] += 1

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
            
            stats["unique_pct_lemma_per_sentence"].append((unique_lemmas / unique_total * 100) if unique_total > 0 else 0)
            stats["unique_pct_category_per_sentence"].append((unique_cats / unique_total * 100) if unique_total > 0 else 0)
            stats["unique_pct_synonyms_per_sentence"].append((unique_syns / unique_total * 100) if unique_total > 0 else 0)
            stats["unique_pct_wn_per_sentence"].append((unique_wn / unique_total * 100) if unique_total > 0 else 0)

            for w in sent_words:
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

    total_sentences = stats['sentence_count']
    
    rows = []
    
    # Overall metrics (all words)
    rows.append({
        "metric_group": "overall_all_words",
        "metric": "total_sentence_pairs",
        "value": len(dataset),
        "unit": "count"
    })
    rows.append({
        "metric_group": "overall_all_words",
        "metric": "total_words",
        "value": stats["total_words"],
        "unit": "count"
    })
    rows.append({
        "metric_group": "overall_all_words",
        "metric": "words_with_lemma",
        "value": stats["words_with_lemma"],
        "unit": "count"
    })
    rows.append({
        "metric_group": "overall_all_words",
        "metric": "words_with_lemma_pct",
        "value": round(stats["words_with_lemma"] / stats["total_words"] * 100, 1),
        "unit": "percent"
    })
    rows.append({
        "metric_group": "overall_all_words",
        "metric": "words_with_concept_entry",
        "value": stats["words_with_concept_entry"],
        "unit": "count"
    })
    rows.append({
        "metric_group": "overall_all_words",
        "metric": "words_with_concept_entry_pct",
        "value": round(stats["words_with_concept_entry"] / stats["total_words"] * 100, 1),
        "unit": "percent"
    })
    rows.append({
        "metric_group": "overall_all_words",
        "metric": "words_with_category",
        "value": stats["words_with_category"],
        "unit": "count"
    })
    rows.append({
        "metric_group": "overall_all_words",
        "metric": "words_with_category_pct",
        "value": round(stats["words_with_category"] / stats["total_words"] * 100, 1),
        "unit": "percent"
    })
    rows.append({
        "metric_group": "overall_all_words",
        "metric": "words_with_synonyms",
        "value": stats["words_with_synonyms"],
        "unit": "count"
    })
    rows.append({
        "metric_group": "overall_all_words",
        "metric": "words_with_synonyms_pct",
        "value": round(stats["words_with_synonyms"] / stats["total_words"] * 100, 1),
        "unit": "percent"
    })
    rows.append({
        "metric_group": "overall_all_words",
        "metric": "words_with_wn_entry",
        "value": stats["words_with_wn_entry"],
        "unit": "count"
    })
    rows.append({
        "metric_group": "overall_all_words",
        "metric": "words_with_wn_entry_pct",
        "value": round(stats["words_with_wn_entry"] / stats["total_words"] * 100, 1),
        "unit": "percent"
    })

    # Sentence-level hit metrics
    total_sentences = stats['sentence_count']
    if total_sentences > 0:
        rows.append({
            "metric_group": "sentence_hit_rates",
            "metric": "sentences_total",
            "value": total_sentences,
            "unit": "count"
        })
        rows.append({
            "metric_group": "sentence_hit_rates",
            "metric": "sentences_with_lemma",
            "value": stats["sentences_with_lemma"],
            "unit": "count"
        })
        rows.append({
            "metric_group": "sentence_hit_rates",
            "metric": "sentences_with_lemma_pct",
            "value": round(stats["sentences_with_lemma"] / total_sentences * 100, 1),
            "unit": "percent"
        })
        rows.append({
            "metric_group": "sentence_hit_rates",
            "metric": "sentences_with_cd_entry",
            "value": stats["sentences_with_cd_entry"],
            "unit": "count"
        })
        rows.append({
            "metric_group": "sentence_hit_rates",
            "metric": "sentences_with_cd_entry_pct",
            "value": round(stats["sentences_with_cd_entry"] / total_sentences * 100, 1),
            "unit": "percent"
        })
        rows.append({
            "metric_group": "sentence_hit_rates",
            "metric": "sentences_with_category",
            "value": stats["sentences_with_category"],
            "unit": "count"
        })
        rows.append({
            "metric_group": "sentence_hit_rates",
            "metric": "sentences_with_category_pct",
            "value": round(stats["sentences_with_category"] / total_sentences * 100, 1),
            "unit": "percent"
        })
        rows.append({
            "metric_group": "sentence_hit_rates",
            "metric": "sentences_with_synonyms",
            "value": stats["sentences_with_synonyms"],
            "unit": "count"
        })
        rows.append({
            "metric_group": "sentence_hit_rates",
            "metric": "sentences_with_synonyms_pct",
            "value": round(stats["sentences_with_synonyms"] / total_sentences * 100, 1),
            "unit": "percent"
        })
        rows.append({
            "metric_group": "sentence_hit_rates",
            "metric": "sentences_with_wn_entry",
            "value": stats["sentences_with_wn_entry"],
            "unit": "count"
        })
        rows.append({
            "metric_group": "sentence_hit_rates",
            "metric": "sentences_with_wn_entry_pct",
            "value": round(stats["sentences_with_wn_entry"] / total_sentences * 100, 1),
            "unit": "percent"
        })
        rows.append({
            "metric_group": "sentence_hit_rates",
            "metric": "sentences_with_cd_or_wn_entry",
            "value": stats["sentences_with_cd_or_wn_entry"],
            "unit": "count"
        })
        rows.append({
            "metric_group": "sentence_hit_rates",
            "metric": "sentences_with_cd_or_wn_entry_pct",
            "value": round(stats["sentences_with_cd_or_wn_entry"] / total_sentences * 100, 1),
            "unit": "percent"
        })

        # Pair-level hit metrics (both sentences in pair have hit)
        total_pairs = len(dataset)
        rows.append({
            "metric_group": "pair_hit_rates",
            "metric": "pairs_total",
            "value": total_pairs,
            "unit": "count"
        })
        rows.append({
            "metric_group": "pair_hit_rates",
            "metric": "pairs_with_lemma_both",
            "value": stats["pairs_with_lemma_both"],
            "unit": "count"
        })
        rows.append({
            "metric_group": "pair_hit_rates",
            "metric": "pairs_with_lemma_both_pct",
            "value": round(stats["pairs_with_lemma_both"] / total_pairs * 100, 1),
            "unit": "percent"
        })
        rows.append({
            "metric_group": "pair_hit_rates",
            "metric": "pairs_with_cd_entry_both",
            "value": stats["pairs_with_cd_entry_both"],
            "unit": "count"
        })
        rows.append({
            "metric_group": "pair_hit_rates",
            "metric": "pairs_with_cd_entry_both_pct",
            "value": round(stats["pairs_with_cd_entry_both"] / total_pairs * 100, 1),
            "unit": "percent"
        })
        rows.append({
            "metric_group": "pair_hit_rates",
            "metric": "pairs_with_category_both",
            "value": stats["pairs_with_category_both"],
            "unit": "count"
        })
        rows.append({
            "metric_group": "pair_hit_rates",
            "metric": "pairs_with_category_both_pct",
            "value": round(stats["pairs_with_category_both"] / total_pairs * 100, 1),
            "unit": "percent"
        })
        rows.append({
            "metric_group": "pair_hit_rates",
            "metric": "pairs_with_synonyms_both",
            "value": stats["pairs_with_synonyms_both"],
            "unit": "count"
        })
        rows.append({
            "metric_group": "pair_hit_rates",
            "metric": "pairs_with_synonyms_both_pct",
            "value": round(stats["pairs_with_synonyms_both"] / total_pairs * 100, 1),
            "unit": "percent"
        })
        rows.append({
            "metric_group": "pair_hit_rates",
            "metric": "pairs_with_wn_entry_both",
            "value": stats["pairs_with_wn_entry_both"],
            "unit": "count"
        })
        rows.append({
            "metric_group": "pair_hit_rates",
            "metric": "pairs_with_wn_entry_both_pct",
            "value": round(stats["pairs_with_wn_entry_both"] / total_pairs * 100, 1),
            "unit": "percent"
        })
        rows.append({
            "metric_group": "pair_hit_rates",
            "metric": "pairs_with_cd_or_wn_both",
            "value": stats["pairs_with_cd_or_wn_both"],
            "unit": "count"
        })
        rows.append({
            "metric_group": "pair_hit_rates",
            "metric": "pairs_with_cd_or_wn_both_pct",
            "value": round(stats["pairs_with_cd_or_wn_both"] / total_pairs * 100, 1),
            "unit": "percent"
        })

    # Conditional metrics (given lemma) - ALL WORDS
    if stats["words_with_lemma"] > 0:
        rows.append({
            "metric_group": "conditional_given_lemma_all_words",
            "metric": "concept_entry_given_lemma_pct",
            "value": round(stats["words_with_concept_entry"] / stats["words_with_lemma"] * 100, 1),
            "unit": "percent"
        })
        rows.append({
            "metric_group": "conditional_given_lemma_all_words",
            "metric": "category_given_lemma_pct",
            "value": round(stats["words_with_category"] / stats["words_with_lemma"] * 100, 1),
            "unit": "percent"
        })
        rows.append({
            "metric_group": "conditional_given_lemma_all_words",
            "metric": "synonyms_given_lemma_pct",
            "value": round(stats["words_with_synonyms"] / stats["words_with_lemma"] * 100, 1),
            "unit": "percent"
        })
        rows.append({
            "metric_group": "conditional_given_lemma_all_words",
            "metric": "wn_entry_given_lemma_pct",
            "value": round(stats["words_with_wn_entry"] / stats["words_with_lemma"] * 100, 1),
            "unit": "percent"
        })

    # Conditional metrics (given lemma) - UNIQUE WORD FORMS (global)
    if len(all_seen_lemmas) > 0:
        rows.append({
            "metric_group": "conditional_given_lemma_unique_words",
            "metric": "concept_entry_given_lemma_pct",
            "value": round(len(all_seen_lemmas) / len(all_seen_lemmas) * 100, 1),
            "unit": "percent"
        })
        rows.append({
            "metric_group": "conditional_given_lemma_unique_words",
            "metric": "category_given_lemma_pct",
            "value": round(len(all_seen_categories) / len(all_seen_lemmas) * 100, 1),
            "unit": "percent"
        })
        rows.append({
            "metric_group": "conditional_given_lemma_unique_words",
            "metric": "synonyms_given_lemma_pct",
            "value": round(len(all_seen_synonym_lemmas) / len(all_seen_lemmas) * 100, 1),
            "unit": "percent"
        })
        rows.append({
            "metric_group": "conditional_given_lemma_unique_words",
            "metric": "wn_entry_given_lemma_pct",
            "value": round(len(all_seen_wn_lemmas) / len(all_seen_lemmas) * 100, 1),
            "unit": "percent"
        })

    # Unique lemmas (global)
    rows.append({
        "metric_group": "unique_lemmas_global",
        "metric": "unique_lemmas_with_concept_entry",
        "value": len(stats["unique_lemmas_with_entry"]),
        "unit": "count"
    })
    rows.append({
        "metric_group": "unique_lemmas_global",
        "metric": "unique_lemmas_with_category",
        "value": len(stats["unique_lemmas_with_category"]),
        "unit": "count"
    })
    rows.append({
        "metric_group": "unique_lemmas_global",
        "metric": "unique_lemmas_with_synonyms",
        "value": len(stats["unique_lemmas_with_synonyms"]),
        "unit": "count"
    })
    rows.append({
        "metric_group": "unique_lemmas_global",
        "metric": "unique_lemmas_with_wn_entry",
        "value": len(stats["unique_lemmas_with_wn"]),
        "unit": "count"
    })

    # Global unique word forms
    rows.append({
        "metric_group": "unique_word_forms_global",
        "metric": "unique_word_forms_total",
        "value": len(all_seen_words),
        "unit": "count"
    })
    rows.append({
        "metric_group": "unique_word_forms_global",
        "metric": "unique_word_forms_with_lemma",
        "value": len(all_seen_lemmas),
        "unit": "count"
    })
    rows.append({
        "metric_group": "unique_word_forms_global",
        "metric": "unique_word_forms_with_lemma_pct",
        "value": round(len(all_seen_lemmas) / len(all_seen_words) * 100, 1),
        "unit": "percent"
    })
    rows.append({
        "metric_group": "unique_word_forms_global",
        "metric": "unique_word_forms_with_category",
        "value": len(all_seen_categories),
        "unit": "count"
    })
    rows.append({
        "metric_group": "unique_word_forms_global",
        "metric": "unique_word_forms_with_category_pct",
        "value": round(len(all_seen_categories) / len(all_seen_words) * 100, 1),
        "unit": "percent"
    })
    rows.append({
        "metric_group": "unique_word_forms_global",
        "metric": "unique_word_forms_with_synonyms",
        "value": len(all_seen_synonym_lemmas),
        "unit": "count"
    })
    rows.append({
        "metric_group": "unique_word_forms_global",
        "metric": "unique_word_forms_with_synonyms_pct",
        "value": round(len(all_seen_synonym_lemmas) / len(all_seen_words) * 100, 1),
        "unit": "percent"
    })
    rows.append({
        "metric_group": "unique_word_forms_global",
        "metric": "unique_word_forms_with_wn_entry",
        "value": len(all_seen_wn_lemmas),
        "unit": "count"
    })
    rows.append({
        "metric_group": "unique_word_forms_global",
        "metric": "unique_word_forms_with_wn_entry_pct",
        "value": round(len(all_seen_wn_lemmas) / len(all_seen_words) * 100, 1),
        "unit": "percent"
    })

    # Per-sentence averages (all words)
    if total_sentences > 0:
        rows.append({
            "metric_group": "per_sentence_all_words",
            "metric": "sentences_analyzed",
            "value": total_sentences,
            "unit": "count"
        })
        rows.append({
            "metric_group": "per_sentence_all_words",
            "metric": "avg_words_per_sentence",
            "value": round(stats["sentence_word_counts"] / total_sentences, 1),
            "unit": "count"
        })
        rows.append({
            "metric_group": "per_sentence_all_words",
            "metric": "avg_words_with_lemma_per_sentence",
            "value": round(stats["sentence_lemma_counts"] / total_sentences, 1),
            "unit": "count"
        })
        rows.append({
            "metric_group": "per_sentence_all_words",
            "metric": "avg_words_with_lemma_pct",
            "value": round(stats["sentence_pct_lemma"] / total_sentences, 1),
            "unit": "percent"
        })
        rows.append({
            "metric_group": "per_sentence_all_words",
            "metric": "avg_words_with_category_per_sentence",
            "value": round(stats["sentence_category_counts"] / total_sentences, 1),
            "unit": "count"
        })
        rows.append({
            "metric_group": "per_sentence_all_words",
            "metric": "avg_words_with_category_pct",
            "value": round(stats["sentence_pct_category"] / total_sentences, 1),
            "unit": "percent"
        })
        rows.append({
            "metric_group": "per_sentence_all_words",
            "metric": "avg_words_with_synonyms_per_sentence",
            "value": round(stats["sentence_synonym_counts"] / total_sentences, 1),
            "unit": "count"
        })
        rows.append({
            "metric_group": "per_sentence_all_words",
            "metric": "avg_words_with_synonyms_pct",
            "value": round(stats["sentence_pct_synonyms"] / total_sentences, 1),
            "unit": "percent"
        })
        rows.append({
            "metric_group": "per_sentence_all_words",
            "metric": "avg_words_with_wn_entry_per_sentence",
            "value": round(stats["sentence_wn_counts"] / total_sentences, 1),
            "unit": "count"
        })
        rows.append({
            "metric_group": "per_sentence_all_words",
            "metric": "avg_words_with_wn_entry_pct",
            "value": round(stats["sentence_pct_wn"] / total_sentences, 1),
            "unit": "percent"
        })

    # Per-sentence averages (unique words)
    if total_sentences > 0:
        rows.append({
            "metric_group": "per_sentence_unique_words",
            "metric": "sentences_analyzed",
            "value": total_sentences,
            "unit": "count"
        })
        rows.append({
            "metric_group": "per_sentence_unique_words",
            "metric": "avg_unique_words_per_sentence",
            "value": round(stats["unique_words_total"] / total_sentences, 1),
            "unit": "count"
        })
        rows.append({
            "metric_group": "per_sentence_unique_words",
            "metric": "avg_unique_words_with_lemma_per_sentence",
            "value": round(stats["unique_lemma_total"] / total_sentences, 1),
            "unit": "count"
        })
        rows.append({
            "metric_group": "per_sentence_unique_words",
            "metric": "avg_unique_words_with_lemma_pct",
            "value": round(sum(stats["unique_pct_lemma_per_sentence"]) / total_sentences, 1),
            "unit": "percent"
        })
        rows.append({
            "metric_group": "per_sentence_unique_words",
            "metric": "avg_unique_words_with_category_per_sentence",
            "value": round(stats["unique_category_total"] / total_sentences, 1),
            "unit": "count"
        })
        rows.append({
            "metric_group": "per_sentence_unique_words",
            "metric": "avg_unique_words_with_category_pct",
            "value": round(sum(stats["unique_pct_category_per_sentence"]) / total_sentences, 1),
            "unit": "percent"
        })
        rows.append({
            "metric_group": "per_sentence_unique_words",
            "metric": "avg_unique_words_with_synonyms_per_sentence",
            "value": round(stats["unique_synonym_total"] / total_sentences, 1),
            "unit": "count"
        })
        rows.append({
            "metric_group": "per_sentence_unique_words",
            "metric": "avg_unique_words_with_synonyms_pct",
            "value": round(sum(stats["unique_pct_synonyms_per_sentence"]) / total_sentences, 1),
            "unit": "percent"
        })
        rows.append({
            "metric_group": "per_sentence_unique_words",
            "metric": "avg_unique_words_with_wn_entry_per_sentence",
            "value": round(stats["unique_wn_total"] / total_sentences, 1),
            "unit": "count"
        })
        rows.append({
            "metric_group": "per_sentence_unique_words",
            "metric": "avg_unique_words_with_wn_entry_pct",
            "value": round(sum(stats["unique_pct_wn_per_sentence"]) / total_sentences, 1),
            "unit": "percent"
        })

    # Comparison: Concept Dictionary vs WordNet
    rows.append({
        "metric_group": "comparison_cd_vs_wn",
        "metric": "cd_words_with_entry",
        "value": stats["words_with_concept_entry"],
        "unit": "count"
    })
    rows.append({
        "metric_group": "comparison_cd_vs_wn",
        "metric": "wn_words_with_entry",
        "value": stats["words_with_wn_entry"],
        "unit": "count"
    })
    rows.append({
        "metric_group": "comparison_cd_vs_wn",
        "metric": "cd_unique_lemmas",
        "value": len(stats["unique_lemmas_with_entry"]),
        "unit": "count"
    })
    rows.append({
        "metric_group": "comparison_cd_vs_wn",
        "metric": "wn_unique_lemmas",
        "value": len(stats["unique_lemmas_with_wn"]),
        "unit": "count"
    })
    rows.append({
        "metric_group": "comparison_cd_vs_wn",
        "metric": "cd_unique_word_forms",
        "value": len(all_seen_lemmas),
        "unit": "count"
    })
    rows.append({
        "metric_group": "comparison_cd_vs_wn",
        "metric": "wn_unique_word_forms",
        "value": len(all_seen_wn_lemmas),
        "unit": "count"
    })
    if stats["words_with_lemma"] > 0:
        rows.append({
            "metric_group": "comparison_cd_vs_wn",
            "metric": "cd_coverage_given_lemma_pct",
            "value": round(stats["words_with_concept_entry"] / stats["words_with_lemma"] * 100, 1),
            "unit": "percent"
        })
        rows.append({
            "metric_group": "comparison_cd_vs_wn",
            "metric": "wn_coverage_given_lemma_pct",
            "value": round(stats["words_with_wn_entry"] / stats["words_with_lemma"] * 100, 1),
            "unit": "percent"
        })

    with open("coverage_metrics_summary.csv", "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=["metric_group", "metric", "value", "unit"], delimiter=";")
        writer.writeheader()
        writer.writerows(rows)

    print(f"Saved {len(rows)} metrics to coverage_metrics_summary.csv")

if __name__ == "__main__":
    main()