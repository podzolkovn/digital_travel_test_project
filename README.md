
# Тестовое задание 

## Описание

Разработать REST API сервис для управления заказами (Order) с учётом требований к
качеству кода, архитектуре и дополнительным возможностям. Реализация должна
включать авторизацию, кэширование, логирование и управление событиями.


## Установка

### Требования

- python3.12+


### Шаги установки

1. Склонируйте репозиторий:
    ```sh
    git clone https://github.com/podzolkovn/digital_travel_test_project
    ```
2. Перейдите в директорию проекта:
    ```sh
    cd digital_travel_test_project
    ```
3. Создать виртуальное окружение:
    ```sh
    python -m venv venv
    ```
4. Активировать виртуальное окружение:
    ```sh
    ./venv/Script/activate
    ```

    Если Windows:
    ```sh
    .\venv\Scripts\activate
    ```
    Если macOS / Linux:
    ```sh
    source venv/bin/activate
    ```
    
6. Установить зависимости:
    ```sh
    pip3 install -r reqs.txt
    ```
    
## Подготовка к запуску
1. Запустить докер компоус:
    ```sh
    docker compose up -d --build
    ```
2. Прогнать миграции:
    ```sh
    alembic upgrade head
    ```
## Тестирование
2. Прогнать миграции:
    ```sh
    pytest
    ```
## Запуск проекта

1. Запустите локальный сервер:
    ```sh
    uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
    ```
2. Откройте браузер и перейдите по адресу `http://localhost:8000/docs`
