# main.py
import tkinter as tk
from ui import SudokuSolverGUI


if __name__ == "__main__":
    root = tk.Tk()
    app = SudokuSolverGUI(root)
    root.mainloop()