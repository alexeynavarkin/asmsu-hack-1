def _parse_matrix(matrix_str: str) -> list[list[int]]:
    return [
        [int(val.strip()) for val in line.split(",")]
        for line in matrix_str.strip().split("\n")
    ]
