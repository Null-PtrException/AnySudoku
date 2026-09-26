# tasks.py
import threading
import queue
import time


class BackgroundTask:
    """通用后台任务封装：线程 + 队列 + 主线程轮询。"""

    def __init__(self, root, worker, on_done, poll_ms=100):
        self.root = root
        self.worker = worker
        self.on_done = on_done
        self.poll_ms = poll_ms
        self.queue = queue.Queue()
        self._running = False
        self._poll()

    @property
    def running(self):
        return self._running

    def start(self, *args, **kwargs):
        if self._running:
            return False
        self._running = True
        t = threading.Thread(target=self._run, args=args,
                             kwargs=kwargs, daemon=True)
        t.start()
        return True

    def _run(self, *args, **kwargs):
        try:
            result = self.worker(*args, **kwargs)
            self.queue.put(("ok", result))
        except Exception as e:
            self.queue.put(("error", str(e)))

    def _poll(self):
        try:
            while True:
                kind, payload = self.queue.get_nowait()
                self._running = False
                try:
                    self.on_done(kind, payload)
                except Exception:
                    pass
        except queue.Empty:
            pass
        self.root.after(self.poll_ms, self._poll)


def solve_worker(solver, board):
    start = time.time()
    sol = solver.solve(board)
    cost = time.time() - start
    return sol, cost


def count_worker(solver, board, limit, num_threads):
    return solver.count_solutions(board, limit=limit, num_threads=num_threads)


def generate_worker(gen_cls, mode, min_givens,
                    box_w, box_h, num_x, num_y, min_num, max_num):
    gen = gen_cls(box_w, box_h, num_x, num_y, min_num, max_num)
    if mode == "unique":
        puzzle, full = gen.generate_puzzle(unique=True,
                                           min_givens=min_givens,
                                           tolerance=2)
    else:
        puzzle, full = gen.generate_multi(min_solutions=2,
                                          target_solutions=10,
                                          max_solutions=200,
                                          min_givens=min_givens)
    return puzzle, full