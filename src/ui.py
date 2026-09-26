# ui.py
import tkinter as tk

from model import BoardModel
from board_view import BoardView
from main_window import MainWindow
from controller import Controller


class SudokuSolverGUI:
    def __init__(self, root):
        self.root = root
        self.window = MainWindow(root)

        self.model = BoardModel(9, 9)
        self.board_view = BoardView(self.window.grid_area, self.model,
                                    3, 3,
                                    on_cell_click=self._on_cell_click)

        self.controller = Controller(root, self.window,
                                     self.board_view, self.model)

        self.board_view.draw(9, 9, 3, 3)
        self.window.bind_commands(self.controller)
        self.window.bind_keys(self.controller)
        root.focus_set()

    def _on_cell_click(self, r, c):
        self.root.focus_set()