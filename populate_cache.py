"""
Pre-populate lemma and concept caches for SKLEP dataset.

This script iterates over the SKLEP dataset and:
1. Extracts lemmas for both sentences in each pair (populates lemma_cache.json)
2. Fetches concept data for all unique lemmas (populates concept_cache.json)
3. Builds trees for all word pairs to ensure complete cache coverage

This reduces API calls during actual experiments by pre-caching all required data.
"""

import json
import os
from api_utils import get_sentence_lemmas, build_tree_from_concepts

def load_sklep_dataset(filepath):
    """Load SKLEP dataset from JSON file."""
    data = []
    with open(filepath, "r", encoding="utf-8-sig") as f:
        for line in f:
            entry = json.loads(line.strip())
            data.append((
                entry["sentence1"],
                entry["sentence2"],
                float(entry["similarity_score"])
            ))
    return data

def populate_caches(dataset):
    """
    Populate lemma and concept caches for all sentence pairs.
    
    Args:
        dataset: List of (sentence1, sentence2, score) tuples
    """
    total = len(dataset)
    
    for i, (sentence1, sentence2, score) in enumerate(dataset):
        print(f"Processing {i+1}/{total} (score: {score})")

        # Step 1: Get lemmas for both sentences (populates lemma_cache)
        print(f"  Extracting lemmas for sentence 1...")
        lemmas1 = get_sentence_lemmas(sentence1)
        print(f"    Found {len(lemmas1)} lemmas: {lemmas1}")
        
        print(f"  Extracting lemmas for sentence 2...")
        lemmas2 = get_sentence_lemmas(sentence2)
        print(f"    Found {len(lemmas2)} lemmas: {lemmas2}")
        
        # Step 2: Build tree from all unique lemmas (populates concept_cache)
        all_lemmas = list(set(lemmas1 + lemmas2))
        
        if all_lemmas:
            print(f"  Building tree for {len(all_lemmas)} unique lemmas...")
            root = build_tree_from_concepts(all_lemmas)
            print(f"    Tree built with {root.count_nodes()} nodes")
        else:
            print(f"  No lemmas to process for this pair")
        
        print()

def main():
    """Main execution function."""
    print("=" * 60)
    print("SKLEP Dataset Cache Population Script")
    print("=" * 60)
    print()
    
    # Ensure cache directories exist
    os.makedirs("caches/endpoint_caches", exist_ok=True)
    print("Cache directories verified")
    print()
    
    # Load dataset
    print("Loading SKLEP dataset from sklep.json...")
    dataset = load_sklep_dataset("sklep.json")
    print(f"Loaded {len(dataset)} sentence pairs")
    print()
    
    # Populate caches
    print("Starting cache population...")
    print("This will take time due to API rate limiting (0.5s per concept)")
    print()
    
    populate_caches(dataset)
    
    print()
    print("=" * 60)
    print("Cache population complete!")
    print("=" * 60)
    print()
    print("Cache files updated:")
    print("  - lemma_cache.json (processed lemmas per sentence)")
    print("  - concept_cache.json (concept data per lemma)")
    print("  - caches/endpoint_caches/cache_extractor.json (raw API responses)")
    print("  - missing_lemmas.csv (lemmas without concepts, if any)")

if __name__ == "__main__":
    main()
