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
import os
import os.path
import requests
import dateutil.parser
import urllib.parse
import re
import tempfile
import html2text
from yaplon import oyaml
from orderedattrdict import AttrDict as ad
import img2pdf
import pikepdf

from . import *

log = logging.logger('pypolona')

try:
    from .__init__ import __version__ as version
except ImportError:
    from pypolona.__init__ import __version__ as version


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
                hit.url = 'https://polona.pl/item/%s,%s/' % (
                    hit.slug, hit.id)
                if hit.scans:
                    if len(hit.scans):
                        self.save_downloaded(hit, progress)

    def save_downloaded(self, hit, progress):
        out_path = os.path.join(self.dldir, hit.subdir)
        if self.o.images:
            desttext = 'folder'
            yaml_path = os.path.join(out_path, "%s.yaml" % (hit.id))
        else:
            desttext = 'PDF'
            yaml_path = out_path + '.yaml'
            out_path += '.pdf'

        overwrite = True
        if self.o.max_pages > 0:
            total = len(hit.scans[:self.o.max_pages])
        else:
            total = len(hit.scans)
        log.info('%s: Downloading %03d/%03d pages in %s...' %
                 (progress, total, len(hit.scans), hit.subdir[:40]))
        if os.path.exists(out_path):
            if self.o.skip:
                overwrite = False
                log.info('Skipping %s %s' % (desttext, out_path))
            else:
                log.warn('Overwriting %s %s' % (desttext, out_path))
        else:
            if self.o.images:
                os.makedirs(out_path)
        if self.o.images:
            with open(yaml_path, 'w') as yamlfile:
                yamlfile.write(oyaml.yaml_dump(hit))
        if overwrite:
            memimages = []
            jpeg_mask = ''
            for idx, scan in enumerate(hit.scans[:total]):
                progressp = '[page %03d/%03d]' % (idx + 1, total)
                if self.o.images:
                    jpeg_mask = '%s-%04d.jpg' % (hit.id, idx + 1)
                log.info('%s %s: downloading' %
                         (progress, progressp))
                url = scan['resources'][0]['url']
                img = self.download_scan(url)
                if img:
                    if self.o.images:
                        jpeg_path = os.path.join(out_path, jpeg_mask)
                        with open(jpeg_path, "wb") as jpeg_file:
                            jpeg_file.write(img)
                    else:
                        memimages.append(img)
                else:
                    log.error('Cannot download %s' % (url))
            if not self.o.images:
                log.info('Saving %s' % out_path)
                if self.save_pdf(out_path, hit, memimages):
                    log.info('Saved PDF')

    def save_pdf(self, pdf_path, hit, memimages):
        with open(pdf_path, "wb") as pdffile:
            pdffile.write(img2pdf.convert(memimages))
        pdf = pikepdf.open(pdf_path, allow_overwriting_input=True)
        with pdf.open_metadata() as meta:
            meta['xmp:CreatorTool'] = 'PyPolona %s' % (version)
            id = hit.get('id', None)
            ids = []
            if id:
                ids.append(id)
                meta['dc:identifier'] = hit['id']
            if hit.get('isbn', None):
                meta['prism2:isbn'] = hit['isbn']
                ids.append(hit['isbn'])
            if hit.get('issn', None):
                meta['prism2:issn'] = hit['isbn']
                ids.append(hit['issn'])
            if hit.get('academica_id', None):
                ids.append(hit['academica_id'])
            if hit.get('oclc_no', None):
                ids.append(hit['oclc_no'])
            ids += hit.get('call_no', [])
            meta['xmp:Identifier'] = set(["%s" % i for i in ids])
            if hit.get('title', None):
                meta['dc:title'] = hit['title']
            if hit.get('date', None):
                meta['dc:date'] = [hit['date']]
            if hit.get('date_descriptive', None):
                meta['prism2:timePeriod'] = [hit['date_descriptive']]
            if hit.get('url', None):
                meta['dc:source'] = hit['url']
                meta['prism2:url'] = hit['url']
            author = hit.get('creator_name', None)
            if not author:
                author = hit.get('creator', None)
            contributors = hit.get('contributor', [])
            if len(contributors):
                meta['dc:contributor'] = set(contributors)
                if not author:
                    author = contributors[0]
            meta['dc:creator'] = [author.replace(",", " ").replace("  ", " ")]
            meta['dc:source'] = hit['url']
            rights = hit.get('rights')
            if rights:
                if type(rights) is list:
                    rights = ";".join(rights)
                    meta['dc:rights'] = rights
                    meta['xmpRights:WebStatement'] = rights
            categories = hit.get('categories', [])
            if len(categories):
                meta['dc:type'] = set(categories)
                meta['prism2:contentType'] = "; ".join(categories)
            keywords = \
                hit.get('subject', []) + \
                hit.get('keywords', []) + \
                hit.get('categories', []) + \
                hit.get('metatypes', []) + \
                hit.get('projects', [])
            if len(keywords):
                meta['dc:subject'] = set(keywords)
                meta['pdf:Keywords'] = "; ".join(keywords)
            publisher = []
            if hit.get('publisher', None):
                publisher.append(hit['publisher'])
            if hit.get('imprint', None):
                publisher.append(hit['imprint'])
            if len(publisher):
                meta['dc:publisher'] = set(publisher)
            if hit.get('publish_place', None):
                meta['prism2:location'] = hit['publish_place']
            description = []
            if hit.get('press_title', None):
                meta['prism2:seriesTitle'] = hit['press_title']
                description.append(hit['press_title'])
            description += \
                hit.get('notes', []) + \
                hit.get('physical_description', []) + \
                hit.get('sources', []) + \
                hit.get('projects', [])
            if len(description):
                description_text = "; ".join(description)
                meta['dc:description'] = description_text

        pdf.save(pdf_path)
        return True

    def download_scan(self, url):
        r = requests.get(url, stream=True)
        if r.headers['content-type'] == 'image/jpeg':
            return r.content
        else:
            return None

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
