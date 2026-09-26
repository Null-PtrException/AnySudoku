# que.py
import random
import copy
from ans import SudokuSolver


class SudokuGenerator:
    """自动出题器：唯一解 / 多解，支持任意 box_w × box_h 棋盘。"""

    def __init__(self, box_w=3, box_h=3, num_boxes_x=3, num_boxes_y=3,
                 min_num=1, max_num=9, seed=None):
        self.solver = SudokuSolver(box_w, box_h, num_boxes_x, num_boxes_y,
                                   min_num, max_num)
        self.box_w = box_w
        self.box_h = box_h
        self.num_boxes_x = num_boxes_x
        self.num_boxes_y = num_boxes_y
        self.min_num = min_num
        self.max_num = max_num
        self.grid_w = self.solver.grid_w
        self.grid_h = self.solver.grid_h
        if seed is not None:
            random.seed(seed)

    # ============================================================
    #  生成完整终盘
    # ============================================================
    def _fill_board(self, board):
        n, m = self.grid_h, self.grid_w
        b_h, b_w = self.box_h, self.box_w

        def find_empty():
            for r in range(n):
                for c in range(m):
                    if board[r][c] == 0:
                        return r, c
            return -1, -1

        def candidates(r, c):
            used = set(board[r])
            used.update(board[i][c] for i in range(n))
            br, bc = (r // b_h) * b_h, (c // b_w) * b_w
            for i in range(br, br + b_h):
                for j in range(bc, bc + b_w):
                    used.add(board[i][j])
            return [v for v in range(self.min_num, self.max_num + 1)
                    if v not in used]

        def bt():
            r, c = find_empty()
            if r == -1:
                return True
            cands = candidates(r, c)
            random.shuffle(cands)
            for v in cands:
                board[r][c] = v
                if bt():
                    return True
                board[r][c] = 0
            return False

        return bt()

    def generate_full(self):
        board = [[0] * self.grid_w for _ in range(self.grid_h)]
        if not self._fill_board(board):
            return None
        return board

    # ============================================================
    #  挖洞顺序：按宫轮流
    # ============================================================
    def _make_dig_order(self):
        """
        生成一个"均匀分布"的挖洞顺序：
        先按宫分组，宫内格子随机；再轮流从各宫取一个格子。
        这样挖洞会均匀地分布到整个棋盘，而不是从上往下挖。
        """
        n, m = self.grid_h, self.grid_w
        b_h, b_w = self.box_h, self.box_w

        boxes = []
        for r0 in range(0, n, b_h):
            for c0 in range(0, m, b_w):
                box_cells = []
                for r in range(r0, min(r0 + b_h, n)):
                    for c in range(c0, min(c0 + b_w, m)):
                        box_cells.append((r, c))
                random.shuffle(box_cells)
                boxes.append(box_cells)

        random.shuffle(boxes)

        # 轮流从每个宫取一个，直到所有宫都取完
        order = []
        max_len = max(len(b) for b in boxes) if boxes else 0
        for i in range(max_len):
            for b in boxes:
                if i < len(b):
                    order.append(b[i])
        return order

    # ============================================================
    #  唯一解出题
    # ============================================================
    def generate_puzzle(self, unique=True, min_givens=24,
                        tolerance=3, max_tries=None):
        """
        唯一解出题：
        - 用均匀的挖洞顺序，尽量挖到 min_givens（可以略多 tolerance 个）
        - 每次尝试都重新生成一个新终盘
        - 达不到返回 None
        """
        n, m = self.grid_h, self.grid_w
        total_cells = n * m
        min_givens = max(1, min(min_givens, total_cells - 1))

        if max_tries is None:
            max_tries = max(20, 5 * total_cells)

        for attempt in range(max_tries):
            full = self.generate_full()
            if full is None:
                continue

            puzzle = copy.deepcopy(full)
            order = self._make_dig_order()

            givens = total_cells
            for (r, c) in order:
                if givens <= min_givens:
                    break
                backup = puzzle[r][c]
                puzzle[r][c] = 0
                cnt = self.solver.count_solutions(puzzle, limit=2,
                                                  num_threads=1)
                if cnt == 1:
                    givens -= 1
                else:
                    puzzle[r][c] = backup

            final_cnt = self.solver.count_solutions(puzzle, limit=2,
                                                    num_threads=1)
            if final_cnt != 1:
                continue
            if givens <= min_givens + tolerance:
                return puzzle, full

        return None, None

    # ============================================================
    #  多解出题
    # ============================================================
    def generate_multi(self, min_solutions=2, target_solutions=10,
                       max_solutions=200, min_givens=18,
                       max_tries=None):
        """
        多解出题：
        - 用均匀的挖洞顺序，先挖到 min_givens 附近
        - 统计解数量，优先返回解数量 >= target_solutions 的
        """
        n, m = self.grid_h, self.grid_w
        total_cells = n * m
        min_givens = max(1, min(min_givens, total_cells - 1))

        if max_tries is None:
            max_tries = max(20, 3 * total_cells)

        best_puzzle = None
        best_full = None
        best_count = 0

        for attempt in range(max_tries):
            full = self.generate_full()
            if full is None:
                continue

            puzzle = [row[:] for row in full]
            order = self._make_dig_order()

            target_givens = min_givens + random.randint(0, 1)
            target_givens = min(target_givens, total_cells - 1)
            remove_count = total_cells - target_givens

            for i in range(min(remove_count, len(order))):
                r, c = order[i]
                puzzle[r][c] = 0

            cnt = self.solver.count_solutions(puzzle,
                                              limit=max_solutions + 1,
                                              num_threads=8)
            if cnt < min_solutions:
                continue
            if cnt >= target_solutions:
                return puzzle, full
            if cnt > best_count:
                best_count = cnt
                best_puzzle = [row[:] for row in puzzle]
                best_full = full

        if best_puzzle is not None:
            return best_puzzle, best_full
        return None, None