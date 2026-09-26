# task_hub.py
from tasks import BackgroundTask, solve_worker, count_worker, generate_worker


class TaskHub:
    """
    统一管理后台任务：
    - solve   求解（用于“开始计算”和“作答前求答案”）
    - count   多解统计
    - gen     自动出题
    """

    def __init__(self, root, solver, generator_cls,
                 box_w, box_h, num_x, num_y, min_num, max_num,
                 multi_limit, on_solve, on_count, on_gen, on_answer):
        self.solve = BackgroundTask(
            root,
            worker=lambda board: solve_worker(solver, board),
            on_done=on_solve,
        )
        self.count = BackgroundTask(
            root,
            worker=lambda board: count_worker(solver, board,
                                              multi_limit, 8),
            on_done=on_count,
        )
        self.gen = BackgroundTask(
            root,
            worker=lambda mode, givens: generate_worker(
                generator_cls, mode, givens,
                box_w, box_h, num_x, num_y, min_num, max_num
            ),
            on_done=on_gen,
        )
        self.answer = BackgroundTask(
            root,
            worker=lambda board: solve_worker(solver, board),
            on_done=on_answer,
        )

    def reconfigure(self, box_w, box_h, num_x, num_y, min_num, max_num):
        """棋盘变化后更新出题任务的参数。"""
        root = self.gen.root
        self.gen.worker = lambda mode, givens: generate_worker(
            self.gen.gen_cls, mode, givens,
            box_w, box_h, num_x, num_y, min_num, max_num
        )