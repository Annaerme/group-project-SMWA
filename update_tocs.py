"""
update_tocs.py

Gebruik (vanuit de projectroot, notebooks gesloten of opgeslagen):
    python update_tocs.py
"""
import json, re, sys, uuid
from pathlib import Path
from urllib.parse import quote

ROOT       = Path(__file__).parent
SKIP       = {"A. Lectures", "data_retrieval"}
TOC_MARKER = "<!-- toc -->"


def get_notebooks():
    return sorted(
        p for p in ROOT.rglob("*.ipynb")
        if not any(part in SKIP for part in p.parts)
        and p.name != "project_overview.ipynb"
        and p.read_text(encoding="utf-8").strip()
    )


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def save(path, nb):
    path.write_text(json.dumps(nb, ensure_ascii=False, indent=1), encoding="utf-8")


def heading_items(nb, skip_toc=True, skip_title=False):
    """(level, title, anchor) voor alle markdown-headings.
    skip_title=True slaat de eerste # titelregel over (vermijdt dubbele vermelding)."""
    items = []
    title_seen = False
    for cell in nb["cells"]:
        if cell["cell_type"] != "markdown":
            continue
        src = "".join(cell["source"])
        if skip_toc and TOC_MARKER in src:
            continue
        for line in src.splitlines():
            if not line.startswith("#"):
                continue
            level = len(line) - len(line.lstrip("#"))
            title = line.lstrip("#").strip()
            anchor = re.sub(r"[^\w\s-]", "", title.lower())
            anchor = re.sub(r"\s+", "-", anchor.strip())
            # Sla de allereerste # titelregel over als skip_title aan staat
            if skip_title and not title_seen and level == 1:
                title_seen = True
                continue
            items.append((level, title, anchor))
    return items


def toc_source(items):
    if not items:
        return TOC_MARKER + "\n## Contents\n"
    # Normaliseer: kleinste level wordt niveau 0 (geen inspringing)
    min_lvl = min(l for l, _, _ in items)
    lines = [TOC_MARKER + "\n## Contents\n"]
    for level, title, anchor in items:
        indent = "  " * (level - min_lvl)
        lines.append(f"{indent}- [{title}](#{anchor})\n")
    return "".join(lines)


# ── Stap 1 & 2: verwijder show_toc code cel + update markdown TOC ─────────────

def find_insert_pos(cells):
    """Geeft de index direct na de eerste # titelcel, of 0 als die er niet is."""
    for i, cell in enumerate(cells):
        if cell["cell_type"] != "markdown":
            continue
        src = "".join(cell.get("source", []))
        if TOC_MARKER in src:
            continue
        # Eerste regel die begint met één enkel #
        for line in src.splitlines():
            if re.match(r"^#[^#]", line):
                return i + 1
    return 0


def process_notebook(nb_path):
    nb      = load(nb_path)
    changed = False

    # Verwijder overbodige show_toc code cellen
    keep = []
    for cell in nb["cells"]:
        src = "".join(cell.get("source", []))
        if cell["cell_type"] == "code" and "show_toc" in src and "def show_toc" not in src:
            changed = True
        else:
            keep.append(cell)
    nb["cells"] = keep

    # Nieuwe TOC berekenen (zonder TOC-cel én zonder de # titelregel)
    items      = heading_items(nb, skip_toc=True, skip_title=True)
    new_source = toc_source(items)

    # Zoek bestaande TOC-cel
    toc_idx = next(
        (i for i, c in enumerate(nb["cells"])
         if c["cell_type"] == "markdown" and TOC_MARKER in "".join(c.get("source", []))),
        None
    )
    target = find_insert_pos(nb["cells"])

    if not items:
        # Geen headings gevonden — verwijder eventuele lege TOC-cel maar voeg geen nieuwe in
        if toc_idx is not None:
            nb["cells"].pop(toc_idx)
            changed = True
        if changed:
            save(nb_path, nb)
        return changed

    if toc_idx is not None:
        # Verwijder de bestaande TOC-cel zodat we hem op de juiste plek terugzetten
        nb["cells"].pop(toc_idx)
        # Pas target aan als de verwijdering de index verschuift
        if toc_idx < target:
            target -= 1
        changed = True  # altijd opnieuw invoegen op juiste positie

    nb["cells"].insert(target, {
        "cell_type": "markdown",
        "id": uuid.uuid4().hex[:8],
        "metadata": {},
        "source": [new_source],
    })
    changed = True

    if changed:
        save(nb_path, nb)
    return changed


# ── Stap 3: project_overview.ipynb ────────────────────────────────────────────

def build_overview(notebooks):
    # Groepeer per top-level map → submap (de directe map van het notebook)
    groups = {}
    for nb_path in notebooks:
        parts  = nb_path.relative_to(ROOT).parts
        top    = parts[0]
        sub    = parts[-2] if len(parts) > 2 else ""
        groups.setdefault(top, {}).setdefault(sub, []).append(nb_path)

    lines = ["# Project Overview\n\n"]

    for top in sorted(groups):
        lines.append(f"## {top}\n\n")
        for sub in sorted(groups[top]):
            if sub and sub != top:
                lines.append(f"### {sub}\n\n")
            for nb_path in groups[top][sub]:
                rel_raw = nb_path.relative_to(ROOT).as_posix()
                # URL-encode elk padonderdeel zodat spaties (%20) e.d. kloppen in links
                rel = "/".join(quote(part, safe="") for part in rel_raw.split("/"))
                name = nb_path.stem.replace("_", " ").replace("-", " ").title()
                nb   = load(nb_path)
                # Sla titelregel over — de bold notebooknaam is al de titel
                items = heading_items(nb, skip_toc=True, skip_title=True)

                if not items:
                    lines.append(f"- [{name}]({rel})\n")
                    continue

                # Normaliseer: eerste subsectie-level wordt inspringing 1
                min_lvl = min(l for l, _, _ in items)

                lines.append(f"- **[{name}]({rel})**\n")
                for level, title, anchor in items:
                    depth  = level - min_lvl + 1   # eerste subsectie = 1 inspring
                    indent = "  " * depth
                    lines.append(f"{indent}- [{title}]({rel}#{anchor})\n")

            lines.append("\n")

    nb_struct = {
        "nbformat": 4,
        "nbformat_minor": 5,
        "metadata": {
            "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
            "language_info": {"name": "python"},
        },
        "cells": [{
            "cell_type": "markdown",
            "id": "overview00",
            "metadata": {},
            "source": ["".join(lines)],
        }],
    }
    return nb_struct


# ── Main ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    notebooks = get_notebooks()

    print("Notebooks verwerken...")
    for nb_path in notebooks:
        changed = process_notebook(nb_path)
        print(f"  {'bijgewerkt' if changed else 'ongewijzigd':<12} {nb_path.relative_to(ROOT)}")

    print("\nproject_overview.ipynb genereren...")
    save(ROOT / "project_overview.ipynb", build_overview(notebooks))
    print("  klaar")
