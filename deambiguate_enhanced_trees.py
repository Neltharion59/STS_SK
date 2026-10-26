from json import loads, dumps

with open('trees_raw.json', "r", encoding="utf-8-sig") as f:
        print('Found existing trees')
        enhanced_trees = loads(f.read())

enhanced_trees_fixed = {}
for key in enhanced_trees:
    key_fixed = ' '.join(sorted(key.split(' ')))
    enhanced_trees_fixed[key_fixed] = enhanced_trees[key]

with open('trees_raw_deambiguated.json', "w+", encoding="utf-8-sig") as f:
    f.write(dumps(enhanced_trees_fixed, indent=4))