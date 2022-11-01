from typing import NamedTuple, Callable, Iterator, Any
from logger import Logger
from datetime import date
from re import match
from pathlib import Path
from os import listdir
from subprocess import run, PIPE
from dataclasses import dataclass
from csv import writer

logger = Logger("Fortuneo reader")


@dataclass
class Transaction:
    transaction_date: date
    payee: str
    amount: int
    true_date: date
    payee_normalized: str
    notes: str = ""

    def __iter__(self) -> Iterator[Any]:
        yield self.true_date
        yield self.transaction_date
        yield self.payee_normalized
        yield self.payee
        yield self.amount / 100
        yield self.notes


class ParseResult(NamedTuple):
    data: list[Transaction]
    nb_debit: int
    nb_credit: int
    total_credit: int
    total_debit: int
    old_total: int
    new_total: int
    has_warnings: bool = False


AMOUNT_REGEX = r"\d{1,3} \d\d\d,\d\d|\d+,\d\d"


def is_credit(line: str):
    return len(line) in [
        142,
        143,
        144,
        145,
        146,
        147,
        148,
        149,
        150,
        151,
        152,
        153,
        154,
        155,
        156,
        157,
        158,
        159,
        160,
        161,
        162,
        163,
        164,
        165,
        166,
        167,
        168,
        169,
        170,
        216,
        217,
        218,
        219,
        220,
    ]


def get_amount(amount: str) -> int:
    """Parses an amount into a int"""
    return int(amount.replace(",", "").replace(" ", ""))


def pp_amount(amount: int) -> str:
    return "{:,.2f} €".format(amount / 100).replace(",", " ").replace(".", ",")


def parse_line(line: str, is_credit: Callable[[str], bool]) -> Transaction | None:
    """Parse a single transaction line"""
    regex = r"^ +\d\d/\d\d +(\d\d)/(\d\d)/(\d\d\d\d)\s+(.*?)\s+(" + AMOUNT_REGEX + ")$"
    m = match(regex, line)
    if m is None:
        return None
    true_time = time = date(day=int(m[1]), month=int(m[2]), year=int(m[3]))
    pn = payee = m[4]
    amount = get_amount(m[5])
    if not is_credit(line):
        amount *= -1

    m2 = match(r"CARTE (\d\d)/(\d\d)", payee)
    if m2 is not None:
        true_time = date(day=int(m2[1]), month=int(m2[2]), year=time.year)
        pn = "CARTE" + payee[11:]
    return Transaction(
        transaction_date=time,
        payee=payee,
        amount=amount,
        true_date=true_time,
        payee_normalized=pn,
    )


def parse_txt(plain_file: str, is_credit: Callable[[str], bool]) -> ParseResult:
    """Parse a plaintext representation of the PDF file"""
    data = []
    nb_debit = 0
    nb_credit = 0
    total_credit = -1
    total_debit = -1
    old_total = -1
    new_total = -1
    measured_credit = 0
    measured_debit = 0

    lines = plain_file.split("\n")
    add_extra_lines_as_memo = False

    for ii, line in enumerate(lines):
        result = parse_line(line, is_credit)
        if result is not None:
            data.append(result)
            if result.amount >= 0:
                nb_credit += 1
                measured_credit += result.amount
            else:
                nb_debit += 1
                measured_debit -= result.amount
            add_extra_lines_as_memo = True
        else:
            # Special lines
            m = match("^\\s+ANCIEN SOLDE .*?(" + AMOUNT_REGEX + ")", line)
            if m is not None:
                amount = get_amount(m[1])
                if old_total != -1:
                    logger.warn(
                        f"Mulitple matches for OLD TOTAL : {pp_amount(old_total)} and {pp_amount(amount)}"
                    )
                old_total = amount
                add_extra_lines_as_memo = False
                continue

            m = match("^\\s+NOUVEAU SOLDE CRÉDITEUR .*?(" + AMOUNT_REGEX + ")", line)
            if m is not None:
                amount = get_amount(m[1])
                if new_total != -1:
                    logger.warn(
                        f"Mulitple matches for NEW TOTAL : {pp_amount(new_total)} and {pp_amount(amount)}"
                    )
                new_total = amount
                add_extra_lines_as_memo = False
                continue

            m = match(
                f"^\\s+TOTAL DES OPÉRATIONS DU RELEVÉ .*?({AMOUNT_REGEX})  \\s+({AMOUNT_REGEX})",
                line,
            )
            if m is not None:
                amount_debit = get_amount(m[1])
                if total_debit != -1:
                    logger.warn(
                        f"Mulitple matches for AMOUNT DEBIT : {pp_amount(total_debit)} and {pp_amount(amount_debit)}"
                    )
                total_debit = amount_debit
                amount_credit = get_amount(m[2])
                if total_credit != -1:
                    logger.warn(
                        f"Mulitple matches for AMOUNT CREDIT : {pp_amount(total_credit)} and {pp_amount(amount_credit)}"
                    )
                total_credit = amount_credit
                add_extra_lines_as_memo = False
                continue
            if not line.isspace() and line:
                if "Relevé de Compte" in line:
                    add_extra_lines_as_memo = False
                if add_extra_lines_as_memo:
                    if data[-1].notes:
                        data[-1].notes += "\n"
                    data[-1].notes += line.strip()
                logger.debug(f"{ii+1:3} {line.strip()}")

    has_warnings = False
    if old_total == -1:
        logger.warn("OLD TOTAL not found")
        has_warnings = True
    if new_total == -1:
        logger.warn("OLD TOTAL not found")
        has_warnings = True
    if total_debit == -1:
        logger.warn("AMOUNT DEBIT not found")
        has_warnings = True
    elif total_debit != measured_debit:
        logger.warn(
            f"Transaction debit doesn't add up : bank {pp_amount(total_debit)} is not my {pp_amount(measured_debit)}"
        )
        has_warnings = True
    if total_credit == -1:
        logger.warn("AMOUNT CREDIT not found")
        has_warnings = True
    elif total_credit != measured_credit:
        logger.warn(
            f"Transaction credit doesn't add up : bank {pp_amount(amount_credit)}"
            f" is not my {pp_amount(measured_credit)}"
        )
        has_warnings = True
    if new_total - old_total != total_credit - total_debit:
        logger.warn(
            f"Total mismatch: actual {pp_amount(new_total - old_total)}"
            f", measured: {pp_amount(total_credit - total_debit)}"
        )
        has_warnings = True
    data.sort(key=lambda x: x.true_date)
    return ParseResult(
        data,
        nb_debit,
        nb_credit,
        total_credit,
        total_debit,
        old_total,
        new_total,
        has_warnings,
    )


def parse_pdf(path: Path) -> ParseResult:
    proc = run(f"less '{path}'", stdout=PIPE, shell=True)
    if proc.returncode != 0:
        logger.error("Could not parse '{path}'")
        exit(1)
    text = proc.stdout.decode()
    res = parse_txt(text, is_credit)
    if res.has_warnings:
        res1 = parse_txt(text, lambda _: False)
        if not res1.has_warnings:
            logger.info("{FgGreen}FIXED{Reset} warnings with all debit")
            res = res1
        else:
            res1 = parse_txt(text, lambda _: True)
            if not res1.has_warnings:
                logger.info("{FgGreen}FIXED{Reset} warnings with all credit")
                res = res1
    if not res.data:
        logger.info("Processed  0 transactions from '{path}'")
    else:
        total = res.total_credit - res.total_debit
        color = "{FgRed}" if total < 0 else "{FgGreen}"
        logger.verbose_info(
            f"Processed {res.nb_debit + res.nb_credit:2} transactions from '{path}'\n"
            f"    Dates:   {res.data[0].transaction_date} and {res.data[-1].transaction_date}\n"
            f"    Credit:  {{FgGreen}}{pp_amount(res.total_credit):>11}{{Reset}} in {res.nb_credit:2} transactions\n"
            f"    Debit:   {{FgRed}}{pp_amount(res.total_debit):>11}{{Reset}} in {res.nb_debit:2} transactions\n"
            f"    Total:   {color}{pp_amount(total):>11}{{Reset}}\n"
            f"    Balance: {pp_amount(res.old_total):>11} -> {pp_amount(res.new_total):>11}"
        )
        if res.has_warnings:
            with open("./less.md", "wb") as file:
                file.write(proc.stdout)
            exit(1)
    return res


# logger.set_verbosity(2)
def parse_all_in(folder: Path) -> list[ParseResult]:
    files = listdir(folder)
    res = []
    for file in files:
        res.append(parse_pdf(folder / file))
    res.sort(key=lambda x: x.data[0].true_date)
    return res


def safe_csv(value: str):
    return value.replace('"', '""')


def to_csv(contents: list[ParseResult], path: Path) -> None:
    transactions = [y for x in contents for y in x.data]
    with open(path, "w") as file:
        w = writer(file)
        for transaction in transactions:
            w.writerow(transaction)


res = parse_all_in(Path("/home/dorian/Downloads/Releves de compte/"))
to_csv(res, Path("./fortuneo_transactions.csv"))
