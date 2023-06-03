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

## Результаты тестов сервера

Результаты **http-test-suite** теста:

``` bash
 *  Executing task in folder homeworks: python httptest.py 

directory index file exists ... ok
document root escaping forbidden ... ok
Send bad http headers ... ok
file located in nested folders ... ok
absent file returns 404 ... ok
urlencoded filename ... ok
file with two dots in name ... ok
query string after filename ... ok
slash after filename ... ok
filename with spaces ... ok
Content-Type for .css ... ok
Content-Type for .gif ... ok
Content-Type for .html ... ok
Content-Type for .jpeg ... ok
Content-Type for .jpg ... ok
Content-Type for .js ... ok
Content-Type for .png ... ok
Content-Type for .swf ... ok
head method support ... ok
directory index file absent ... ok
large file downloaded correctly ... ok
post method forbidden ... ok
Server header exists ... ok

----------------------------------------------------------------------
Ran 23 tests in 0.097s
```

Результаты **Apache Benchmark** теста (timeout = 5 секунд):

``` bash
This is ApacheBench, Version 2.3 <$Revision: 1843412 $>
Copyright 1996 Adam Twiss, Zeus Technology Ltd, http://www.zeustech.net/
Licensed to The Apache Software Foundation, http://www.apache.org/

Benchmarking 127.0.0.1 (be patient)
Completed 5000 requests
Completed 10000 requests
Completed 15000 requests
Completed 20000 requests
Completed 25000 requests
Completed 30000 requests
Completed 35000 requests
Completed 40000 requests
Completed 45000 requests
Completed 50000 requests
Finished 50000 requests


Server Software:        Python-edu-server/0.1.0
Server Hostname:        127.0.0.1
Server Port:            8080

Document Path:          /httptest/dir2/page.html
Document Length:        38 bytes

Concurrency Level:      100
Time taken for tests:   117.163 seconds
Complete requests:      50000
Failed requests:        263
   (Connect: 0, Receive: 83, Length: 97, Exceptions: 83)
Non-2xx responses:      14
Total transferred:      9536415 bytes
HTML transferred:       1896846 bytes
Requests per second:    426.75 [#/sec] (mean)
Time per request:       234.327 [ms] (mean)
Time per request:       2.343 [ms] (mean, across all concurrent requests)
Transfer rate:          79.49 [Kbytes/sec] received

Connection Times (ms)
              min  mean[+/-sd] median   max
Connect:        0   22 375.1      0   15580
Processing:     1  165 4147.3      2  114000
Waiting:        0   12 561.9      1   70130
Total:          1  187 4395.2      2  117150

Percentage of the requests served within a certain time (ms)
  50%      2
  66%      2
  75%      2
  80%      2
  90%      3
  95%      3
  98%      3
  99%      6
 100%  117150 (longest request)
```
