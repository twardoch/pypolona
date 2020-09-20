# pypolona

**[PyPolona](https://twardoch.github.io/pypolona/)** is a free and open-source GUI (graphical) app that allows you to search in and download images from the [Polona.pl](https://polona.pl/) digital library. It also works as a `ppolona` CLI (command-line) tool. And it’s a Python package available from [PyPI](https://pypi.org/project/pypolona/). The source is on [Github](https://github.com/twardoch/pypolona).

**Polona.pl** provides digitized books, magazines, graphics, maps, music, fliers and manuscripts from collections of the National Library of Poland and co-operating institutions.

With PyPolona, you can:

- search Polona
- print or save the search results as a list of URLs, a YAML file, a JSON file and a simple list of Polona document IDs
- download all or some high-resolution images from Polona for the search results, or for a provided list of Polona document IDs

The PyPolona GUI version is made from the command-line version, and uses the same settings as the `ppolona` tool.

> Remember: to **run the GUI on macOS for the first time**, _Ctrl+click_ the DMG, choose _Open_, then _Open_, then drag to Applications folder, there _Ctrl+click_ the app icon, choose _Open_, then _Open_.

## What’s new

Current version is **1.6.0**.

#### 1.6.0

- unless you specify `--no-text-pdf`, PyPolona now downloads an additional PDF that has searchable text if it’s available
- `--skip` is now `--no-overwrite`
- improved PDF metadata import, bugfixes

#### 1.5.0

- `-i` saves each downloaded document as subfolder with images, otherwise as one PDF (with metadata)
- `--skip` instead of `--overwrite` flag

#### 1.0.0

- initial release

## Install standalone PyPolona app

### <a class="github-button btn btn-primary" href="https://github.com/twardoch/pypolona/raw/master/download/pypolona-mac.dmg" data-color-scheme="no-preference: dark; light: dark; dark: dark;" data-icon="octicon-download" data-size="large" aria-label="Download DMG for macOS">Download DMG for macOS</a>

On **macOS**, **Ctrl+click** the downloaded DMG, choose **Open**, then **Open** again, then drag the icon to the `/Applications` folder.

When you **run the app for the first time**, **Ctrl+click** the Polona.app, choose **Open**, then click **Open**. Later, you can just double-click the icon. If the app does not run, double-click again.

### <a class="github-button btn btn-primary" href="https://github.com/twardoch/pypolona/raw/master/download/pypolona-win.zip" data-color-scheme="no-preference: dark; light: dark; dark: dark;" data-icon="octicon-download" data-size="large" aria-label="Download ZIP for Windows">Download ZIP for Windows</a>

On **Windows**, unzip the downloaded ZIP, double-click the `setup_pypolona.exe` icon to install the app. You need 64-bit Windows.

## Install pypolona Python package on macOS or Windows

If you have Python 3.8+, you can install the Python version with `python3 -m pip install pypolona`.

## Using the graphical PyPolona app (GUI)

- If you installed the standalone app on macOS, **Ctrl**-click **`/Applications/PyPolona.app`** and choose **Open**, then choose **Open**. You can just double-click the next time to run it.
- If you installed the standalone app on Windows, run **`PyPolona`** from your start menu.
- If you installed the Python version, run `ppolona` or `python3 -m pypolona`

### Search settings

![Input tab](https://raw.githubusercontent.com/twardoch/pypolona/master/docs/img/pypolona_url.png)

In the Input tab:

In **query**, you can paste one or more URLs from Polona.pl (space-separated).

![Search in input](https://raw.githubusercontent.com/twardoch/pypolona/master/docs/img/pypolona_search.png)

In **Choose One** you can change what the **query** field means:

- if nothing is selected, the query is interpreted as one or more URLs from Polona.pl
- **search**: choose this and in the **query** field, enter a simple search query like `adam mickiewicz`; go to the **Options** tab to customize
- **advanced**: you can use the advanced query syntax, see [documentation](https://polona.pl/api/entities/); go to the **Options** tab to customize
- **ids**: Polona uses IDs for documents, you can just paste a list of space-separated IDs if you already know them

In the **Options** tab:

- In **Space-separated languages**, you can enter a space-separated list of languages like Polona uses them, e.g. `polski niemiecki angielski`. Use the sidebar on the [Polona](https://polona.pl) website to find them.

- In **Sort search**, you can sort the results by score, date, title or creator, in ascending or descending order.

- In **Output search results in format**, you can choose a format in which search results will be output. If you choose ids, you click **Restart** and then paste them back into the query field. Choose urls to get clickable links.

- In **Save search results**, you can optionally save the search results into the file.

### Download settings

Turn on **Download found docs** to download the content of the queried result.

- Turn on **Download JPEGs into subfolders** to download each document content as a series of JPEGs. In the download folder, one subfolder will be created per document. The subfolder name starts with the publication year, then part of the title, then the ID. If you are also downloading searchable PDFs, an additional PDF with the `_text` suffix will be saved in the subfolder. Also, a YAML file with some metadata will be saved in the subfolder.

- Turn off **Download JPEGs into subfolders** to download each document content as one PDF. The app will not create subfolders. The PDF name starts with the publication year, then part of the title, then the ID. If you are also downloading searchable PDFs, an additional PDF with the `_text` suffix will be also saved.

In the **Options** tab:

![Options](https://raw.githubusercontent.com/twardoch/pypolona/master/docs/img/pypolona_options.png)

- In **Save downloaded docs in this folder**, you can choose into which folder the app will download the documents. By default it uses the `polona` subfolder on your desktop.

- In **Download max pages**, you can limit the maximum number of pages that the app downloads for each document. This is useful for test downloads, since some documents may have hundreds or pages.

- For some documents, Polona has an extra lower-resolution searchable PDF. By default, that PDF is also downloaded, and saved with a `_text` suffix. Turn on **Skip downloading searchable PDFs** to not download these additional PDFs.

- By default, the app will re-download and overwrite previously downloaded documents. Turn on **Skip existing subfolders/PDFs** to skip them.

### Buttons

![Result](https://raw.githubusercontent.com/twardoch/pypolona/master/docs/img/pypolona_result_urls.png)

- Click **Start** to start the search or download.
- Click **Cancel** to close the app.
- If you’ve started and the search or download has finished, you can:
  - click **Restart** to start the search or download with the same settings
  - click **Edit** to go back to change the settings, so you can start another search or download.
- If the download is running, you can click **Stop** to interrupt it.

## Using the CLI

_Note: the CLI is `ppolona`, not `pypolona`_

- If you installed the standalone DMG on macOS, use the CLI via `/Applications/PyPolona.app/Contents/MacOS/ppolona -h`
- If you installed the Python version, run `ppolona -h` or `python3 -m pypolona -h`
- Command-line options:

```
usage: ppolona [-h] [-S | -A | -I] [-D] [-i] [-l [language [language ...]]] [-s {score desc,date desc,date asc,title asc,creator asc}]
               [-f {ids,urls,yaml,json}] [-o results_file] [-d download_folder] [-M num_pages] [-T] [-O]
               query [query ...]

Search in and download from Polona.pl. GUI: Help › PyPolona 1.6.0 Help. CLI: ppolona -h

optional arguments:
  -h, --help            show this help message and exit

Input:
  query                 query is a Polona.pl URL unless you choose search, advanced or ids
  -S, --search          Query is search query, see Options
  -A, --advanced        Query is advanced search query, see Documentation
  -I, --ids             Query is space-separated IDs
  -D, --download        Download found docs, see Options
  -i, --images          Download JPEGs into subfolders instead of PDF

Options:
  -l [language [language ...]], --lang [language [language ...]]
                        Space-separated languages: polski angielski niemiecki...
  -s {score desc,date desc,date asc,title asc,creator asc}, --sort {score desc,date desc,date asc,title asc,creator asc}
                        Sort search results by score, date, title or creator (descending or ascending)
  -f {ids,urls,yaml,json}, --format {ids,urls,yaml,json}
                        Output search results in format
  -o results_file, --output results_file
                        Save search results to this file
  -d download_folder, --download-dir download_folder
                        Save downloaded docs in this folder
  -M num_pages, --max-pages num_pages
                        Download max pages per doc (0: all)
  -T, --no-text-pdf     Skip downloading searchable PDFs
  -O, --no-overwrite    Skip existing subfolders/PDFs
```
## More about Polona

The [Polona](https://polona.pl/) is a bit overcomplicated to use, but fortunately, Polona publishes a [JSON API](https://polona.pl/api/entities/). The pypolona package uses that API.

- [Polona](https://polona.pl/) — the main Polona website
- [Polona/API](https://polona.pl/api/entities/) — the JSON API that pypolona uses
- [Polona/blog](http://www.blog.polona.pl/) — the blog
- [Polona/typo](http://typo.polona.pl/en/) — a cool minisite that lets you typeset a word and renders it with letters from random publications

## Development

- This project uses [Gooey](https://github.com/chriskiehl/Gooey). With Gooey, I could rapidly turn the Python command-line app which uses the `argparse` module into a simple GUI app. This project serves as a good example in how this can be done.
- This project uses [PyInstaller](https://www.pyinstaller.org/) to build the standalone app.

### Building on macOS

To build the Python package, the Mac DMG and the Win EXE (via Wine):

```
./macdeploy prep && ./macdeploy build
```

### Building on Windows

1. Install Python 3.8 from [Python.org](https://www.python.org/) (not the Windows Store!)
2. Install [Inno Setup](https://jrsoftware.org/isinfo.php)

```
pip3 install --user --upgrade .[dev]
python -m PyInstaller --distpath="app/build/dist-win" --workpath="app/build" -y "app/pyinstaller-win.spec"
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" /dMyAppVersion="1.1.7" app/pypolona.iss /Q
```

## License and Copyright

Copyright © 2020 Adam Twardoch. Licensed under the terms of the [MIT license](./LICENSE). This project is not affiliated with and not endorsed by Polona.

<!-- Place this tag in your head or just before your close body tag. -->
<script async defer src="https://buttons.github.io/buttons.js"></script>


