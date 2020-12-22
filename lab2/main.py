import itertools
import time


def read_baskets():
    baskets = []
    with open('T10I4D100K.dat') as f:
        for line in f:
            items = line.split(' ')
            items.remove('\n')
            baskets.append(list(map(int, items)))
    return baskets


def count_singletons(baskets):
    count = {}
    for basket in baskets:
        for item in basket:
            if item in count:
                count[item] += 1
            else:
                count[item] = 1
    return count


def filter_frequent_items(items_count, support):
    return {item: items_count[item] for item in items_count if items_count[item] >= support}


def generate_candidates(items, singletons):
    print("items: ", items)
    candidates = {}
    for item in items:
        for singleton in singletons:
            if singleton[0] not in item:
                candidate = tuple(sorted(item + singleton))
                if candidate not in candidates:
                    candidates[candidate] = 0
    return candidates


# SLOW IMPLEMENTATION: Check if each item of candidate tuples exists in basket
# def count_candidates(baskets, candidates, candidate_length):
#     for basket in baskets:
#         for candidate in candidates:
#             in_basket = True
#             for item in candidate:
#                 if item not in basket:
#                     in_basket = False
#                     break
#             if in_basket:
#                 candidates[candidate] += 1
#     return candidates


# FAST IMPLEMENTATION: Generate all possible basket items combinations and check if they exist in candidates
def count_candidates(baskets, candidates, candidate_length):
    for basket in baskets:
        basket_variations = itertools.combinations(basket, candidate_length)
        for combination in basket_variations:
            if combination in candidates:
                candidates[combination] += 1
    return candidates


def conf(k_tuple, arrow_position, frequent_itemsets):
    before_arrow = k_tuple[:arrow_position]
    union_support = get_support(k_tuple, frequent_itemsets)
    single_support = get_support(before_arrow, frequent_itemsets)
    return union_support / single_support


def get_support(k_tuple, frequent_itemsets):
    return frequent_itemsets[len(k_tuple) - 1][tuple(sorted(k_tuple))]


def main():
    support = 1000
    confidence = 0.5
    frequent_itemsets = []  # Results
    associations = set()

    baskets = read_baskets()                                                 # Read data file
    singletons_count = count_singletons(baskets)                             # Find and count singletons
    filtered_items = filter_frequent_items(singletons_count, support)        # Filter frequent singletons
    frequent_singletons = {(i,): filtered_items[i] for i in filtered_items} # Wrap singletons in tuple to use the same data structure for pairs, triplets, etc..
    frequent_itemsets.append(frequent_singletons)
    print("Frequent singletons:", frequent_singletons)
    print("Frequent itemsets", len(frequent_itemsets))

    k = 1
    while len(frequent_itemsets[k - 1]) > 0:                                                # While new frequent elements are found
        candidates = generate_candidates(frequent_itemsets[k - 1], frequent_itemsets[0])    # Generate candidates from previous frequent itemset and singletons
        candidates_count = count_candidates(baskets, candidates, k + 1)                     # Count candidates frequency
        frequent_itemset = filter_frequent_items(candidates_count, support)                 # Filter frequent items
        frequent_itemsets.append(frequent_itemset)
        print("Frequent " + str(k + 1) + "-tuples:", frequent_itemsets[k])
        k += 1

    for frequent_itemset in frequent_itemsets[1:]:
        for k_tuple in frequent_itemset:
            for tuple_permutation in itertools.permutations(k_tuple, len(k_tuple)):
                for arrow_position in reversed(range(1, len(tuple_permutation))): # arrow_position = 1 means: A -> B,C,D. arrow_position = 2 means: A,B -> C,D etc..
                    c = conf(tuple_permutation, arrow_position, frequent_itemsets)
                    if c >= confidence:
                        associations.add((', '.join(map(str, sorted(tuple_permutation[:arrow_position]))) + ' -> ' + ', '.join(map(str, sorted(tuple_permutation[arrow_position:]))), c))
                    else:
                        break # Known rule: If A,B,C -> D is below confidence so that A,B -> C,D. So no need to iterate over arrow positions futher

    print("Associations:", associations)


start_time = time.time()
main()
print("--- %s seconds ---" % (time.time() - start_time))
