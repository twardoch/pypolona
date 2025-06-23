#!/usr/bin/env python3
"""
pypolona library
----------------
Copyright (c) 2020 Adam Twardoch <adam+github@twardoch.com>
MIT license. Python 3.9+
"""

import json
import mimetypes
import os
import os.path
import re
import sys
import urllib.parse
from typing import Any  # For type hints

import dateutil.parser
import html2text  # type: ignore[import-untyped]
import img2pdf  # type: ignore[import-untyped]
import lxml2json  # type: ignore[import-untyped]
import pikepdf  # type: ignore[import-untyped]
import requests

# Import logging from ezgooey, as it's initialized there
from ezgooey import logging as ezgooey_logging
from lxml import etree
from orderedattrdict import AttrDict as ad  # type: ignore[import-untyped]
from yaplon import oyaml  # type: ignore[import-untyped]

try:
    # This specific version import is used in pdf_add_meta.
    # It refers to the package's own version.
    from .__init__ import __version__
except ImportError:
    from pypolona import __version__  # type: ignore[no-redef]


log = ezgooey_logging.logger("pypolona")


class Polona:
    def __init__(self, **opts: Any):
        log.debug(opts)
        self.o = ad(opts)
        self.ids: list[str] = []
        self.hits: ad | None = None
        self.dldir: str | None = None

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
            log.success(f"Finished downloading into file://{self.o.download_dir}")

    def parse_urls(self, urls: list[str]):
        RE_URL = r"^https://polona\.pl/item/.*?,([A-Za-z0-9]+)/.*"
        for url in urls:
            mo = re.search(RE_URL, url, re.M)
            if mo:
                self.ids.append(mo.group(1))

    def _requests_encode_dict(self, dic: dict, name: str) -> str:
        url_str = ""  # Renamed url to url_str
        for k, v in dic.items():
            fragm = f"{name}[{k}]"
            if isinstance(v, list):  # Use isinstance for type checking
                for i in v:
                    url_str += f"&{fragm}[]={i}"
            else:
                url_str += f"&{fragm}={v}"
        return url_str

    def search(self):
        filters: dict[str, Any] = {"public": 1}  # Type hint for filters
        if self.o.search_languages:
            filters["language"] = self.o.search_languages
        params: dict[str, Any] = {  # Type hint for params
            "query": " ".join(self.o.query),
            "sort": self.o.sort,
            "size": 150,
        }
        if self.o.advanced:
            params["advanced"] = 1
        base_url = "https://polona.pl/api/entities/"  # Renamed url to base_url
        urlparams = urllib.parse.urlencode(params) + self._requests_encode_dict(
            filters, "filters"
        )
        log.debug(f"{base_url}?{urlparams}")
        r = requests.get(f"{base_url}?{urlparams}")
        jhits = None
        try:
            jhits = ad(r.json())
        except Exception as e:  # Catch specific exception
            h = html2text.HTML2Text()  # type: ignore[no-untyped-call]
            log.critical(f"Error parsing JSON response: {e}\n{h.handle(r.text)}")  # type: ignore[no-untyped-call]
        self.ids = []
        if jhits:
            self.hits = ad()
            # Renamed jhit to jhit_data to avoid PLW2901/clearer assignment
            for jhit_data in jhits.get("hits", ad()):
                current_jhit = ad(jhit_data)  # Processed jhit data
                if current_jhit.id:
                    self.ids.append(current_jhit.id)
                    hit = ad()
                    hit.id = current_jhit.id
                    hit.title = current_jhit.title
                    hit.slug = current_jhit.slug
                    year = current_jhit.date
                    if year:
                        hit.year = dateutil.parser.parse(year).year
                    hit.url = f"https://polona.pl/item/{hit.slug},{hit.id}/"
                    self.hits[current_jhit.id] = hit

    def save_search_results(self):
        output_str: str  # Type hint for output_str
        if self.o.format == "yaml":
            output_str = oyaml.yaml_dump(self.hits)  # type: ignore[no-untyped-call]
        elif self.o.format == "json":
            output_str = json.dumps(self.hits)
        elif self.o.format == "urls":
            output_str = "\n".join([hit.url for hit in self.hits.values()])
        else:
            output_str = " ".join(self.hits.keys())

        if self.o.output:
            with open(
                self.o.output, "w", encoding="utf-8"
            ) as outfile:  # Ensure encoding and use with
                outfile.write(output_str)
        else:
            sys.stdout.write(output_str)  # Use sys.stdout.write for consistency
            sys.stdout.write("\n")  # Add newline if printing to stdout

        if self.o.output:
            log.success(f"Search results saved in: file://{self.o.output}")

    def can_download(self) -> bool:
        can_dl = False
        if self.ids and self.o.download:  # Check if self.ids is not empty
            self.dldir = os.path.abspath(self.o.download_dir)
            if not os.path.isdir(self.dldir):
                try:
                    os.makedirs(self.dldir)
                except Exception as e:  # Catch specific exception
                    log.critical(f"Cannot create dir file://{self.dldir}: {e}")
            if os.path.isdir(self.dldir):
                can_dl = True
        return can_dl

    def _process_hit(self, hit: ad) -> ad:
        hit.subdir_parts: list[str] = []  # Use a temporary list for clarity
        year = hit.date
        if year:
            parsed_year = dateutil.parser.parse(year).year
            hit.year = parsed_year  # Store parsed year if needed elsewhere
            hit.subdir_parts.append(f"{parsed_year}-")
        hit.subdir_parts.append(hit.slug[:64])
        hit.subdir_parts.append(f"-{hit.id}")
        hit.subdir = "".join(hit.subdir_parts)  # Join parts
        hit.url = f"https://polona.pl/item/{hit.slug},{hit.id}/"
        return hit

    def _process_textpdf(self, hit: ad) -> ad:  # Added type hint
        return hit

    def _process_dc(self, hit: ad) -> ad:  # Added type hint
        r = requests.get(hit.dc_url, stream=True)
        content_type = r.headers.get("content-type", "")
        if ".xml" in mimetypes.guess_all_extensions(content_type.split(";")[0]):
            try:
                # Ensure r.content is bytes for etree.XML
                xml_content = r.content
                if isinstance(xml_content, str):
                    xml_content = xml_content.encode("utf-8")

                dc_root_xml = etree.XML(xml_content)
                # Check if dc_root_xml has children before accessing dc_root_xml[0]
                if len(dc_root_xml):  # type: ignore[arg-type]
                    dc_data_converted = lxml2json.convert(  # type: ignore[no-untyped-call]
                        dc_root_xml[0],  # type: ignore[index]
                        ordered=True,
                        alwaysList=[
                            ".//language",
                            ".//country",
                            ".//contributor",
                            ".//creator",
                            ".//subject",
                            ".//tags",
                        ],
                    )
                    dc = dc_data_converted.get(  # type: ignore[union-attr]
                        "{http://www.w3.org/1999/02/22-rdf-syntax-ns#}Description", {}
                    )
                    if dc:  # Check if dc is not empty
                        hit.dc = dc
            except etree.XMLSyntaxError as e:
                log.error(f"Failed to parse DC XML for {hit.id}: {e}")
        return hit

    def _process_resources(self, hit: ad) -> ad:  # Added type hint
        if not hit.resources:  # Guard against missing resources
            return hit
        for resource in hit.resources:
            mime_type = resource.get("mime", "")
            if ".pdf" in mimetypes.guess_all_extensions(mime_type):
                hit.textpdf_url = resource.get("url", None)
            if ".xml" in mimetypes.guess_all_extensions(mime_type):
                hit.dc_url = resource.get("url", None)
                if hit.dc_url:
                    hit = self._process_dc(hit)  # Assign back
        return hit

    def download_id(self, item_id: str, progress: str = "") -> bool:
        success = False
        api_url = (
            f"https://polona.pl/api/entities/{item_id}"  # Use f-string, rename var
        )
        log.debug(api_url)
        r = requests.get(api_url)
        hit_data: ad | None = None  # Type hint, rename var
        try:
            hit_data = ad(r.json())
        except Exception as e:  # Catch specific exception
            h = html2text.HTML2Text()  # type: ignore[no-untyped-call]
            log.critical(f"Failed to parse JSON for {item_id}: {e}\n{h.handle(r.text)}")  # type: ignore[no-untyped-call]
            return False  # Early exit if JSON parsing fails

        if hit_data and hasattr(hit_data, "id") and hit_data.id:  # Check structure
            current_hit = self._process_hit(
                hit_data
            )  # Use current_hit for processed data
            current_hit.textpdf_url = None  # Initialize these attributes
            current_hit.dc_url = None
            if hasattr(current_hit, "resources") and current_hit.resources:
                current_hit = self._process_resources(current_hit)

            if (
                hasattr(current_hit, "scans")
                and current_hit.scans
                and len(current_hit.scans) > 0
            ):
                success = self.save_downloaded(current_hit, progress)
        elif hit_data:
            log.warn(
                f"Hit data for {item_id} does not have an 'id' or is empty: {hit_data}"
            )
        else:
            # Logged during exception or if r.json() was None but didn't except (unlikely for ad(r.json()))
            pass

        return success

    def save_downloaded(self, hit: ad, progress: str) -> bool:
        if self.dldir is None:  # Guard against unset download directory
            log.error("Download directory (self.dldir) is not set.")
            return False

        success = True  # Assume success initially
        out_path_base = os.path.join(self.dldir, hit.subdir)  # Base path for item
        textpdf_path = None

        if self.o.images:
            desttext = "folder"
            # Ensure directory exists for images and YAML
            os.makedirs(out_path_base, exist_ok=True)
            yaml_path = os.path.join(out_path_base, f"{hit.id}.yaml")
            if hit.textpdf_url:
                textpdf_path = os.path.join(out_path_base, f"{hit.id}_text.pdf")
            # For images, out_path_final is the directory itself
            out_path_final = out_path_base
        else:
            desttext = "PDF"
            # For PDF, out_path_base is the filename without extension yet
            yaml_path = f"{out_path_base}.yaml"
            if hit.textpdf_url:
                textpdf_path = f"{out_path_base}_text.pdf"
            out_path_final = f"{out_path_base}.pdf"

        should_overwrite = True
        num_scans_available = len(hit.scans) if hasattr(hit.scans, "__len__") else 0

        pages_to_download_count = num_scans_available
        if self.o.max_pages > 0:
            pages_to_download_count = min(num_scans_available, self.o.max_pages)

        log.info(
            f"{progress}: Downloading {pages_to_download_count}/{num_scans_available} pages into {hit.subdir[:40]}..."
        )

        if os.path.exists(out_path_final):
            if self.o.skip:
                should_overwrite = False
                log.info(f"Skipping {desttext} {out_path_final}")
            else:
                log.warn(f"Overwriting {desttext} {out_path_final}")

        # Save YAML metadata for images (always, if images mode, even if skipping image download)
        if self.o.images:
            try:
                with open(yaml_path, "w", encoding="utf-8") as yamlfile:
                    oyaml.dump(hit, yamlfile)  # type: ignore[no-untyped-call]
            except OSError as e:
                log.error(f"Failed to write YAML file {yaml_path}: {e}")
                success = False  # Consider this a failure

        if (
            should_overwrite and success
        ):  # Proceed only if not skipping and YAML write (if any) was okay
            memimages: list[bytes] = []
            scans_to_process = (
                hit.scans[:pages_to_download_count]
                if hasattr(hit.scans, "__getitem__")
                else []
            )

            for page_idx, scan_data in enumerate(scans_to_process):
                progress_page = (
                    f"[page {page_idx + 1:03d}/{pages_to_download_count:03d}]"
                )
                jpeg_filename = ""
                if self.o.images:
                    jpeg_filename = f"{hit.id}-{page_idx + 1:04d}.jpg"

                log.info(f"{progress} {progress_page}: downloading")

                for res_data in scan_data.get("resources", []):
                    if res_data.get("mime") == "image/jpeg":
                        scan_url_str = res_data.get("url")
                        if scan_url_str:
                            img_bytes = self.download_scan(scan_url_str)
                            if img_bytes:
                                if self.o.images:
                                    # out_path_final is the directory for images mode
                                    jpeg_full_path = os.path.join(
                                        out_path_final, jpeg_filename
                                    )
                                    try:
                                        with open(jpeg_full_path, "wb") as jpeg_file:
                                            jpeg_file.write(img_bytes)
                                    except OSError as e:
                                        log.error(
                                            f"Failed to write JPEG {jpeg_full_path}: {e}"
                                        )
                                        success = False  # Mark as failure
                                else:
                                    memimages.append(img_bytes)
                            else:
                                log.error(f"Cannot download {scan_url_str}")
                                success = False  # Mark as failure for this page
                        break  # Found jpeg, process next scan_data

            if not self.o.images and memimages:  # If PDF mode and images were collected
                log.info(f"Saving {out_path_final}")
                pdf_save_ok = self.pdf_save(out_path_final, memimages)
                if pdf_save_ok:
                    meta_add_ok = self.pdf_add_meta(out_path_final, hit)
                    if meta_add_ok:
                        log.info(f"Saved high-res image PDF to file://{out_path_final}")
                    success = success and meta_add_ok
                else:
                    success = False
            elif not self.o.images and not memimages and pages_to_download_count > 0:
                # PDF mode, but no images downloaded (e.g. all downloads failed or no JPEG resources)
                log.error(f"No images downloaded for PDF: {out_path_final}")
                success = False

        # Process text PDF regardless of main content overwrite status, if path exists and not skipping text PDFs
        # However, its success should contribute to the overall success if it was attempted.
        if textpdf_path and not self.o.textpdf_skip:
            attempt_text_pdf_download = True
            if os.path.exists(textpdf_path) and self.o.skip:
                log.info(f"Skipping existing text PDF {textpdf_path}")
                attempt_text_pdf_download = (
                    False  # Don't try to download or add meta if skipping existing
                )

            if attempt_text_pdf_download:
                text_pdf_dl_ok = self.download_save_textpdf(
                    hit.textpdf_url, textpdf_path
                )
                if text_pdf_dl_ok:
                    text_pdf_meta_ok = self.pdf_add_meta(textpdf_path, hit)
                    if text_pdf_meta_ok:
                        log.info(f"Saved searchable text PDF to file://{textpdf_path}")
                    success = (
                        success and text_pdf_meta_ok
                    )  # Overall success depends on this too
                else:
                    success = False  # Failed to download/save text PDF

        return success

    def pdf_add_meta(self, pdf_path: str, hit: ad) -> bool:
        try:
            pdf = pikepdf.open(pdf_path, allow_overwriting_input=True)  # type: ignore[no-untyped-call]
            with pdf.open_metadata(set_pikepdf_as_editor=False) as meta:  # type: ignore[no-untyped-call]
                meta["xmp:CreatorTool"] = (
                    f"PyPolona {__version__}"  # Use imported __version__
                )

                id_val = hit.get("id")  # Renamed id to id_val
                meta_ids: list[Any] = []  # Renamed ids to meta_ids, allow Any initially
                if id_val:
                    meta_ids.append(id_val)
                    meta["dc:identifier"] = str(id_val)  # Ensure string

                dc = hit.get("dc", ad())  # Default to empty AttrDict

                if hit.get("isbn"):
                    meta["prism2:isbn"] = str(hit["isbn"])
                    meta_ids.append(hit["isbn"])
                if hit.get("issn"):
                    meta["prism2:issn"] = str(hit["issn"])  # Corrected from hit['isbn']
                    meta_ids.append(hit["issn"])
                if hit.get("academica_id"):
                    meta_ids.append(hit["academica_id"])
                if hit.get("oclc_no"):
                    meta_ids.append(hit["oclc_no"])

                meta_ids.extend(hit.get("call_no", []))
                if meta_ids:
                    # pikepdf expects list of strings for xmp:Identifier
                    meta["xmp:Identifier"] = [str(i) for i in set(meta_ids)]

                if hit.get("title"):
                    meta["dc:title"] = str(hit["title"])
                if hit.get("date"):
                    meta["dc:date"] = [
                        str(hit["date"])
                    ]  # Ensure it's a list of strings
                if hit.get("date_descriptive"):
                    meta["prism2:timePeriod"] = [str(hit["date_descriptive"])]
                if hit.get("url"):
                    meta["dc:source"] = str(hit["url"])
                    meta["prism2:url"] = str(hit["url"])

                author = str(hit.get("creator_name", "") or hit.get("creator", ""))
                contributors = hit.get("contributor", [])
                if isinstance(contributors, list) and contributors:
                    meta["dc:contributor"] = [str(c) for c in set(contributors)]
                    if not author:  # Check if author still empty
                        author = str(contributors[0])

                meta["dc:creator"] = [author.replace(",", " ").replace("  ", " ")]
                # meta["dc:source"] is already set if hit.url exists

                dc_langs_list = dc.get("language", [])
                if isinstance(dc_langs_list, list) and dc_langs_list:
                    valid_langs = [
                        str(s["text"]).strip()
                        for s in dc_langs_list
                        if isinstance(s, dict) and "text" in s
                    ]
                    if valid_langs:
                        meta["dc:language"] = list(set(valid_langs))

                rights_list_val = hit.get("rights", [])
                if isinstance(rights_list_val, list) and rights_list_val:
                    rights_str_val = ";".join(
                        str(r) for r in rights_list_val
                    )  # Ensure strings
                    meta["dc:rights"] = rights_str_val
                    meta["xmpRights:WebStatement"] = rights_str_val

                categories_list = hit.get("categories", [])
                if (
                    isinstance(categories_list, list) and categories_list
                ):  # Check if list and not empty
                    str_categories = [str(c) for c in categories_list]
                    meta["dc:type"] = list(set(str_categories))
                    meta["prism2:contentType"] = "; ".join(str_categories)

                keywords_agg: list[Any] = []  # Renamed keywords to keywords_agg
                keywords_agg.extend(hit.get("subject", []))
                keywords_agg.extend(hit.get("keywords", []))
                # categories already added to dc:type, avoid duplicate in keywords if not intended
                # keywords_agg.extend(hit.get("categories", []))
                keywords_agg.extend(hit.get("metatypes", []))
                keywords_agg.extend(hit.get("projects", []))

                dc_tags_list = dc.get("tags", [])
                if isinstance(dc_tags_list, list) and dc_tags_list:
                    keywords_agg.extend(
                        s["text"]
                        for s in dc_tags_list
                        if isinstance(s, dict) and "text" in s
                    )

                if keywords_agg:
                    # Ensure all keywords are strings and then get unique sorted list
                    unique_keywords_str = sorted(
                        list(set(str(k) for k in keywords_agg))
                    )
                    meta["dc:subject"] = unique_keywords_str
                    meta["pdf:Keywords"] = "; ".join(unique_keywords_str)

                publisher_list: list[str] = []  # Renamed publisher to publisher_list
                if hit.get("publisher"):
                    publisher_list.append(str(hit["publisher"]))
                if hit.get("imprint"):
                    publisher_list.append(str(hit["imprint"]))
                if publisher_list:
                    meta["dc:publisher"] = list(set(publisher_list))

                location_parts_list: list[str] = []  # Renamed location_parts
                location_parts_list.extend(str(p) for p in hit.get("publish_place", []))
                location_parts_list.extend(str(c) for c in hit.get("country", []))
                if location_parts_list:
                    meta["prism2:location"] = ", ".join(location_parts_list)

                description_parts_list: list[
                    str
                ] = []  # Renamed description to description_parts_list
                if hit.get("series"):
                    series_str = str(hit["series"])
                    meta["prism2:seriesTitle"] = series_str
                    description_parts_list.append(series_str)

                dc_freq_text = dc.get("frequency", {}).get("text")
                if dc_freq_text:
                    dc_freq_str = str(dc_freq_text)
                    meta["prism2:publishingFrequency"] = dc_freq_str
                    description_parts_list.append(dc_freq_str)
                if hit.get("press_title"):
                    press_title_str = str(hit["press_title"])
                    meta["prism2:publicationName"] = press_title_str
                    description_parts_list.append(press_title_str)

                description_parts_list.extend(str(n) for n in hit.get("notes", []))
                description_parts_list.extend(
                    str(pd) for pd in hit.get("physical_description", [])
                )
                description_parts_list.extend(str(s) for s in hit.get("sources", []))
                description_parts_list.extend(str(p) for p in hit.get("projects", []))

                if description_parts_list:
                    description_text_str = "; ".join(description_parts_list)  # Renamed
                    meta["dc:description"] = description_text_str
            pdf.save(pdf_path)  # type: ignore[no-untyped-call]
            return True
        except Exception as e:
            log.error(f"Failed to add metadata to PDF {pdf_path}: {e}")
            return False

    def pdf_save(self, pdf_path: str, memimages: list[bytes]) -> bool:
        if not memimages:  # Check if empty
            return False
        try:
            with open(pdf_path, "wb") as pdffile:
                pdffile.write(img2pdf.convert(memimages))  # type: ignore[no-untyped-call]
            return True
        except OSError as e:
            log.error(f"Failed to write PDF {pdf_path}: {e}")
            return False
        except Exception as e:  # Catch other img2pdf errors
            log.error(f"Failed to convert images to PDF for {pdf_path}: {e}")
            return False

    def download_save_textpdf(self, url_str: str, pdf_path: str) -> bool:
        try:
            r = requests.get(url_str, stream=True)
            r.raise_for_status()  # Check for HTTP errors
            content_type = r.headers.get("content-type", "")
            if (
                ".pdf" in mimetypes.guess_all_extensions(content_type)
                or "application/pdf" in content_type
            ):
                with open(pdf_path, "wb") as pdf_file:
                    pdf_file.write(r.content)
                return True
            else:
                # Enhanced JPEG detection
                if content_type.lower().startswith("image/jpeg") or content_type.lower().startswith("image/pjpeg"):
                    # Content type is a JPEG variant
                    return r.content
                # Fallback: check JPEG file signature (magic number)
                if r.content[:2] == b'\xff\xd8' and r.content[-2:] == b'\xff\xd9':
                    # JPEG files start with FF D8 and end with FF D9
                    log.info(f"JPEG detected by file signature for {url_str}")
                    return r.content
                log.warn(f"Content type for {url_str} is not PDF or JPEG: {content_type}")
                return False
        except requests.RequestException as e:
            log.error(f"Failed to download text PDF from {url_str}: {e}")
            return False
        except OSError as e:
            log.error(f"Failed to write text PDF to {pdf_path}: {e}")
            return False

    def download_scan(self, url_str: str) -> bytes | None:
        try:
            r = requests.get(url_str, stream=True)
            r.raise_for_status()
            content_type = r.headers.get("content-type", "")
            # Check common JPEG mime types and extensions
            if (
                ".jpg" in mimetypes.guess_all_extensions(content_type)
                or ".jpeg" in mimetypes.guess_all_extensions(content_type)
                or "image/jpeg" in content_type
            ):
                return r.content
            else:
                log.warn(f"Content type for scan {url_str} is not JPEG: {content_type}")
                return None
        except requests.RequestException as e:
            log.error(f"Failed to download scan from {url_str}: {e}")
            return None

    def download_ids(self):
        all_ids_local = self.ids[
            :
        ]  # Create a copy if modification during iteration is a concern
        total = len(all_ids_local)
        for idx, item_id_local in enumerate(all_ids_local):
            progress_str = f"[doc {idx + 1:03d}/{total:03d}]"
            if self.download_id(
                item_id_local, progress_str
            ):  # item_id_local was already correctly named
                log.info(f"{progress_str}: {item_id_local} processed")

    def download(self):
        if self.can_download():
            self.download_ids()
