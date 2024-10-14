from math import sqrt
from typing import Generic, TypeVar

N = TypeVar("N", int, float)


class Stats(Generic[N]):
    """Compute various statistical indicators for a list of numbers"""

    size: int
    sum: N
    max: N
    min: N
    sum_squares: N
    average: float
    median: N | float
    q1: N | float
    q3: N | float
    variance: float
    std_deviation: float
    deviation_percent: int  # standard deviation as a percent of the mean

    def __init__(self, items: list[N]) -> None:
        self.size = len(items)
        self.sum = sum(items)
        self.sum_squares = sum(x * x for x in items)
        if self.size != 0:
            self.average = self.sum / self.size
            self.variance = (self.sum_squares / self.size) - (
                self.average * self.average
            )
            self.std_deviation = sqrt(self.variance)
            self.deviation_percent = int(self.std_deviation * 100.0 / self.average)
            sorted_items = sorted(items)
            self.min = items[0]
            self.max = items[-1]
            self.median, median_indices = self.find_median(sorted_items)
            if self.size >= 3:
                self.q1, _ = self.find_median(sorted_items[: median_indices[0]])
                self.q3, _ = self.find_median(sorted_items[median_indices[-1] + 1 :])
            else:
                self.q1 = self.median
                self.q3 = self.median

    def find_median(self, sorted_list: list[N]) -> tuple[N | float, list[int]]:
        indices = []
        list_size = len(sorted_list)
        half = list_size // 2
        if list_size % 2 == 0:
            indices.append(half - 1)  # -1 because index starts from 0
            indices.append(half)
            return (sorted_list[indices[0]] + sorted_list[indices[1]]) / 2, indices
        indices.append(half)
        return sorted_list[indices[0]], indices


class DiffStats(Generic[N]):
    """Various stats for diffs between two lists of numbers"""

    diff: Stats[N]  # Stats for the diffs 'b - a'
    diff_normalized: Stats[float]  # Stats for the normalized diff '(b - a) / a'
    positive: Stats[N]  # Stats for positive diffs 'b - a when > 0'
    negative: Stats[N]  # Stats for the negative diffs 'b - a when < 0'

    def __init__(self, a: list[N], b: list[N]) -> None:
        assert len(a) == len(b)
        diffs = [b[i] - a[i] for i in range(len(a))]
        self.diff = Stats(diffs)
        self.diff_normalized = Stats(
            [diffs[i] / a[i] for i in range(len(a)) if a[i] != 0]
        )
        self.positive = Stats([x for x in diffs if x > 0])
        self.negative = Stats([x for x in diffs if x < 0])
