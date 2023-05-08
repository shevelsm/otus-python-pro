# Scoring API

## Запуск

Приложение представляет собой Python HTTP сервер, который запускается, используя команду в терминале:

``` python api.py ```

## Конфигурация

Приложению можно передать путь к файлу с логами, а так же порт.

``` bash
Usage: api.py [options]

Options:
  -h, --help            show this help message and exit
  -p PORT, --port=PORT  
  -l LOG, --log=LOG
```

## Использование

После запуска, сервис ожидает POST запрос по адресу:

``` http
localhost:8080/method
```

Пример запроса:

``` bash
curl --request POST \
  --url http://localhost:8080/method \
  --header 'Content-Type: application/json' \
  --data '{
        "account": "horns&hoofs",
        "login": "h&f",
        "method": "online_score",
        "token": "55cc9ce545bcd144300fe9efc28e65d415b923ebb6be1e19d2750a2c03e80dd209a27954dca045e5bb12418e7d89b6d718a9e35af34e14e1d5bcd5a08f21fc95",
        "arguments": {
            "phone": "79995002040",
            "email": "agent007@mi5.org",
            "first_name": "James",
            "last_name": "Bond",
            "birthday": "11.11.2000",
            "gender": 1
        }
    }'
```

Пример ответа:

``` bash
{"response": {"score": 5.0}, "code": 200}
```

## Запуск тестов

Так же для приложения имеются тесты, которые можно запустить командой:

``` bash
python -m unittest
```
