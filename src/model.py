# model.py
class BoardModel:
    """棋盘数据模型：只存数据，不碰 UI。"""

    def __init__(self, grid_w, grid_h):
        self.grid_w = grid_w
        self.grid_h = grid_h
        self.board = [[0] * grid_w for _ in range(grid_h)]
        self.solution = [[0] * grid_w for _ in range(grid_h)]
        self.original_fixed = [[False] * grid_w for _ in range(grid_h)]

    def reset(self, grid_w=None, grid_h=None):
        if grid_w is not None:
            self.grid_w = grid_w
        if grid_h is not None:
            self.grid_h = grid_h
        self.board = [[0] * self.grid_w for _ in range(self.grid_h)]
        self.solution = [[0] * self.grid_w for _ in range(self.grid_h)]
        self.original_fixed = [[False] * self.grid_w
                               for _ in range(self.grid_h)]

    def set_cell(self, r, c, val):
        self.board[r][c] = val
        self.solution[r][c] = val
        self.original_fixed[r][c] = (val != 0)

    def clear_board(self):
        self.reset()

    def clear_solution_only(self):
        n, m = self.grid_h, self.grid_w
        self.solution = [row[:] for row in self.board]
        for r in range(n):
            for c in range(m):
                if not self.original_fixed[r][c]:
                    self.solution[r][c] = 0

    def load_matrix(self, matrix):
        n, m = self.grid_h, self.grid_w
        self.board = [row[:] for row in matrix]
        self.solution = [row[:] for row in matrix]
        self.original_fixed = [[matrix[r][c] != 0 for c in range(m)]
                               for r in range(n)]

    def to_text(self, box_w, box_h):
        n, m = self.grid_h, self.grid_w
        num_boxes_x = m // box_w

        # 分隔行：首尾段 box_w*2 个 -，中间段 box_w*2+1 个 -
        seg_first = "-" * (box_w * 2)
        seg_mid = "-" * (box_w * 2 + 1)
        seg_last = "-" * (box_w * 2)

        if num_boxes_x == 1:
            sep_line = "-" * (box_w * 2 + 1)
        else:
            parts = [seg_first] + [seg_mid] * (num_boxes_x - 2) + [seg_last]
            sep_line = "+".join(parts)

        lines = []
        for r in range(n):
            if r > 0 and r % box_h == 0:
                lines.append(sep_line)
            row_tokens = []
            for c in range(m):
                if c > 0 and c % box_w == 0:
                    row_tokens.append("|")
                val = self.board[r][c]
                row_tokens.append(str(val) if val != 0 else ".")
            lines.append(" ".join(row_tokens))
        return "\n".join(lines)