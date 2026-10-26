[
    {
        "role": "user",
        "content": "There is a taxonomical hierarchical relationship between Slovak terms, meaning that the left is above the right:\nžena - mami\n\nWhat are some possible additional terms between them in the hierarchy? Provide a comma-separated list ordered by position in the taxonomy. Do not add any extra formatting nor explanations.",
        "cache_control": {
            "type": "ephemeral"
        }
    },
    {
        "role": "system",
        "content": "žena, žena v rodine, matka, mami",
        "cache_control": {
            "type": "ephemeral"
        }
    },
    {
        "role": "user",
        "content": "There is a taxonomical hierarchical relationship between Slovak terms, meaning that the left is above the right:\nAktivity - jazdiť\nAktivity - nie\njazdiť - jazdenie\nZvieratá - kôň\nRoly - žena\nžena - mami\nWhat are some possible additional terms between them in the hierarchy? Provide a comma-separated list ordered by position in the taxonomy. Do not add any extra formatting nor explanations.",
        "cache_control": {
            "type": "ephemeral"
        }
    },
    {
        "role": "system",
        "content": "Aktivity, šport, cyklistika, jazdiť\nAktivity, pasívne, nie\njazdiť, jazdenie, cyklovanie\nZvieratá, stavovce, cicavce, kôň\nRoly, rodinné, žena\nžena, matka, mami",
        "cache_control": {
            "type": "ephemeral"
        }
    },
    {
        "role": "user",
        "content": "There is a taxonomical hierarchical relationship between Slovak terms, meaning that the left is above the right:\n{INPUT_PAIRS}\nWhat are some possible additional terms between them in the hierarchy? Provide a comma-separated list ordered by position in the taxonomy. Do not add any extra formatting nor explanations.",
        "cache_control": {
            "type": "ephemeral"
        }
    }
]