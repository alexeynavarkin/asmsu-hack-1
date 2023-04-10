MatrixT = list[list[int]]
ContainersSizesT = list[int]


def parse_matrix(matrix_str: str) -> MatrixT:
    return [
        [int(val.strip()) for val in line.split(",")]
        for line in matrix_str.strip().split("\n")
    ]


def load_from_file(file_path: str) -> tuple[ContainersSizesT, MatrixT]:
    with open(file_path) as f:
        containers_sizes_line = [
            int(container_size)
            for container_size in f.readline().split(":")[1].split(",")
        ]
        matrix = parse_matrix(f.read())

    return containers_sizes_line, matrix
