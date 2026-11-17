#!/usr/bin/env python3
"""Verify that every published report has versioned DOCX/PDF in Git/Pages.

Checks file signatures, hashes, Markdown source freshness, page counts and
byte-for-byte integrity between repository exports and the Pages downloads.
"""
from __future__ import annotations
import hashlib
import json
import subprocess
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

index = json.loads((ROOT/'catalog/index.json').read_text(encoding='utf-8'))
verified = 0
for ref in index['domains']:
    domain = json.loads((ROOT/ref['path']).read_text(encoding='utf-8'))
    base = ROOT/'reports'/domain['id']/'exports'
    manifest_file = base/'manifest.json'
    assert manifest_file.exists(), f'Missing archive manifest: {manifest_file}'
    manifest = json.loads(manifest_file.read_text(encoding='utf-8'))
    assert manifest['domainId'] == domain['id']
    for report in domain['reports']:
        rid = report['id']
        entry = next((x for x in manifest['files'] if x['id'] == rid), None)
        assert entry is not None, f'Manifest missing report {rid}'
        md = ROOT/report['path']
        docx = base/(rid+'.docx')
        pdf = base/(rid+'.pdf')
        assert sha(md) == entry['sourceSha256'], f'Stale documents for {rid}'
        assert docx.stat().st_size > 10_000, f'Empty Word file: {docx}'
        assert pdf.stat().st_size > 10_000, f'Empty PDF file: {pdf}'
        assert sha(docx) == entry['docxSha256'], f'Word hash mismatch: {rid}'
        assert sha(pdf) == entry['pdfSha256'], f'PDF hash mismatch: {rid}'
        with zipfile.ZipFile(docx) as z:
            assert z.testzip() is None, f'Corrupted Word ZIP: {rid}'
            assert 'word/document.xml' in z.namelist()
        assert pdf.read_bytes().startswith(b'%PDF-'), f'Invalid PDF header: {rid}'
        info = subprocess.run(['pdfinfo',str(pdf)],capture_output=True,text=True,check=True).stdout
        pages = next((int(s.split(':',1)[1]) for s in info.splitlines() if s.startswith('Pages:')),0)
        assert pages > 1, f'PDF must have multiple pages: {rid}'
        for artifact in (docx,pdf):
            public = ROOT/'dist'/'downloads'/artifact.name
            assert public.is_file(), f'Missing Pages download: {public}'
            assert sha(public) == sha(artifact), f'Pages download differs from Git: {public}'
        verified += 1
        print(f'PASS {rid}: {pages} pages, DOCX {docx.stat().st_size} B, PDF {pdf.stat().st_size} B')
assert verified, 'No reports verified'
print(f'Verified {verified} report(s), {verified*2} binary assets and {verified*2} Pages downloads.')
