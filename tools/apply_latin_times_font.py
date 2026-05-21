from __future__ import annotations

import argparse
import re
import shutil
import tempfile
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

from lxml import etree


NS = {"a": "http://schemas.openxmlformats.org/drawingml/2006/main"}
LATIN_FONT = "Times New Roman"
DEFAULT_EAST_ASIA_FONT = "Microsoft YaHei"
LATIN_RE = re.compile(r"[A-Za-z]")


def _ensure_typeface(r_pr, tag: str, typeface: str) -> None:
    child = r_pr.find(f"a:{tag}", NS)
    if child is None:
        child = etree.SubElement(r_pr, f"{{{NS['a']}}}{tag}")
    child.set("typeface", typeface)


def _run_text(run) -> str:
    return "".join(node.text or "" for node in run.findall(".//a:t", NS))


def _patch_slide_xml(blob: bytes) -> tuple[bytes, int]:
    parser = etree.XMLParser(remove_blank_text=False, recover=True)
    root = etree.fromstring(blob, parser=parser)
    patched = 0

    for paragraph in root.xpath(".//a:p", namespaces=NS):
        p_pr = paragraph.find("a:pPr", NS)
        if p_pr is None:
            p_pr = etree.Element(f"{{{NS['a']}}}pPr")
            paragraph.insert(0, p_pr)
        p_pr.set("latinLnBrk", "0")
        p_pr.set("eaLnBrk", "1")
        p_pr.set("hangingPunct", "0")

    for run in root.xpath(".//a:r|.//a:fld", namespaces=NS):
        text = _run_text(run)
        if not LATIN_RE.search(text):
            continue
        r_pr = run.find("a:rPr", NS)
        if r_pr is None:
            r_pr = etree.Element(f"{{{NS['a']}}}rPr")
            run.insert(0, r_pr)

        old_latin = r_pr.find("a:latin", NS)
        east_asia_font = DEFAULT_EAST_ASIA_FONT
        if old_latin is not None:
            candidate = old_latin.get("typeface")
            if candidate and candidate != LATIN_FONT:
                east_asia_font = candidate

        _ensure_typeface(r_pr, "ea", east_asia_font)
        _ensure_typeface(r_pr, "latin", LATIN_FONT)
        patched += 1

    return etree.tostring(root, xml_declaration=True, encoding="UTF-8", standalone=True), patched


def patch_pptx(path: Path) -> int:
    path = path.resolve()
    patched_runs = 0
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir) / path.name
        with ZipFile(path, "r") as zin, ZipFile(tmp_path, "w", ZIP_DEFLATED) as zout:
            for item in zin.infolist():
                data = zin.read(item.filename)
                if item.filename.startswith("ppt/slides/slide") and item.filename.endswith(".xml"):
                    data, patched = _patch_slide_xml(data)
                    patched_runs += patched
                zout.writestr(item, data)
        shutil.move(str(tmp_path), str(path))
    return patched_runs


def main() -> None:
    parser = argparse.ArgumentParser(description="Set Latin letters in PPT slide text to Times New Roman.")
    parser.add_argument("paths", nargs="+", type=Path)
    args = parser.parse_args()

    pptx_paths: list[Path] = []
    for path in args.paths:
        if path.is_dir():
            pptx_paths.extend(sorted(p for p in path.rglob("*.pptx") if not p.name.startswith("~$")))
        else:
            if not path.name.startswith("~$"):
                pptx_paths.append(path)

    for path in pptx_paths:
        try:
            patched = patch_pptx(path)
            print(f"patched {patched:04d} text runs | {path}")
        except PermissionError:
            print(f"locked; skipped | {path}")


if __name__ == "__main__":
    main()
