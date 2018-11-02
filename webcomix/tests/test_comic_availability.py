import pytest

from webcomix.comic import Comic
from webcomix.supported_comics import supported_comics
from webcomix.util import check_first_pages


@pytest.mark.slow
def test_supported_comics():
    for comic_name, comic_info in supported_comics.items():
        comic = Comic(comic_name, *comic_info)
        first_pages = comic.verify_xpath()
        check_first_pages(first_pages)
