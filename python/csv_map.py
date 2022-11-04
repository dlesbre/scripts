#!/usr/bin/env python3
from argparse import ArgumentParser
from csv import reader, writer
from typing import Callable, Generic, TypeVar
from pathlib import Path

MapType = Callable[[int, list[str]], list | None]
T = TypeVar("T")

TCSVMap = TypeVar("TCSVMap", bound="CSVMap", covariant=True)


class CSVMap(Generic[T]):
    """Class used to perform a map/filter operation on a CSV
    Use a subclass which overrides the map method
    Usage:
    >>> cm = CSVMap()
    >>> cm.read(path_to_file) # or initialize cm.rows_in directly
    >>> cm()
    >>> cm.write(path_to_file) # or do something with cm.rows_out
    """

    def __init__(self) -> None:
        self.rows_in: list[list[str]] = []
        self.rows_out: list[list[T]] = []

    def map(self, index: int, row: list[str]) -> list[T] | None:
        """The map/filter function for a given row, overwrite in subclasses"""
        raise ValueError("VIRTUAL METHOD, should be overwritten")

    def read(self, path: Path):
        """Initialize self.rows_in with the contents of file"""
        with open(path, "r") as file:
            csv_reader = reader(file)
            for row in csv_reader:
                self.rows_in.append(row)

    def write(self, path: Path):
        """Write the content of self.rows_out to the given file"""
        with open(path, "w") as file:
            csv_writer = writer(file)
            csv_writer.writerows(self.rows_out)

    def __call__(self) -> list[list[T]]:
        """Performs the map operation"""
        for i, row in enumerate(self.rows_in):
            result = self.map(i, row)
            if result is not None:
                self.rows_out.append(result)
        return self.rows_out

    @classmethod
    def from_files(cls: type[TCSVMap], input: Path, output: Path) -> TCSVMap:
        """Shorthand for read/compute/write when using files"""
        c = cls()
        c.read(input)
        c()
        c.write(output)
        return c


class CSVFilter(CSVMap[str]):
    """Subclass of CSVMap used when simply filtering,
    override the filter method to use"""

    def map(self, index: int, row: list[str]) -> list[str] | None:
        if self.filter(index, row):
            return row
        return None

    def filter(self, index: int, row: list[str]) -> bool:
        raise ValueError("VIRTUAL METHOD, should be overwritten")


class FilterColumnNotIn(CSVFilter):
    column: int = 0
    filter_out: set[str] = {"", "0", " "}

    def filter(self, _index: int, row: list[str]) -> bool:
        return len(row) > self.column and row[self.column] not in self.filter_out


parser = ArgumentParser("csv_map.py")
parser.add_argument("input", type=Path)
parser.add_argument("output", type=Path, nargs="?", default=Path("./output.csv"))

if __name__ == "__main__":
    args = parser.parse_args()
    FilterColumnNotIn.from_files(args.input, args.output)
