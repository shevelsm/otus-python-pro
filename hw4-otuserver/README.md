# Homework 04: OTUServer

## Введение

Задание: разработать веб-сервер частично реализующий протокол HTTP.

Веб-сервер должен уметь:

- Масштабироваться на несколько worker'ов;
- Числов worker'ов задается аргументом командной строки -w;
- Отвечать 200, 403 или 404 на GET-запросы и HEAD-запросы;
- Отвечать 405 на прочие запросы;
- Возвращать файлы по произвольному пути в DOCUMENT_ROOT;
- Вызов /file.html должен возвращать содердимое DOCUMENT_ROOT/file.html;
- DOCUMENT_ROOT задается аргументом командной строки -r;
- Возвращать index.html как индекс директории;
- Вызов /directory/ должен возвращать DOCUMENT_ROOT/directory/index.html;
- Отвечать следующими заголовками для успешных GET-запросов: Date, Server,Content-Length, Content-Type, Connection;
- Корректный Content-Type для: .html, .css, .js, .jpg, .jpeg, .png, .gif, .swf

## Конфигурация и запуск

Данные сервер имеет несколько настроек реализуемых через ключи.

```bash
$ python3 httpd.py -h

usage: httpd.py [-h] [-s HOST] [-p PORT] [-w WORKERS] [-r ROOT] [-d]

OTUServer

optional arguments:
  -h, --help            show this help message and exit
  -s HOST, --host HOST  Hostname
  -p PORT, --port PORT  Port number
  -w WORKERS, --workers WORKERS
                        Number of workers
  -r ROOT, --root ROOT  Files root directory (DOCUMENT_ROOT)
  -d, --debug           Show debug messages
```

## Тестирование

Для тестирования используется готовый сценарий с нужными материалами.

```bash
# Clone repository with test files
git clone https://github.com/s-stupnikov/http-test-suite www
# Set 8080 port 
sed -i 's/80/8080/g' www/httptest.py
# Unit-tests
python3 httptest.py
# Load testing with "Apache Benchmark"
ab -n 50000 -c 100 -r http://127.0.0.1:8080/httptest/dir2/page.html
```
