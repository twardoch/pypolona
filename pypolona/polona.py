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
        self.options = ad(opts)
        self.ids: list[str] = []
        self.hits: ad | None = None
        self.dldir: str | None = None

        if self.options.ids:
            self.ids = self.options.query
        elif self.options.search or self.options.advanced:
            self.search()
            if self.options.download:
                if self.options.output:
                    self.save_search_results()
            else:
                self.save_search_results()
        else:
            self.parse_urls(self.options.query)

        if self.options.download:
            self.download()
            log.success(f"Finished downloading into file://{self.options.download_dir}")

    def parse_urls(self, urls: list[str]):
        RE_URL = r"^https://polona\.pl/item/.*?,([A-Za-z0-9]+)/.*"
        for url_string in urls:
            match_object = re.search(RE_URL, url_string, re.M)
            if match_object:
                self.ids.append(match_object.group(1))

    def _requests_encode_dict(self, data_dict: dict, name: str) -> str:
        encoded_params = ""
        for k, v in data_dict.items():
            param_fragment = f"{name}[{k}]"
            if isinstance(v, list):  # Use isinstance for type checking
                for i in v:
                    encoded_params += f"&{param_fragment}[]={i}"
            else:
                encoded_params += f"&{param_fragment}={v}"
        return encoded_params

    def search(self):
        filters: dict[str, Any] = {"public": 1}  # Type hint for filters
        if self.options.search_languages:
            filters["language"] = self.options.search_languages
        params: dict[str, Any] = {  # Type hint for params
            "query": " ".join(self.options.query),
            "sort": self.options.sort,
            "size": 150,
        }
        if self.options.advanced:
            params["advanced"] = 1
        base_url = "https://polona.pl/api/entities/"
        urlparams = urllib.parse.urlencode(params) + self._requests_encode_dict(
            filters, "filters"
        )
        log.debug(f"{base_url}?{urlparams}")
        response = requests.get(f"{base_url}?{urlparams}")
        json_hits_data = None
        try:
            json_hits_data = ad(response.json())
        except requests.exceptions.JSONDecodeError as e:
            h = html2text.HTML2Text()  # type: ignore[no-untyped-call]
            log.critical(f"Error parsing JSON response: {e}\n{h.handle(response.text)}")  # type: ignore[no-untyped-call]
        self.ids = []
        if json_hits_data:
            self.hits = ad()
            for jhit_data in json_hits_data.get("hits", ad()):
                processed_json_hit = ad(jhit_data)
                if processed_json_hit.id:
                    self.ids.append(processed_json_hit.id)
                    hit = ad()
                    hit.id = processed_json_hit.id
                    hit.title = processed_json_hit.title
                    hit.slug = processed_json_hit.slug
                    if year := processed_json_hit.date:
                        hit.year = dateutil.parser.parse(year).year
                    hit.url = f"https://polona.pl/item/{hit.slug},{hit.id}/"
                    self.hits[processed_json_hit.id] = hit

    def save_search_results(self):
        output_str: str
        if self.options.format == "yaml":
            output_str = oyaml.yaml_dump(self.hits)  # type: ignore[no-untyped-call]
        elif self.options.format == "json":
            output_str = json.dumps(self.hits)
        elif self.options.format == "urls":
            output_str = "\n".join([hit.url for hit in self.hits.values()])
        else:
            output_str = " ".join(self.hits.keys())

        if self.options.output:
            with open(
                self.options.output, "w", encoding="utf-8"
            ) as outfile:
                outfile.write(output_str)
        else:
            sys.stdout.write(output_str)
            sys.stdout.write("\n")

        if self.options.output:
            log.success(f"Search results saved in: file://{self.options.output}")

    def can_download(self) -> bool:
        can_dl = False
        if self.ids and self.options.download:
            self.dldir = os.path.abspath(self.options.download_dir)
            if not os.path.isdir(self.dldir):
                try:
                    os.makedirs(self.dldir)
                except OSError as e:
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
        hit.subdir = "".join(hit.subdir_parts)
        hit.url = f"https://polona.pl/item/{hit.slug},{hit.id}/"
        return hit

    def _process_textpdf(self, hit: ad) -> ad:
        return hit

    def _process_dc(self, hit: ad) -> ad:
        response = requests.get(hit.dc_url, stream=True)
        content_type = response.headers.get("content-type", "")
        if ".xml" in mimetypes.guess_all_extensions(content_type.split(";")[0]):
            try:
                xml_content = response.content
                if isinstance(xml_content, str):
                    xml_content = xml_content.encode("utf-8")

                dc_root_xml = etree.XML(xml_content)
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
                    if dc_metadata := dc_data_converted.get(  # type: ignore[union-attr]
                        "{http://www.w3.org/1999/02/22-rdf-syntax-ns#}Description",
                        {},
                    ):
                        hit.dc = dc_metadata
            except etree.XMLSyntaxError as e:
                log.error(f"Failed to parse DC XML for {hit.id}: {e}")
        return hit

    def _process_resources(self, hit: ad) -> ad:
        if not hit.resources:
            log.warning(f"Hit {getattr(hit, 'id', '<unknown>')} has no resources. This may indicate upstream data issues.")
            return hit
        for resource in hit.resources:
            mime_type = resource.get("mime", "")
            if ".pdf" in mimetypes.guess_all_extensions(mime_type):
                hit.textpdf_url = resource.get("url", None)
            if ".xml" in mimetypes.guess_all_extensions(mime_type):
                hit.dc_url = resource.get("url", None)
                if hit.dc_url:
                    hit = self._process_dc(hit)
        return hit

    def download_id(self, item_id: str, progress: str = "") -> bool:
        success = False
        api_url = f"https://polona.pl/api/entities/{item_id}"
        log.debug(api_url)
        response = requests.get(api_url)
        item_json_data: ad | None = None
        try:
            item_json_data = ad(response.json())
        except requests.exceptions.JSONDecodeError as e:
            h = html2text.HTML2Text()  # type: ignore[no-untyped-call]
            log.critical(f"Failed to parse JSON for {item_id}: {e}\n{h.handle(response.text)}")  # type: ignore[no-untyped-call]
            return False

        if item_json_data and hasattr(item_json_data, "id") and item_json_data.id:
            processed_item_data = self._process_hit(item_json_data)
            processed_item_data.textpdf_url = None
            processed_item_data.dc_url = None
            if hasattr(processed_item_data, "resources") and processed_item_data.resources:
                processed_item_data = self._process_resources(processed_item_data)

            if (
                hasattr(processed_item_data, "scans")
                and processed_item_data.scans
                and len(processed_item_data.scans) > 0
            ):
                success = self.save_downloaded(processed_item_data, progress)
        elif item_json_data:
            log.warn(
                f"Hit data for {item_id} does not have an 'id' or is empty: {item_json_data}"
            )
        return success

    def _prepare_download_paths(self, hit: ad) -> tuple[str, str | None, str, str]:
        out_path_base = os.path.join(self.dldir, hit.subdir)
        textpdf_path = None
        yaml_path: str
        out_path_final: str
        desttext: str

        if self.options.images:
            desttext = "folder"
            os.makedirs(out_path_base, exist_ok=True) # Ensure dir exists for images and YAML
            yaml_path = os.path.join(out_path_base, f"{hit.id}.yaml")
            if hit.textpdf_url:
                textpdf_path = os.path.join(out_path_base, f"{hit.id}_text.pdf")
            out_path_final = out_path_base # For images, out_path_final is the directory
        else:
            desttext = "PDF"
            yaml_path = f"{out_path_base}.yaml" # For PDF, out_path_base is filename without ext
            if hit.textpdf_url:
                textpdf_path = f"{out_path_base}_text.pdf"
            out_path_final = f"{out_path_base}.pdf"
        return yaml_path, textpdf_path, out_path_final, desttext

    def _download_item_images(
        self,
        hit: ad,
        pages_to_download_count: int,
        progress_string: str,
        # out_path_final is the directory path if saving JPEGs, otherwise unused by this func
        out_path_for_jpegs: str
    ) -> tuple[list[bytes] | None, bool]:
        """
        Downloads images for the given hit.
        If options.images is True, saves JPEGs to out_path_for_jpegs and returns (None, success_status).
        If options.images is False, returns (list_of_image_bytes, success_status).
        """
        memimages: list[bytes] = []
        images_download_success = True # Assume success until a download fails
        scans_to_process = (
            hit.scans[:pages_to_download_count]
            if hasattr(hit.scans, "__getitem__")
            else []
        )

        for page_idx, scan_data in enumerate(scans_to_process):
            page_progress_string = (
                f"[page {page_idx + 1:03d}/{pages_to_download_count:03d}]"
            )
            current_jpeg_filename = ""
            if self.options.images:
                current_jpeg_filename = f"{hit.id}-{page_idx + 1:04d}.jpg"

            log.info(f"{progress_string} {page_progress_string}: downloading")

            jpeg_resource_url = None
            for res_data in scan_data.get("resources", []):
                if res_data.get("mime") == "image/jpeg":
                    jpeg_resource_url = res_data.get("url")
                    break

            if jpeg_resource_url:
                img_bytes = self.download_scan(jpeg_resource_url)
                if img_bytes:
                    if self.options.images:
                        jpeg_full_path = os.path.join(
                            out_path_for_jpegs, current_jpeg_filename
                        )
                        try:
                            with open(jpeg_full_path, "wb") as jpeg_file:
                                jpeg_file.write(img_bytes)
                        except OSError as e:
                            log.error(
                                f"Failed to write JPEG {jpeg_full_path}: {e}"
                            )
                            images_download_success = False
                    else: # PDF mode
                        memimages.append(img_bytes)
                else: # img_bytes is None
                    log.error(f"Cannot download image from {jpeg_resource_url}")
                    images_download_success = False
            else: # No jpeg resource found for this scan_data
                log.warn(f"{progress_string} {page_progress_string}: No JPEG resource URL found for scan.")
                # Consider if this should mark images_download_success as False
                # For now, if one page is missing, we still try others.

        if self.options.images:
            return None, images_download_success # JPEGs saved directly, return None for image data
        else:
            return memimages, images_download_success # Return image data for PDF creation

    def _create_pdf_from_images(self, hit:ad, image_bytes_list: list[bytes], pdf_output_path: str) -> bool:
        log.info(f"Saving PDF to {pdf_output_path}")
        if not image_bytes_list:
             log.error(f"No images provided to create PDF: {pdf_output_path}")
             return False
        pdf_save_ok = self.pdf_save(pdf_output_path, image_bytes_list)
        if pdf_save_ok:
            meta_add_ok = self.pdf_add_meta(pdf_output_path, hit)
            if meta_add_ok:
                log.info(f"Saved high-res image PDF to file://{pdf_output_path}")
            return meta_add_ok
        return False

    def _download_and_save_text_pdf(self, hit: ad, text_pdf_path: str | None) -> bool:
        if not text_pdf_path or not hit.textpdf_url or self.options.textpdf_skip :
            return True # Nothing to do or explicitly skipping

        if os.path.exists(text_pdf_path) and self.options.skip:
            log.info(f"Skipping existing text PDF {text_pdf_path}")
            return True

        log.info(f"Downloading searchable text PDF to {text_pdf_path}")
        text_pdf_content_retrieved = self.download_save_textpdf( # This function now correctly returns bool
            hit.textpdf_url, text_pdf_path
        )
        if text_pdf_content_retrieved:
            # Assuming download_save_textpdf saved the file if it returned True
            meta_add_ok = self.pdf_add_meta(text_pdf_path, hit)
            if meta_add_ok:
                log.info(f"Saved and added metadata to searchable text PDF: file://{text_pdf_path}")
            return meta_add_ok
        else:
            log.error(f"Failed to download or save text PDF from {hit.textpdf_url}")
            return False

    def save_downloaded(self, hit: ad, progress_string: str) -> bool:
        if self.dldir is None:
            log.error("Download directory (self.dldir) is not set.")
            return False

        overall_success = True
        yaml_path, textpdf_path, out_path_final, desttext = self._prepare_download_paths(hit)

        num_scans_available = len(hit.scans) if hasattr(hit.scans, "__len__") else 0
        pages_to_download_count = num_scans_available
        if self.options.max_pages > 0:
            pages_to_download_count = min(num_scans_available, self.options.max_pages)

        log.info(
            f"{progress_string}: Downloading {pages_to_download_count}/{num_scans_available} pages for {hit.id} into {desttext} '{hit.subdir[:40]}...'"
        )

        should_process_main_content = True # Determines if we download JPEGs/create main PDF
        if os.path.exists(out_path_final):
            if self.options.skip:
                should_process_main_content = False
                log.info(f"Skipping existing {desttext}: file://{out_path_final}")
            else:
                log.warn(f"Overwriting existing {desttext}: file://{out_path_final}")

        # Save YAML metadata (always in images mode, even if skipping image download;
        # for PDF mode, it's saved alongside the PDF if main content is processed)
        if self.options.images: # In image mode, out_path_final is the directory
            try:
                with open(yaml_path, "w", encoding="utf-8") as yamlfile:
                    oyaml.dump(hit, yamlfile)
            except OSError as e:
                log.error(f"Failed to write YAML file {yaml_path}: {e}")
                overall_success = False # Critical failure if YAML can't be written in image mode

        if should_process_main_content and overall_success:
            # out_path_final is the directory for JPEGs if self.options.images is True
            image_data_list, images_download_success = self._download_item_images(
                hit, pages_to_download_count, progress_string, out_path_final
            )
            overall_success = overall_success and images_download_success

            if not self.options.images and overall_success: # PDF mode
                if image_data_list:
                    # For PDF mode, save YAML here, only if PDF creation is attempted
                    try:
                        with open(yaml_path, "w", encoding="utf-8") as yamlfile:
                           oyaml.dump(hit, yamlfile)
                    except OSError as e:
                        log.error(f"Failed to write YAML file {yaml_path}: {e}")
                        overall_success = False # YAML fail is part of PDF process fail

                    if overall_success: # Proceed only if YAML was saved
                        pdf_creation_success = self._create_pdf_from_images(hit, image_data_list, out_path_final)
                        overall_success = overall_success and pdf_creation_success
                elif pages_to_download_count > 0 :
                    log.error(f"No images were downloaded for PDF: {out_path_final}")
                    overall_success = False
            elif self.options.images and not images_download_success and pages_to_download_count > 0:
                 log.error(f"Failed to download one or more images for item {hit.id} into {out_path_final}")
                 # overall_success is already False due to images_download_success

        # Attempt to download text PDF regardless of main content processing, unless skipped
        text_pdf_processing_success = self._download_and_save_text_pdf(hit, textpdf_path)
        overall_success = overall_success and text_pdf_processing_success

        return overall_success

    def pdf_add_meta(self, pdf_path: str, hit: ad) -> bool:
        try:
            pdf = pikepdf.open(pdf_path, allow_overwriting_input=True)  # type: ignore[no-untyped-call]
            with pdf.open_metadata(set_pikepdf_as_editor=False) as meta:  # type: ignore[no-untyped-call]
                meta["xmp:CreatorTool"] = (
                    f"PyPolona {__version__}"
                )

                item_id_value = hit.get("id")
                metadata_ids_list: list[Any] = []
                if item_id_value:
                    metadata_ids_list.append(item_id_value)
                    meta["dc:identifier"] = str(item_id_value)

                dc_metadata = hit.get("dc", ad())

                if hit.get("isbn"):
                    meta["prism2:isbn"] = str(hit["isbn"])
                    metadata_ids_list.append(hit["isbn"])
                if hit.get("issn"):
                    meta["prism2:issn"] = str(hit["issn"])
                    metadata_ids_list.append(hit["issn"])
                if hit.get("academica_id"):
                    metadata_ids_list.append(hit["academica_id"])
                if hit.get("oclc_no"):
                    metadata_ids_list.append(hit["oclc_no"])

                metadata_ids_list.extend(hit.get("call_no", []))
                if metadata_ids_list:
                    meta["xmp:Identifier"] = [str(i) for i in set(metadata_ids_list)]

                if hit.get("title"):
                    meta["dc:title"] = str(hit["title"])
                if hit.get("date"):
                    meta["dc:date"] = [
                        str(hit["date"])
                    ]
                if hit.get("date_descriptive"):
                    meta["prism2:timePeriod"] = [str(hit["date_descriptive"])]
                if hit.get("url"):
                    meta["dc:source"] = str(hit["url"])
                    meta["prism2:url"] = str(hit["url"])

                author = str(hit.get("creator_name", "") or hit.get("creator", ""))
                contributors = hit.get("contributor", [])
                if isinstance(contributors, list) and contributors:
                    meta["dc:contributor"] = [str(c) for c in set(contributors)]
                    if not author:
                        author = str(contributors[0])

                meta["dc:creator"] = [author.replace(",", " ").replace("  ", " ")]

                dc_languages_list = dc_metadata.get("language", [])
                if isinstance(dc_languages_list, list) and dc_languages_list:
                    valid_languages = [
                        str(s["text"]).strip()
                        for s in dc_languages_list
                        if isinstance(s, dict) and "text" in s
                    ]
                    if valid_languages:
                        meta["dc:language"] = list(set(valid_languages))

                rights_list = hit.get("rights", [])
                if isinstance(rights_list, list) and rights_list:
                    rights_string = ";".join(
                        str(r) for r in rights_list
                    )
                    meta["dc:rights"] = rights_string
                    meta["xmpRights:WebStatement"] = rights_string

                item_categories_list = hit.get("categories", [])
                if (
                    isinstance(item_categories_list, list) and item_categories_list
                ):
                    string_categories = [str(c) for c in item_categories_list]
                    meta["dc:type"] = list(set(string_categories))
                    meta["prism2:contentType"] = "; ".join(string_categories)

                aggregated_keywords_list: list[Any] = []
                aggregated_keywords_list.extend(hit.get("subject", []))
                aggregated_keywords_list.extend(hit.get("keywords", []))
                aggregated_keywords_list.extend(hit.get("metatypes", []))
                aggregated_keywords_list.extend(hit.get("projects", []))

                dc_tags_list_from_metadata = dc_metadata.get("tags", [])
                if isinstance(dc_tags_list_from_metadata, list) and dc_tags_list_from_metadata:
                    aggregated_keywords_list.extend(
                        s["text"]
                        for s in dc_tags_list_from_metadata
                        if isinstance(s, dict) and "text" in s
                    )

                if aggregated_keywords_list:
                    unique_keywords_string_list = sorted(
                        list(set(str(k) for k in aggregated_keywords_list))
                    )
                    meta["dc:subject"] = unique_keywords_string_list
                    meta["pdf:Keywords"] = "; ".join(unique_keywords_string_list)

                item_publishers_list: list[str] = []
                if hit.get("publisher"):
                    item_publishers_list.append(str(hit["publisher"]))
                if hit.get("imprint"):
                    item_publishers_list.append(str(hit["imprint"]))
                if item_publishers_list:
                    meta["dc:publisher"] = list(set(item_publishers_list))

                item_location_parts_list: list[str] = []
                item_location_parts_list.extend(str(p) for p in hit.get("publish_place", []))
                item_location_parts_list.extend(str(c) for c in hit.get("country", []))
                if item_location_parts_list:
                    meta["prism2:location"] = ", ".join(item_location_parts_list)

                item_description_parts_list: list[
                    str
                ] = []
                if hit.get("series"):
                    series_string = str(hit["series"])
                    meta["prism2:seriesTitle"] = series_string
                    item_description_parts_list.append(series_string)

                dc_frequency_text = dc_metadata.get("frequency", {}).get("text")
                if dc_frequency_text:
                    dc_frequency_string = str(dc_frequency_text)
                    meta["prism2:publishingFrequency"] = dc_frequency_string
                    item_description_parts_list.append(dc_frequency_string)
                if hit.get("press_title"):
                    press_title_string = str(hit["press_title"])
                    meta["prism2:publicationName"] = press_title_string
                    item_description_parts_list.append(press_title_string)

                item_description_parts_list.extend(str(n) for n in hit.get("notes", []))
                item_description_parts_list.extend(
                    str(pd) for pd in hit.get("physical_description", [])
                )
                item_description_parts_list.extend(str(s) for s in hit.get("sources", []))
                item_description_parts_list.extend(str(p) for p in hit.get("projects", []))

                if item_description_parts_list:
                    description_text_string = "; ".join(item_description_parts_list)
                    meta["dc:description"] = description_text_string
            pdf.save(pdf_path)  # type: ignore[no-untyped-call]
            return True
        except (pikepdf.PdfError, TypeError, KeyError, AttributeError) as e: # More specific exceptions
            log.error(f"Failed to add metadata to PDF {pdf_path}: {e}")
            return False
        except Exception as e: # Fallback for other unexpected pikepdf errors
            log.error(f"Unexpected error adding metadata to PDF {pdf_path}: {e}")
            return False


    def pdf_save(self, pdf_path: str, memimages: list[bytes]) -> bool:
        if not memimages:
            return False
        try:
            with open(pdf_path, "wb") as pdffile:
                pdffile.write(img2pdf.convert(memimages))  # type: ignore[no-untyped-call]
            return True
        except OSError as e:
            log.error(f"Failed to write PDF {pdf_path}: {e}")
            return False
        except img2pdf.PdfCreationError as e: # More specific
            log.error(f"Failed to convert images to PDF for {pdf_path}: {e}")
            return False
        except Exception as e:  # Catch other img2pdf errors
            log.error(f"Unexpected error converting images to PDF for {pdf_path}: {e}")
            return False

    def download_save_textpdf(self, url_string: str, pdf_path: str) -> bool:
        try:
            response = requests.get(url_string, stream=True)
            response.raise_for_status()
            content_type = response.headers.get("content-type", "")
            if (
                ".pdf" in mimetypes.guess_all_extensions(content_type)
                or "application/pdf" in content_type
            ):
                with open(pdf_path, "wb") as pdf_file:
                    pdf_file.write(response.content)
                return True
            else:
                # Enhanced JPEG detection
                if content_type.lower().startswith("image/jpeg") or content_type.lower().startswith("image/pjpeg"):
                    # Content type is a JPEG variant, but we expect to save a PDF.
                    # This path should ideally not be taken if the primary goal is textpdf.
                    # For now, align with original logic's intent if it was to handle unexpected JPEGs.
                    # However, the function is download_SAVE_textPDF. Returning True might be misleading.
                    # Sticking to correcting the immediate bug of returning bytes.
                    log.warn(f"Expected PDF, received JPEG for {url_string}. Cannot save as text PDF.")
                    return False # Corrected: Should be boolean, and False as it's not a PDF.
                # Fallback: check JPEG file signature (magic number)
                if response.content[:2] == b'\xff\xd8' and response.content[-2:] == b'\xff\xd9':
                    # JPEG files start with FF D8 and end with FF D9
                    log.info(f"JPEG detected by file signature for {url_string}. Cannot save as text PDF.")
                    return False # Corrected: Should be boolean, and False as it's not a PDF.
                log.warn(f"Content type for {url_string} is not PDF or JPEG: {content_type}")
                return False
        except requests.RequestException as e:
            log.error(f"Failed to download text PDF from {url_string}: {e}")
            return False
        except OSError as e:
            log.error(f"Failed to write text PDF to {pdf_path}: {e}")
            return False

    def download_scan(self, url_string: str) -> bytes | None:
        try:
            response = requests.get(url_string, stream=True)
            response.raise_for_status()
            content_type = response.headers.get("content-type", "")
            if (
                ".jpg" in mimetypes.guess_all_extensions(content_type)
                or ".jpeg" in mimetypes.guess_all_extensions(content_type)
                or "image/jpeg" in content_type
            ):
                return response.content
            else:
                log.warn(f"Content type for scan {url_string} is not JPEG: {content_type}")
                return None
        except requests.RequestException as e:
            log.error(f"Failed to download scan from {url_string}: {e}") # Corrected log message
            return None

    def download_ids(self):
        all_item_ids_local = self.ids[
            :
        ]
        total = len(all_item_ids_local)
        for idx, single_item_id_local in enumerate(all_item_ids_local):
            progress_string = f"[doc {idx + 1:03d}/{total:03d}]"
            if self.download_id(
                single_item_id_local, progress_string
            ):
                log.info(f"{progress_string}: {single_item_id_local} processed")

    def download(self):
        if self.can_download():
            self.download_ids()
