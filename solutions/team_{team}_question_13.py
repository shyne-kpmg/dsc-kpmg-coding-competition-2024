from collections.abc import Callable  # Don't worry about what this line does


def Solution(
    # This first argument is telling you that `gradient_func` is a function
    # that takes in one float and returns one float
    gradient_func: Callable[[float], float],
    x_0: float,
    lr: float,
    n_iters: int,
) -> float:
    return ...