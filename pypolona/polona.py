#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
    pypolona
    --------
    Copyright (c) 2020 Adam Twardoch <adam+github@twardoch.com>
    MIT license. Python 3.7.

    Image downloader for the polona.pl website of the Polish National Library
    Usage: 'pypolona' for GUI, 'pypolona -h' for CLI
"""

import json
import sys
import os.path
from typing import OrderedDict as od
import requests
import dateutil.parser
import urllib.parse
import html2text
try:
    from yaplon import oyaml
except ImportError:
    print('pip3 install --upgrade yaplon')
try:
    from orderedattrdict import AttrDict as ad
except ImportError:
    print('pip3 install --upgrade orderedattrdict')

from . import *


class Polona(object):
    def __init__(self, **opts):
        log.debug(opts)
        self.o = ad(opts)
        self.ids = []
        self.hits = None
        self.dldir = None
        if self.o.ids:
            self.ids = self.o.query
        elif self.o.search or self.o.search_advanced:
            self.search()
            if self.o.download:
                if self.o.output:
                    self.save_search_results()
            else:
                self.save_search_results()
        if self.o.download:
            self.download()
            log.success('Finished downloading into file://%s' %
                        self.o.download_dir)

    def _requests_encode_dict(self, dic, name):
        url = ''
        for k, v in dic.items():
            fragm = '%s[%s]' % (name, k)
            if type(v) == type([]):
                for i in v:
                    url += '&%s[]=%s' % (fragm, i)
            else:
                url += '&%s=%s' % (fragm, v)
        return url

    def search(self):
        filters = {
            'public': 1
        }
        if self.o.search_languages:
            filters['language'] = self.o.search_languages
        params = {
            'query': ' '.join(self.o.query),
            'sort': self.o.sort,
            'size': 150,
        }
        if self.o.search_advanced:
            params['advanced'] = 1
        url = 'https://polona.pl/api/entities/'
        urlparams = urllib.parse.urlencode(
            params) + self._requests_encode_dict(filters, 'filters')
        log.debug(url + '?' + urlparams)
        r = requests.get(url + '?' + urlparams)
        jhits = None
        try:
            jhits = ad(r.json())
        except:
            h = html2text.HTML2Text()
            log.critical(h.handle(r.text))
        self.ids = []
        if jhits:
            self.hits = ad()
            for jhit in jhits.get('hits', ad()):
                jhit = ad(jhit)
                if jhit.id:
                    self.ids.append(jhit.id)
                    hit = ad()
                    hit.id = jhit.id
                    hit.title = jhit.title
                    hit.slug = jhit.slug
                    year = jhit.date
                    if year:
                        hit.year = dateutil.parser.parse(year).year
                    hit.url = 'https://polona.pl/item/%s,%s/' % (
                        hit.slug, hit.id)
                    self.hits[jhit.id] = hit

    def save_search_results(self):
        if self.o.format == 'yaml':
            output = oyaml.yaml_dump(self.hits)
        elif self.o.format == 'json':
            output = json.dumps(self.hits)
        elif self.o.format == 'urls':
            output = '\n'.join([hit.url for hit in self.hits.values()])
        else:
            output = ' '.join(self.hits.keys())
        if self.o.output:
            outfile = open(self.o.output, 'w')
        else:
            outfile = sys.stdout
        outfile.write(output)
        if self.o.output:
            outfile.close()
        else:
            print()
        if self.o.output:
            log.success('Search results saved in: file://%s' % (self.o.output))

    def can_download(self):
        can_dl = False
        if len(self.ids) and self.o.download:
            self.dldir = os.path.abspath(self.o.download_dir)
            if not os.path.isdir(self.dldir):
                try:
                    os.makedirs(self.dldir)
                except:
                    log.critical('Cannot create dir file://%s' % (self.dldir))
            if os.path.isdir(self.dldir):
                can_dl = True
        return can_dl

    def download_id(self, id, progress=''):
        url = 'https://polona.pl/api/entities/' + id
        log.debug(url)
        r = requests.get(url)
        hit = None
        try:
            hit = ad(r.json())
        except:
            h = html2text.HTML2Text()
            log.critical(h.handle(r.text))
        if hit:
            if hit.id:
                hit.subdir = []
                year = hit.date
                if year:
                    hit.year = dateutil.parser.parse(year).year
                    hit.subdir.append('%s-' % hit.year)
                hit.subdir.append(hit.slug[:64])
                hit.subdir.append('-%s' % hit.id)
                hit.subdir = '-'.join(hit.subdir)
                if hit.scans:
                    if len(hit.scans):
                        total = len(hit.scans)
                        log.info('%s: %03d pages in %s...' %
                                 (progress, total, hit.subdir[:40]))
                        subdir = os.path.join(self.dldir, hit.subdir)
                        if os.path.isdir(subdir):
                            log.warn('Folder %s exists' % (subdir))
                        else:
                            os.makedirs(subdir)
                        for idx, scan in enumerate(hit.scans):
                            progress = '[page %03d/%03d]' % (idx+1, total)
                            filemask = '%s-%04d.jpg' % (hit.id, idx+1)
                            log.info('%s: downloading %s' %
                                     (progress, filemask))
                            self.download_scan(scan, subdir, filemask)

    def download_scan(self, scan, subdir, filemask):
        url = scan['resources'][0]['url']
        r = requests.get(url, stream=True)
        if r.headers['content-type'] == 'image/jpeg':
            log.info
            jpeg_path = os.path.join(subdir, filemask)
            with open(jpeg_path, "wb") as handle:
                handle.write(r.content)
        else:
            log.error('Cannot download %s to %s' % (url, filemask))

    def download_ids(self):
        all = self.ids
        total = len(all)
        for idx, id in enumerate(all):
            progress = '[doc %03d/%03d]' % (idx+1, total)
            self.download_id(id, progress)
            log.info('%s: %s downloaded' % (progress, id))

    def download(self):
        if self.can_download():
            self.download_ids()
