import argparse
import logging

from logging.handlers import RotatingFileHandler

from constants import (
    PRETTY_ARGUMENT,
    FILE_ARGUMENT,
    LOG_DIR,
    LOG_FILE,
    LOG_FORMAT,
    DT_FORMAT
)


def configure_argument_parser(available_models):
    parser = argparse.ArgumentParser(description='Парсер документации Python')
    parser.add_argument(
        'mode',
        choices=available_models,
        help='Режимы работы парсера',
    )
    parser.add_argument(
        '-c',
        '--clear-cache',
        action='store_true',
        help='Очистка кеша',
    )
    parser.add_argument(
        '-o',
        '--output',
        choices=(PRETTY_ARGUMENT, FILE_ARGUMENT),
        help='Дополнительные способы вывода данных'
    )
    return parser


def configure_logging():
    LOG_DIR.mkdir(exist_ok=True)
    rotating_handler = RotatingFileHandler(
        LOG_FILE,
        maxBytes=10 ** 6,
        backupCount=5,
        encoding='utf-8'
    )
    logging.basicConfig(
        datefmt=DT_FORMAT,
        format=LOG_FORMAT,
        level=logging.INFO,
        handlers=(rotating_handler, logging.StreamHandler())
    )
