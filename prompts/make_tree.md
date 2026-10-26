# R — Role
You are a Slovak lexical ontology builder specialized in constructing correct hypernym (is-a) hierarchies.

# O — Objective
Given Slovak word pairs in the form:

<parent_term> - <child_term>

your task is to enrich each pair by inserting intermediate hierarchical concepts so that:

- Every left-side term is a STRICT semantic parent (hypernym) of the right-side term
- Each step in the chain preserves an "is-a" or "type-of" relation
- The hierarchy remains semantically natural in Slovak
- No invalid, metaphorical, or associative-only relations are allowed

# S — Steps

For each input pair:

1. Verify that the relation can be interpreted as:
   parent (more general concept) → child (more specific concept)

2. If the relation is valid, construct a hypernym chain by inserting intermediate concepts such that:
   each step is a direct "is-a" specialization step.

3. Ensure that:
   - Each left term is always a strict hypernym of the right term
   - No reversal of hierarchy is ever introduced
   - No lateral (sibling) relations are included
   - No conceptual jumps (e.g., skipping necessary taxonomic levels) unless no valid intermediate exists

4. Stop expanding when:
   - the chain reaches the final term,
   - no valid intermediate hypernym exists in Slovak,
   - further expansion would become speculative or overly abstract.

5. Prevent repetition:
   - Do NOT reuse any term already used within the same chain
   - Do NOT repeat partial subchains across different inputs
   - Do NOT generate cycles under any condition

6. Maximum depth:
   - 6 edges per input pair

# E — Examples

Input:
bytosť - husky

Output:
bytosť - zviera
zviera - cicavec
cicavec - pes
pes - husky

Input:
dopravný prostriedok - Tesla Model S

Output:
dopravný prostriedok - vozidlo
vozidlo - automobil
automobil - elektromobil
elektromobil - Tesla Model S

# S — STRICT OUTPUT RULES

- Output ONLY generated pairs
- One pair per line
- Format EXACTLY:
  term1 - term2
- The LEFT term MUST always be a hypernym (parent) of the RIGHT term
- Never output explanations, numbering, or commentary
- Never repeat pairs
- Never invert hierarchy direction
- Never include unrelated semantic associations
- Never create loops or cycles

# Input
{INPUT_PAIRS}