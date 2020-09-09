# pypolona

GUI (graphical) and CLI (command-line) app that allows you to search in and download images from the [Polona](https://polona.pl/) digital library. Polona provides digitized books, magazines, graphics, maps, music, fliers and manuscripts from collections of the National Library of Poland and co-operating institutions.

The [Polona](https://polona.pl/) is a bit overcomplicated to use, but fortunately, Polona publishes a [JSON API](https://polona.pl/api/entities/). The pypolona package uses that API.

The pypolona package consists of a graphical app **PyPolona** and a command-line tool `ppolona`. But in fact, it’s just one app. The GUI version is made from the command-line version, and uses the same settings.

With pypolona, you can:

- search Polona
- print or save the search results as a list of URLs, a YAML file, a JSON file and a simple list of Polona document IDs
- download all or some high-resolution images from Polona for the search results, or for a provided list of Polona document IDs

## Installing PyPolona

### Install standalone PyPolona app for macOS

[Download the standalone PyPolona DMG for macOS](https://github.com/twardoch/pypolona/raw/master/download/pypolona-mac.dmg), install it (drag to the `/Applications` folder). Then Ctrl+click the icon and choose Open, then click Open to open the GUI. Later, you can just double-click the icon.

### Install standalone PyPolona app for Windows

[Download the standalone PyPolona ZIP for Windows](https://github.com/twardoch/pypolona/raw/master/download/pypolona-win.zip), unzip it, double-click the icon to open the GUI. (You may need 64-bit Windows to run this).

### Install pypolona Python package on macOS or Windows

If you have Python 3.8+, you can install the Python version with `python3 -m pip install pypolona`.

## Running the graphical PyPolona app

- If you installed the standalone app on macOS, just double-click `/Applications/PyPolona.app`
- If you installed the standalone app on Windows, just double-click `pypolona.exe`
- If you installed the Python version, run `ppolona` or `python3 -m pypolona`

## Running the CLI

- If you installed the standalone DMG on macOS, use the CLI via `/Applications/PyPolona.app/Contents/MacOS/ppolona -h`
- If you installed the Python version, run `ppolona -h` or `python3 -m pypolona -h`
- Command-line options:

```
usage: ppolona [-h] [-q query [query ...]] [-D] [-S | -A | -I] [-l [language [language ...]]] [-s {score desc,date desc,date asc,title asc,creator asc}]
               [-f {ids,urls,yaml,json}] [-o save results] [-d download to folder] [-O] [-M number of pages]

Search in and download from Polona.pl. GUI: ppolona, CLI: ppolona -h

optional arguments:
  -h, --help            show this help message and exit

Input:
  -q query [query ...], --query query [query ...]
                        Search query or Advanced search query or IDs
  -D, --download        Download images from results. See Download options
  -S, --search          Query is search query. See Search options
  -A, --advanced-search
                        Query is advanced search query. field:value OR field:value AND (field:value OR field:value). Allowed fields are: title, author,
                        keywords, publication_place, publisher, frequency, sources, call_number, entire_description, content
  -I, --ids             Query is space-separated IDs

Search options:
  -l [language [language ...]], --lang [language [language ...]]
                        Space-separated languages: polski angielski niemiecki...
  -s {score desc,date desc,date asc,title asc,creator asc}, --sort {score desc,date desc,date asc,title asc,creator asc}
                        Sort search results by score, date, title or creator (descending or ascending)
  -f {ids,urls,yaml,json}, --format {ids,urls,yaml,json}
                        Output search results in format
  -o save results, --output save results
                        Save search results to this file

Download options:
  -d download to folder, --download-dir download to folder
                        Download images into subfolders in this folder
  -O, --overwrite       Overwrite if folder exists
  -M number of pages, --max-pages number of pages
                        Maximum number of pages to download per doc (0: all)
```

## More about Polona

- [Polona](https://polona.pl/) — the main Polona website
- [Polona/API](https://polona.pl/api/entities/) — the JSON API that pypolona uses
- [Polona/blog](http://www.blog.polona.pl/) — the blog
- [Polona/typo](http://typo.polona.pl/en/) — a cool minisite that lets you typeset a word and renders it with letters from random publications

## Development

- This project uses [Gooey](https://github.com/chriskiehl/Gooey). With Gooey, I could rapidly turn the Python command-line app which uses the `argparse` module into a simple GUI app. This project serves as a good example in how this can be done.
- This project uses [PyInstaller](https://www.pyinstaller.org/) to build the standalone app.

### Building on macOS

In `Terminal.app`, install Homebrew:

```
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install.sh)";
```

Then:

```
brew install upx;
pip3 install --user --upgrade .[dev];
pyinstaller -y app/pyinstaller-mac.spec;
dmgbuild -s dmgbuild_settings.py "PyPolona" "download/pypolona-mac.dmg";
```

### Building on Windows

Install [UPX](https://upx.github.io/) in a location accessible in PATH. Then run `cmd.exe` and in the command-line:

```
pip3 install --user --upgrade .[dev]
pyinstaller -y app/pyinstaller-win.spec
del download/pypolona-win.zip
powershell "Compress-Archive dist/pypolona.exe download/pypolona-win.zip"
```

## License and Copyright

Copyright © 2020 Adam Twardoch. Licensed under the terms of the [MIT license](./LICENSE). This project is not affiliated with and not endorsed by Polona.
