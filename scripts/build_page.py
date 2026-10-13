#!/usr/bin/env python3
"""Build public/index.html from src/weekly-business-review.html.

The source file is written in the Claude artifact format: no doctype, no <html>, <head> or <body>;
it starts with <title>, a font <link> and one <style>, then the markup and one <script>.
This wraps it in a normal HTML document and adds the standalone data layer (src/standalone-shim.js)
in front of the page script, so the same source runs on Vercel or any static host.

usage: python3 scripts/build_page.py
"""
import os, re
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = open(os.path.join(ROOT, 'src', 'weekly-business-review.html'), encoding='utf8').read()
shim = open(os.path.join(ROOT, 'src', 'standalone-shim.js'), encoding='utf8').read()

m = re.match(r'\s*(<title>.*?</title>)\s*(<link[^>]*>)\s*(<style>.*?</style>)(.*)\Z', src, re.S)
if not m: raise SystemExit('source does not start with <title>, <link>, <style>')
title, link, style, body = m.groups()
i = body.rindex('<script>')
body = body[:i] + '<script>\n' + shim + '</script>\n' + body[i:]
html = ('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">\n'
        '<meta name="robots" content="noindex,nofollow">\n<link rel="icon" href="data:,">\n' + title + '\n' + link + '\n'
        '<style>body{margin:0}[hidden]{display:none!important}img{max-width:100%}</style>\n' + style + '\n</head>\n<body>' + body.rstrip() + '\n</body>\n</html>\n')
os.makedirs(os.path.join(ROOT, 'public'), exist_ok=True)
open(os.path.join(ROOT, 'public', 'index.html'), 'w', encoding='utf8').write(html)
print('public/index.html', len(html), 'bytes')
