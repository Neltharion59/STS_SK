#!/usr/bin/env python
"""
Stopword analysis for Slovak SICK-SK dataset.
Counts absolute and ratio of stopwords for both unique words and total word tokens.
Uses combined stopword lists from:
- stopwords-iso (https://github.com/stopwords-iso/stopwords-sk) - 418 words
- stopwords-json (https://github.com/6/stopwords-json) - 110 words
Combined: 430 unique Slovak stopwords
"""

from dataset_utils import load_dataset
from collections import Counter
from pathlib import Path

def load_stopwords():
    """Load combined Slovak stopword list from file"""
    stopword_file = Path("slovak_stopwords_combined.txt")
    if stopword_file.exists():
        with open(stopword_file, "r", encoding="utf-8") as f:
            words = {line.strip() for line in f if line.strip()}
        print(f"Loaded {len(words)} Slovak stopwords from {stopword_file}")
        return words
    else:
        print(f"Warning: {stopword_file} not found, using empty set")
        return set()

ALL_STOPWORDS = load_stopwords()

def normalize_word(word):
    """Normalize word for comparison: lowercase, strip punctuation"""
    return word.lower().strip('.,;:!?()[]{}"\'–—')

def analyze():
    dataset = load_dataset("sick_sk.txt")
    
    total_tokens = 0
    total_stopwords = 0
    unique_tokens = set()
    unique_stopwords = set()
    
    word_freq = Counter()
    
    for sent1, sent2, score in dataset:
        for sentence in [sent1, sent2]:
            words = sentence.split()
            for word in words:
                norm = normalize_word(word)
                total_tokens += 1
                word_freq[norm] += 1
                unique_tokens.add(norm)
                
                if norm in ALL_STOPWORDS:
                    total_stopwords += 1
                    unique_stopwords.add(norm)
    
    unique_total = len(unique_tokens)
    unique_sw_count = len(unique_stopwords)
    
    print("=" * 60)
    print("SLOVAK STOPWORD ANALYSIS - SICK-SK Dataset")
    print("=" * 60)
    print(f"\nStopword list size: {len(ALL_STOPWORDS)}")
    print(f"\n--- TOTAL WORD TOKENS ---")
    print(f"Total tokens: {total_tokens:,}")
    print(f"Stopword tokens: {total_stopwords:,}")
    print(f"Stopword ratio: {total_stopwords/total_tokens*100:.2f}%")
    print(f"Non-stopword tokens: {total_tokens - total_stopwords:,} ({(total_tokens - total_stopwords)/total_tokens*100:.2f}%)")
    
    print(f"\n--- UNIQUE WORD FORMS ---")
    print(f"Unique word forms: {unique_total:,}")
    print(f"Unique stopwords: {unique_sw_count:,}")
    print(f"Stopword ratio: {unique_sw_count/unique_total*100:.2f}%")
    print(f"Unique non-stopwords: {unique_total - unique_sw_count:,} ({(unique_total - unique_sw_count)/unique_total*100:.2f}%)")
    
    print(f"\n--- TOP 20 MOST FREQUENT STOPWORDS ---")
    sw_freq = [(w, c) for w, c in word_freq.most_common() if w in ALL_STOPWORDS]
    for word, count in sw_freq[:20]:
        pct = count / total_tokens * 100
        safe_word = word.encode('ascii', 'replace').decode('ascii')
        print(f"  {safe_word:15s} {count:6d} ({pct:.2f}%)")
    
    print(f"\n--- TOP 20 MOST FREQUENT NON-STOPWORDS ---")
    nsw_freq = [(w, c) for w, c in word_freq.most_common() if w not in ALL_STOPWORDS]
    for word, count in nsw_freq[:20]:
        pct = count / total_tokens * 100
        safe_word = word.encode('ascii', 'replace').decode('ascii')
        print(f"  {safe_word:15s} {count:6d} ({pct:.2f}%)")
    
    # Save to CSV
    with open("stopword_analysis.csv", "w", newline="", encoding="utf-8-sig") as f:
        f.write("metric;total_tokens;unique_forms\n")
        f.write(f"total_tokens;{total_tokens};{unique_total}\n")
        f.write(f"stopword_tokens;{total_stopwords};{unique_sw_count}\n")
        f.write(f"stopword_ratio_pct;{total_stopwords/total_tokens*100:.2f};{unique_sw_count/unique_total*100:.2f}\n")
        f.write(f"non_stopword_tokens;{total_tokens - total_stopwords};{unique_total - unique_sw_count}\n")
        f.write(f"non_stopword_ratio_pct;{(total_tokens - total_stopwords)/total_tokens*100:.2f};{(unique_total - unique_sw_count)/unique_total*100:.2f}\n")
    
    print(f"\nSaved to stopword_analysis.csv")
    
    # Also list stopwords found in data
    found_stopwords = sorted([w for w in unique_tokens if w in ALL_STOPWORDS])
    safe_found = [w.encode('ascii', 'replace').decode('ascii') for w in found_stopwords]
    print(f"\nStopwords found in dataset ({len(found_stopwords)}):")
    print(", ".join(safe_found))
    
    # List stopwords NOT found
    not_found = sorted(ALL_STOPWORDS - unique_tokens)
    safe_not_found = [w.encode('ascii', 'replace').decode('ascii') for w in not_found]
    print(f"\nStopwords from list NOT in dataset ({len(not_found)}):")
    print(", ".join(safe_not_found))

if __name__ == "__main__":
    analyze()