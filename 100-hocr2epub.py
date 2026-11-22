#!/usr/bin/env python3

import glob
import os
import re
import shutil
import subprocess
import sys
import zipfile
import shlex
from datetime import datetime
from pathlib import Path

from _shared import (
    load_config,
    get_page_num,
)


src = Path("090-ocr")

# write EPUB file
# dst = Path(Path(__file__).stem + ".epub")

# write unpacked EPUB files to workdir
dst = Path(".")


config = load_config()


if dst != Path(".") and dst.exists():
    print(f"error: output exists: {dst}")
    sys.exit(1)


# downscale to 300 dpi
# 600 dpi -> 300 dpi: 90 MB -> 60 MB
scale = 300 / config.scan_resolution


hocr_to_epub_fxl = "hocr-to-epub-fxl"

# TODO dont commit
if 1:
    hocr_to_epub_fxl = "/home/user/src/archive-hocr-tools/bin/hocr-to-epub-fxl"

args = [
    hocr_to_epub_fxl,
    "--output", str(dst),
]

if dst == Path("."):
    args.append("--output-unpacked")


def git_modified():
    return subprocess.check_output(
        ["git", "show", "-s", "--format=%cI", "HEAD"],
        text=True,
    ).strip()


def stat_modified(path):
    ts = Path(path).stat().st_mtime
    dt = datetime.fromtimestamp(ts).astimezone()
    return dt.isoformat(timespec="seconds")


doc_modified = max(
    git_modified(),
    stat_modified(src),
)


args += [
    "--scale", str(scale),
    "--image-format", "avif",
    "--text-format", "html",
    # TODO? move these config items to 000-config.py
    "--doc-modified", doc_modified,
    "--doc-title", "Die digitale Entmündigung",
    "--doc-subtitle", "Daten, Vermögen, Selbstbestimmung. Wie digitale ID, Big Tech und Banken sie dir nehmen - und 47 Hacks, sie zurückzuholen.",
    # "--doc-subject", "",
    "--doc-date", "2026-11-16",
    "--doc-edition", "1",
    "--doc-extent", "128 pages",
    "--color-image-pages", "129,130",
    "--doc-author", "Alexander Schreiner",
    # "--doc-introducer", "",
    # "--doc-contributor", "",
    # "--doc-translator", "",
    "--doc-publisher", "Edition Zeitfragen",
    "--doc-language", "de", # german
    # "--doc-language", "en", # english
    "--doc-isbn", "9783985844227",
    "--doc-cover-image", "075-level/129.tiff",
    "--canonical-url-base", "https://milahu.github.io/alexander-schreiner-die-digitale-entmuendigung-2026/",
    "--doc-description", """
Wann hast du zuletzt etwas online erledigt, ohne dich auszuweisen?
Dich anzumelden? Identifiziert zu werden?

Das, was die EU als Komfort tarnt,
ist der größte Eingriff in deine Selbstbestimmung seit Generationen.

Am 2. Januar 2027 startet die EU Digital Identity Wallet – der digitale Personalausweis,
ohne den künftig kaum noch ein Behördengang, ein Bankkonto oder ein Login funktionieren soll.
52 Prozent der Deutschen haben noch nie davon gehört.

Parallel dazu läuft der digitale Euro in der Pilotphase,
die elektronische Patientenakte ist bereits da,
Chatkontrolle und Klarnamenpflicht stehen vor der Tür.

Schritt für Schritt entsteht ein System,
in dem deine Daten erfasst, dein Geld kontrolliert und deine Meinung zum Risiko wird.

Was Orwell „Gedankenverbrechen“ nannte, sind heute Klarnamenpflicht und Meldung bei staatlich finanzierten Meldestellen –
und kann strafrechtliche Konsequenzen haben, auch wenn die Äußerung eigentlich legal ist.

Die meisten Bücher zu diesem Thema beschreiben nur das Problem.
Dieses Buch zeigt dir, was du jetzt konkret tun kannst – Schritt für Schritt,
mit Anleitungen, die heute funktionieren und die du an einem Wochenende umsetzen kannst.

**In 47 erprobten Hacks lernst du:**

- Wie du deine Verbindungen, Geräte und sozialen Profile so absicherst,
  dass du keine verwertbaren Spuren mehr hinterlässt.
- Wie du eine getrennte Online-Identität aufbaust und alte Daten aus dem Netz zurückholst – inklusive deinem „Recht auf Vergessenwerden“ bei Google.
- Wie du dein Vermögen mit Bitcoin, Edelmetallen und internationalen Banken so aufstellst,
  dass keine zentrale Stelle den Zugriff darauf verweigern kann.
- Wie du der elektronischen Patientenakte gezielt Grenzen setzt, ohne den Komplettausstieg zu wagen.
- Welche Länder, Konten und Lebensmodelle dir auch dann Freiheit lassen,
  wenn die digitale ID irgendwann verpflichtend wird.

Geschrieben für alle, die Familie, Vermögen oder einfach ihre Privatsphäre schützen wollen,
ohne sich gleich aus dem modernen Alltag zu verabschieden.
Kein IT-Studium nötig.

Inklusive Videoanleitungen zu den zentralen Hacks – per QR-Code direkt aus dem Buch abrufbar.

*„Du hast mehr Einfluss auf dein Leben, als dir erzählt wird. Dieses Buch zeigt dir, wie du ihn nutzt.“* – Alexander Schreiner
""",
]


print(">", shlex.join(args + sys.argv[1:]) + f" {src}/*.hocr")


hocr_files = list(src.glob("*.hocr"))

hocr_files.sort()

subprocess.run(
    args + sys.argv[1:] + hocr_files,
    check=True,
)


if dst == Path("."):
    print("done ./index.xhtml")
    sys.exit(0)


print(f"done {dst}")


# extract the EPUB content files

# rm -rf $dst.unzip
unzip_dir = Path(str(dst) + ".unzip")
shutil.rmtree(unzip_dir, ignore_errors=True)
unzip_dir.mkdir()


# unzip -q ../$dst
with zipfile.ZipFile(dst) as z:
    z.extractall(unzip_dir)


print(f"done {unzip_dir}/index.html")
