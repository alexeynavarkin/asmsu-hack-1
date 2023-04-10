from __future__ import annotations

import logging

from helpers import MatrixT


class Task:
    def __init__(
        self,
        matrix: MatrixT,
        containers: list[int],
    ) -> None:
        self._matrix = matrix
        self._containers: list[int] = containers
        self._nodes_idx_array = [i for i in range(len(self._matrix))]
        self._groups_idx_array = []

    def solve(self):
        logging.info("------ Solve started ------")
        self.init_node_idx_array_and_containers()

        self._build_group_idx_array()
        logging.info(f"Start groups {self.build_groups()}")

        logging.info(f"Initial package Q={self.calc_q()}\n")

        self.optimize_groups()
        logging.info(f"Optimized package Q={self.calc_q()}")

        logging.info(f"Final groups {self.build_groups()}")
        logging.info("------ Solve finished ------")

        return self.build_groups()

    def build_groups(self):
        groups = []
        for group_idx in range(len(self._containers)):
            group_start = self._groups_idx_array[group_idx]
            group_end = self._groups_idx_array[group_idx + 1]
            groups.append(self._nodes_idx_array[group_start:group_end])

        return groups

    def init_node_idx_array_and_containers(self):
        for container_idx, container in enumerate(self._containers):
            min_indexes = self._get_min_indexes(
                curr_container_idx=container_idx, exclude_vertexes=[]
            )
            v_siblings = self._get_vertex_siblings(
                curr_container_idx=container_idx, vertex_idx=min_indexes[0]
            )

            appending_vertexes = sorted(v_siblings + [min_indexes[0]])

            while len(appending_vertexes) < container:
                min_indexes_upd = self._get_min_indexes(
                    curr_container_idx=container_idx,
                    exclude_vertexes=appending_vertexes,
                )
                assert len(min_indexes_upd)

                v_siblings_upd = self._get_vertex_siblings(
                    vertex_idx=min_indexes_upd[0],
                    curr_container_idx=container_idx,
                )
                appending_vertexes.extend(
                    v_siblings_upd + [min_indexes_upd[0]]
                )

            if len(appending_vertexes) > container:
                appending_vertexes = self.fit_nodes_to_size(
                    appending_vertexes, container, container_idx
                )

            if len(appending_vertexes) == container:
                for i in range(
                    sum(self._containers[:container_idx]),
                    sum(self._containers[:container_idx])
                    + len(appending_vertexes),
                ):
                    self.swap_nodes(
                        i,
                        self._nodes_idx_array.index(
                            appending_vertexes[
                                i - sum(self._containers[:container_idx])
                            ]
                        ),
                    )

    def _calc_fit_delta(
        self,
        node_idx: int,
        siblings_idx: list[int],
        curr_container_idx: int,
    ) -> int:
        """
        Вычисляет дельту для исключения узлов из группы.
        """
        siblings_sum = sum(
            self._matrix[node_idx][
                sum(self._containers[:curr_container_idx]) :
            ]
        )
        group_sum = sum(
            self._matrix[node_idx][idx]
            for idx in siblings_idx
            if idx >= sum(self._containers[:curr_container_idx])
        )
        return siblings_sum - group_sum

    def fit_nodes_to_size(
        self,
        nodes_idx_array: list[int],
        target_size: int,
        curr_container_idx: int,
    ) -> list[int]:
        """
        Уменьшает размер группы до необходимого.
        """
        nodes_idx_delta_mapping = {}
        for node_idx in nodes_idx_array:
            nodes_idx_delta_mapping[node_idx] = self._calc_fit_delta(
                node_idx=node_idx,
                siblings_idx=nodes_idx_array,
                curr_container_idx=curr_container_idx,
            )

        while len(nodes_idx_array) > target_size:
            node_idx_to_remove = max(
                nodes_idx_delta_mapping,
                key=nodes_idx_delta_mapping.get,
            )
            nodes_idx_array.remove(node_idx_to_remove)
            nodes_idx_delta_mapping.pop(node_idx_to_remove)

        return nodes_idx_array

    def _get_min_indexes(
        self, curr_container_idx: int, exclude_vertexes: list[int]
    ):
        raw_exclude_vertexes = [
            self._nodes_idx_array[i] for i in exclude_vertexes
        ]

        sums = self._count_vertex_sum(curr_container_idx=curr_container_idx)
        sums = list(filter(lambda i: i not in raw_exclude_vertexes, sums))

        min_sums_rows = [
            index for index, item in enumerate(sums) if item == min(sums)
        ]
        raw_idx = sorted(
            min_sums_rows,
            key=lambda vertex: max(
                self._matrix[vertex][
                    sum(self._containers[:curr_container_idx]) :
                ]
            ),
        )

        return [
            self._nodes_idx_array[
                i + sum(self._containers[:curr_container_idx])
            ]
            for i in raw_idx
        ]

    def _count_vertex_sum(self, curr_container_idx: int) -> list[int]:
        res = []
        for line in self._matrix[sum(self._containers[:curr_container_idx]) :]:
            res.append(sum(line[sum(self._containers[:curr_container_idx]) :]))

        return res

    def _get_vertex_siblings(self, vertex_idx: int, curr_container_idx: int):
        raw_idx = [
            index
            for index, item in enumerate(
                self._matrix[vertex_idx][
                    sum(self._containers[:curr_container_idx]) :
                ]
            )
            if item != 0
        ]

        return [
            self._nodes_idx_array[
                i + sum(self._containers[:curr_container_idx])
            ]
            for i in raw_idx
        ]

    def optimize_groups(self):
        """
        Оптимизирует размещение элементов по группам.
        """
        total_swaps = 0
        for group_idx in range(len(self._containers) - 1):
            total_swaps += self.optimize_group_by_idx(group_idx)

        logging.info(f"\nTotal swaps: {total_swaps}\n")

    def _build_group_idx_array(self):
        """
        Создает список id групп.
        """
        groups_idx_array = [0]
        group = 0
        for cont in self._containers:
            group += cont
            groups_idx_array.append(group)

        self._groups_idx_array = groups_idx_array

    def get_group_idx_by_node_idx(self, matrix_node_idx: int) -> int:
        """
        Возвращает Id группы, которая содержит элемент.
        """
        target_node_idx = self._nodes_idx_array.index(matrix_node_idx)
        for idx, el in enumerate(self._groups_idx_array):
            if target_node_idx < el:
                return idx - 1  # :)

        raise IndexError("Group not found.")

    def get_delta(self, group_idx: int, node_idx_true: int):
        """
        Возвращает элементы группы.
        """
        node_idx_matrix = self._nodes_idx_array.index(node_idx_true)
        group_start = self._groups_idx_array[group_idx]
        group_end = self._groups_idx_array[group_idx + 1]
        return sum(self._matrix[node_idx_matrix][group_start:group_end])

    def find_permutation_weight(self, i: int, j: int):
        """
        Находит вес для перемещения узлов.
        """
        S_ij = self._matrix[i][j] * 2  # Связи между собой.
        i_group = self.get_group_idx_by_node_idx(self._nodes_idx_array[i])
        j_group = self.get_group_idx_by_node_idx(self._nodes_idx_array[j])
        delta_S_i = self.get_delta(
            j_group, self._nodes_idx_array[i]
        ) - self.get_delta(i_group, self._nodes_idx_array[i])
        delta_S_j = self.get_delta(
            i_group, self._nodes_idx_array[j]
        ) - self.get_delta(j_group, self._nodes_idx_array[j])
        return delta_S_i + delta_S_j - S_ij

    def find_to_swap(self, group_idx: int) -> tuple[int, int, int]:
        """
        Ищет узлы для перестановки.
        """
        max_elem = -1
        index_i = None
        index_j = None

        delta_S = []

        for node_idx_matrix in range(
            self._groups_idx_array[group_idx],
            self._groups_idx_array[group_idx + 1],
        ):
            row = []
            for node_idx_matrix_out in range(
                self._groups_idx_array[group_idx + 1],
                len(self._matrix),
            ):
                weight = self.find_permutation_weight(
                    node_idx_matrix,
                    node_idx_matrix_out,
                )
                row.append(weight)

                if max_elem < weight:
                    max_elem = weight
                    index_i = node_idx_matrix
                    index_j = node_idx_matrix_out
            delta_S.append(row)

        return index_i, index_j, max_elem

    def swap_nodes(self, i: int, j: int) -> None:
        """
        Меняет узлы местами.
        """
        self._nodes_idx_array[i], self._nodes_idx_array[j] = (
            self._nodes_idx_array[j],
            self._nodes_idx_array[i],
        )
        self._matrix[i], self._matrix[j] = (
            self._matrix[j],
            self._matrix[i],
        )
        for k in range(len(self._matrix)):
            self._matrix[k][i], self._matrix[k][j] = (
                self._matrix[k][j],
                self._matrix[k][i],
            )

    def optimize_group_by_idx(self, group_idx: int) -> int:
        """
        Оптимизирует одну группу по Id.
        """
        index_i, index_j, max_elem = self.find_to_swap(group_idx)
        swaps_cnt = 0

        while max_elem > 0:
            assert index_i is not None
            assert index_j is not None
            self.swap_nodes(index_i, index_j)
            index_i, index_j, max_elem = self.find_to_swap(group_idx)
            # logging.info(f"Need to swap: {index_i} {index_j}, {max_elem}")
            swaps_cnt += 1
            if swaps_cnt > len(self._matrix) * 2:
                logging.info("Too many swaps probably loop")
                break

        logging.info(
            f"Group {group_idx + 1}/{len(self._containers)} swaps {swaps_cnt}"
        )

        return swaps_cnt

    def calc_q(self):
        q = 0

        cur_group_idx = 0
        curr_group = self._containers[cur_group_idx]
        for idx, line in enumerate(self._matrix):
            if idx >= curr_group:
                cur_group_idx += 1
                curr_group += self._containers[cur_group_idx]
            q += sum(line[curr_group:])

        return q
