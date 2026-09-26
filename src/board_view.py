# board_view.py
import tkinter as tk


BOLD_GAP = 4
THIN_GAP = 1


class BoardView:
    """网格绘制 + 格子交互 + 尺寸计算。"""

    def __init__(self, parent, model, box_w, box_h, on_cell_click=None):
        self.parent = parent
        self.model = model
        self.box_w = box_w
        self.box_h = box_h
        self.on_cell_click = on_cell_click

        self.CELL_PX = 50
        self.cells = []
        self.selected_cell = None

        # 作答模式状态（由 solve.AnswerSession 控制）
        self.answer_mode = False
        self.answer_values = None

        self.grid_frame = tk.Frame(parent, bg="#5A5A5A", bd=2, relief=tk.SOLID)
        self.grid_frame.pack()

    # ---------- 尺寸 ----------
    def calc_cell_px(self, grid_w, grid_h):
        max_side = max(grid_w, grid_h)
        if max_side <= 6:
            return 60
        elif max_side <= 9:
            return 55
        elif max_side <= 12:
            return 45
        elif max_side <= 16:
            return 38
        elif max_side <= 20:
            return 32
        else:
            return 26

    def grid_pixel_width(self, grid_w, box_w):
        total = 0
        for c in range(grid_w):
            total += self.CELL_PX
            total += BOLD_GAP if (c == 0 or c % box_w == 0) else THIN_GAP
        total += BOLD_GAP
        return total

    def grid_pixel_height(self, grid_h, box_h):
        total = 0
        for r in range(grid_h):
            total += self.CELL_PX
            total += BOLD_GAP if (r == 0 or r % box_h == 0) else THIN_GAP
        total += BOLD_GAP
        return total

    # ---------- 绘制 ----------
    def draw(self, grid_w, grid_h, box_w, box_h):
        self.box_w = box_w
        self.box_h = box_h
        self.CELL_PX = self.calc_cell_px(grid_w, grid_h)

        for w in self.grid_frame.winfo_children():
            w.destroy()
        for r in range(30):
            self.grid_frame.grid_rowconfigure(r, weight=0, minsize=0)
        for c in range(30):
            self.grid_frame.grid_columnconfigure(c, weight=0, minsize=0)

        cell_px = self.CELL_PX
        font_size = max(9, int(cell_px * 0.42))
        self.font_normal = ("Consolas", font_size)
        self.font_fixed = ("Consolas", font_size, "bold")
        self.font_solved = ("Consolas", font_size, "bold")

        self.cells = [[None] * grid_w for _ in range(grid_h)]

        for r in range(grid_h):
            self.grid_frame.grid_rowconfigure(r, minsize=cell_px)
            for c in range(grid_w):
                self.grid_frame.grid_columnconfigure(c, minsize=cell_px)

                is_col_bold = (c % box_w == 0)
                is_row_bold = (r % box_h == 0)
                left = BOLD_GAP if is_col_bold else THIN_GAP
                top = BOLD_GAP if is_row_bold else THIN_GAP
                right = BOLD_GAP if c == grid_w - 1 else 0
                bottom = BOLD_GAP if r == grid_h - 1 else 0

                cell = tk.Label(self.grid_frame, text="", width=1, height=1,
                                font=self.font_normal, bg="white",
                                relief=tk.FLAT, borderwidth=0)
                cell.grid(row=r, column=c, padx=(left, right),
                          pady=(top, bottom), sticky="nsew")
                cell.grid_propagate(False)
                cell.bind("<Button-1>",
                          lambda e, row=r, col=c: self._on_click(row, col))
                self.cells[r][c] = cell

        self.selected_cell = None

    # ---------- 交互 ----------
    def _on_click(self, r, c):
        self.set_selected(r, c)
        if self.on_cell_click:
            self.on_cell_click(r, c)

    def set_selected(self, r, c):
        if self.selected_cell:
            pr, pc = self.selected_cell
            self._restore_cell_bg(pr, pc)

        self.selected_cell = (r, c)
        self.cells[r][c].config(bg="#cce6ff")

    def _restore_cell_bg(self, r, c):
        if self.answer_mode and self.answer_values is not None:
            if self.model.original_fixed[r][c]:
                self.cells[r][c].config(bg="white")
            else:
                if self.answer_values[r][c] == 0:
                    self.cells[r][c].config(bg="white")
                else:
                    self.cells[r][c].config(bg="#aaddff")
        else:
            if (not self.model.original_fixed[r][c]
                    and self.model.solution[r][c] != 0
                    and self.model.board[r][c] == 0):
                self.cells[r][c].config(bg="#e6f2ff")
            else:
                self.cells[r][c].config(bg="white")

    def move_selected(self, dr, dc, grid_w, grid_h):
        if not self.selected_cell:
            return
        r, c = self.selected_cell
        nr = min(max(r + dr, 0), grid_h - 1)
        nc = min(max(c + dc, 0), grid_w - 1)
        self.set_selected(nr, nc)

    # ---------- 刷新 ----------
    def render_all(self):
        n, m = self.model.grid_h, self.model.grid_w
        for r in range(n):
            for c in range(m):
                val = self.model.board[r][c]
                if val == 0:
                    self.cells[r][c].config(text="", bg="white",
                                            font=self.font_normal)
                else:
                    self.cells[r][c].config(text=str(val), fg="black",
                                            bg="white", font=self.font_fixed)

    def render_solution(self):
        n, m = self.model.grid_h, self.model.grid_w
        for r in range(n):
            for c in range(m):
                if not self.model.original_fixed[r][c]:
                    self.cells[r][c].config(text=str(self.model.solution[r][c]),
                                            fg="#0066cc", bg="#e6f2ff",
                                            font=self.font_solved)
                else:
                    self.cells[r][c].config(text=str(self.model.solution[r][c]),
                                            fg="black", bg="white",
                                            font=self.font_fixed)

    # ---------- 作答视图 ----------
    def enter_answer_mode(self, user_answers):
        self.answer_mode = True
        self.answer_values = user_answers
        n, m = self.model.grid_h, self.model.grid_w
        for r in range(n):
            for c in range(m):
                if self.model.original_fixed[r][c]:
                    self.cells[r][c].config(text=str(self.model.board[r][c]),
                                            fg="black", bg="white",
                                            font=self.font_fixed)
                else:
                    self.cells[r][c].config(text="", bg="white",
                                            font=self.font_normal)

    def exit_answer_mode(self):
        self.answer_mode = False
        self.answer_values = None

    def update_answer_cell(self, r, c, val):
        """只更新一个格子的作答内容 + 底色，不重绘整个棋盘。"""
        if val == 0:
            if self.selected_cell == (r, c):
                self.cells[r][c].config(text="", bg="#cce6ff",
                                        font=self.font_normal)
            else:
                self.cells[r][c].config(text="", bg="white",
                                        font=self.font_normal)
        else:
            if self.selected_cell == (r, c):
                self.cells[r][c].config(text=str(val), fg="black",
                                        bg="#cce6ff", font=self.font_fixed)
            else:
                self.cells[r][c].config(text=str(val), fg="black",
                                        bg="#aaddff", font=self.font_fixed)

    def set_cell_text(self, r, c, val, bg=None, selected=False):
        if bg is None:
            bg = "#cce6ff" if selected else "white"
        if val == 0:
            self.cells[r][c].config(text="", bg=bg, font=self.font_normal)
        else:
            self.cells[r][c].config(text=str(val), fg="black", bg=bg,
                                    font=self.font_fixed)

    def set_cell_bg(self, r, c, bg):
        self.cells[r][c].config(bg=bg)