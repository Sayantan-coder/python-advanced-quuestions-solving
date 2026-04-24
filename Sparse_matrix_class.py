class SparseMatrix:
    def __init__(self, rows, columns):
        self.rows = rows
        self.columns = columns
        self.data = {}

    def add_entry(self, r, c, val):
        if val != 0:
            self.data[(r, c)] = val

    def __add__(self, other):

        result = SparseMatrix(self.rows, self.columns)

        for (r, c), v in self.data.items():
            result.data[(r, c)] = v

        for (r, c), v in other.data.items():
            result.data[(r, c)] = result.data.get((r, c), 0) + v
            if result.data[(r, c)] == 0:
                del result.data[(r, c)]
        return result

    def __mul__(self, other):

        result = SparseMatrix(self.rows, other.columns)
        for (r, c), v in self.data.items():
            for k in range(other.columns):
                if (c, k) in other.data:
                    result.data[(r, k)] = (
                        result.data.get((r, k), 0) + v * other.data[(c, k)]
                    )

        result.data = {pos: val for pos, val in result.data.items() if val != 0}
        return result

    def __str__(self):

        mat = ""
        for i in range(self.rows):
            row = []
            for j in range(self.columns):
                row.append(str(self.data.get((i, j), 0)))
            mat += " ".join(row) + "\n"
        return mat


A = SparseMatrix(2, 2)
A.add_entry(0, 1, 5)
A.add_entry(1, 0, 3)
B = SparseMatrix(2, 2)
B.add_entry(0, 0, 2)
B.add_entry(1, 0, -3)
print("A + B =")
print(A + B)
