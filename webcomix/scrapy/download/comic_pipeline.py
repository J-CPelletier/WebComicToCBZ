import os
from zipfile import ZipFile

import click
import scrapy
from scrapy.exceptions import DropItem
from scrapy.pipelines.files import FilesPipeline

from webcomix.comic import Comic


class ComicPipeline(FilesPipeline):
    def get_media_requests(self, item, info):
        click.echo("Saving image {}".format(item.get("url")))
        image_path_directory = Comic.save_image_location(
            item.get("url"), item.get("page"), info.spider.directory
        )
        if os.path.isfile(image_path_directory) or self.image_in_zipfile(
            item, info.spider.directory
        ):
            click.echo("The image was already downloaded. Skipping...")
            raise DropItem("The image was already downloaded. Skipping...")
        yield scrapy.Request(
            item.get("url"),
            meta={
                "image_file_name": Comic.save_image_location(
                    item.get("url"), item.get("page")
                )
            },
        )

    def item_completed(self, results, item, info):
        file_paths = [data["path"] for ok, data in results if ok]
        if not file_paths:
            click.echo("Could not find comic image.")
            raise DropItem("Could not find comic image.")

        return item

    def file_path(self, request, response=None, info=None):
        return request.meta.get("image_file_name")

    @staticmethod
    def image_in_zipfile(item, directory):
        zipfile_path = "{}.cbz".format(directory)
        if os.path.isfile(zipfile_path):
            return False
        image_path_cbz = Comic.save_image_location(item.get("url"), item.get("page"))
        with ZipFile(zipfile_path, "r") as zipfile:
            return image_path_cbz in zipfile.namelist()
