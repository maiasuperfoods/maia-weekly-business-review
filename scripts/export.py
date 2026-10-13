#!/usr/bin/env python3
"""Refresh public/data/db.json from an export of the page database.

The export is a folder with one sub-folder per collection and one JSON file per document:
  <export>/weeks/2026-10-05.json, <export>/items/<id>.json, <export>/plan/model.json, ...

usage: python3 -I scripts/export.py <export folder> [YYYY-MM-DD]

Each collection found in the export replaces that collection in the snapshot. A collection
that is missing from the export keeps what the snapshot already has, so a partial export
never empties a tab. The script writes one file, public/data/db.json, and nothing else.

It stops without writing if the export contains something that looks like an email address,
a phone number or a card number. The page database holds counts, rates and first names only.
"""
import sys, os, re, json, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'public', 'data', 'db.json')
NAME = re.compile(r'^[A-Za-z0-9_\-.~:@+]{1,200}$')
PERSONAL = [
    ('an email address', re.compile(r'[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+\.[A-Za-z]{2,}')),
    ('a phone number', re.compile(r'(?<![\w.])\+?1?[ .-]?\(?\d{3}\)?[ .-]\d{3}[ .-]\d{4}(?!\d)|\+\d{10,14}(?!\d)')),
    ('a card number', re.compile(r'(?<![\d.])(?:\d[ -]?){13,19}(?![\d.])')),
]


def strings(v, path):
    if isinstance(v, str):
        yield path, v
    elif isinstance(v, dict):
        for k, x in v.items():
            yield path + '.' + str(k), str(k)
            yield from strings(x, path + '.' + str(k))
    elif isinstance(v, list):
        for i, x in enumerate(v):
            yield from strings(x, '%s[%d]' % (path, i))


def main():
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    exp = sys.argv[1]
    day = sys.argv[2] if len(sys.argv) > 2 else datetime.date.today().isoformat()
    if not re.match(r'^\d{4}-\d{2}-\d{2}$', day):
        raise SystemExit('the date must be YYYY-MM-DD')
    if not os.path.isdir(exp):
        raise SystemExit('not a folder: ' + exp)

    fresh = {}
    for c in sorted(os.listdir(exp)):
        d = os.path.join(exp, c)
        if not os.path.isdir(d) or not NAME.match(c):
            continue
        docs = {}
        for f in sorted(os.listdir(d)):
            if not f.endswith('.json') or not NAME.match(f[:-5]):
                continue
            with open(os.path.join(d, f), encoding='utf8') as h:
                doc = json.load(h)
            if isinstance(doc, dict):
                docs[f[:-5]] = doc
        if docs:
            fresh[c] = docs
    if not fresh:
        raise SystemExit('nothing to export: no collection folders with JSON documents in ' + exp)

    hits = []
    for c, docs in fresh.items():
        for i, doc in docs.items():
            for path, s in strings(doc, c + '/' + i):
                for what, rx in PERSONAL:
                    if rx.search(s):
                        hits.append('%s looks like it holds %s' % (path, what))
    if hits:
        raise SystemExit('Stopped, nothing written:\n  ' + '\n  '.join(hits[:20]))

    old = {}
    if os.path.exists(OUT):
        with open(OUT, encoding='utf8') as h:
            j = json.load(h)
        old = j.get('collections', {}) if isinstance(j, dict) else {}
    if 'weeks' in fresh and 'weeks' in old and len(fresh['weeks']) < len(old['weeks']) - 1:
        raise SystemExit('Stopped, nothing written: the export has %d weeks and the snapshot has %d. '
                         'List the collection again with a limit of 1000.' % (len(fresh['weeks']), len(old['weeks'])))

    cols = dict(old)
    cols.update(fresh)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, 'w', encoding='utf8') as h:
        json.dump({'exportedAt': day, 'collections': {k: cols[k] for k in sorted(cols)}}, h,
                  separators=(',', ':'), sort_keys=True, ensure_ascii=False)
        h.write('\n')
    kept = sorted(set(old) - set(fresh))
    print('wrote public/data/db.json, %d bytes, dated %s' % (os.path.getsize(OUT), day))
    print('replaced: ' + ', '.join('%s (%d)' % (k, len(v)) for k, v in sorted(fresh.items())))
    print('kept from the previous snapshot: ' + (', '.join(kept) if kept else 'nothing'))
    weeks = sorted(cols.get('weeks', {}))
    if weeks:
        print('latest week in the snapshot: ' + weeks[-1])


main()
