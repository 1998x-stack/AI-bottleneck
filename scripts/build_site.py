#!/usr/bin/env python3
"""Build a research site with versioned Word/PDF files committed to Git.

Markdown reports are the canonical sources. DOCX is rendered with python-docx;
PDF is converted from DOCX via LibreOffice. SHA256 manifests track source/exports.
"""
from __future__ import annotations
import hashlib
import json
import re
import shutil
import subprocess
import tempfile
from pathlib import Path
from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / 'dist'
SOURCE = ['index.html', 'styles.css', 'app.js', 'markdown.js']
DIRS = ['assets', 'catalog', 'reports']
ACCENT = RGBColor(17, 102, 109)

def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def add_inline(par, text: str) -> None:
    pattern = re.compile(r'(\*\*[^*]+\*\*|`[^`]+`|\[[^]]+\]\(https?://[^)]+\))')
    for piece in pattern.split(text):
        if not piece:
            continue
        if piece.startswith('**') and piece.endswith('**'):
            run = par.add_run(piece[2:-2]); run.bold = True
        elif piece.startswith(chr(96)) and piece.endswith(chr(96)):
            run = par.add_run(piece[1:-1]); run.font.name = 'Consolas'; run.font.size = Pt(8.5)
        elif piece.startswith('[') and '](' in piece:
            label, addr = piece[1:].split('](', 1)
            par.add_run(label + ' (' + addr[:-1] + ')')
        else:
            par.add_run(piece.replace('~~', '').replace('*', ''))

def shade(cell, fill: str) -> None:
    tc_pr = cell._tc.get_or_add_tcPr()
    sh = OxmlElement('w:shd')
    sh.set(qn('w:fill'), fill)
    tc_pr.append(sh)

def repeat_header(row) -> None:
    tr_pr = row._tr.get_or_add_trPr()
    el = OxmlElement('w:tblHeader')
    el.set(qn('w:val'), 'true')
    tr_pr.append(el)

def table_cells(line: str) -> list[str]:
    return [x.strip() for x in line.strip().strip('|').split('|')]

def is_table_rule(line: str) -> bool:
    cells = table_cells(line)
    return bool(cells) and all(re.fullmatch(r':?-{3,}:?', c) for c in cells)

def export_docx(markdown: Path, target: Path) -> None:
    doc = Document()
    sec = doc.sections[0]
    sec.page_height = Cm(29.7); sec.page_width = Cm(21)
    sec.left_margin = Cm(2.1); sec.right_margin = Cm(2.0)
    sec.top_margin = Cm(1.8); sec.bottom_margin = Cm(1.7)
    normal = doc.styles['Normal']
    normal.font.name = 'Calibri'; normal.font.size = Pt(9.5)
    normal.font.color.rgb = RGBColor(35, 49, 63)
    normal._element.rPr.rFonts.set(qn('w:eastAsia'), 'Noto Sans CJK SC')
    normal.paragraph_format.space_after = Pt(6)
    normal.paragraph_format.line_spacing = 1.18
    for name, size in [('Title', 20), ('Heading 1', 16), ('Heading 2', 13), ('Heading 3', 11)]:
        style = doc.styles[name]
        style.font.name = 'Calibri'; style.font.size = Pt(size)
        style.font.bold = True; style.font.color.rgb = ACCENT
        style._element.rPr.rFonts.set(qn('w:eastAsia'), 'Noto Sans CJK SC')
        style.paragraph_format.space_before = Pt(0 if name == 'Title' else 14)
        style.paragraph_format.space_after = Pt(6)
    header = sec.header.paragraphs[0]
    header.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    r = header.add_run('AI BOTTLENECK  /  RESEARCH ARCHIVE')
    r.font.size = Pt(7); r.font.color.rgb = RGBColor(125,139,147)
    footer = sec.footer.paragraphs[0]
    footer.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = footer.add_run('AI Bottleneck Observatory   •   ')
    r.font.size = Pt(7)
    page = OxmlElement('w:fldSimple')
    page.set(qn('w:instr'), 'PAGE')
    footer._p.append(page)
    doc.core_properties.subject = 'Source: ' + markdown.name
    doc.core_properties.keywords = 'AI-bottleneck; research; evidence; solutions'
    lines = markdown.read_text(encoding='utf-8').replace('\r\n', '\n').split('\n')
    inside_code = False
    code_lines = []
    i = 0
    while i < len(lines):
        line = lines[i].rstrip()
        trim = line.strip()
        if trim.startswith(chr(96) * 3):
            inside_code = not inside_code
            if inside_code:
                code_lines = []
            elif code_lines:
                p = doc.add_paragraph(style='Normal')
                p.paragraph_format.left_indent = Cm(.45)
                p.paragraph_format.space_after = Pt(8)
                r = p.add_run('\n'.join(code_lines))
                r.font.name = 'Consolas'; r.font.size = Pt(7.5)
                sh = OxmlElement('w:shd')
                sh.set(qn('w:fill'), 'EDF3F4')
                p._p.get_or_add_pPr().append(sh)
            i += 1
            continue
        if inside_code:
            code_lines.append(line)
            i += 1
            continue
        if not trim:
            i += 1
            continue
        heading = re.match(r'^(#{1,6})\s+(.+)$', line)
        if heading:
            level = len(heading.group(1))
            p = doc.add_paragraph(style='Title') if level == 1 else doc.add_heading(level=min(level-1,3))
            add_inline(p, heading.group(2))
            i += 1
            continue
        if '|' in line and i+1 < len(lines) and is_table_rule(lines[i+1]):
            heads = table_cells(line)
            rows = []
            i += 2
            while i < len(lines) and lines[i].strip() and '|' in lines[i]:
                rows.append(table_cells(lines[i]))
                i += 1
            width = max([len(heads)] + [len(x) for x in rows])
            tbl = doc.add_table(rows=1, cols=width)
            tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
            tbl.style = 'Table Grid'
            repeat_header(tbl.rows[0])
            for j in range(width):
                cell = tbl.rows[0].cells[j]
                cell.text = heads[j] if j < len(heads) else ''
                shade(cell, 'E6F1F0')
            for values in rows:
                row = tbl.add_row()
                for j in range(width):
                    cell = row.cells[j]
                    cell.text = values[j] if j < len(values) else ''
                    cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
            for row in tbl.rows:
                for cell in row.cells:
                    for p in cell.paragraphs:
                        p.paragraph_format.space_after = Pt(2)
                        for r in p.runs:
                            r.font.size = Pt(7.5 if width >= 4 else 8)
            doc.add_paragraph()
            continue
        if re.fullmatch(r'[-_*]{3,}', trim):
            i += 1
            continue
        if re.match(r'^\s*>', line):
            p = doc.add_paragraph()
            p.paragraph_format.left_indent = Cm(.4)
            add_inline(p, re.sub(r'^\s*>\s?', '', line))
            i += 1
            continue
        bullet = re.match(r'^\s*[-*+]\s+(.+)$', line)
        if bullet:
            p = doc.add_paragraph(style='List Bullet')
            add_inline(p, bullet.group(1))
            i += 1
            continue
        numbered = re.match(r'^\s*\d+\.\s+(.+)$', line)
        if numbered:
            p = doc.add_paragraph(style='List Number')
            add_inline(p, numbered.group(1))
            i += 1
            continue
        p = doc.add_paragraph()
        add_inline(p, line)
        i += 1
    target.parent.mkdir(parents=True, exist_ok=True)
    doc.save(target)

def export_pdf(docx: Path, pdf: Path) -> None:
    exe = shutil.which('libreoffice') or shutil.which('soffice')
    if not exe:
        raise RuntimeError('Missing LibreOffice: install libreoffice-writer to render PDFs.')
    with tempfile.TemporaryDirectory(prefix='ai-bottleneck-') as tmp:
        result = subprocess.run([
            exe, '-env:UserInstallation=file://' + tmp + '/lo',
            '--headless','--convert-to','pdf',
            '--outdir',str(pdf.parent),str(docx)
        ], capture_output=True, text=True, timeout=240)
        if result.returncode != 0 or not pdf.is_file():
            raise RuntimeError(f'Cannot export {pdf}: {result.stdout} {result.stderr}')

def export_documents() -> list[dict]:
    index = json.loads((ROOT/'catalog/index.json').read_text(encoding='utf-8'))
    files = []
    for ref in index['domains']:
        domain = json.loads((ROOT/ref['path']).read_text(encoding='utf-8'))
        directory = ROOT/'reports'/domain['id']/'exports'
        manifest = directory/'manifest.json'
        old = json.loads(manifest.read_text(encoding='utf-8')) if manifest.is_file() else {}
        entries = []
        for report in domain['reports']:
            rid = report['id']
            source = ROOT/report['path']
            docx = directory/(rid+'.docx')
            pdf = directory/(rid+'.pdf')
            sha = digest(source)
            prev = next((x for x in old.get('files',[]) if x['id']==rid),None)
            if not prev or prev.get('sourceSha256')!=sha or not docx.is_file() or not pdf.is_file():
                print('Converting research report: '+rid,flush=True)
                export_docx(source,docx)
                export_pdf(docx,pdf)
            entry = {
                'id':rid,'source':report['path'],'sourceSha256':sha,
                'docxSha256':digest(docx),'pdfSha256':digest(pdf),
                'docxBytes':docx.stat().st_size,'pdfBytes':pdf.stat().st_size
            }
            entries.append(entry)
        directory.mkdir(parents=True,exist_ok=True)
        manifest.write_text(json.dumps({
            'schemaVersion':1,'domainId':domain['id'],'files':entries
        },ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        files.extend(entries)
    return files

def build_site() -> None:
    if DIST.exists():
        shutil.rmtree(DIST)
    DIST.mkdir(parents=True)
    for file in SOURCE:
        shutil.copy2(ROOT/file,DIST/file)
    for directory in DIRS:
        shutil.copytree(ROOT/directory,DIST/directory)
    (DIST/'.nojekyll').write_text('',encoding='utf-8')
    index=json.loads((ROOT/'catalog/index.json').read_text(encoding='utf-8'))
    downloads=DIST/'downloads'
    downloads.mkdir(exist_ok=True)
    for ref in index['domains']:
        domain=json.loads((ROOT/ref['path']).read_text(encoding='utf-8'))
        export_dir=ROOT/'reports'/domain['id']/'exports'
        for report in domain['reports']:
            for ext in ('.docx','.pdf'):
                artifact=export_dir/(report['id']+ext)
                if not artifact.is_file():
                    raise RuntimeError('Missing committed export: '+str(artifact))
                shutil.copy2(artifact,downloads/artifact.name)
    print('Built dist/ with full Markdown, Word, PDF and research catalog.')

if __name__=='__main__':
    exports=export_documents()
    build_site()
    for item in exports:
        print(f"{item['id']}: DOCX {item['docxBytes']} B, PDF {item['pdfBytes']} B")
