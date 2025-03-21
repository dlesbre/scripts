from typing import Literal, TypeVar, Union

from .display import Display

C = TypeVar("C")

Number = Union[int, float]
STR_OR_NUM = Union[str, Number]

SEPARATOR: Literal["---"] = "---"
HEADERS: Literal["headers"] = "headers"
TableRow = list[str | None] | Literal["---", "headers"]
TableValue = list[TableRow]

Alignement = Literal["l", "c", "r"]


def cast_alignement(x: str) -> Alignement:
    x = x.lower()
    if x == "l":
        return "l"
    elif x == "c":
        return "c"
    elif x == "r":
        return "r"
    raise ValueError(x + " is not a valid alignment")


class Table:
    """Pretty print tables"""

    headers: list[str] | None
    values: list[TableRow]
    width: int
    column_sep: str
    column_align: list[Alignement]
    header_style: str

    def __init__(
        self,
        values: list[TableRow],
        headers: list[str] | None = None,
        column_align: list[Alignement] | str | None = None,
        column_sep: str = " ",
        header_style: str = "{ST:bold}",
    ) -> None:
        self.headers = headers
        self.values = values
        self.width = len(self.values[0])
        self.column_sep = column_sep
        if headers is not None and len(headers) != self.width:
            raise ValueError(
                "Table has width {}, but only received {} headers".format(
                    self.width, len(headers)
                )
            )
        if column_align is None:
            self.column_align = ["l"] * self.width
        else:
            self.column_align = [cast_alignement(x) for x in column_align]
        if len(self.column_align) != self.width:
            raise ValueError(
                "Table has width {}, but only received {} column aligns".format(
                    self.width, len(self.column_align)
                )
            )
        self.header_style = header_style

    def compute_widths(self) -> list[int]:
        """Return a list of widths for each column"""
        widths = [0] * self.width
        if self.headers is not None:
            for i, hd in enumerate(self.headers):
                widths[i] = Display.len(hd)
        for row in self.values:
            if row == SEPARATOR or row == HEADERS:
                continue
            for i, x in enumerate(row):
                if x is not None:
                    widths[i] = max(widths[i], Display.len(x))
        return widths

    def justify(self, cell: str | None, align: Alignement, width: int) -> str:
        """return cell padded to the specified width"""
        if cell is None:
            cell = ""
        difference = len(cell) - Display.len(cell)
        if align == "l":
            return cell.ljust(width + difference)
        elif align == "c":
            return cell.center(width + difference)
        elif align == "r":
            return cell.rjust(width + difference)

    def render(self) -> str:
        """Render the table as a string"""
        render = ""
        widths = self.compute_widths()

        if self.headers is not None:
            headers = self.header_style
            for i, header in enumerate(self.headers):
                headers += self.justify(header, "l", widths[i])
                if i + 1 < self.width:
                    headers += self.column_sep
                else:
                    headers += "\n"
            headers += "{Reset}"
        render += headers
        sum_widths = sum(widths) + len(self.column_sep) * (self.width - 1)
        separator = "-" * sum_widths + "\n"
        for row in self.values:
            if row == SEPARATOR:
                render += separator
                continue
            if row == HEADERS:
                if self.headers is None:
                    raise ValueError("headers in table without headers")
                render += headers
                continue
            for i, cell in enumerate(row):
                render += self.justify(cell, self.column_align[i], widths[i])
                if i + 1 < self.width:
                    render += self.column_sep
                else:
                    render += "\n"

        return render
