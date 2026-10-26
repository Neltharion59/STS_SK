# AGENTS.md

This file provides guidance to agents when working with code in this repository.

## Critical Non-Obvious Patterns

### API Authentication & Caching
- **Credentials file required**: Create `udaje.txt` with format `email password` (space-separated, single line) - not documented in code comments
- **Cache files are UTF-8-sig encoded**: All JSON cache files (`concept_cache.json`, `lemma_cache.json`) use `utf-8-sig` encoding, not standard `utf-8`
- **Global token state**: `api_utils.py` uses module-level `token` variable that persists across imports
- **API rate limiting**: Hard-coded 0.5s sleep in `get_concept_data()` before each API call (line 149)
- **Missing lemmas tracking**: Lemmas without concepts are logged to `missing_lemmas.csv` and tracked in global `missing_lemmas` set to avoid duplicate logging

### Tree Building & Similarity
- **Namespace fallback logic**: When building trees, namespace is extracted from `typeOf[0]` first, then falls back to `synonymum[0]`, then defaults to "Nezaradené" (not "Unknown" or "Uncategorized")
- **Circular reference prevention**: `Node.add_child()` walks up parent chain to prevent cycles before adding child (lines 10-14 in tree.py)
- **Power parameter format**: Power values are strings like "power7", not integers - extracted via `int(power.replace("power", ""))` in `exponentiate_score()`
- **Local vs global power scope**: `power_scope="local"` applies exponentiation to individual scores before aggregation; `"global"` applies after aggregation

### Dataset & Evaluation
- **Dataset format**: Tab-separated with score in column 0, sentence1 in column 1, sentence2 in column 2 (not typical CSV)
- **Stratified split uses composite labels**: Combines score bucket + length bucket + name bucket as single stratification key (e.g., "3_medium_1")
- **Score scaling for metrics**: Model scores (0-1 range) are scaled to 1-5 via `1 + s * 4` for MAE/MSE/RMSE calculations in `final_test.py`
- **Pearson results delimiter**: CSV output uses semicolon `;` delimiter, not comma

### Experiment Configuration
- **Conditional config generation**: `one_to_many` matching generates configs with both word_agg and sentence_agg; other matchings only use sentence_agg (word_agg is None)
- **Index weighting replaces aggregation**: When `index_weight_type` is set (linear/prime/exponential), it replaces sentence-level aggregation, not supplements it
- **Prime weights use sympy**: Prime number generation uses `sympy.primerange(0,1000)` - requires sympy dependency

## Commands

```bash
# Run parameter grid search experiment (uses train split)
python experiment.py

# Evaluate all configurations with Pearson correlation
python pearson_eval.py

# Run final test on test split with best config
python final_test.py

# Analyze parameter correlations with Pearson scores
python analyze_correlation.py
```

## Dependencies

```bash
pip install scipy scikit-learn pandas matplotlib requests sympy
```
