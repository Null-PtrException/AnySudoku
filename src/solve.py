# solve.py
import tkinter as tk
from tkinter import messagebox

from dialogs import AnswerDialog


class AnswerSession:
    """
    作答模式状态机（纯 UI 逻辑，不做后台计算）：
    - idle      未进入作答
    - answering 正在作答
    - submitted 已提交，等待用户点“结束作答”

    求答案的耗时操作由 ui 层通过 BackgroundTask 完成，
    完成后调用 begin_with_solution(sol) 进入作答。
    """

    IDLE = "idle"
    ANSWERING = "answering"
    SUBMITTED = "submitted"

    def __init__(self, root, board_view, model,
                 answer_btn, solve_btn, set_status_text,
                 min_num, max_num):
        self.root = root
        self.board_view = board_view
        self.model = model
        self.answer_btn = answer_btn
        self.solve_btn = solve_btn
        self.set_status_text = set_status_text

        self.min_num = min_num
        self.max_num = max_num

        self.state = self.IDLE
        self.user_answers = None
        self.solution_backup = None

    # ============================================================
    #  对外接口
    # ============================================================
    @property
    def active(self):
        return self.state != self.IDLE

    @property
    def submitted(self):
        return self.state == self.SUBMITTED

    @property
    def answering(self):
        return self.state == self.ANSWERING

    def begin_with_solution(self, sol):
        """由 ui 层求好答案后调用，进入作答模式。"""
        self.solution_backup = sol
        self.user_answers = [[0] * self.model.grid_w
                             for _ in range(self.model.grid_h)]
        self.state = self.ANSWERING

        self.answer_btn.config(text="提交答案", bg="#ffcc99")
        self.solve_btn.config(state=tk.DISABLED)
        self.set_status_text("作答中", "#0066cc")

        self.board_view.selected_cell = None
        self.board_view.enter_answer_mode(self.user_answers)

    def submit(self):
        """提交答案，弹出校验窗口；保留作答显示，等待用户点“结束作答”。"""
        if self.state != self.ANSWERING:
            return

        n, m = self.model.grid_h, self.model.grid_w
        blanks = 0
        for r in range(n):
            for c in range(m):
                if (not self.model.original_fixed[r][c]
                        and self.user_answers[r][c] == 0):
                    blanks += 1
        if blanks > 0:
            if not messagebox.askyesno(
                    "提示",
                    f"还有 {blanks} 个空格未填，是否仍然提交？"):
                return

        AnswerDialog(self.root, self.user_answers, self.solution_backup,
                     self.model.original_fixed,
                     self.board_view.box_w, self.board_view.box_h)

        self.state = self.SUBMITTED
        self.answer_btn.config(text="结束作答", bg="#ccffcc")
        self.set_status_text("已提交", "#009900")

    def exit(self):
        """退出作答模式，恢复普通视图。"""
        if self.state == self.IDLE:
            return
        self.state = self.IDLE
        self.user_answers = None
        self.solution_backup = None

        self.board_view.exit_answer_mode()
        self.board_view.render_all()

        self.answer_btn.config(state=tk.NORMAL, text="开始作答", bg="#ffddaa")
        self.solve_btn.config(state=tk.NORMAL)
        self.set_status_text("未计算", "#333333")

    def handle_key(self, r, c, event):
        """
        作答模式下的键盘处理。
        返回 True 表示已消费该事件。
        """
        if self.state == self.IDLE:
            return False
        if self.state == self.SUBMITTED:
            return True
        if self.model.original_fixed[r][c]:
            return True

        key = event.char
        if key.isdigit():
            val = int(key)
            if val < self.min_num:
                val = self.min_num
            elif val > self.max_num:
                val = self.max_num
            self.user_answers[r][c] = val
            self.board_view.update_answer_cell(r, c, val)
            return True
        elif event.keysym in ('BackSpace', 'Delete'):
            self.user_answers[r][c] = 0
            self.board_view.update_answer_cell(r, c, 0)
            return True
        return True

    def update_num_range(self, min_num, max_num):
        self.min_num = min_num
        self.max_num = max_num