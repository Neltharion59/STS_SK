import json
import csv

def convert_json_to_csv(input_file="concept_coverage_analysis.json", output_file="concept_coverage_analysis.csv"):
    with open(input_file, "r", encoding="utf-8-sig") as f:
        data = json.load(f)

    rows = []
    for pair_idx, pair in enumerate(data):
        score = pair["score"]
        for sent_idx, (sent_key, sent_label) in enumerate([("words1", "sentence1"), ("words2", "sentence2")]):
            sentence = pair[sent_key.replace("words", "sentence")]
            for word_idx, word_data in enumerate(pair[sent_key]):
                row = {
                    "pair_id": pair_idx + 1,
                    "sentence_id": sent_idx + 1,
                    "sentence_label": sent_label,
                    "score": score,
                    "sentence_text": sentence,
                    "word_position": word_idx + 1,
                    "word": word_data["word"],
                    "lemma": word_data["lemma"] if word_data["lemma"] else "",
                    "has_lemma": word_data["has_lemma"],
                    "has_concept_entry": word_data["has_concept_entry"],
                    "has_category": word_data["has_category"],
                    "category": word_data["category"] if word_data["category"] else "",
                    "has_synonyms": word_data["has_synonyms"],
                    "synonym_count": word_data["synonym_count"],
                    "has_wn_entry": word_data["has_wn_entry"],
                    "wn_synset_count": word_data["wn_synset_count"]
                }
                rows.append(row)

    with open(output_file, "w", newline="", encoding="utf-8-sig") as f:
        fieldnames = list(rows[0].keys())
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=";")
        writer.writeheader()
        writer.writerows(rows)

    print(f"Converted {len(rows)} rows from {len(data)} sentence pairs")
    print(f"Saved to {output_file}")

if __name__ == "__main__":
    convert_json_to_csv()