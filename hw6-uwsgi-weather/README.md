# Homework 06: IP2w

## Requires

- CentOS 7
- Python3.x
- python-requests library
- nginx
- uwsgi
- systemd


## ip2w rpm package

Для сборки rpm пакета необходимо в текущей папке запустить скрипт по сборке:

```bash
bash buildrpm.sh ip2w.spec
```

Для установки собранного пакета необхожимо выполнить команду:

```bash
sudo rpm -i ip2w-0.0.1-1.noarch.rpm
```

Чтобы запустить systemd сервис нужно воспользовать командой:

```bash
systemctl start ip2w
systemctl start nginx
```

## Request Example

```bash
$ curl http://localhost/ip2w/178.219.186.12
# {"city": "Mytishchi", "temp": "+17", "conditions": "ясно"}
```

## Tests

Для запуска функицональных тестов в папке ip2w выполнить команду:

``` bash
>>> python tests.py
```
