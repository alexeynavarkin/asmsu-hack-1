import itertools


def gen_combinations(size: list[int], target: int):
    res = []
    curr = []
    has_gen_started = False
    i = 1

    while len(curr) > 0 or not has_gen_started:
        curr = list(sorted(el) for el in itertools.combinations_with_replacement(size, i) if sum(el) == target)
        res.extend(curr)
        i += 1
        if len(curr) > 0:
            has_gen_started = True

    return res
