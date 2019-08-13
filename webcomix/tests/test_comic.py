import os
import shutil
from zipfile import ZipFile, BadZipFile

import pytest

from webcomix.comic import Comic, SPLASH_SETTINGS
from webcomix.supported_comics import supported_comics
from webcomix.tests.fake_websites.fixture import three_webpages_uri, one_webpage_uri


@pytest.fixture
def cleanup_test_directories():
    if os.path.isfile("xkcd.cbz"):
        os.remove("xkcd.cbz")
    if os.path.isfile("test.cbz"):
        os.remove("test.cbz")
    if os.path.isdir("xkcd"):
        shutil.rmtree("xkcd")
    if os.path.isdir("test"):
        shutil.rmtree("test")
    yield None
    if os.path.isdir("xkcd"):
        shutil.rmtree("xkcd")
    if os.path.isdir("test"):
        shutil.rmtree("test")
    if os.path.isfile("xkcd.cbz"):
        os.remove("xkcd.cbz")
    if os.path.isfile("test.cbz"):
        os.remove("test.cbz")


@pytest.fixture
def fake_downloaded_xkcd_comic():
    if os.path.isfile("xkcd.cbz"):
        os.remove("xkcd.cbz")
    if os.path.isdir("xkcd"):
        shutil.rmtree("xkcd")
    comic = Comic(
        "xkcd",
        "http://xkcd.com/1/",
        "//div[@id='comic']/img/@src",
        "//a[@rel='next']/@href",
        False,
    )
    os.mkdir("xkcd")
    for i in range(1, 6):
        with open("xkcd/{}.txt".format(i), "w") as image_file:
            image_file.write("testing {}".format(i))
    yield comic
    if os.path.isfile("xkcd.cbz"):
        os.remove("xkcd.cbz")
    if os.path.isdir("xkcd"):
        shutil.rmtree("xkcd")


def test_save_image_location():
    assert (
        Comic.save_image_location(
            "http://imgs.xkcd.com/comics/barrel_cropped_(1).jpg", 1, "foo"
        )
        == "foo/1.jpg"
    )
    assert Comic.save_image_location("", 1, "bar") == "bar/1"


def test_make_cbz(fake_downloaded_xkcd_comic):
    fake_downloaded_xkcd_comic.convert_to_cbz()
    with ZipFile("xkcd.cbz") as cbz_file:
        for i in range(1, 6):
            with cbz_file.open("{}.txt".format(i), "r") as image_file:
                assert image_file.read().decode("ascii") == "testing {}".format(i)


def test_make_cbz_corrupted_archive(mocker, capfd, fake_downloaded_xkcd_comic):
    mocker.patch.object(ZipFile, "testzip", return_value=mocker.ANY)
    with pytest.raises(BadZipFile):
        fake_downloaded_xkcd_comic.convert_to_cbz()


def test_download_runs_the_worker(mocker, cleanup_test_directories):
    mock_crawler_running = mocker.patch(
        "webcomix.scrapy.crawler_worker.CrawlerWorker.start"
    )
    comic = Comic(
        "xkcd",
        "http://xkcd.com/1/",
        "//div[@id='comic']//img/@src",
        "//a[@rel='next']/@href",
        False,
    )
    comic.download()
    assert mock_crawler_running.call_count == 1


def test_download_saves_the_files(cleanup_test_directories, three_webpages_uri):
    comic = Comic("test", three_webpages_uri, "//img/@src", "//a/@href", False)
    comic.download()
    path, dirs, files = next(os.walk("test"))
    assert len(files) == 2


def test_download_does_not_add_crawlers_in_main_process(
    mocker, cleanup_test_directories, three_webpages_uri
):
    mocker.patch("webcomix.scrapy.crawler_worker.CrawlerWorker.start")
    mock_add_to_crawl = mocker.patch("scrapy.crawler.Crawler.crawl")
    comic = Comic("test", three_webpages_uri, "//img/@src", "//a/@href", False)
    comic.download()
    assert mock_add_to_crawl.call_count == 0


def test_convert_to_cbz_adds_all_files_to_cbz(
    cleanup_test_directories, three_webpages_uri
):
    comic = Comic("test", three_webpages_uri, "//img/@src", "//a/@href", False)
    comic.download()
    comic.convert_to_cbz()
    with ZipFile("{}.cbz".format(comic.name), mode="r") as cbz_file:
        assert len(cbz_file.infolist()) == 2


def test_verify_xpath():
    comic = Comic("xkcd", *supported_comics["xkcd"])
    assert comic.verify_xpath() == [
        {
            "page": 1,
            "url": "https://xkcd.com/1/",
            "image_urls": ["https://imgs.xkcd.com/comics/barrel_cropped_(1).jpg"],
        },
        {
            "page": 2,
            "url": "https://xkcd.com/2/",
            "image_urls": ["https://imgs.xkcd.com/comics/tree_cropped_(1).jpg"],
        },
        {
            "page": 3,
            "url": "https://xkcd.com/3/",
            "image_urls": ["https://imgs.xkcd.com/comics/island_color.jpg"],
        },
    ]


def test_verify_xpath_only_verifies_one_page_with_single_page(one_webpage_uri):
    comic = Comic("test", one_webpage_uri, "//img/@src", "//a/@href", True)
    actual = comic.verify_xpath()
    assert len(actual) == 1
    assert len(actual[0]["image_urls"]) == 2


def test_download_will_run_javascript_settings_if_javascript(mocker):
    mocker.patch("os.path.isdir")
    mock_crawler_worker = mocker.patch("webcomix.comic.CrawlerWorker")
    comic = Comic(mocker.ANY, mocker.ANY, mocker.ANY, mocker.ANY, mocker.ANY, True)
    comic.download()
    settings = mock_crawler_worker.call_args_list[0][0][0]
    assert all(setting in settings for setting in SPLASH_SETTINGS)


def test_download_will_not_run_javascript_settings_if_not_javascript(mocker):
    mocker.patch("os.path.isdir")
    mock_crawler_worker = mocker.patch("webcomix.comic.CrawlerWorker")
    comic = Comic(mocker.ANY, mocker.ANY, mocker.ANY, mocker.ANY, mocker.ANY, False)
    comic.download()
    settings = mock_crawler_worker.call_args_list[0][0][0]
    assert all(setting not in settings for setting in SPLASH_SETTINGS)


def test_verify_xpath_will_run_javascript_settings_if_javascript(mocker):
    mocker.patch("os.path.isdir")
    mock_crawler_worker = mocker.patch("webcomix.comic.CrawlerWorker")
    comic = Comic(mocker.ANY, mocker.ANY, mocker.ANY, mocker.ANY, mocker.ANY, True)
    comic.verify_xpath()
    settings = mock_crawler_worker.call_args_list[0][0][0]
    assert all(setting in settings for setting in SPLASH_SETTINGS)


def test_verify_xpath_will_not_run_javascript_settings_if_not_javascript(mocker):
    mocker.patch("os.path.isdir")
    mock_crawler_worker = mocker.patch("webcomix.comic.CrawlerWorker")
    comic = Comic(mocker.ANY, mocker.ANY, mocker.ANY, mocker.ANY, mocker.ANY, False)
    comic.verify_xpath()
    settings = mock_crawler_worker.call_args_list[0][0][0]
    assert all(setting not in settings for setting in SPLASH_SETTINGS)