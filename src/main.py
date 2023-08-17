import re
import logging
from collections import defaultdict
from urllib.parse import urljoin

import requests_cache
from bs4 import BeautifulSoup
from tqdm import tqdm

from exceptions import LatestVersionException
from constants import BASE_DIR, MAIN_DOC_URL, MAIN_PEP_URL, EXPECTED_STATUS
from configs import configure_argument_parser, configure_logging
from outputs import control_output
from utils import get_response, find_tag, make_soup


def whats_new(session):
    whats_new_url = urljoin(MAIN_DOC_URL, 'whatsnew/')
    soup = make_soup(session, whats_new_url)
    main_div = find_tag(soup, 'section', attrs={'id': 'what-s-new-in-python'})
    div_with_ul = find_tag(main_div, 'div', attrs={'class': 'toctree-wrapper'})
    sections_by_python = div_with_ul.find_all('li',
                                              attrs={'class': 'toctree-l1'})
    results = [('Ссылка на статью', 'Заголовок', 'Редактор, Автор')]

    for section in tqdm(sections_by_python):
        version_a_tag = section.find('a')
        href = version_a_tag['href']
        version_link = urljoin(whats_new_url, href)
        response = get_response(session, version_link)
        if response is None:
            error_msg = 'Ответ не получен'
            logging.error(error_msg, stack_info=True)
            continue
        soup = BeautifulSoup(response.text, features='lxml')
        h1 = find_tag(soup, 'h1')
        dl = find_tag(soup, 'dl')
        dl_text = dl.text.replace('\n', ' ')
        results.append((version_link, h1.text, dl_text))

    return results


def latest_versions(session):
    soup = make_soup(session, MAIN_DOC_URL)
    sidebar = find_tag(soup, 'div', attrs={'class': 'sphinxsidebarwrapper'})
    ul_tags = sidebar.find_all('ul')
    for ul in ul_tags:
        if 'All versions' in ul.text:
            a_tags = ul.find_all('a')
            break
    else:
        raise LatestVersionException('Ничего не нашлось')

    results = [('Ссылка на документацию', 'Версия', 'Статус')]
    pattern = r'Python (?P<version>\d\.\d+) \((?P<status>.*)\)'
    for a_tag in a_tags:
        link = a_tag['href']
        text_match = re.search(pattern, a_tag.text)
        if text_match is not None:
            version, status = text_match.groups()
        else:
            version, status = a_tag.text, ''

        results.append((link, version, status))

    return results


def download(session):
    downloads_url = urljoin(MAIN_DOC_URL, 'download.html')
    soup = make_soup(session, downloads_url)
    table = find_tag(soup, 'table', attrs='docutils')
    pdf_a4_tag = find_tag(table, 'a', {'href': re.compile(r'.+pdf-a4\.zip$')})
    pdf_a4_link = pdf_a4_tag['href']
    archive_url = urljoin(downloads_url, pdf_a4_link)
    filename = archive_url.split('/')[-1]
    downloads_dir = BASE_DIR / 'downloads'
    downloads_dir.mkdir(exist_ok=True)
    archive_path = downloads_dir / filename
    response = session.get(archive_url)
    with open(archive_path, 'wb') as file:
        file.write(response.content)
    logging.info(f'Архив был загружен и сохранен: {archive_path}')


def pep(session):
    soup = make_soup(session, MAIN_PEP_URL)
    main_tag = find_tag(soup, 'section', {'id': 'numerical-index'})
    tbody_tag = find_tag(main_tag, 'tbody')
    tr_tags = tbody_tag.find_all('tr')
    status_sum = defaultdict(int)
    total_peps = 0
    results = [('Статус', 'Количество')]

    for tr_tag in tr_tags:
        td_tag = find_tag(tr_tag, 'td')
        preview_status = td_tag.text[1:]
        a_tag = find_tag(tr_tag, 'a')
        href = a_tag['href']
        link = urljoin(MAIN_PEP_URL, href)
        soup = make_soup(session, link)
        dt_tags = soup.find_all('dt')
        for dt_tag in dt_tags:
            if dt_tag.text == 'Status:':
                total_peps += 1
                status = dt_tag.find_next_sibling().string
                status_sum[status] += 1
                if status not in EXPECTED_STATUS[preview_status]:
                    error_msg = (
                        'Несовпадающие статусы:\n'
                        f'{link}\n'
                        f'Статус в картрочке: {status}\n'
                        f'Ожидаемые статусы: {EXPECTED_STATUS[preview_status]}'
                    )
                    logging.warning(error_msg)
    results.extend([(status, status_sum[status]) for status in status_sum])
    results.append(('Total', total_peps))
    return results


MODE_TO_FUNCTION = {
    'whats-new': whats_new,
    'latest-versions': latest_versions,
    'download': download,
    'pep': pep,
}


def main():
    configure_logging()
    logging.info('Парсер запущен!')
    args_parser = configure_argument_parser(MODE_TO_FUNCTION.keys())
    args = args_parser.parse_args()
    logging.info(f'Аргументы командной строки: {args}')
    session = requests_cache.CachedSession()
    if args.clear_cache:
        session.cache.clear()
    parser_mode = args.mode
    results = MODE_TO_FUNCTION[parser_mode](session)

    if results is not None:
        control_output(results, args)
    logging.info('Парсер завершил работу.')


if __name__ == '__main__':
    main()
