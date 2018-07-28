from click.testing import CliRunner

from webcomix import main
from webcomix.comic import Comic
from webcomix.supported_comics import supported_comics


def test_print_verification(capfd):
    verification = Comic.verify_xpath(*supported_comics["xkcd"])
    main.print_verification(verification)
    out, err = capfd.readouterr()
    assert out == (
        "Page 1: \n"
        "Page URL: http://xkcd.com/1/\n"
        "Image URL: http://imgs.xkcd.com/comics/barrel_cropped_(1).jpg\n"
        "\n"
        "Page 2: \n"
        "Page URL: http://xkcd.com/2/\n"
        "Image URL: http://imgs.xkcd.com/comics/tree_cropped_(1).jpg\n"
        "\n"
        "Page 3: \n"
        "Page URL: http://xkcd.com/3/\n"
        "Image URL: http://imgs.xkcd.com/comics/island_color.jpg\n\n")


def test_comics():
    runner = CliRunner()
    result = runner.invoke(main.comics)
    assert result.exit_code == 0
    assert len(result.output) > 0


def mock_download(comic, name):
    print(name)


first_comic = list(sorted(supported_comics.keys()))[0]


def test_good_download(monkeypatch):
    runner = CliRunner()
    monkeypatch.setattr(Comic, "download", mock_download)

    result = runner.invoke(main.download, [first_comic])
    assert result.exit_code == 0
    assert result.output.strip() == first_comic


def test_bad_download(monkeypatch):
    runner = CliRunner()
    monkeypatch.setattr(Comic, "download", mock_download)

    result = runner.invoke(main.download, ["foo"])
    assert result.exit_code == 0
    assert result.output == ""


def mock_make_cbz(comic_class, name, source_directory):
    print(".cbz created")


def test_good_download_makecbz(monkeypatch):
    runner = CliRunner()
    monkeypatch.setattr(Comic, "download", mock_download)
    monkeypatch.setattr(Comic, "make_cbz", mock_make_cbz)

    result = runner.invoke(main.download, [first_comic, "--cbz"])
    assert result.exit_code == 0
    assert result.output.strip() == "\n".join([first_comic, ".cbz created"])


def test_bad_download_make_cbz(monkeypatch):
    runner = CliRunner()
    monkeypatch.setattr(Comic, "download", mock_download)
    monkeypatch.setattr(Comic, "make_cbz", mock_make_cbz)

    result = runner.invoke(main.download, ["foo", "--cbz"])
    assert result.exit_code == 0
    assert result.output == ""


def mock_verify_xpath(url, next_page, comic_image):
    print("Verified")


def mock_print_verification(validation):
    print("Printed")


def test_custom(monkeypatch):
    runner = CliRunner()
    monkeypatch.setattr(Comic, "download", mock_download)
    monkeypatch.setattr(Comic, "verify_xpath", mock_verify_xpath)
    monkeypatch.setattr(main, "print_verification", mock_print_verification)

    result = runner.invoke(main.custom, [
        "--comic_name=foo", "--start_url=url", "--next_page_xpath=next_page",
        "--image_xpath=image"
    ], "yes")
    assert result.exit_code == 0
    assert result.output.strip() == "\n".join([
        "Verified", "Printed",
        "Verify that the links above are correct.",
        "Are you sure you want to proceed? [y/N]: yes", "foo"
    ])


def test_custom_make_cbz(monkeypatch):
    runner = CliRunner()
    monkeypatch.setattr(Comic, "download", mock_download)
    monkeypatch.setattr(Comic, "verify_xpath", mock_verify_xpath)
    monkeypatch.setattr(main, "print_verification", mock_print_verification)
    monkeypatch.setattr(Comic, "make_cbz", mock_make_cbz)

    result = runner.invoke(main.custom, [
        "--comic_name=foo", "--start_url=url", "--next_page_xpath=next_page",
        "--image_xpath=image", "--cbz"
    ], "y")
    assert result.exit_code == 0
    assert result.output.strip() == "\n".join([
        "Verified", "Printed",
        "Verify that the links above are correct.",
        "Are you sure you want to proceed? [y/N]: y", "foo", ".cbz created"
    ])


def mock_discovery(url):
    return Comic("url", "next_page", "comic_image")


def test_search(monkeypatch):
    runner = CliRunner()
    main.discovery = mock_discovery
    monkeypatch.setattr(Comic, "download", mock_download)
    monkeypatch.setattr(Comic, "verify_xpath", mock_verify_xpath)
    monkeypatch.setattr(main, "print_verification", mock_print_verification)

    result = runner.invoke(main.search, ["foo", "--start_url=good"], "y")
    assert result.exit_code == 0
    assert result.output.strip() == "\n".join([
        "Verified", "Printed",
        "Verify that the links above are correct.",
        "Are you sure you want to proceed? [y/N]: y", "foo"
    ])