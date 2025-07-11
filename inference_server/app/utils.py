import numpy as np


def softmax(x: np.ndarray) -> np.ndarray:
    """
    Compute the softmax of a vector or array of scores.

    The softmax function converts a vector of raw scores into
    probabilities that sum to 1. It is commonly used in
    classification tasks.
    :param x: (np.ndarray) Input array of scores.
    :return: np.ndarray Softmax probabilities with the same shape as the input.
    """
    e_x = np.exp(x - np.max(x))
    return e_x / e_x.sum()
