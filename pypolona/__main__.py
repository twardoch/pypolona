#!/usr/bin/env python3
"""
ppolona
-------
Copyright (c) 2020 Adam Twardoch <adam+github@twardoch.com>
MIT license. Python 3.9+

Search in and download from Polona.pl
Usage: 'ppolona' for GUI, 'ppolona -h' for CLI
"""

import pathlib
import argparse
from ezgooey import ezgooey_decorator as ezgooey
from ezgooey import logging as ezgooey_logging

try:
    from .polona import Polona
except ImportError:
    from pypolona.polona import Polona  # type: ignore[no-redef]

try:
    from .__init__ import __version__ as version
except ImportError:
    from pypolona import __version__ as version  # type: ignore[no-redef]


# from cli2gui import Cli2Gui

ezgooey_logging.init(level=ezgooey_logging.INFO)
log = ezgooey_logging.logger("pypolona")

GUI_NAME = f"PyPolona {version}"
CLI_NAME = "ppolona"
DESCRIPTION = f"Search in and download from Polona.pl. GUI: Help > {GUI_NAME} Help. CLI: {CLI_NAME} -h"


@ezgooey( # type: ignore
    advanced=True,
    auto_start=False,
    default_size=(800, 600),
    disable_progress_bar_animation=False,
    disable_stop_button=False,
    group_by_type=True,
    header_show_title=True,
    header_height=80,
    hide_progress_msg=False,
    optional_cols=1,
    program_description=None,
    program_name=GUI_NAME,
    progress_expr=None,
    progress_regex=None,
    required_cols=1,
    richtext_controls=True,
    show_failure_modal=True,
    show_success_modal=False,
    suppress_gooey_flag=True,
    tabbed_groups=True,
    target=None,
    use_legacy_titles=True,
    menu=[
        {
            "name": "Help",
            "items": [
                {
                    "type": "AboutDialog",
                    "menuTitle": "About",
                    "name": GUI_NAME,
                    "description": "Click the link for more info",
                    "website": "https://twardoch.github.io/pypolona/",
                    "license": "MIT",
                },
                {
                    "type": "Link",
                    "menuTitle": f"{GUI_NAME} Documentation",
                    "url": "https://twardoch.github.io/pypolona/",
                },
            ],
        }
    ],
)
def gui():
    return cli()


# @Cli2Gui(auto_enable=True, parser="argparse", gui="pysimpleguiweb",
#          theme=None, darkTheme=None, sizes=None, image=None, program_name=None,
#          program_description=None, max_args_shown=5)
# def webgui():
#     return cli()


def cli():
    parser = argparse.ArgumentParser(prog="ppolona", description=DESCRIPTION)

    query_help = "query is a Polona.pl URL unless you choose search, advanced or ids"

    parser_q = parser.add_argument_group(
        "Input", gooey_options={"show_border": True, "columns": 2, "margin_top": 0}
    )
    parser_q.add_argument(
        nargs="+",
        dest="query",
        type=str,
        metavar="query",
        help=query_help,
        widget="Textarea",
        gooey_options={
            "show_help": True,
            "height": 120,
            "placeholder": "Enter Polona.pl URL or choose query type and enter search query, advanced query or space-separated Polona IDs",
        },
    )

    command = parser_q.add_mutually_exclusive_group(
        required=False,
        gooey_options={
            "show_help": True,
            "title": "query type",
        },
    )
    command.add_argument(
        "-S",
        "--search",
        dest="search",
        action="store_true",
        help="Query is search query, see Options",
        gooey_options={
            "show_help": True,
        },
    )
    command.add_argument(
        "-A",
        "--advanced",
        dest="advanced",
        action="store_true",
        help="Query is advanced search query, see Documentation",
        gooey_options={
            "show_help": True,
        },
    )
    command.add_argument(
        "-I",
        "--ids",
        dest="ids",
        action="store_true",
        help="Query is space-separated IDs",
        gooey_options={
            "show_help": True,
        },
    )
    parser_q.add_argument(
        "-D",
        "--download",
        dest="download",
        action="store_true",
        help="Download found docs, see Options",
        gooey_options={
            "show_label": False,
        },
    )
    parser_q.add_argument(
        "-i",
        "--images",
        dest="images",
        action="store_true",
        help="Download JPEGs into subfolders instead of PDF",
        gooey_options={
            "show_label": False,
        },
    )
    parser_s = parser.add_argument_group(
        "Options", gooey_options={"show_border": True, "columns": 2, "margin_top": 0}
    )
    parser_s.add_argument(
        "-l",
        "--lang",
        nargs="*",
        dest="search_languages",
        type=str,
        metavar="language",
        help="Space-separated languages: polski angielski niemiecki...",
        gooey_options={
            "show_label": False,
            "placeholder": "polski angielski niemiecki",
        },
    )
    parser_s.add_argument(
        "-s",
        "--sort",
        dest="sort",
        type=str,
        choices=["score desc", "date desc", "date asc", "title asc", "creator asc"],
        default="score desc",
        help="Sort search results by score, date, title or creator (descending or ascending)",
        gooey_options={
            "show_label": False,
        },
    )
    parser_s.add_argument(
        "-f",
        "--format",
        dest="format",
        type=str,
        choices=["ids", "urls", "yaml", "json"],
        default="ids",
        help="Output search results in format",
        gooey_options={"show_label": False, "full_width": False},
    )
    parser_s.add_argument(
        "-o",
        "--output",
        dest="output",
        type=str,
        widget="FileSaver",
        metavar="results_file",
        help="Save search results to this file",
        gooey_options={
            "show_label": False,
        },
    )
    parser_s.add_argument(
        "-d",
        "--download-dir",
        dest="download_dir",
        type=str,
        default=str(pathlib.Path.home() / "Desktop" / "polona"),
        widget="DirChooser",
        metavar="download_folder",
        help="Save downloaded docs in this folder",
        gooey_options={
            "show_label": False,
        },
    )
    parser_s.add_argument(
        "-M",
        "--max-pages",
        dest="max_pages",
        type=int,
        default=0,
        metavar="num_pages",
        help="Download max pages per doc (0: all)",
        gooey_options={"show_label": False, "full_width": False},
    )
    parser_s.add_argument(
        "-T",
        "--no-text-pdf",
        dest="textpdf_skip",
        action="store_true",
        help="Skip downloading searchable PDFs",
        gooey_options={
            "show_label": False,
        },
    )
    parser_s.add_argument(
        "-O",
        "--no-overwrite",
        dest="skip",
        action="store_true",
        help="Skip existing subfolders/PDFs",
        gooey_options={
            "show_label": False,
        },
    )

    parser_q.add_argument("-V", "--version", action="version", version=f"%(prog)s {version}")

    return parser


def main(*args, **kwargs):
    #    if '--web' in sys.argv:
    #        sys.argv.pop(sys.argv.index('--web'))
    #        parser = webgui(*args, **kwargs)
    #    else:
    if True:
        parser = gui(*args, **kwargs)
    opts = parser.parse_args()
    if opts:
        opts_dict = vars(opts)
        Polona(**opts_dict)


if __name__ == "__main__":
    main()
