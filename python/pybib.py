#!/home/dorian/Documents/Github/scripts/python/venv/bin/python3

from pathlib import Path
from argparse import ArgumentParser
from os import rename

try:
    from bibtexautocomplete import BibtexAutocomplete
    from bibtexautocomplete.bibtex.author import Author
    from bibtexautocomplete.bibtex.normalize import normalize_str
except ImportError:
    print("Error: btac not found.")
    exit(1)

OBS_PATH = Path("/home/dorian/Documents/Obsidian")
if not OBS_PATH.exists():
    print(f"Error: could not find obsidiant path {OBS_PATH}")
    exit(2)

BIBLIO_PATH = OBS_PATH / "07 Recherche" / "Biblio"

try:
    from pypdf import PdfReader

    def read_pdf_title(pdf_file_path: Path) -> str | None:
        """Try to obtain the title of a pdf"""
        try:
            with open(pdf_file_path, "rb") as f:
                pdf_reader = PdfReader(f)
                return pdf_reader.metadata.title
        except IOError:
            print("Error reading file")
            return None
except ImportError:

    def read_pdf_title(pdf_file_path: Path) -> str | None:
        print("Warning: pyPdf not found.")
        return None


parser = ArgumentParser(
    "pybib",
    usage="pybib PDF_FILE",
    description="Generate an obsidian note for the given PDF",
)
parser.add_argument("input", type=Path)

file = parser.parse_args().input


title = read_pdf_title(file)
if title is None or title.strip() == "":
    title = input("Could not read title, please specify one manually: ")
else:
    other = input(f"Read title as:\n  '{title}'\nIf incorrect, please specify correct title, else leave blank: ")
    if other:
        title = other

print("\nFinding bibliographic information:")

completer = BibtexAutocomplete()
completer.load_entry({"title": title, "ENTRYTYPE": "article", "ID": "pybib"})
completer.autocomplete()
result = completer.write_entry()[0][0]

print("\nFound the following bib:")
for key in result:
    if key not in ("ID", "ENTRYTYPE"):
        print(f"  {key} = {{{result[key]}}},")
print()

key = "unknown"
authors = []
if "author" in result:
    authors = Author.from_namelist(result["author"])
    key = authors[0].lastname
if "year" in result:
    key += str(result["year"])
else:
    key += "XXXX"

BASIC_WORDS = [
    "a",
    "the",
    "in",
    "of",
    "with",
    "on",
    "to",
    "an",
    "as",
    "at",
    "by",
    "for",
    "or",
    "and",
]

ntitle = normalize_str(title)
key += "_".join(x for x in ntitle.split(" ") if x not in BASIC_WORDS).capitalize()

nkey = input(f"Selected key: {key}.\nPress ENTER to confirm, else enter new key: ")
if nkey != "":
    key = nkey

print()

target = BIBLIO_PATH / "PDFs" / (key + ".pdf")
rename(file, target)
print(f"Moved pdf file to {target}")

md_content = "---\nconference:\n"
if "year" in result:
    md_content += f"year: {result['year']}\n"
if "doi" in result:
    md_content += f"doi: {result['doi']}\n"

md_content += f"""type: biblio
key: {key}
aliases: {key}
title: {title}
read-status: "intro|skimmed|basic|good|advanced"
---
# {title}

**Mot clés**::
**Fichier**:: [[{key}.pdf]]
**Diapos**::

"""
for author in authors:
    name = author.lastname
    if author.firstnames is not None:
        name = author.firstnames + " " + author.lastname
    md_content += f"**Auteurs:** [[{name}]]\n"

md_content += f"""

> [!Abstract]
> abstract goes here

```bibtex
@article{{{key},\n"""
for key in result:
    if key not in ("ID", "ENTRYTYPE"):
        md_content += f"  {key} = {{{result[key]}}},\n"
md_content += "}\n```\n"

md = BIBLIO_PATH / (ntitle.capitalize() + ".md")
i = 0

while md.exists():
    i += 1
    md = BIBLIO_PATH / (ntitle.capitalize() + "_" + str(i) + ".md")
with open(md, "w") as md_file:
    md_file.write(md_content)
print(f"Initialized obsidian note at {md_file}")
