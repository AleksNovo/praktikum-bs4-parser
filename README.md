# Парсер документации python и PEP

### Перед использованием
Клонируйте репозиторий:
```
git clone git@github.com:t1sha-py/bs4_parser_pep.git
```

Создайте виртуальное окружение и установите зависимости.
```
python -m venv venv
```
```
pip install -r requirements.txt
```
### Запуск парсера:
```
main.py [-h] [-c] [-o {pretty,file}] {whats-new,latest-versions,download,pep}
Парсер документации Python

positional arguments:
  {whats-new,latest-versions,download,pep}
                        Режимы работы парсера

optional arguments:
  -h, --help            show this help message and exit
  -c, --clear-cache     Очистка кеша
  -o {pretty,file}, --output {pretty,file}
                        Дополнительные способы вывода данных
```
### Режимы работы парсера:
1. ```python main.py whats-new``` - Парсер статей по нововведениям в Python.
2. ```python main.py latest-versions``` - Статусы последних версий со ссылками на документацию.
3. ```python main.py download``` - Скачивание документации по последней версии Python.
4. ```python main.py pep``` - Формирование таблицы с количеством PEP в разрезе по статусам.
