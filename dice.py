from random import randint


def d12() -> int:
    return randint(1, 12)

def d12_less(target: int) -> bool:
    """
    Returns:
        bool: Returns true if the d12 hits the target or less
    """
    return d12() <= target