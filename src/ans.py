# ans.py
import heapq
import threading
import numpy as np


class SudokuSolver:
    """数独求解器核心：NumPy 加速候选数 + MRV + LCV + 传播 + 多解统计。"""

    def __init__(self, box_w=3, box_h=3, num_boxes_x=3, num_boxes_y=3,
                 min_num=1, max_num=9):
        self.box_w = box_w
        self.box_h = box_h
        self.num_boxes_x = num_boxes_x
        self.num_boxes_y = num_boxes_y
        self.min_num = min_num
        self.max_num = max_num

        self.grid_w = num_boxes_x * box_w
        self.grid_h = num_boxes_y * box_h

        self._final_board = None

    def board_to_np(self, board):
        return np.array(board, dtype=np.int16)

    def get_candidates_np(self, arr, r, c):
        n, m = self.grid_h, self.grid_w
        b_h, b_w = self.box_h, self.box_w
        used = set(arr[r, :].tolist())
        used.update(arr[:, c].tolist())
        br = (r // b_h) * b_h
        bc = (c // b_w) * b_w
        used.update(arr[br:br + b_h, bc:bc + b_w].ravel().tolist())
        return {v for v in range(self.min_num, self.max_num + 1)
                if v not in used}

    def build_candidates(self, board):
        arr = self.board_to_np(board)
        n, m = self.grid_h, self.grid_w
        b_h, b_w = self.box_h, self.box_w

        candidates = [[None] * m for _ in range(n)]
        heap = []

        row_used = [set(arr[r, :].tolist()) for r in range(n)]
        col_used = [set(arr[:, c].tolist()) for c in range(m)]
        box_used = {}
        for br in range(0, n, b_h):
            for bc in range(0, m, b_w):
                box_used[(br, bc)] = set(
                    arr[br:br + b_h, bc:bc + b_w].ravel().tolist())

        all_nums = set(range(self.min_num, self.max_num + 1))

        for r in range(n):
            for c in range(m):
                if arr[r, c] == 0:
                    br = (r // b_h) * b_h
                    bc = (c // b_w) * b_w
                    used = row_used[r] | col_used[c] | box_used[(br, bc)]
                    cands = all_nums - used
                    candidates[r][c] = cands
                    heapq.heappush(heap, (len(cands), r, c))
        return candidates, heap

    def update_affected(self, board, candidates, heap, row, col, num):
        n, m = self.grid_h, self.grid_w
        b_h, b_w = self.box_h, self.box_w
        conflict = False

        affected = set()
        for c2 in range(m):
            affected.add((row, c2))
        for r2 in range(n):
            affected.add((r2, col))
        br, bc = b_h * (row // b_h), b_w * (col // b_w)
        for i in range(br, min(br + b_h, n)):
            for j in range(bc, min(bc + b_w, m)):
                affected.add((i, j))
        affected.discard((row, col))

        for (r2, c2) in affected:
            if board[r2][c2] != 0:
                continue
            cands = candidates[r2][c2]
            if cands is None:
                continue
            if num in cands:
                cands.discard(num)
                if len(cands) == 0:
                    conflict = True
                elif len(cands) == 1:
                    heapq.heappush(heap, (1, r2, c2))
        return conflict

    def propagate(self, board, candidates, heap):
        while heap:
            while heap:
                cnt, r, c = heap[0]
                if (board[r][c] != 0
                        or candidates[r][c] is None
                        or len(candidates[r][c]) != cnt):
                    heapq.heappop(heap)
                else:
                    break
            if not heap:
                break
            cnt, r, c = heap[0]
            if cnt == 0:
                return False
            if cnt >= 2:
                break
            heapq.heappop(heap)
            val = next(iter(candidates[r][c]))
            board[r][c] = val
            candidates[r][c] = None
            if self.update_affected(board, candidates, heap, r, c, val):
                return False
        return True

    def find_mrv_cell(self, board, candidates, heap):
        while heap:
            cnt, r, c = heapq.heappop(heap)
            if (board[r][c] == 0
                    and candidates[r][c] is not None
                    and len(candidates[r][c]) == cnt):
                return r, c, candidates[r][c]
        n, m = self.grid_h, self.grid_w
        for r in range(n):
            for c in range(m):
                if board[r][c] == 0:
                    cnt2 = len(candidates[r][c])
                    heapq.heappush(heap, (cnt2, r, c))
                    return r, c, candidates[r][c]
        return -1, -1, None

    def count_impact(self, board, candidates, r, c, val):
        n, m = self.grid_h, self.grid_w
        b_h, b_w = self.box_h, self.box_w
        cnt = 0
        affected = set()
        for c2 in range(m):
            affected.add((r, c2))
        for r2 in range(n):
            affected.add((r2, c))
        br, bc = b_h * (r // b_h), b_w * (c // b_w)
        for i in range(br, min(br + b_h, n)):
            for j in range(bc, min(bc + b_w, m)):
                affected.add((i, j))
        affected.discard((r, c))
        for (rr, cc) in affected:
            if board[rr][cc] == 0 and candidates[rr][cc] is not None:
                if val in candidates[rr][cc]:
                    cnt += 1
        return cnt

    def backtrack(self, board, collect_all=False, limit=None, counter=None,
                  stop_event=None):
        if stop_event is not None and stop_event.is_set():
            return False
        board = [row[:] for row in board]
        candidates, heap = self.build_candidates(board)
        if not self.propagate(board, candidates, heap):
            return False
        r, c, cands = self.find_mrv_cell(board, candidates, heap)
        if r == -1:
            if collect_all:
                counter[0] += 1
                if counter[0] >= limit:
                    if stop_event is not None:
                        stop_event.set()
                    return True
                return False
            else:
                self._final_board = board
                return True

        sorted_vals = sorted(
            cands, key=lambda v: self.count_impact(board, candidates, r, c, v))
        for val in sorted_vals:
            if stop_event is not None and stop_event.is_set():
                return False
            board[r][c] = val
            if self.backtrack(board, collect_all, limit, counter, stop_event):
                return True
            board[r][c] = 0
        return False

    def solve(self, board):
        self._final_board = None
        ok = self.backtrack([row[:] for row in board])
        return self._final_board if ok else None

    def count_solutions(self, board, limit=20000, num_threads=8):
        board = [row[:] for row in board]
        candidates, heap = self.build_candidates(board)
        if not self.propagate(board, candidates, heap):
            return 0
        r, c, cands = self.find_mrv_cell(board, candidates, heap)
        if r == -1:
            return 1

        root_vals = list(cands)
        stop_event = threading.Event()
        lock = threading.Lock()
        total_counter = [0]

        def rec(bd, local_counter):
            if stop_event.is_set():
                return True
            bd2 = [row[:] for row in bd]
            cands2, heap2 = self.build_candidates(bd2)
            if not self.propagate(bd2, cands2, heap2):
                return False
            rr, cc, ccands = self.find_mrv_cell(bd2, cands2, heap2)
            if rr == -1:
                with lock:
                    total_counter[0] += 1
                    if total_counter[0] >= limit:
                        stop_event.set()
                local_counter[0] += 1
                return stop_event.is_set()
            srt = sorted(ccands,
                         key=lambda v: self.count_impact(bd2, cands2, rr, cc, v))
            for v in srt:
                if stop_event.is_set():
                    return True
                bd2[rr][cc] = v
                if rec(bd2, local_counter):
                    return True
                bd2[rr][cc] = 0
            return False

        def worker(vals_chunk):
            local_counter = [0]
            for val in vals_chunk:
                if stop_event.is_set():
                    break
                b = [row[:] for row in board]
                b[r][c] = val
                rec(b, local_counter)

        chunks = [[] for _ in range(num_threads)]
        for i, v in enumerate(root_vals):
            chunks[i % num_threads].append(v)

        threads = []
        for ch in chunks:
            if not ch:
                continue
            th = threading.Thread(target=worker, args=(ch,), daemon=True)
            threads.append(th)
            th.start()
        for th in threads:
            th.join()
        return total_counter[0]

    # ============================================================
    #  校验
    # ============================================================
    def find_conflict(self, board):
        """
        查找第一个冲突位置。
        返回 (r, c, val, reason) 或 None。
        """
        n, m = self.grid_h, self.grid_w

        # 行冲突
        for r in range(n):
            seen = {}
            for c in range(m):
                v = board[r][c]
                if v == 0:
                    continue
                if v in seen:
                    return (r, c, v,
                            f"与第 {seen[v] + 1} 列同行重复")
                seen[v] = c

        # 列冲突
        for c in range(m):
            seen = {}
            for r in range(n):
                v = board[r][c]
                if v == 0:
                    continue
                if v in seen:
                    return (r, c, v,
                            f"与第 {seen[v] + 1} 行同列重复")
                seen[v] = r

        # 宫冲突
        b_h, b_w = self.box_h, self.box_w
        for r0 in range(0, n, b_h):
            for c0 in range(0, m, b_w):
                seen = {}
                for r in range(r0, min(r0 + b_h, n)):
                    for c in range(c0, min(c0 + b_w, m)):
                        v = board[r][c]
                        if v == 0:
                            continue
                        if v in seen:
                            pr, pc = seen[v]
                            return (r, c, v,
                                    f"与第 {pr + 1} 行第 {pc + 1} 列同宫重复")
                        seen[v] = (r, c)

        # 数值越界
        for r in range(n):
            for c in range(m):
                v = board[r][c]
                if v != 0 and not (self.min_num <= v <= self.max_num):
                    return (r, c, v,
                            f"超出允许范围 [{self.min_num}, {self.max_num}]")

        return None

    def is_valid_board(self, board):
        return self.find_conflict(board) is None

    def is_complete(self, board):
        n, m = self.grid_h, self.grid_w
        for r in range(n):
            for c in range(m):
                if board[r][c] == 0:
                    return False
        return self.is_valid_board(board)