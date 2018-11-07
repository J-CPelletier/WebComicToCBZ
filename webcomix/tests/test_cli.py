from click.testing import CliRunner

from webcomix import cli
from webcomix.comic import Comic
from webcomix.supported_comics import supported_comics

first_comic = list(sorted(supported_comics.keys()))[0]


def test_print_verification(capfd):
    comic = Comic("xkcd", *supported_comics["xkcd"])
    verification = comic.verify_xpath()
    cli.print_verification(verification)
    out, err = capfd.readouterr()
    assert out == (
        "Page 1:\n"
        "Page URL: https://xkcd.com/1/\n"
        "Image URLs:\n"
        "https://imgs.xkcd.com/comics/barrel_cropped_(1).jpg\n"
        "\n"
        "Page 2:\n"
        "Page URL: https://xkcd.com/2/\n"
        "Image URLs:\n"
        "https://imgs.xkcd.com/comics/tree_cropped_(1).jpg\n"
        "\n"
        "Page 3:\n"
        "Page URL: https://xkcd.com/3/\n"
        "Image URLs:\n"
        "https://imgs.xkcd.com/comics/island_color.jpg\n"
        "\n"
    )


def test_comics():
    runner = CliRunner()
    result = runner.invoke(cli.comics)
    assert result.exit_code == 0
    assert len(result.output) > 0


def test_good_download_ends_up_downloading(mocker):
    runner = CliRunner()
    mock_download = mocker.patch("webcomix.comic.Comic.download")

    result = runner.invoke(cli.download, [first_comic])
    assert result.exit_code == 0
    assert mock_download.call_count == 1


def test_predefined_unknown_comic_does_not_download(mocker):
    runner = CliRunner()
    mock_download = mocker.patch("webcomix.comic.Comic.download")

    result = runner.invoke(cli.download, ["foo"])
    assert result.exit_code == 0
    assert mock_download.call_count == 0


def test_predefined_downloadable_comic_downloads_the_comic(mocker):
    runner = CliRunner()
    mock_download = mocker.patch("webcomix.comic.Comic.download")

    result = runner.invoke(cli.download, [first_comic])
    assert result.exit_code == 0
    assert mock_download.call_count == 1


def test_predefined_downloadable_comic_makes_the_cbz_file(mocker):
    runner = CliRunner()
    mock_download = mocker.patch("webcomix.comic.Comic.download")
    mock_convert_to_cbz = mocker.patch("webcomix.comic.Comic.convert_to_cbz")

    result = runner.invoke(cli.download, [first_comic, "--cbz"])
    assert result.exit_code == 0
    assert mock_convert_to_cbz.call_count == 1


def test_predefined_unknown_comic_does_not_make_the_cbz_file(mocker):
    runner = CliRunner()
    mock_download = mocker.patch("webcomix.comic.Comic.download")
    mock_convert_to_cbz = mocker.patch("webcomix.comic.Comic.convert_to_cbz")

    result = runner.invoke(cli.download, ["foo", "--cbz"])
    assert result.exit_code == 0
    assert mock_convert_to_cbz.call_count == 0


def test_custom_comic_asks_for_verification_before_downloading(mocker):
    runner = CliRunner()
    mock_manager = mocker.Mock()
    mock_download = mocker.patch("webcomix.comic.Comic.download")
    mock_verify_xpath = mocker.patch("webcomix.comic.Comic.verify_xpath")
    mock_print_verification = mocker.patch("webcomix.cli.print_verification")
    mock_manager.attach_mock(mock_download, "download")
    mock_manager.attach_mock(mock_verify_xpath, "verify_xpath")
    mock_manager.attach_mock(mock_print_verification, "print_verification")

    result = runner.invoke(
        cli.custom,
        [
            "--comic_name=foo",
            "--start_url=url",
            "--next_page_xpath=next_page",
            "--image_xpath=image",
        ],
        "yes",
    )
    assert result.exit_code == 0
    mock_manager.assert_has_calls(
        [
            mocker.call.verify_xpath(),
            mocker.call.print_verification(mocker.ANY),
            mocker.call.download(),
        ]
    )


def test_custom_comic_makes_the_cbz_file(mocker):
    runner = CliRunner()
    mock_download = mocker.patch("webcomix.comic.Comic.download")
    mock_verify_xpath = mocker.patch("webcomix.comic.Comic.verify_xpath")
    mock_print_verification = mocker.patch("webcomix.cli.print_verification")
    mock_convert_to_cbz = mocker.patch("webcomix.comic.Comic.convert_to_cbz")

    result = runner.invoke(
        cli.custom,
        [
            "--comic_name=foo",
            "--start_url=url",
            "--next_page_xpath=next_page",
            "--image_xpath=image",
            "--cbz",
        ],
        "y",
    )
    assert result.exit_code == 0
    assert mock_convert_to_cbz.call_count == 1


def test_discovered_comic_searches_for_a_comic(mocker):
    runner = CliRunner()
    mock_discovery = mocker.patch(
        "webcomix.cli.discovery",
        return_value=Comic(mocker.ANY, mocker.ANY, mocker.ANY, mocker.ANY),
    )
    mock_download = mocker.patch("webcomix.comic.Comic.download")
    mock_verify_xpath = mocker.patch("webcomix.comic.Comic.verify_xpath")
    mock_print_verification = mocker.patch("webcomix.cli.print_verification")

    result = runner.invoke(cli.search, ["foo", "--start_url=good"], "y")
    assert result.exit_code == 0
    assert mock_discovery.call_count == 1


def test_discovered_comic_asks_for_verification_before_downloading(mocker):
    runner = CliRunner()
    mock_manager = mocker.Mock()
    mock_discovery = mocker.patch(
        "webcomix.cli.discovery",
        return_value=Comic(mocker.ANY, mocker.ANY, mocker.ANY, mocker.ANY),
    )
    mock_download = mocker.patch("webcomix.comic.Comic.download")
    mock_verify_xpath = mocker.patch("webcomix.comic.Comic.verify_xpath")
    mock_print_verification = mocker.patch("webcomix.cli.print_verification")
    mock_manager.attach_mock(mock_download, "download")
    mock_manager.attach_mock(mock_verify_xpath, "verify_xpath")
    mock_manager.attach_mock(mock_print_verification, "print_verification")

    result = runner.invoke(cli.search, ["foo", "--start_url=good"], "y")
    assert result.exit_code == 0
    mock_manager.assert_has_calls(
        [
            mocker.call.verify_xpath(),
            mocker.call.print_verification(mocker.ANY),
            mocker.call.download(),
        ]
    )


def test_discovered_comic_makes_cbz_file(mocker):
    runner = CliRunner()
    mock_discovery = mocker.patch(
        "webcomix.cli.discovery",
        return_value=Comic(mocker.ANY, mocker.ANY, mocker.ANY, mocker.ANY),
    )
    mock_download = mocker.patch("webcomix.comic.Comic.download")
    mock_verify_xpath = mocker.patch("webcomix.comic.Comic.verify_xpath")
    mock_print_verification = mocker.patch("webcomix.cli.print_verification")
    mock_convert_to_cbz = mocker.patch("webcomix.comic.Comic.convert_to_cbz")

    result = runner.invoke(cli.search, ["foo", "--start_url=good", "--cbz"], "y")
    assert result.exit_code == 0
    assert mock_convert_to_cbz.call_count == 1