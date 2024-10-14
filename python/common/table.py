from typing import TypeVar, Union

C = TypeVar("C")

Number = Union[int, float]
STR_OR_NUM = Union[str, Number]


class Table:
    headers: list[str]
    values: list[C]
    keys: list[C]

    def __init__(self, values, keys: list[str | int] | int | None = None):
        if isinstance(values, list):
            self.values = values
        else:
            self.values = list(values)
        if keys is None:
            if not isinstance(self.values[0], list):
                try:
                    self.values = [list(x) for x in self.values]
                except TypeError:
                    raise ValueError("Table keys argument must be specified unless")
            self.keys = list(range(len(self.values[0])))
        elif isinstance(keys, int):
            self.keys = list(range(len(self.values[0])))
        else:
            self.keys = keys

    def get_cell(self, key: str | int, value: C):
        try:
            if isinstance(key, str) and hasattr(value, key):
                return getattr(value, key)
            return value[key]  # type: ignore
        except (KeyError, AttributeError, IndexError):
            return None


MILLION = "\033[31mM\033[37m"
THOUSAND = "\033[33mk\033[37m"


class Table2:
    """Used to pretty-print a table"""

    table: list[list[STR_OR_NUM]]
    widths: list[int]

    column_delimiter: str = " "  # "|"
    line_delimiter: str = "-"
    cross_delimiter: str = "+"

    odd_row_format: str = ""

    footer = 2

    def column_width(self, column: int) -> int:
        """Compute the width of a column"""
        width = 0
        for row in self.table:
            elt = row[column]
            if isinstance(elt, float):
                elt = round(elt, 2)
                if len(str(elt)) >= 4:
                    elt = round(elt)
            if (isinstance(elt, int) or isinstance(elt, float)) and elt > 1_000:
                if elt > 1_000_000:
                    elt = str(round(elt / 1_000_000)) + "M"
                else:
                    elt = str(round(elt / 1_000)) + "k"
            width = max(width, len(str(elt)))
        return width

    def pad_column(self, column: int, pad_numbers_right: bool = True) -> list[str]:
        """Create a padded version of the column"""
        width = self.widths[column]
        padded = list()
        for row in self.table:
            elt = row[column]
            if isinstance(elt, float):
                elt = round(elt, 2)
                if len(str(elt)) >= 4:
                    elt = round(elt)
            if isinstance(elt, int) or isinstance(elt, float):
                extra_width = 0  # extra width to account for ANSI codes
                if elt > 1_000_000:
                    elt = str(round(elt / 1_000_000)) + MILLION
                    extra_width = len(MILLION) - 1
                elif elt > 1_000:
                    elt = str(round(elt / 1_000)) + THOUSAND
                    extra_width = len(THOUSAND) - 1
                if pad_numbers_right:
                    padded.append(str(elt).rjust(width + extra_width))
                else:
                    padded.append(str(elt).ljust(width + extra_width))
            elif pad_numbers_right and elt == "--":
                padded.append(str(elt).rjust(width))
            else:
                padded.append(str(elt).ljust(width))
        return padded

    def __init__(self, values: list[list[STR_OR_NUM]]) -> None:
        self.table = values
        self.widths = [self.column_width(i) for i in range(len(values[0]))]

    def pp_ascii_line_sep(self, use_ansi: bool) -> None:
        sep = self.cross_delimiter.join(
            self.line_delimiter * width for width in self.widths
        )
        if use_ansi:
            sep = "\033[1;32m" + sep + "\033[0m"
        print(sep)

    def pp_ascii(self, use_ansi: bool) -> None:
        """Render as ascii and print to stdout"""
        padded = [self.pad_column(i) for i in range(len(self.widths))]
        # self.pp_ascii_line_sep(use_ansi)
        bg_colors = ("\033[48;5;17m", "\033[48;5;16m")  # blue, black
        if use_ansi:
            # Bold first line
            print("\033[1;32;4;48;5;16m", end="")
        size = len(padded[0])
        for row in range(size):
            if row == size - self.footer:
                bg_colors = (bg_colors[1], bg_colors[0])
                if use_ansi:
                    print(bg_colors[row % 2], end="")
                self.pp_ascii_line_sep(use_ansi)
            text = self.column_delimiter.join(col[row] for col in padded)
            if use_ansi:
                if row == 0:
                    text = "\033[1;32;4;48;5;16m" + text + "\033[0m"
                else:
                    text = "\033[37m" + bg_colors[row % 2] + text + "\033[0m"
            print(text)
            if row == 0 and not use_ansi:
                self.pp_ascii_line_sep(use_ansi)
        # self.pp_ascii_line_sep(use_ansi)
