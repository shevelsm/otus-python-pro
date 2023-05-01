# Log analyzer

## Описание

Скрипт обрабатывает последний (дата определяется по имени файла) nginx лог вида "nginx-access-ui.log-YYYYMMDD" и формирует HTML-отчет со следующими столбцами:

`count` - количество вхождений URL (из параметра $request)

`count_perc` - количество вхождений URL в процентнах относительно общего числа запросов

`time_sum` - суммарное время $request_time для данного URL

`time_perc` - суммарное время $request_time для данного URL, в процентах относительно общего $request_time всех запросов

`time_avg` - среднее время $request_time для данного URL

`time_max` - маĸсимальное время $request_time для данного URL

`time_med` - медиана $request_time для данного URL

## Конфиг

`REPORT_SIZE` - количество строк в отчёте (по умолчанию 1000). Строки отортированы request_time DESC

`REPORT_DIR` - каталог, в котором хранятся отчёты (по умолчанию "./reports")

`LOG_DIR` - каталог, в котором хранятся обрабатываемые лог-файлы (по умолчанию "./log")

`REPORT_TEMPLATE` - шаблон для генерации отчёта (по умолчанию "report.html")

`MAX_ERROR_RATE` - максимально допустимая доля ошибок в обрабатываемом лог-файле

## Запуск скрипта

``` bash
python3 log_analyzer.py [--config config.ini]
```

`--config config.ini` - опциональный параметр для загрузки конфигурации из ini файла.

## Запуск тестов

``` bash
python3 -m unittest -v tests.py
```
