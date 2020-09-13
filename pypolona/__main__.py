#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
    ppolona
    -------
    Copyright (c) 2020 Adam Twardoch <adam+github@twardoch.com>
    MIT license. Python 3.8+

    Image downloader for the polona.pl website of the Polish National Library
    Usage: 'ppolona' for GUI, 'ppolona -h' for CLI
"""

try:
    from .polona import *
except ImportError:
    from pypolona.polona import *
import pathlib
try:
    import gooey
except ImportError:
    gooey = None

try:
    from . import *
except ImportError:
    from pypolona import *

from ezgooey.ez import *

logging.init(level=logging.INFO)
log = logging.logger('pypolona')


@ezgooey
def get_parser():
    parser = ArgumentParser(
        prog='ppolona',
        description='Search in and download from Polona.pl. GUI: ppolona, CLI: ppolona -h'
    )

    query_help = 'query is a Polona.pl URL unless you choose search, advanced or ids'

    parser_q = parser.add_argument_group('Input')
    parser_q.add_argument(
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
        '--advanced',
        dest='advanced',
        action='store_true',
        help='Query is advanced search query. field:value OR field:value AND (field:value OR field:value). Allowed '
             'fields are: title, author, keywords, publication_place, publisher, frequency, sources, call_number, '
             'entire_description, content '
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
    parser_d.add_argument(
        '-O',
        '--overwrite',
        dest='overwrite',
        action='store_true',
        help='Overwrite if folder exists'
    )
    parser_d.add_argument(
        '-M',
        '--max-pages',
        dest='max_pages',
        type=int,
        default=0,
        metavar='number of pages',
        help='Maximum number of pages to download per doc (0: all)'
    )
    return parser


def main():
    parser = get_parser()
    opts = parser.parse_args()
    if opts:
        opts = vars(opts)
        polona = Polona(**opts)


if __name__ == '__main__':
    main()
