#!/bin/bash

set -e  # Прерывать выполнение при любой ошибке

echo "🚀 Начало инициализации MongoDB кластера..."
echo "⏳ Ожидание запуска контейнеров..."

# Функция для проверки готовности MongoDB
wait_for_mongo() {
    local host=$1
    local port=$2
    local max_attempts=30
    local attempt=1
    
    echo "⌛ Ожидание готовности $host:$port..."
    
    while [ $attempt -le $max_attempts ]; do
        if mongosh --host $host --port $port --eval "db.adminCommand('ping')" &>/dev/null; then
            echo "✅ $host:$port готов"
            return 0
        fi
        
        echo "⏳ Попытка $attempt/$max_attempts: $host:$port еще не готов..."
        sleep 2
        ((attempt++))
    done
    
    echo "❌ Таймаут ожидания $host:$port"
    return 1
}

# Инициализация конфигурационного сервера как набора реплик
init_config_servers() {
    echo "📋 Инициализация конфигурационных серверов..."
    
    # Ждем готовности основного конфиг-сервера
    wait_for_mongo "mongocfg1" 27017
    
    mongosh --host mongocfg1 --port 27017 --eval "
        try {
            rs.initiate({
                _id: \"mongors1conf\", 
                configsvr: true, 
                members: [
                    {_id: 0, host: \"mongocfg1:27017\"},
                    {_id: 1, host: \"mongocfg2:27017\"}, 
                    {_id: 2, host: \"mongocfg3:27017\"}
                ]
            })
        } catch (e) {
            if (e.codeName === 'AlreadyInitialized') {
                print('Config servers already initialized');
            } else {
                throw e;
            }
        }
    "
    
    echo "✅ Конфигурационные серверы инициализированы"
}

# Инициализация шарда 1
init_shard1() {
    echo "🔢 Инициализация шарда 1 (mongors1)..."
    
    wait_for_mongo "mongors1n1" 27017
    
    mongosh --host mongors1n1 --port 27017 --eval "
        try {
            rs.initiate({
                _id: \"mongors1\",
                members: [
                    {_id: 0, host: \"mongors1n1:27017\"},
                    {_id: 1, host: \"mongors1n2:27017\"},
                    {_id: 2, host: \"mongors1n3:27017\"}
                ]
            })
        } catch (e) {
            if (e.codeName === 'AlreadyInitialized') {
                print('Shard 1 already initialized');
            } else {
                throw e;
            }
        }
    "
    
    echo "✅ Шард 1 инициализирован"
}

# Инициализация шарда 2  
init_shard2() {
    echo "🔢 Инициализация шарда 2 (mongors2)..."
    
    wait_for_mongo "mongors2n1" 27017
    
    mongosh --host mongors2n1 --port 27017 --eval "
        try {
            rs.initiate({
                _id: \"mongors2\", 
                members: [
                    {_id: 0, host: \"mongors2n1:27017\"},
                    {_id: 1, host: \"mongors2n2:27017\"},
                    {_id: 2, host: \"mongors2n3:27017\"}
                ]
            })
        } catch (e) {
            if (e.codeName === 'AlreadyInitialized') {
                print('Shard 2 already initialized');
            } else {
                throw e;
            }
        }
    "
    
    echo "✅ Шард 2 инициализирован"
}

# Добавление шардов в кластер через mongos
add_shards_to_cluster() {
    echo "🔄 Добавление шардов в кластер через mongos..."
    
    # Ждем готовности mongos
    wait_for_mongo "mongos1" 27017
    sleep 5  # Дополнительное время для стабилизации
    
    echo "➕ Добавление шарда 1..."
    mongosh --host mongos1 --port 27017 --eval "
        try {
            sh.addShard(\"mongors1/mongors1n1:27017,mongors1n2:27017,mongors1n3:27017\")
        } catch (e) {
            if (e.codeName === 'ShardAlreadyExists') {
                print('Shard 1 already added');
            } else {
                throw e;
            }
        }
    "
    
    echo "➕ Добавление шарда 2..."  
    mongosh --host mongos1 --port 27017 --eval "
        try {
            sh.addShard(\"mongors2/mongors2n1:27017,mongors2n2:27017,mongors2n3:27017\")
        } catch (e) {
            if (e.codeName === 'ShardAlreadyExists') {
                print('Shard 2 already added');
            } else {
                throw e;
            }
        }
    "
    
    echo "✅ Шарды добавлены в кластер"
}

# Включение шардирования для базы данных ugc
enable_sharding_for_ugc() {
    echo "🗄️ Включение шардирования для базы данных ugc..."
    
    mongosh --host mongos1 --port 27017 --eval "
        // Включение шардирования для базы данных ugc
        sh.enableSharding('ugc')
        
        // Создание индексов для коллекций
        db = db.getSiblingDB('ugc')
        
        // Для закладок - шардирование по user_id
        db.bookmarks.createIndex({ user_id: 1 })
        sh.shardCollection('ugc.bookmarks', { user_id: 1 })
        
        // Для оценок - шардирование по filmwork_id  
        db.ratings.createIndex({ filmwork_id: 1 })
        sh.shardCollection('ugc.ratings', { filmwork_id: 1 })
        
        // Для рецензий - шардирование по filmwork_id
        db.reviews.createIndex({ filmwork_id: 1 })
        sh.shardCollection('ugc.reviews', { filmwork_id: 1 })
        
        // Для лайков рецензий - шардирование по review_id
        db.review_likes.createIndex({ review_id: 1 })
        sh.shardCollection('ugc.review_likes', { review_id: 1 })
    "
    
    echo "✅ Шардирование для ugc настроено"
}

# Проверка статуса кластера
check_cluster_status() {
    echo "📊 Проверка статуса кластера..."
    
    echo "🔍 Статус шардирования:"
    mongosh --host mongos1 --port 27017 --eval "sh.status()"
    
    echo "🎉 Кластер инициализирован и готов к работе!"
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
    
    enable_sharding_for_ugc
    sleep 2
    
    check_cluster_status
    
    echo ""
    echo "📍 Точки подключения:"
    echo "   - Mongos 1: localhost:27019"
    echo "   - Mongos 2: localhost:27020"
}

# Запуск основной функции
main "$@"