#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
    yaplon
    ------
    Copyright (c) 2020 Adam Twardoch <adam+github@twardoch.com>
    MIT license. Python 3.7.

    Image downloader for the polona.pl website of the Polish National Library
    Usage: 'pypolona' for GUI, 'pypolona -h' for CLI
'''

import sys
from typing import OrderedDict
from .polona import *
import argparse
import pathlib
from yaplon import oyaml
try:
    import gooey
except ImportError:
    gooey = None

from . import *

try:
    from orderedattrdict import AttrDict
except ImportError:
    print('pip3 install --user --upgrade orderedattrdict')


class Unbuffered(object):
    def __init__(self, stream):
        self.stream = stream

    def write(self, data):
        self.stream.write(data)
        self.stream.flush()

    def writelines(self, datas):
        self.stream.writelines(datas)
        self.stream.flush()

    def __getattr__(self, attr):
        return getattr(self.stream, attr)


sys.stdout = Unbuffered(sys.stdout)


def flex_add_argument(f):
    '''Make the add_argument accept (and ignore) the widget option.'''

    def f_decorated(*args, **kwargs):
        kwargs.pop('widget', None)
        return f(*args, **kwargs)

    return f_decorated


# Monkey-patching a private class…
argparse._ActionsContainer.add_argument = flex_add_argument(
    argparse.ArgumentParser.add_argument)

# Do not run GUI if it is not available or if command-line arguments are given.
if gooey is None or len(sys.argv) > 1:
    ArgumentParser = argparse.ArgumentParser

    def gui_decorator(f):
        return f
else:
    ArgumentParser = gooey.GooeyParser
    gui_decorator = gooey.Gooey(
        program_name='PyPolona',
        suppress_gooey_flag=True,
        richtext_controls=True,
        advanced=True,
        tabbed_groups=True,
        navigation='Tabbed',
        optional_cols=1,
        image_dir=os.path.join(os.path.dirname(__file__), 'icons')
    )


@gui_decorator
def main():
    parser = ArgumentParser(
        prog='pypolona',
        description='Search in and download from Polona.pl. GUI: pypolona, CLI: pypolona -h'
    )

    query_help = 'Search query or Advanced search query or IDs'

    parser_q = parser.add_argument_group('Input')
    parser_q.add_argument(
        '-q',
        '--query',
        nargs='+',
        dest='query',
        type=str,
        metavar='query',
        help=query_help
    )

    parser_q.add_argument(
        '-D',
        '--download',
        dest='download',
        action='store_true',
        help='Download images from results. See Download options'
    )

    command = parser_q.add_mutually_exclusive_group(required=False)
    command.add_argument(
        '-S',
        '--search',
        dest='search',
        action='store_true',
        help='Query is search query. See Search options'
    )
    command.add_argument(
        '-A',
        '--advanced-search',
        dest='search_advanced',
        action='store_true',
        help='Query is advanced search query. field:value OR field:value AND (field:value OR field:value). Allowed fields are: title, author, keywords, publication_place, publisher, frequency, sources, call_number, entire_description, content'
    )
    command.add_argument(
        '-I',
        '--ids',
        dest='ids',
        action='store_true',
        help='Query is space-separated IDs'
    )

    parser_s = parser.add_argument_group('Search options')
    parser_s.add_argument(
        '-l',
        '--lang',
        nargs='*',
        dest='search_languages',
        type=str,
        metavar='language',
        help='Space-separated languages: polski angielski niemiecki...'
    )
    parser_s.add_argument(
        '-s',
        '--sort',
        dest='sort',
        type=str,
        choices=['score desc', 'date desc',
                 'date asc', 'title asc', 'creator asc'],
        default='score desc',
        help='Sort search results by score, date, title or creator (descending or ascending)'
    )
    parser_s.add_argument(
        '-f',
        '--format',
        dest='format',
        type=str,
        choices=['ids', 'urls', 'yaml', 'json'],
        default='ids',
        help='Output search results in format'
    )
    parser_s.add_argument(
        '-o',
        '--output',
        dest='output',
        type=str,
        widget='FileSaver',
        metavar='save results',
        help='Save search results to this file'
    )
    parser_d = parser.add_argument_group('Download options')
    parser_d.add_argument(
        '-d',
        '--download-dir',
        dest='download_dir',
        type=str,
        default=str(pathlib.Path.home() / 'Desktop' / 'polona'),
        widget='DirChooser',
        metavar='download to folder',
        help='Download images into subfolders in this folder'
    )

    opts = parser.parse_args()
    if opts:
        opts = vars(opts)
        polona = Polona(**opts)


if __name__ == '__main__':
    main()
