from bs4 import BeautifulSoup

from requests import RequestException

from exceptions import ParserFindTagException

from constants import ENCODING_UTF


def get_response(session, url):
    try:
        response = session.get(url)
        response.encoding = ENCODING_UTF
        return response
    except RequestException:
        error_msg = f'Возникла ошибка при загрузке страницы {url}'
        raise ConnectionError(error_msg)


def make_soup(session, url):
    return BeautifulSoup(get_response(session, url).text, features='lxml')


def find_tag(soup, tag, attrs=None):
    searched_tag = soup.find(tag, attrs=(attrs or {}))
    if searched_tag is None:
        error_msg = f'Не найден тег {tag} {attrs}'
        raise ParserFindTagException(error_msg)

    return searched_tag
