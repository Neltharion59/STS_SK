import sympy
from nltk.corpus import wordnet as wn

primes = list(sympy.primerange(0,1000))

def one_to_many(lemmas1, lemmas2, root, similarity_type, tree_type):
    result = []

    for w1 in lemmas1:
        word_result = []
        
        for w2 in lemmas2:
            score = compute_word_similarity(root, w1, w2, similarity_type, tree_type)
            word_result.append(score)
            
        result.append(word_result)
        
    return result

def all_to_all(lemmas1, lemmas2, root, similarity_type, tree_type):
    result = []
    
    for w1 in lemmas1:
        for w2 in lemmas2:
            score = compute_word_similarity(root, w1, w2, similarity_type, tree_type)
            result.append(score)
                
    return result

def element_wise(lemmas1, lemmas2, root, similarity_type, tree_type):
    result = []

    for i in range(min(len(lemmas1), len(lemmas2))):
        score = compute_word_similarity(root, lemmas1[i], lemmas2[i], similarity_type, tree_type)
        result.append(score)

    return result

def aggregate(scores, mode):
    if scores == []:
        return 0
    
    if mode == "max":
        return max(scores)
    elif mode == "min":
        return min(scores)
    elif mode == "avg":
        return sum(scores) / len(scores)

def aggregate_lists(scores, mode):
    result = []
    
    for score in scores:
        result.append(aggregate(score,mode))
        
    return result

def exponentiate_score(score, power):
    try:
        power = int(power.replace("power", ""))
    except:
        power = 1
    return score ** power
    
def index_weighted_average(scores, weight_type=None):
    if weight_type not in ["linear", "prime", "exponential"]:
        raise ValueError("weight type must be prime, linear or exponential")
    
    if not scores:
        return 0
    
    weighted_sum = 0
    weight_sum = 0

    if weight_type == "linear":
        for i,score in enumerate(scores):
            weighted_sum += (i+1) * score
            weight_sum += i+1

    elif weight_type == "prime":
        for i,score in enumerate(scores):
            weighted_sum += primes[i] * score
            weight_sum += primes[i]

    elif weight_type == "exponential":
        for i,score in enumerate(scores):
            weighted_sum += 2**(i+1) * score
            weight_sum += 2**(i+1)

    return weighted_sum / weight_sum


def avg(values):
    if len(values) == 0:
        return 0

    return sum(values)/len(values)

def compute_word_similarity(root, w1, w2, similarity_type, tree_type):
    w1 = w1.lower()
    w2 = w2.lower()

    if 'cd' in tree_type:
        if similarity_type == "wupalmer":
            return root.wupalmer(w1, w2)
        elif similarity_type == "spath":
            return root.shortest_path(w1, w2)
        elif similarity_type == "lch":
            return root.leacock_chodorow(w1, w2)
        else:
            return 0
    elif tree_type == "wn":
        synsets1 = wn.synsets(w1, lang="slk")
        synsets2 = wn.synsets(w2, lang="slk")

        
        if similarity_type == "wupalmer":
            similarity_func = lambda s1, s2: s1.wup_similarity(s2)
        elif similarity_type == "spath":
            similarity_func = lambda s1, s2: s1.path_similarity(s2)
        elif similarity_type == "lch":
            similarity_func = lambda s1, s2: s1.lch_similarity(s2)
        else:
            similarity_func = lambda s1, s2: 0
        
        result = avg([similarity_func(s1, s2) for s1 in synsets1 for s2 in synsets2 if s1.pos == s2.pos])

        return result
    else:
        raise ValueError(f"tree_type=={tree_type}")
    
def compute_similarity(lemmas1, lemmas2, root,
                       matching, word_agg, sentence_agg,
                       direction,
                       similarity_type, 
                       power=1,
                       index_weight_type=None,
                       power_scope="local",
                       tree_type="cd_basic"):

    def directional(l1, l2):

        if matching == "one_to_many":
            scores = one_to_many(l1, l2, root, similarity_type, tree_type)

            if power_scope == "local":
                scores = [[exponentiate_score(s, power) for s in sublist] for sublist in scores]

            word_scores = aggregate_lists(scores, word_agg)

            if index_weight_type:
                final_score = index_weighted_average(word_scores, index_weight_type)
            else:
                final_score = aggregate(word_scores, sentence_agg)

            if power_scope == "global":
                final_score = exponentiate_score(final_score, power)

            return final_score

        elif matching == "all_to_all":
            scores = all_to_all(l1, l2, root, similarity_type, tree_type)

            if power_scope == "local":
                scores = [exponentiate_score(s, power) for s in scores]

            final_score = aggregate(scores, sentence_agg)

            if power_scope == "global":
                final_score = exponentiate_score(final_score, power)

            return final_score

        elif matching == "element_wise":
            scores = element_wise(l1, l2, root, similarity_type, tree_type)

            if power_scope == "local":
                scores = [exponentiate_score(s, power) for s in scores]

            if index_weight_type:
                final_score = index_weighted_average(scores, index_weight_type)
            else:
                final_score = aggregate(scores, sentence_agg)

            if power_scope == "global":
                final_score = exponentiate_score(final_score, power)

            return final_score

        return 0
    
    if direction == "single":
        return directional(lemmas1, lemmas2)

    elif direction == "symmetric":
        s1 = directional(lemmas1, lemmas2)
        s2 = directional(lemmas2, lemmas1)
        return (s1 + s2) / 2

    return 0
