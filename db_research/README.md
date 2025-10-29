# Инструкция по запуску тестов производительности

## Подготовка

Необходимо убедиться в наличии следующих программ на вашем ПК:
  1. Docker.
  2. Python >= 3.13.

## Запуск кластера MongoDB

1. Из корня проекта выполнить команду:
    ```
    docker compose up -d
    ```
2. Последовательно выполнить скрипты инициализации кластера и базы данных:
    ```
    chmod +x init_mongo_cluster.sh
    chmod +x init_database.sh
    ```
    ```
    ./init_mongo_cluster.sh
    ./init_database.sh
    ```
3. Создать и активировать виртуальное окружение с python 3.13:
    ```
    python3.13 -m venv venv
    ```
    ```
    . venv/bin/activate
    ```
    ```
    pip install --upgrade pip
    ```
    ```
    pip install -r requirements.txt
    ```
4. Запустить тесты производительности и дождаться результата их выполнения:
    ```
    python src/mongo_db_tester.py
    ```

В результате выполнения тестов в консоли появится подробный отчет.