from django.utils import crypto
from config.settings import TEMP＿ROOT, RANDOM_STRING_LENGTH
from .models import File
import os
import subprocess
import shutil
import requests
import cairosvg

Latexmkrc = """#!/usr/bin/env perl
$latex = 'platex -synctex=1 -halt-on-error -interaction=nonstopmode -file-line-error %O %S';
$bibtex = 'pbibtex %O %S';
$biber = 'biber --bblencoding=utf8 -u -U --output_safechars %O %S';
$makeindex = 'mendex %O -o %D %S';
$dvipdf = 'dvipdfmx %O -o %D %S';

$max_repeat = 5;
$pdf_mode = 3;
"""

def GetFile(url, request):
    if url.startswith('http'):
        if url.startswith(request._current_scheme_host):
            response = requests.get(url, cookies=request.COOKIES)
        else:
            response = requests.get(url)
    else:
        response = requests.get(request._current_scheme_host + url,
                                cookies=request.COOKIES)
    if response.status_code == 200:
        return response.content
    else:
        return None

def SVG2PDF(content):
    try:
        return cairosvg.svg2pdf(bytestring=content)
    except:
        return None

def Tex2PDF(model, text, request):
    randomstr = crypto.get_random_string(length=RANDOM_STRING_LENGTH)
    path = os.path.join(TEMP＿ROOT, 'Article_' + randomstr)
    os.makedirs(path)
    texpath = os.path.join(path, randomstr + '.tex')
    with open(texpath, 'w') as f:
        f.write(text)
    files = File.objects.filter(upper=model)
    for file in files:
        filepath = os.path.join(path, file.name)
        if file.svg2pdf:
            name, ext = os.path.splitext(filepath)
            filepath = name + '.pdf'
        if file.file:
            content = file.file.read()
        elif file.url:
            content = GetFile(file.url, request)
        if content and file.svg2pdf:
            content = SVG2PDF(content)
        if content:
            with open(filepath, 'wb') as f:
                f.write(content)
    mkrcpath = os.path.join(path, '.latexmkrc')
    with open(mkrcpath, 'w') as f:
        f.write(Latexmkrc)
    stdpath = os.path.join(path, randomstr + '.stdouterr')
    cmd = 'latexmk ' + texpath + '&> ' + stdpath
    subprocess.run(cmd, shell=True, cwd=path, executable="/bin/bash")
    pdfpath = os.path.join(path, randomstr + '.pdf')
    if os.path.exists(pdfpath):
        with open(pdfpath, 'rb') as f:
            value = f.read()
    else:
        value = None
    logpath = os.path.join(path, randomstr + '.log')
    with open(logpath, 'r') as f:
        log = f.read()
    with open(stdpath, 'r') as f:
        std = f.read()
    shutil.rmtree(path)
    return value, log, std
