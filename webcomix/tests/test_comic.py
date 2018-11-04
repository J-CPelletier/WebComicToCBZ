import os
import shutil
from zipfile import ZipFile, BadZipFile

import pytest

from webcomix.comic import Comic
from webcomix.supported_comics import supported_comics


def test_save_image_location():
    assert (
        Comic.save_image_location(
            "http://imgs.xkcd.com/comics/barrel_cropped_(1).jpg", 1, "foo"
        )
        == "foo/1.jpg"
    )
    assert Comic.save_image_location("", 1, "bar") == "bar/1"


def test_make_cbz():
    comic = Comic(
        "xkcd",
        "http://xkcd.com/1/",
        "//a[@rel='next']/@href",
        "//div[@id='comic']/img/@src",
    )
    os.mkdir("xkcd")
    for i in range(1, 6):
        with open("xkcd/{}.txt".format(i), "w") as image_file:
            image_file.write("testing {}".format(i))
    comic.convert_to_cbz()
    with ZipFile("xkcd.cbz") as cbz_file:
        for i in range(1, 6):
            with cbz_file.open("{}.txt".format(i), "r") as image_file:
                assert str(image_file.read()).strip("b'") == "testing {}".format(i)
    os.remove("xkcd.cbz")


def test_make_cbz_corrupted_archive(mocker, capfd):
    corrupted_archive = mocker.patch.object(ZipFile, "testzip", return_value=mocker.ANY)
    comic = Comic(
        "xkcd",
        "http://xkcd.com/1/",
        "//a[@rel='next']/@href",
        "//div[@id='comic']/img/@src",
    )
    os.mkdir("xkcd")
    for i in range(1, 6):
        with open("xkcd/{}.txt".format(i), "w") as image_file:
            image_file.write("testing {}".format(i))
    with pytest.raises(BadZipFile):
        comic.convert_to_cbz()
    os.remove("xkcd.cbz")


def test_download_runs_the_spider(mocker):
    mock_spider_running = mocker.patch("webcomix.comic.Comic.run_spider")
    comic = Comic(
        "xkcd",
        "http://xkcd.com/1/",
        "//a[@rel='next']/@href",
        "//div[@id='comic']//img/@src",
    )
    comic.download()
    assert mock_spider_running.call_count == 1
    shutil.rmtree("xkcd")


def test_download_saves_the_files():
    comic = Comic(
        "test",
        "https://j-cpelletier.github.io/webcomix/1.html",
        "//a/@href",
        "//img/@src",
    )
    comic.download()
    path, dirs, files = next(os.walk("test"))
    assert len(files) == 2
    shutil.rmtree("test")


def test_download_does_not_add_crawlers_in_main_process(mocker):
    mock_spider_running = mocker.patch("webcomix.comic.Comic.run_spider")
    mock_add_to_crawl = mocker.patch("scrapy.crawler.Crawler.crawl")
    comic = Comic(
        "test",
        "https://j-cpelletier.github.io/webcomix/1.html",
        "//a/@href",
        "//img/@src",
    )
    comic.download()
    assert mock_add_to_crawl.call_count == 0


def test_verify_xpath():
    comic = Comic("xkcd", *supported_comics["xkcd"])
    assert comic.verify_xpath() == [
        ("http://xkcd.com/1/", ["http://imgs.xkcd.com/comics/barrel_cropped_(1).jpg"]),
        ("http://xkcd.com/2/", ["http://imgs.xkcd.com/comics/tree_cropped_(1).jpg"]),
        ("http://xkcd.com/3/", ["http://imgs.xkcd.com/comics/island_color.jpg"]),
    ]
