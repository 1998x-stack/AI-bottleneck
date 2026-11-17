#!/usr/bin/env python3
"""Build a dependency-free static Pages bundle and optional DOCX report downloads.

Run: python scripts/build_site.py
If python-docx is installed, generate Word downloads for every Markdown research report.
"""
from __future__ import annotations
import json
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
SOURCE = ["index.html","styles.css","app.js","markdown.js"]
DIRS = ["assets","catalog","reports"]

def export_docx(markdown: Path, output: Path) -> None:
    from docx import Document
    from docx.shared import Cm, Pt
    from docx.oxml.ns import qn
    doc = Document()
    sec=doc.sections[0]
    sec.top_margin=sec.bottom_margin=Cm(2)
    sec.left_margin=sec.right_margin=Cm(2.1)
    style=doc.styles['Normal']
    style.font.name='Calibri'
    style.font.size=Pt(10)
    style._element.rPr.rFonts.set(qn('w:eastAsia'),'Microsoft YaHei')
    text=markdown.read_text(encoding='utf-8')
    code=False
    for line in text.splitlines():
        raw=line.rstrip()
        if raw.strip().startswith('\\\\\\\\'):
            continue
        if raw.startswith('```'):
            code=not code
            continue
        if not raw.strip():
            continue
        h=re.match(r'^(#{1,6})\\s+(.+)$',raw)
        if h and not code:
            lvl=min(len(h.group(1)),3)
            doc.add_heading(h.group(2).replace('**',''),level=lvl)
            continue
        if code:
            doc.add_paragraph(raw,style='Normal')
            continue
        if re.match(r'^\\s*[-*]\\s+',raw):
            doc.add_paragraph(re.sub(r'^\\s*[-*]\\s+','',raw).replace('**',''),style='List Bullet')
        elif re.match(r'^\\s*\\d+\\.\\s+',raw):
            doc.add_paragraph(re.sub(r'^\\s*\\d+\\.\\s+','',raw).replace('**',''),style='List Number')
        elif re.match(r'^\\s*>',raw):
            doc.add_paragraph(raw.lstrip('> ').replace('**',''))
        else:
            doc.add_paragraph(raw.replace('**',''))
    output.parent.mkdir(parents=True, exist_ok=True)
    doc.save(output)

def main() -> None:
    if DIST.exists():
        shutil.rmtree(DIST)
    DIST.mkdir(parents=True)
    for file in SOURCE:
        shutil.copy2(ROOT/file,DIST/file)
    for dir in DIRS:
        shutil.copytree(ROOT/dir,DIST/dir)
    (DIST/'.nojekyll').write_text('',encoding='utf-8')
    idx=json.loads((ROOT/'catalog/index.json').read_text(encoding='utf-8'))
    count=0
    try:
        from docx import Document # noqa: F401
        docx_available=True
    except ImportError:
        docx_available=False
        print('python-docx missing, Word downloads skipped (install python-docx)')
    for item in idx['domains']:
        domain=json.loads((ROOT/item['path']).read_text(encoding='utf-8'))
        for report in domain['reports']:
            if docx_available:
                export_docx(ROOT/report['path'],DIST/'downloads'/(report['id']+'.docx'))
                count+=1
    print(f'Built Pages at {DIST}, {len(idx["domains"])} domain(s), {count} Word documents')

if __name__ == '__main__':
    main()
