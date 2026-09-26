# controller.py
import tkinter as tk
from tkinter import messagebox

from ans import SudokuSolver
from que import SudokuGenerator
from dialogs import ImportDialog, GenDialog
from solve import AnswerSession
from task_hub import TaskHub


MULTI_SOLVE_LIMIT = 20000
MULTI_SOLVE_TIME_TRIGGER = 0.2


class Controller:
    """业务调度：求解、出题、导入、作答、清空、应用设置、键盘交互。"""

    def __init__(self, root, window, board_view, model):
        self.root = root
        self.window = window
        self.board_view = board_view
        self.model = model

        # 棋盘配置
        self.box_w = 3
        self.box_h = 3
        self.num_boxes_x = 3
        self.num_boxes_y = 3
        self.min_num = 1
        self.max_num = 9

        self.grid_w = self.num_boxes_x * self.box_w
        self.grid_h = self.num_boxes_y * self.box_h

        self.solver = SudokuSolver(self.box_w, self.box_h,
                                   self.num_boxes_x, self.num_boxes_y,
                                   self.min_num, self.max_num)

        # 后台任务
        self.tasks = TaskHub(
            root, self.solver, SudokuGenerator,
            self.box_w, self.box_h, self.num_boxes_x, self.num_boxes_y,
            self.min_num, self.max_num,
            MULTI_SOLVE_LIMIT,
            on_solve=self._on_solve_done,
            on_count=self._on_count_done,
            on_gen=self._on_gen_done,
            on_answer=self._on_answer_solve_done,
        )

        # 作答会话
        self.answer_session = AnswerSession(
            root, board_view, model,
            window.answer_btn, window.solve_btn,
            window.set_solution_count_text,
            self.min_num, self.max_num,
        )

    # ============================================================
    #  应用棋盘大小
    # ============================================================
    def apply_settings(self):
        self.answer_session.exit()
        self.read_num_range()

        try:
            bw, bh, nx, ny = self.window.get_board_size()
        except ValueError:
            messagebox.showerror("错误", "请输入有效的整数！")
            return
        if bw <= 0 or bh <= 0 or nx <= 0 or ny <= 0:
            messagebox.showerror("错误", "宫格相关数值必须大于0！")
            return

        # 自动把最大数设为 宫宽 × 宫高，最小数 1
        self.min_num = 1
        self.max_num = bw * bh
        self.window.set_num_range(self.min_num, self.max_num)
        self.answer_session.update_num_range(self.min_num, self.max_num)

        total = bw * nx * bh * ny
        num_range = self.max_num - self.min_num + 1
        if num_range < max(bw * nx, bh * ny, bw * bh):
            messagebox.showerror(
                "错误",
                f"候选数范围 [{self.min_num}, {self.max_num}] 太小，"
                f"无法覆盖棋盘所需。"
            )
            return

        self.box_w = bw
        self.box_h = bh
        self.num_boxes_x = nx
        self.num_boxes_y = ny
        self.grid_w = bw * nx
        self.grid_h = bh * ny

        self.model.reset(self.grid_w, self.grid_h)
        self.solver = SudokuSolver(self.box_w, self.box_h,
                                   self.num_boxes_x, self.num_boxes_y,
                                   self.min_num, self.max_num)

        # 重建 TaskHub（因为求解器/尺寸变了）
        self.tasks = TaskHub(
            self.root, self.solver, SudokuGenerator,
            self.box_w, self.box_h, self.num_boxes_x, self.num_boxes_y,
            self.min_num, self.max_num,
            MULTI_SOLVE_LIMIT,
            on_solve=self._on_solve_done,
            on_count=self._on_count_done,
            on_gen=self._on_gen_done,
            on_answer=self._on_answer_solve_done,
        )

        self.board_view.draw(self.grid_w, self.grid_h,
                             self.box_w, self.box_h)
        self.window.set_solution_count_text("未计算", "#333333")

    # ============================================================
    #  导入
    # ============================================================
    def open_import_dialog(self):
        self.answer_session.exit()

        def on_loaded():
            self.board_view.render_all()
            self.window.set_solution_count_text("未计算", "#333333")
            conflict = self.solver.find_conflict(self.model.board)
            if conflict is not None:
                r, c, val, reason = conflict
                messagebox.showwarning(
                    "注意",
                    f"棋盘已加载，但检测到冲突：\n"
                    f"第 {r + 1} 行 第 {c + 1} 列 的数字 {val} {reason}。"
                )
            else:
                messagebox.showinfo("导入成功", "棋盘已加载！")

        ImportDialog(self.root, self.model, self.box_w, self.box_h,
                     self.min_num, self.max_num, on_loaded)

    # ============================================================
    #  出题
    # ============================================================
    def open_gen_dialog(self):
        self.answer_session.exit()

        def on_start(mode, min_givens):
            self._start_generate(mode, min_givens)
        GenDialog(self.root, self.grid_w, self.grid_h, on_start)

    def _start_generate(self, mode, min_givens):
        if self.tasks.gen.running:
            messagebox.showinfo("提示", "正在出题中，请稍候……")
            return
        self.window.gen_btn.config(state=tk.DISABLED, text="出题中…")
        self.window.set_solution_count_text("出题中…", "#0066cc")
        self.tasks.gen.start(mode, min_givens)

    def _on_gen_done(self, kind, payload):
        self.window.gen_btn.config(state=tk.NORMAL, text="自动出题")
        if kind == "ok":
            puzzle, _full = payload
            if puzzle is None:
                self.window.set_solution_count_text("出题失败", "#cc0000")
                messagebox.showerror("出题失败", "未能生成符合条件的题目，请重试。")
            else:
                self.model.load_matrix(puzzle)
                self.board_view.render_all()
                self.window.set_solution_count_text("未计算", "#333333")
                messagebox.showinfo("出题完成", "题目已生成并加载！")
        else:
            self.window.set_solution_count_text("出题出错", "#cc0000")
            messagebox.showerror("出题出错", str(payload))

    # ============================================================
    #  清空
    # ============================================================
    def clear_board(self):
        self.answer_session.exit()
        self.model.clear_board()
        self.board_view.render_all()
        self.window.set_solution_count_text("未计算", "#333333")

    def clear_solution_only(self):
        self.answer_session.exit()
        self.model.clear_solution_only()
        self.board_view.render_all()
        self.window.set_solution_count_text("未计算", "#333333")

    # ============================================================
    #  数字范围
    # ============================================================
    def read_num_range(self, event=None):
        self.min_num, self.max_num = self.window.get_num_range(
            self.min_num, self.max_num)
        self.answer_session.update_num_range(self.min_num, self.max_num)

    # ============================================================
    #  作答
    # ============================================================
    def answer_clicked(self):
        s = self.answer_session
        if s.state == AnswerSession.IDLE:
            self._prepare_answer()
        elif s.state == AnswerSession.ANSWERING:
            s.submit()
        else:
            s.exit()

    def _prepare_answer(self):
        board = [row[:] for row in self.model.board]
        conflict = self.solver.find_conflict(board)
        if conflict is not None:
            r, c, val, reason = conflict
            messagebox.showerror(
                "错误",
                f"当前盘面存在冲突：\n"
                f"第 {r + 1} 行 第 {c + 1} 列 的数字 {val} {reason}。\n\n"
                f"请检查并修正该位置后再进入作答模式。"
            )
            return
        if self.tasks.answer.running:
            return
        self.window.answer_btn.config(state=tk.DISABLED, text="准备中…")
        self.window.set_solution_count_text("准备中…", "#0066cc")
        self.tasks.answer.start(board)

    def _on_answer_solve_done(self, kind, payload):
        self.window.answer_btn.config(state=tk.NORMAL)
        if kind != "ok":
            self.window.answer_btn.config(text="开始作答", bg="#ffddaa")
            self.window.set_solution_count_text("出错", "#cc0000")
            messagebox.showerror("错误", f"准备作答失败：{payload}")
            return
        sol, _cost = payload
        if sol is None:
            self.window.answer_btn.config(text="开始作答", bg="#ffddaa")
            self.window.set_solution_count_text("无解", "#cc0000")
            messagebox.showerror("错误", "当前题目无解，无法进入作答模式。")
            return
        self.answer_session.begin_with_solution(sol)

    # ============================================================
    #  求解
    # ============================================================
    def solve_clicked(self):
        if self.answer_session.active:
            return
        if self.tasks.solve.running:
            messagebox.showinfo("提示", "正在计算中，请稍候……")
            return

        self.read_num_range()

        board_to_solve = [row[:] for row in self.model.board]
        max_cells = max(self.grid_w, self.grid_h, self.box_w * self.box_h)
        num_range = self.max_num - self.min_num + 1
        if num_range < max_cells:
            if not messagebox.askyesno(
                    "提示",
                    f"候选数范围大小 ({num_range}) 小于最大格子数 "
                    f"({max_cells})，数学上可能无解。\n是否继续？"):
                return

        conflict = self.solver.find_conflict(board_to_solve)
        if conflict is not None:
            r, c, val, reason = conflict
            messagebox.showerror(
                "错误",
                f"当前盘面存在冲突：\n"
                f"第 {r + 1} 行 第 {c + 1} 列 的数字 {val} {reason}。"
            )
            return

        self.window.solve_btn.config(state=tk.DISABLED, text="计算中…")
        self.window.set_solution_count_text("计算中…", "#0066cc")
        self.tasks.solve.start(board_to_solve)

    def _on_solve_done(self, kind, payload):
        self.window.solve_btn.config(state=tk.NORMAL, text="开始计算")

        if kind == "ok":
            sol, cost = payload
            if sol is not None:
                self.model.solution = sol
                self.board_view.render_solution()
                messagebox.showinfo("完成", f"计算完成！耗时: {cost:.4f} 秒")
                if cost < MULTI_SOLVE_TIME_TRIGGER:
                    self.window.set_solution_count_text("统计中…", "#0066cc")
                    self.tasks.count.start(
                        [row[:] for row in self.model.board])
                else:
                    self.window.set_solution_count_text(
                        "未统计（耗时较长）", "#888888")
            else:
                self.window.set_solution_count_text("无解", "#cc0000")
                messagebox.showerror("无解", f"无解！耗时: {cost:.4f} 秒")
        else:
            self.window.set_solution_count_text("出错", "#cc0000")
            messagebox.showerror("错误", f"计算出错：{payload}")

    # ============================================================
    #  多解统计
    # ============================================================
    def _on_count_done(self, kind, payload):
        if kind == "ok":
            count = payload
            if count >= MULTI_SOLVE_LIMIT:
                self.window.set_solution_count_text(
                    f">{MULTI_SOLVE_LIMIT}", "#cc6600")
            elif count == 1:
                self.window.set_solution_count_text("唯一解", "#009900")
            elif count == 0:
                self.window.set_solution_count_text("无解", "#cc0000")
            else:
                self.window.set_solution_count_text(f"{count} 个解", "#cc6600")
        else:
            self.window.set_solution_count_text("统计出错", "#cc0000")

    # ============================================================
    #  键盘交互
    # ============================================================
    def on_key_press(self, event):
        if isinstance(self.root.focus_get(), tk.Entry):
            return
        if not self.board_view.selected_cell:
            return

        if event.keysym == 'Up':
            self.board_view.move_selected(-1, 0, self.grid_w, self.grid_h)
            return
        elif event.keysym == 'Down':
            self.board_view.move_selected(1, 0, self.grid_w, self.grid_h)
            return
        elif event.keysym == 'Left':
            self.board_view.move_selected(0, -1, self.grid_w, self.grid_h)
            return
        elif event.keysym == 'Right':
            self.board_view.move_selected(0, 1, self.grid_w, self.grid_h)
            return

        r, c = self.board_view.selected_cell

        if self.answer_session.active:
            self.answer_session.handle_key(r, c, event)
            return

        key = event.char
        if key.isdigit():
            val = int(key)
            if val < self.min_num:
                val = self.min_num
            elif val > self.max_num:
                val = self.max_num
            self._set_cell(r, c, val)
        elif event.keysym in ('BackSpace', 'Delete'):
            self._set_cell(r, c, 0)

    def _set_cell(self, r, c, val):
        self.model.set_cell(r, c, val)
        self.board_view.set_cell_text(r, c, val, selected=True)
        self.window.set_solution_count_text("未计算", "#333333")