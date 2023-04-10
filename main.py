import sys
from multiprocessing import Pool, cpu_count
import logging

from task import Task
from data import matrix_test
from gen_combinations import gen_combinations
from helpers import load_from_file

logging.basicConfig(
    stream=sys.stderr,
    level=logging.INFO,
    format="[%(asctime)s] [%(processName)s] %(message)s",
)


def test():
    task = Task(
        matrix=matrix_test.matrix,
        containers=matrix_test.containers,
    )
    groups = task.solve()
    for wanted_group in matrix_test.wanted_groups:
        for group in groups:
            if set(group) == set(wanted_group):
                groups.remove(group)
                break

    assert not groups, "Groups differs."


def solve(matrix, containers) -> int:
    task = Task(
        matrix=matrix,
        containers=containers,
    )
    task.solve()
    return task.calc_q()


def main():
    logging.info("Loading matrix")
    containers_sizes, matrix = load_from_file(f"data/{sys.argv[1]}")

    q = []
    res = []
    with Pool(processes=int(cpu_count() * 0.75)) as pool:
        for comb in gen_combinations(containers_sizes, len(matrix)):
            logging.info(f"Start solving: {comb}")
            res.append(pool.apply_async(solve, (matrix, comb)))

        for r in res:
            q.append(r.get())

        logging.info(f"Min Q = {min(q)}")


if __name__ == "__main__":
    # test()
    main()
