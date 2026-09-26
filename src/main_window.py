# main_window.py
import tkinter as tk


CONTROL_H = 45
BUTTON_H = 75
GRID_MARGIN = 30


class MainWindow:
    """主窗口：所有 Tk 控件、布局、尺寸。不含业务逻辑。"""

    def __init__(self, root):
        self.root = root
        root.title("自动数独求解器")

        self._create_control_bar()
        self._create_grid_area()
        self._create_button_bar()

        self._maximize_window()

    # ============================================================
    #  顶部控制栏
    # ============================================================
    def _create_control_bar(self):
        self.control_frame = tk.Frame(self.root, bg="#f0f0f0",
                                      height=CONTROL_H)
        self.control_frame.pack(side=tk.TOP, fill=tk.X)
        self.control_frame.pack_propagate(False)

        def add_label(text, pad=(4, 0)):
            tk.Label(self.control_frame, text=text, bg="#f0f0f0",
                     font=("Arial", 10)).pack(side=tk.LEFT, padx=pad)

        def add_entry(default, width=2):
            e = tk.Entry(self.control_frame, width=width,
                         font=("Arial", 10), justify=tk.CENTER)
            e.insert(0, default)
            e.pack(side=tk.LEFT, padx=2)
            return e

        add_label("宫宽:")
        self.box_w_entry = add_entry("3")
        add_label("宫高:", (8, 0))
        self.box_h_entry = add_entry("3")
        add_label("横宫数:", (8, 0))
        self.num_x_entry = add_entry("3")
        add_label("纵宫数:", (8, 0))
        self.num_y_entry = add_entry("3")
        add_label("最小数:", (8, 0))
        self.min_entry = add_entry("1")
        add_label("最大数:", (8, 0))
        self.max_entry = add_entry("9")

        self.apply_btn = tk.Button(self.control_frame,
                                   text="应用棋盘大小",
                                   bg="#cce6ff",
                                   font=("Arial", 10, "bold"))
        self.apply_btn.pack(side=tk.LEFT, padx=10)

    # ============================================================
    #  中部网格区
    # ============================================================
    def _create_grid_area(self):
        self.grid_area = tk.Frame(self.root, bg="#f0f0f0")
        self.grid_area.pack(side=tk.TOP, expand=True, fill=tk.BOTH,
                            padx=GRID_MARGIN, pady=10)

    # ============================================================
    #  底部按钮栏
    # ============================================================
    def _create_button_bar(self):
        self.btn_frame = tk.Frame(self.root, bg="#f0f0f0", height=BUTTON_H)
        self.btn_frame.pack(side=tk.BOTTOM, fill=tk.X)
        self.btn_frame.pack_propagate(False)

        self.import_btn = tk.Button(self.btn_frame, text="导入文本",
                                    font=("Arial", 12), width=10, bg="#cce6ff")
        self.import_btn.pack(side=tk.LEFT, padx=5, pady=15)

        self.clear_btn = tk.Button(self.btn_frame, text="清空棋盘",
                                   font=("Arial", 12), width=10, bg="#ffcccc")
        self.clear_btn.pack(side=tk.LEFT, padx=5, pady=15)

        self.clear_sol_btn = tk.Button(self.btn_frame, text="仅清空答案",
                                       font=("Arial", 12), width=12,
                                       bg="#ffffcc")
        self.clear_sol_btn.pack(side=tk.LEFT, padx=5, pady=15)

        self.gen_btn = tk.Button(self.btn_frame, text="自动出题",
                                 font=("Arial", 12), width=10, bg="#e6ccff")
        self.gen_btn.pack(side=tk.LEFT, padx=5, pady=15)

        self.solution_count_label = tk.Label(
            self.btn_frame, text="解数量：未计算",
            font=("Arial", 12, "bold"), bg="#f0f0f0",
            fg="#333333", width=18, anchor="w")
        self.solution_count_label.pack(side=tk.LEFT, padx=10, pady=15)

        self.solve_btn = tk.Button(self.btn_frame, text="开始计算",
                                   font=("Arial", 12, "bold"),
                                   width=12, bg="#ccffcc")
        self.solve_btn.pack(side=tk.RIGHT, padx=5, pady=15)

        self.answer_btn = tk.Button(self.btn_frame, text="开始作答",
                                    font=("Arial", 12, "bold"),
                                    width=12, bg="#ffddaa")
        self.answer_btn.pack(side=tk.RIGHT, padx=5, pady=15)

    # ============================================================
    #  绑定
    # ============================================================
    def bind_commands(self, controller):
        self.apply_btn.config(command=controller.apply_settings)
        self.import_btn.config(command=controller.open_import_dialog)
        self.clear_btn.config(command=controller.clear_board)
        self.clear_sol_btn.config(command=controller.clear_solution_only)
        self.gen_btn.config(command=controller.open_gen_dialog)
        self.solve_btn.config(command=controller.solve_clicked)
        self.answer_btn.config(command=controller.answer_clicked)

        self.min_entry.bind("<Return>", controller.read_num_range)
        self.min_entry.bind("<FocusOut>", controller.read_num_range)
        self.max_entry.bind("<Return>", controller.read_num_range)
        self.max_entry.bind("<FocusOut>", controller.read_num_range)

    def bind_keys(self, controller):
        self.root.bind("<Key>", controller.on_key_press)

    # ============================================================
    #  最大化（只做一次）
    # ============================================================
    def _maximize_window(self):
        self.root.update_idletasks()
        try:
            self.root.state('zoomed')
            return
        except tk.TclError:
            pass
        try:
            self.root.attributes('-zoomed', True)
            return
        except tk.TclError:
            pass
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        self.root.geometry(f"{sw}x{sh}+0+0")

    # ============================================================
    #  Label 快捷更新
    # ============================================================
    def set_solution_count_text(self, text, color="#333333"):
        self.solution_count_label.config(text=f"解数量：{text}", fg=color)

    # ============================================================
    #  数字范围
    # ============================================================
    def get_num_range(self, fallback_min, fallback_max):
        try:
            mn = int(self.min_entry.get())
        except ValueError:
            mn = fallback_min
            self.min_entry.delete(0, tk.END)
            self.min_entry.insert(0, str(mn))
        try:
            mx = int(self.max_entry.get())
        except ValueError:
            mx = fallback_max
            self.max_entry.delete(0, tk.END)
            self.max_entry.insert(0, str(mx))
        return mn, mx

    def set_num_range(self, mn, mx):
        self.min_entry.delete(0, tk.END)
        self.min_entry.insert(0, str(mn))
        self.max_entry.delete(0, tk.END)
        self.max_entry.insert(0, str(mx))

    # ============================================================
    #  棋盘大小
    # ============================================================
    def get_board_size(self):
        return (int(self.box_w_entry.get()),
                int(self.box_h_entry.get()),
                int(self.num_x_entry.get()),
                int(self.num_y_entry.get()))