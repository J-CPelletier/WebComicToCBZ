import os
from typing import List, Mapping
from zipfile import ZipFile, BadZipFile
from multiprocessing import Process, Queue

import click
import requests
from fake_useragent import UserAgent
from lxml import html
from scrapy.crawler import CrawlerProcess
from twisted.internet import reactor

from webcomix.comic_spider import ComicSpider
from webcomix.verification_spider import VerificationSpider
from webcomix.crawler_worker import CrawlerWorker

ua = UserAgent()
header = {"User-Agent": str(ua.chrome)}


class Comic:
    def __init__(
        self,
        name: str,
        start_url: str,
        next_page_selector: str,
        comic_image_selector: str,
    ):
        self.name = name
        self.start_url = start_url
        self.next_page_selector = next_page_selector
        self.comic_image_selector = comic_image_selector

    def download(self) -> None:
        """
        Downloads an entire comic page by page starting from the first one
        and saves them in the directory_name created in the current working
        directory
        """
        if not os.path.isdir(self.name):
            os.makedirs(self.name)

        settings = {
            "ITEM_PIPELINES": {
                "webcomix.comic_pipeline.ComicPipeline": 1,
                "scrapy.pipelines.files.FilesPipeline": 500,
            },
            "LOG_ENABLED": False,
            "FILES_STORE": self.name,
            "MEDIA_ALLOW_REDIRECTS": True,
        }

        worker = CrawlerWorker(
            settings,
            False,
            ComicSpider,
            start_urls=[self.start_url],
            next_page_selector=self.next_page_selector,
            comic_image_selector=self.comic_image_selector,
            directory=self.name,
        )

        worker.start()

        click.echo("Finished downloading the images.")

    def convert_to_cbz(self) -> None:
        """
        Takes all of the previously downloaded pages and compresses them in
        a .cbz file, erasing them afterwards.
        """
        with ZipFile("{}.cbz".format(self.name), mode="w") as cbz_file:
            images = os.listdir(self.name)
            for image in images:
                image_location = "{}/{}".format(self.name, image)
                cbz_file.write(image_location, image)
                os.remove(image_location)
            os.rmdir(self.name)
            if cbz_file.testzip() is not None:
                raise BadZipFile(
                    "Error while testing the archive; it might be corrupted."
                )

    def verify_xpath(self) -> List[Mapping]:
        """
        Takes a url and the XPath expressions for the next_page and image to
        go three pages into the comic. It returns a tuple containing the url
        of each page and their respective image urls.
        """
        settings = {"LOG_ENABLED": False}

        worker = CrawlerWorker(
            settings,
            True,
            VerificationSpider,
            start_urls=[self.start_url],
            next_page_selector=self.next_page_selector,
            comic_image_selector=self.comic_image_selector,
            directory=self.name,
        )

        verification = worker.start()

        return verification

    @staticmethod
    def save_image_location(url: str, page: int, directory_name: str = "") -> str:
        """
        Returns the relative location in the filesystem under which the
        webcomic will be saved. If directory_name is specified, it will be
        relative to the current directory; if not specified, it will return
        the name relative to the directory in which it is downloaded.
        """
        if url.count(".") <= 1:
            # No file extension (only dot in url is domain name)
            file_name = str(page)
        else:
            file_name = "{}{}".format(page, url[url.rindex(".") :])
        return os.path.join(directory_name, file_name)
