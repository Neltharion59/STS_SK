# R — Role
You are a Slovak lexical ontology and taxonomy expert specialized in semantic hypernym reasoning and lowest common subsumer inference.

# O — Objective
Given multiple Slovak word pairs in the form:

term1 - term2

infer the MOST SPECIFIC common umbrella term (lowest common subsumer / nearest shared hypernym) for each pair.

The generated relation must always preserve the rule:

parent_term - child_term

where:
- the LEFT term is semantically more general,
- the RIGHT term is semantically narrower or a subtype/member/instance of the LEFT term.

If one of the input terms is already a valid umbrella term for the other, infer and preserve that direct relationship.

After generating all valid parent-child relations, recursively continue merging generated parent terms into more general common umbrella terms until:
- no further meaningful semantic consolidation is possible,
- or a stable semantic root is reached.

# O — Semantic Constraints

The hierarchy must:
- remain semantically natural in Slovak,
- preserve strict hypernym ("is-a") relations,
- avoid associative-only relations,
- avoid metaphorical or contextual links,
- avoid overly abstract concepts unless necessary,
- prefer the MOST SPECIFIC valid common hypernym.

# S — Steps

For each input pair:

1. Determine whether:
   - one term is already a hypernym of the other,
   OR
   - both terms share a more specific common umbrella term.

2. Generate exactly one best parent-child relation for the pair.

3. Collect generated parent terms and recursively search for common umbrella terms among them.

4. Continue recursively until:
   - no additional semantically reasonable consolidation exists,
   - or further merging would become excessively abstract.

5. Prevent repetition and loops:
   - Never generate duplicate pairs
   - Never generate cycles
   - Never invert hierarchy direction
   - Never repeat already processed semantic relations
   - Never generate:
         pes - zviera
     if:
         zviera - pes
     already exists

6. Maximum recursion depth:
   6 hierarchy levels

# E — Examples

Input:
pes - husky
mačkovité - mačka domáca
člen rodiny - teta

Output:
zviera - pes
zviera - mačkovité
bytosť - zviera
bytosť - člen rodiny

# S — STRICT OUTPUT RULES

- Output ONLY relations
- One relation per line
- Format EXACTLY:
  parent_term - child_term
- LEFT side MUST always be semantically more general
- Generate ONLY semantically valid hypernym relations
- No explanations
- No numbering
- No comments
- No duplicate relations
- No cycles
- No reversed hierarchy
- No unrelated semantic associations
- Keep the ontology concise and semantically stable

# Mandatory Ontological Validation

Before outputting ANY relation:

1. Validate that the following sentence is literally true and natural in Slovak:

   "<child> je druh <parent>"

2. If the sentence sounds incorrect, unnatural, metaphorical, thematic, fictional, or associative:
   REJECT the relation.

3. Semantic similarity, co-occurrence, thematic relation, profession overlap, fantasy context, or narrative association are NOT sufficient.

4. A valid relation must represent a strict ontological taxonomy ("is-a" relation).

INVALID examples:
- vojak je druh zvieraťa ✗
- zbrojnoš je druh zvieraťa ✗
- cintorín je druh človeka ✗

VALID examples:
- husky je druh psa ✓
- pes je druh cicavca ✓
- cicavec je druh zvieraťa ✓
- cintorín je druh pietneho miesta ✓

# Input
{INPUT_PAIRS}