from json import loads, dumps
import re

from tree import Node

with open(f'trees_raw_basic.json', "r", encoding="utf-8-sig") as f:
    loaded_enhanced_trees_basic = loads(f.read())

with open(f'trees_raw_subsumer.json', "r", encoding="utf-8-sig") as f:
    loaded_enhanced_trees_subsumer = loads(f.read())

def extract_taxonomy(raw_response):
    lines = raw_response.split('\n')
    for line in lines:
        if ',' in line:
            return [word.strip().lower() for word in line.split(',')]
    
    return []

def load_enhanced_tree_edges(root, lemmas_key, tree_type):
    basic_tree_couples = list(root.tree_to_couples())
    new_couples = []
    for couple in basic_tree_couples:
        couple = [x.strip().lower() for x in couple]
        couple_key = '-'.join(couple)

        if couple_key in loaded_enhanced_trees_basic:
            couple_enhancements = extract_taxonomy(loaded_enhanced_trees_basic[couple_key])
            couple_enhancements = [item for item in couple_enhancements if item not in couple]

            extra_couples = list(zip([couple[0]] + couple_enhancements[:-1], couple_enhancements[1:] + [couple[1]]))
            new_couples = new_couples + extra_couples
        else:
            new_couples.append(couple)

    children = [c[1] for c in new_couples]

    for couple in new_couples:
        if couple[0] != 'root' and couple[0] not in children:
            new_couples.append(['root', couple[0]])
            children.append(couple[0])

    return new_couples

def load_enhanced_tree(root, lemmas_key, tree_type):
    unique_edges = load_enhanced_tree_edges(root, lemmas_key, tree_type)

    nodes = { 'root': Node('root')}
    for edge in unique_edges:
        parent, child = (edge[0], edge[1])
        if parent not in nodes:
            nodes[parent] = Node(parent)

        if child not in nodes:
            nodes[child] = Node(child)
            
        if child not in nodes[parent].children and parent not in nodes[child].children and parent != child:
            nodes[parent].add_child(nodes[child])

    decycle_tree_downwards(nodes['root'])

    return nodes['root']

def decycle_tree_downwards(root):
    root.visited = True
    root.children = [child for child in root.children if not child.visited]
    for child in root.children:
        decycle_tree_downwards(child)