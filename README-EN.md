# AnySudoku

An all-in-one Sudoku toolkit: solve, generate, play, and validate puzzles of any size.

---

## Features

- **Solve**: NumPy-accelerated solver with MRV + LCV heuristics and constraint propagation.
- **Generate**: Unique-solution and multi-solution modes, with customizable minimum givens.
- **Play**: Built-in answer mode with keyboard input and automatic validation.
- **Validate**: Highlights correct, incorrect, and unfilled cells after submission.
- **Multi-solution counting**: Counts the number of solutions, with multi-threaded acceleration.
- **Arbitrary grid size**: Supports custom box width, box height, horizontal and vertical box counts — not limited to 9×9.
- **Custom number range**: Configurable minimum and maximum numbers.

---

## Screenshots

> Add screenshots here, e.g. main window, answer mode, validation result.

```
screenshots/main.png
screenshots/answer.png
screenshots/check.png
```

---

## Requirements

- Python 3.8+
- NumPy
- Tkinter (bundled with Python; on some Linux distributions it must be installed separately)

Install dependencies:

```bash
pip install numpy
```

On Linux, if Tkinter is missing:

```bash
sudo apt install python3-tk
```

---

## Run

```bash
python main.py
```

---

## Project Structure

```
AnySudoku/
├── main.py              # Entry point
├── ui.py                # GUI assembly
├── main_window.py       # Main window widgets and layout
├── board_view.py        # Board rendering and interaction
├── controller.py        # Business logic dispatch
├── model.py             # Board data model
├── ans.py               # Sudoku solver core
├── que.py               # Puzzle generator
├── solve.py             # Answer mode state machine
├── dialogs.py           # Import / generate / validation dialogs
├── task_hub.py          # Background task manager
├── tasks.py             # Background task wrapper
├── README.md
└── LICENSE
```

---

## How to Use

1. **Set board size**
   Enter box width, box height, horizontal box count, and vertical box count in the top control bar, then click "Apply Board Size".

2. **Import a puzzle**
   Click "Import Text", paste the board text, using `.` for empty cells, for example:

   ```
   5 3 . | . 7 . | . . .
   6 . . | 1 9 5 | . . .
   . 9 8 | . . . | . 6 .
   ------+-------+------
   8 . . | . 6 . | . . 3
   4 . . | 8 . 3 | . . 1
   7 . . | . 2 . | . . 6
   ------+-------+------
   . 6 . | . . . | 2 8 .
   . . . | 4 1 9 | . . 5
   . . . | . 8 . | . 7 9
   ```

3. **Auto generate**
   Click "Auto Generate", choose unique or multi-solution mode, set the minimum number of givens, and start.

4. **Solve**
   Click "Solve", the program solves the puzzle, displays the answer, and counts the number of solutions.

5. **Answer mode**
   Click "Start Answering" to enter answer mode. Use the keyboard to input numbers, `Backspace` / `Delete` to clear.
   Click "Submit" to see the validation result.

6. **Clear**
   - "Clear Board": clears everything.
   - "Clear Solution Only": keeps the puzzle, removes the solved result.

---

## Keyboard Shortcuts

| Key | Action |
|---|---|
| Arrow keys | Move selected cell |
| Number keys | Fill in a number |
| Backspace / Delete | Clear current cell |
| Enter | Submit / confirm (in some dialogs) |

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## Acknowledgements

- The solver core is inspired by classic constraint-satisfaction heuristics such as MRV (Minimum Remaining Values) and LCV (Least Constraining Value).
- Thanks to everyone who provided suggestions and feedback.

---

**AnySudoku** — Solve, generate, play, and validate Sudoku of any size.