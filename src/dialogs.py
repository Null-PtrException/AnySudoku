# dialogs.py
import tkinter as tk
from tkinter import messagebox
import re


class ImportDialog:
    """导入棋盘文本弹窗。"""

    def __init__(self, parent, model, box_w, box_h,
                 min_num, max_num, on_loaded):
        self.model = model
        self.box_w = box_w
        self.box_h = box_h
        self.min_num = min_num
        self.max_num = max_num
        self.on_loaded = on_loaded

        self.dlg = tk.Toplevel(parent)
        self.dlg.title("导入棋盘文本")
        self.dlg.transient(parent)
        self.dlg.grab_set()
        self.dlg.geometry("560x460")

        tk.Label(self.dlg, text="粘贴棋盘文本（空格请用 . 表示；不支持 0）:",
                 font=("Arial", 10)).pack(anchor="w", padx=10, pady=(10, 4))

        self.text_widget = tk.Text(self.dlg, font=("Consolas", 15),
                                   width=30, height=15, wrap=tk.NONE)
        self.text_widget.pack(padx=10, pady=4)
        self.text_widget.insert("1.0", self.model.to_text(box_w, box_h))

        btn_bar = tk.Frame(self.dlg)
        btn_bar.pack(fill=tk.X, padx=10, pady=10)

        tk.Button(btn_bar, text="导入", command=self._do_import,
                  font=("Arial", 11, "bold"), bg="#ccffcc", width=10
                  ).pack(side=tk.RIGHT, padx=4)
        tk.Button(btn_bar, text="取消", command=self.dlg.destroy,
                  font=("Arial", 11), width=10).pack(side=tk.RIGHT, padx=4)

    def _do_import(self):
        content = self.text_widget.get("1.0", tk.END)
        ok, msg = self._parse(content)
        if not ok:
            messagebox.showerror("导入失败", msg, parent=self.dlg)
            return
        self.dlg.destroy()
        if self.on_loaded:
            self.on_loaded()

    def _parse(self, content):
        n, m = self.model.grid_h, self.model.grid_w
        rows = []
        for raw_line in content.splitlines():
            line = raw_line.strip()
            if not line:
                continue
            if re.fullmatch(r"[\s\-\+\|]+", line):
                continue
            tokens = re.findall(r"[0-9]+|\.", line)
            if not tokens:
                continue
            rows.append(tokens)

        if len(rows) != n:
            return False, f"行数不匹配：期望 {n} 行，实际解析到 {len(rows)} 行。"

        new_board = [[0] * m for _ in range(n)]
        for r, tokens in enumerate(rows):
            if len(tokens) != m:
                return False, f"第 {r+1} 行列数不匹配：期望 {m} 列，实际 {len(tokens)} 列。"
            for c, tok in enumerate(tokens):
                if tok == ".":
                    new_board[r][c] = 0
                else:
                    try:
                        val = int(tok)
                    except ValueError:
                        return False, f"第 {r+1} 行第 {c+1} 列无法识别：{tok}"
                    if val == 0:
                        return False, (
                            f"第 {r+1} 行第 {c+1} 列出现 0："
                            f"空格请使用 . 表示，不支持 0。"
                        )
                    if not (self.min_num <= val <= self.max_num):
                        return False, (
                            f"第 {r+1} 行第 {c+1} 列数字 {val} "
                            f"不在范围 [{self.min_num}, {self.max_num}] 内。"
                        )
                    new_board[r][c] = val

        self.model.load_matrix(new_board)
        return True, "OK"


class GenDialog:
    """自动出题弹窗。默认已知数按棋盘尺寸分档。"""

    def __init__(self, parent, grid_w, grid_h, on_start):
        self.on_start = on_start
        self.grid_w = grid_w
        self.grid_h = grid_h
        total = grid_w * grid_h

        if total <= 16:          # 4×4
            self.default_unique = 7
            self.default_multi = 5
        elif total <= 36:        # 6×6
            self.default_unique = 12
            self.default_multi = 8
        elif total <= 81:        # 9×9
            self.default_unique = 24
            self.default_multi = 17
        else:
            self.default_unique = max(8, int(total * 0.30))
            self.default_multi = max(6, int(total * 0.22))

        self.default_unique = min(self.default_unique, total - 1)
        self.default_multi = min(self.default_multi, total - 1)

        self.dlg = tk.Toplevel(parent)
        self.dlg.title("自动出题")
        self.dlg.transient(parent)
        self.dlg.grab_set()
        self.dlg.geometry("320x240")
        self.dlg.resizable(False, False)

        self.mode = tk.StringVar(value="unique")

        tk.Label(self.dlg, text="出题类型：", font=("Arial", 11)).pack(
            anchor="w", padx=12, pady=(12, 4))

        self.givens_entry = tk.Entry(self.dlg, width=8,
                                     font=("Arial", 10), justify=tk.CENTER)

        def on_mode_change():
            self.givens_entry.delete(0, tk.END)
            if self.mode.get() == "unique":
                self.givens_entry.insert(0, str(self.default_unique))
            else:
                self.givens_entry.insert(0, str(self.default_multi))

        tk.Radiobutton(self.dlg, text="唯一解", variable=self.mode,
                       value="unique", font=("Arial", 11),
                       command=on_mode_change).pack(anchor="w", padx=24)
        tk.Radiobutton(self.dlg, text="多解", variable=self.mode,
                       value="multi", font=("Arial", 11),
                       command=on_mode_change).pack(anchor="w", padx=24)

        tk.Label(self.dlg, text="最少已知数：",
                 font=("Arial", 10)).pack(anchor="w", padx=12, pady=(10, 2))
        self.givens_entry.insert(0, str(self.default_unique))
        self.givens_entry.pack(anchor="w", padx=24)

        btn_bar = tk.Frame(self.dlg)
        btn_bar.pack(fill=tk.X, padx=12, pady=12)
        tk.Button(btn_bar, text="开始出题", command=self._do_gen,
                  font=("Arial", 11, "bold"), bg="#ccffcc", width=10
                  ).pack(side=tk.RIGHT, padx=4)
        tk.Button(btn_bar, text="取消", command=self.dlg.destroy,
                  font=("Arial", 11), width=10).pack(side=tk.RIGHT, padx=4)

    def _do_gen(self):
        try:
            min_givens = int(self.givens_entry.get())
        except ValueError:
            messagebox.showerror("错误", "最少已知数必须是整数",
                                 parent=self.dlg)
            return
        total = self.grid_w * self.grid_h
        if min_givens < 1 or min_givens > total - 1:
            messagebox.showerror(
                "错误",
                f"最少已知数必须在 1 ~ {total - 1} 之间",
                parent=self.dlg)
            return
        self.dlg.destroy()
        if self.on_start:
            self.on_start(self.mode.get(), min_givens)


class AnswerDialog:
    """
    校验结果窗口：
    - 原始题目：白底黑字
    - 用户填对：绿底，显示正确答案
    - 用户填错 / 未填：红底，显示正确答案
    """

    def __init__(self, parent, user_answers, solution, original_fixed,
                 box_w, box_h):
        self.dlg = tk.Toplevel(parent)
        self.dlg.title("校验结果")
        self.dlg.transient(parent)
        self.dlg.grab_set()

        n = len(solution)
        m = len(solution[0]) if n > 0 else 0

        frame = tk.Frame(self.dlg, bg="#5A5A5A", bd=2, relief=tk.SOLID)
        frame.pack(padx=12, pady=12)

        cell_px = 40 if max(n, m) <= 12 else 32
        font_size = max(10, int(cell_px * 0.45))
        font = ("Consolas", font_size, "bold")

        BOLD_GAP = 4
        THIN_GAP = 1

        for r in range(n):
            frame.grid_rowconfigure(r, minsize=cell_px)
            for c in range(m):
                frame.grid_columnconfigure(c, minsize=cell_px)

                val = solution[r][c]

                if original_fixed[r][c]:
                    bg = "white"
                elif user_answers[r][c] == val:
                    bg = "#99ff99"
                else:
                    bg = "#ff9999"

                is_col_bold = (c % box_w == 0)
                is_row_bold = (r % box_h == 0)
                left = BOLD_GAP if is_col_bold else THIN_GAP
                top = BOLD_GAP if is_row_bold else THIN_GAP
                right = BOLD_GAP if c == m - 1 else 0
                bottom = BOLD_GAP if r == n - 1 else 0

                lbl = tk.Label(frame, text=str(val), width=1, height=1,
                               font=font, bg=bg, fg="black",
                               relief=tk.FLAT, borderwidth=0)
                lbl.grid(row=r, column=c, padx=(left, right),
                         pady=(top, bottom), sticky="nsew")
                lbl.grid_propagate(False)

        legend = tk.Frame(self.dlg)
        legend.pack(pady=6)

        def legend_item(color, text):
            tk.Label(legend, text="  ", bg=color, width=2,
                     relief=tk.SOLID, borderwidth=1).pack(side=tk.LEFT)
            tk.Label(legend, text=text, font=("Arial", 10)).pack(
                side=tk.LEFT, padx=(2, 12))

        legend_item("#99ff99", "正确")
        legend_item("#ff9999", "错误 / 未填")
        legend_item("white", "题目")

        total_blank = 0
        correct = 0
        for r in range(n):
            for c in range(m):
                if not original_fixed[r][c]:
                    total_blank += 1
                    if user_answers[r][c] == solution[r][c]:
                        correct += 1
        rate_text = f"填空正确率：{correct}/{total_blank}"
        tk.Label(self.dlg, text=rate_text, font=("Arial", 11, "bold")
                 ).pack(pady=(0, 6))

        tk.Button(self.dlg, text="关闭", command=self.dlg.destroy,
                  font=("Arial", 11), width=10).pack(pady=(0, 12))