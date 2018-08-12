from webcomix.comic import Comic
from webcomix.search import discovery


def test_search_searchable_website(mocker):
    expected = Comic(
        "http://www.blindsprings.com/comic/blindsprings-cover-book-one",
        "//*[contains(translate(@class, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'), 'next')]//@href",
        "//*[contains(translate(@src, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'), 'comic')]//@src"
    )
    mocker.patch('webcomix.search.possible_next_page_xpath', ["next"])
    mocker.patch('webcomix.search.possible_image_xpath', ["comic"])
    mocker.patch('webcomix.search.possible_tags_image', ["*"])
    mocker.patch('webcomix.search.possible_tags_next', ["*"])
    mocker.patch('webcomix.search.possible_attributes_image', ["@src"])
    mocker.patch('webcomix.search.possible_attributes_next', ["@class"])
    mocker.patch('webcomix.util.check_first_pages')
    result = discovery(
        'http://www.blindsprings.com/comic/blindsprings-cover-book-one')
    assert Comic.verify_xpath(
        expected.start_url, expected.next_page_selector,
        expected.comic_image_selector) == [
            ('http://www.blindsprings.com/comic/blindsprings-cover-book-one',
             ['http://www.blindsprings.com/comics/cover.jpg']),
            ('http://www.blindsprings.com/comic/blindsprings-page-one',
             ['http://www.blindsprings.com/comics/1430199037-TB_01_001.jpg']),
            ('http://www.blindsprings.com/comic/blindsprings-page-two',
             ['http://www.blindsprings.com/comics/1430198957-TB_01_002.jpg'])
        ]

    assert result.start_url == expected.start_url
    assert result.next_page_selector == expected.next_page_selector
    assert result.comic_image_selector == expected.comic_image_selector


def test_search_unsearchable_website(mocker):
    mocker.patch('webcomix.search.possible_next_page_xpath', [])
    mocker.patch('webcomix.search.possible_image_xpath', [])
    mocker.patch('webcomix.search.possible_tags_image', [])
    mocker.patch('webcomix.search.possible_tags_next', [])
    mocker.patch('webcomix.search.possible_attributes_image', [])
    mocker.patch('webcomix.search.possible_attributes_next', [])

    assert discovery("test") is None
