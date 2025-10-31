#!/bin/bash

# Скрипт для инициализации шардированного кластера MongoDB после запуска docker-compose

set -e  # Прерывать выполнение при любой ошибке

echo "🚀 Начало инициализации MongoDB кластера..."
echo "⏳ Ожидание запуска контейнеров..."

# Функция для проверки готовности MongoDB
wait_for_mongo() {
    local container_name=$1
    local max_attempts=30
    local attempt=1
    
    echo "⌛ Ожидание готовности $container_name..."
    
    while [ $attempt -le $max_attempts ]; do
        if docker exec "$container_name" mongosh --eval "db.adminCommand('ping')" &>/dev/null; then
            echo "✅ $container_name готов"
            return 0
        fi
        
        echo "⏳ Попытка $attempt/$max_attempts: $container_name еще не готов..."
        sleep 2
        ((attempt++))
    done
    
    echo "❌ Таймаут ожидания $container_name"
    return 1
}

# Инициализация конфигурационного сервера как набора реплик
init_config_servers() {
    echo "📋 Инициализация конфигурационных серверов..."
    
    # Ждем готовности основного конфиг-сервера
    wait_for_mongo "mongocfg1"
    
    docker exec -it mongocfg1 bash -c '
        echo "rs.initiate({
            _id: \"mongors1conf\", 
            configsvr: true, 
            members: [
                {_id: 0, host: \"mongocfg1\"},
                {_id: 1, host: \"mongocfg2\"}, 
                {_id: 2, host: \"mongocfg3\"}
            ]
        })" | mongosh
    '
    
    echo "✅ Конфигурационные серверы инициализированы"
}

# Инициализация шарда 1
init_shard1() {
    echo "🔢 Инициализация шарда 1 (mongors1)..."
    
    wait_for_mongo "mongors1n1"
    
    docker exec -it mongors1n1 bash -c '
        echo "rs.initiate({
            _id: \"mongors1\",
            members: [
                {_id: 0, host: \"mongors1n1\"},
                {_id: 1, host: \"mongors1n2\"},
                {_id: 2, host: \"mongors1n3\"}
            ]
        })" | mongosh
    '
    
    echo "✅ Шард 1 инициализирован"
}

# Инициализация шарда 2  
init_shard2() {
    echo "🔢 Инициализация шарда 2 (mongors2)..."
    
    wait_for_mongo "mongors2n1"
    
    docker exec -it mongors2n1 bash -c '
        echo "rs.initiate({
            _id: \"mongors2\", 
            members: [
                {_id: 0, host: \"mongors2n1\"},
                {_id: 1, host: \"mongors2n2\"},
                {_id: 2, host: \"mongors2n3\"}
            ]
        })" | mongosh
    '
    
    echo "✅ Шард 2 инициализирован"
}

# Добавление шардов в кластер через mongos
add_shards_to_cluster() {
    echo "🔄 Добавление шардов в кластер через mongos..."
    
    # Ждем готовности mongos
    wait_for_mongo "mongos1"
    sleep 5  # Дополнительное время для стабилизации
    
    echo "➕ Добавление шарда 1..."
    docker exec -it mongos1 bash -c 'echo "sh.addShard(\"mongors1/mongors1n1\")" | mongosh'
    
    echo "➕ Добавление шарда 2..."  
    docker exec -it mongos1 bash -c 'echo "sh.addShard(\"mongors2/mongors2n1\")" | mongosh'
    
    echo "✅ Шарды добавлены в кластер"
}

# Проверка статуса кластера
check_cluster_status() {
    echo "📊 Проверка статуса кластера..."
    
    echo "🔍 Статус шардирования:"
    docker exec -it mongos1 bash -c 'echo "sh.status()" | mongosh'
    
    echo "🔍 Статус конфигурационных серверов:"
    docker exec -it mongocfg1 bash -c 'echo "rs.status()" | mongosh'
    
    echo "🔍 Статус шарда 1:"
    docker exec -it mongors1n1 bash -c 'echo "rs.status()" | mongosh'
    
    echo "🔍 Статус шарда 2:"
    docker exec -it mongors2n1 bash -c 'echo "rs.status()" | mongosh'
}

# Основная функция
main() {
    echo "🎯 Начало процесса инициализации MongoDB кластера"
    echo "================================================"
    
    # Последовательная инициализация
    init_config_servers
    sleep 5
    
    init_shard1  
    sleep 5
    
    init_shard2
    sleep 5
    
    add_shards_to_cluster
    sleep 3
    
    check_cluster_status
    
    echo ""
    echo "🎉 Инициализация кластера завершена!"
    echo "📍 Точки подключения:"
    echo "   - Mongos 1: localhost:27019"
    echo "   - Mongos 2: localhost:27020"
    echo ""
    echo "💡 Для подключения используйте: mongosh localhost:27019"
}

# Запуск основной функции
main "$@"