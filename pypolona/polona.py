#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
    pypolona library
    ----------------
    Copyright (c) 2020 Adam Twardoch <adam+github@twardoch.com>
    MIT license. Python 3.8+
"""

import json
import sys
import os.path
import requests
import dateutil.parser
import urllib.parse
import re
import html2text
from yaplon import oyaml
from orderedattrdict import AttrDict as ad

from . import *
log = logging.logger('pypolona')

class Polona(object):
    def __init__(self, **opts):
        log.debug(opts)
        self.o = ad(opts)
        self.ids = []
        self.hits = None
        self.dldir = None
        if self.o.ids:
            self.ids = self.o.query
        elif self.o.search or self.o.advanced:
            self.search()
            if self.o.download:
                if self.o.output:
                    self.save_search_results()
            else:
                self.save_search_results()
        else:
            self.parse_urls(self.o.query)
        if self.o.download:
            self.download()
            log.success('Finished downloading into file://%s' %
                        self.o.download_dir)

    def parse_urls(self, urls):
        RE_URL = r"^https://polona\.pl/item/.*?,([A-Za-z0-9]+)/.*"
        for url in urls:
            mo = re.search(RE_URL, url, re.M)
            if mo:
                self.ids.append(mo.group(1))

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
        if self.o.advanced:
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
                        overwrite = True
                        if self.o.max_pages > 0:
                            total = len(hit.scans[:self.o.max_pages])
                        else:
                            total = len(hit.scans)
                        log.info('%s: Downloading %03d/%03d pages in %s...' %
                                 (progress, total, len(hit.scans), hit.subdir[:40]))
                        subdir = os.path.join(self.dldir, hit.subdir)
                        if os.path.isdir(subdir):
                            if self.o.overwrite:
                                log.warn('Overwriting folder %s' % (subdir))
                            else:
                                overwrite = False
                                log.info('Skipping folder %s' % (subdir))
                        else:
                            os.makedirs(subdir)
                        filemaskd = "%s.yaml" % (hit.id)
                        with open(os.path.join(subdir, filemaskd), 'w') as yamlfile:
                            yamlfile.write(oyaml.yaml_dump(hit))
                        if overwrite:
                            for idx, scan in enumerate(hit.scans[:total]):
                                progressp = '[page %03d/%03d]' % (idx+1, total)
                                filemaskp = '%s-%04d.jpg' % (hit.id, idx+1)
                                log.info('%s %s: downloading %s' %
                                         (progress, progressp, filemaskp))
                                self.download_scan(scan, subdir, filemaskp)

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
