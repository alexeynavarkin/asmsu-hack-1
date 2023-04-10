from __future__ import annotations

import itertools


def gen_combinations(sizes: list[int], target: int, start: int | None = None):
    i = start or int(target / max(sizes))

    has_non_zero_comb_found = True
    has_comb_found = False

    while has_non_zero_comb_found or not has_comb_found:
        print(f"Attempting to find combinations with {i} containers")
        has_non_zero_comb_found = False
        for el in itertools.combinations_with_replacement(sizes, i):
            if sum(el) == target:
                has_comb_found = True
                has_non_zero_comb_found = True
                yield el

        i += 1
