from task import Task
from data import matrix_test
from gen_combinations import gen_combinations
from helpers import load_from_file


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


def main():
    print("Loading matrix...")
    containers_sizes, matrix = load_from_file("data/matrix1.txt")

    q = []
    for comb in gen_combinations(containers_sizes, len(matrix)):
        print(f"Start solving: {comb}")
        task = Task(
            matrix=matrix,
            containers=comb,
        )
        task.solve()
        q.append(task.calc_q())

        print(f'Current min Q = {min(q)}\n\n')

    print(f'\nMin Q = {min(q)}')


if __name__ == "__main__":
    # test()
    main()
