#!/bin/bash

# init_database.sh
# Скрипт для инициализации структуры данных в MongoDB кластере

set -e  # Прерывать выполнение при любой ошибке

echo "🗃️  Начало инициализации структуры данных MongoDB..."
echo "⏳ Подключение к кластеру..."

# Функция для выполнения команд MongoDB через docker exec
execute_mongo_command() {
    local command=$1
    local description=$2
    
    echo "🔧 $description..."
    docker exec -i mongos1 mongosh --eval "$command"
}

# Основная функция инициализации
init_database_structure() {
    echo "📐 Создание структуры базы данных..."
    
    # Создание базы данных (будет создана автоматически при первом использовании)
    # Мы явно используем базу данных ugc (User Generated Content)
    
    # 1. Создание коллекций и индексов для пользователей
    execute_mongo_command '
        db = db.getSiblingDB("ugc");
        
        // Коллекция пользователей
        if (!db.getCollectionNames().includes("users")) {
            db.createCollection("users");
            print("✅ Коллекция users создана");
        } else {
            print("ℹ️  Коллекция users уже существует");
        }
        
        // Индексы для пользователей
        db.users.createIndex({ "user_id": 1 }, { unique: true });
        db.users.createIndex({ "email": 1 }, { unique: true, sparse: true });
        db.users.createIndex({ "username": 1 });
        print("✅ Индексы для users созданы");
    ' "Создание коллекции пользователей"
    
    # 2. Создание коллекций и индексов для кинопроизведений
    execute_mongo_command '
        db = db.getSiblingDB("ugc");
        
        // Коллекция кинопроизведений
        if (!db.getCollectionNames().includes("movies")) {
            db.createCollection("movies");
            print("✅ Коллекция movies создана");
        } else {
            print("ℹ️  Коллекция movies уже существует");
        }
        
        // Индексы для кинопроизведений
        db.movies.createIndex({ "movie_id": 1 }, { unique: true });
        db.movies.createIndex({ "title": 1 });
        db.movies.createIndex({ "release_year": -1 });
        db.movies.createIndex({ "genres": 1 });
        db.movies.createIndex({ "rating_avg": -1 });
        print("✅ Индексы для movies созданы");
    ' "Создание коллекции кинопроизведений"
    
    # 3. Создание коллекций и индексов для оценок фильмов
    execute_mongo_command '
        db = db.getSiblingDB("ugc");
        
        // Коллекция оценок фильмов
        if (!db.getCollectionNames().includes("movie_ratings")) {
            db.createCollection("movie_ratings");
            print("✅ Коллекция movie_ratings создана");
        } else {
            print("ℹ️  Коллекция movie_ratings уже существует");
        }
        
        // Индексы для оценок фильмов
        db.movie_ratings.createIndex({ "user_id": 1, "movie_id": 1 }, { unique: true });
        db.movie_ratings.createIndex({ "movie_id": 1, "rating": 1 });
        db.movie_ratings.createIndex({ "user_id": 1 });
        db.movie_ratings.createIndex({ "created_at": -1 });
        print("✅ Индексы для movie_ratings созданы");
    ' "Создание коллекции оценок фильмов"
    
    # 4. Создание коллекций и индексов для рецензий
    execute_mongo_command '
        db = db.getSiblingDB("ugc");
        
        // Коллекция рецензий
        if (!db.getCollectionNames().includes("reviews")) {
            db.createCollection("reviews");
            print("✅ Коллекция reviews создана");
        } else {
            print("ℹ️  Коллекция reviews уже существует");
        }
        
        // Индексы для рецензий
        db.reviews.createIndex({ "review_id": 1 }, { unique: true });
        db.reviews.createIndex({ "user_id": 1, "movie_id": 1 });
        db.reviews.createIndex({ "movie_id": 1, "created_at": -1 });
        db.reviews.createIndex({ "user_id": 1 });
        db.reviews.createIndex({ "likes_count": -1 });
        db.reviews.createIndex({ "rating": 1 });
        db.reviews.createIndex({ "text": "text" }); // Текстовый поиск
        print("✅ Индексы для reviews созданы");
    ' "Создание коллекции рецензий"
    
    # 5. Создание коллекций и индексов для лайков рецензий
    execute_mongo_command '
        db = db.getSiblingDB("ugc");
        
        // Коллекция лайков рецензий
        if (!db.getCollectionNames().includes("review_likes")) {
            db.createCollection("review_likes");
            print("✅ Коллекция review_likes создана");
        } else {
            print("ℹ️  Коллекция review_likes уже существует");
        }
        
        // Индексы для лайков рецензий
        db.review_likes.createIndex({ "user_id": 1, "review_id": 1 }, { unique: true });
        db.review_likes.createIndex({ "review_id": 1 });
        db.review_likes.createIndex({ "user_id": 1 });
        db.review_likes.createIndex({ "created_at": -1 });
        print("✅ Индексы для review_likes созданы");
    ' "Создание коллекции лайков рецензий"
    
    # 6. Создание коллекций и индексов для закладок
    execute_mongo_command '
        db = db.getSiblingDB("ugc");
        
        // Коллекция закладок
        if (!db.getCollectionNames().includes("bookmarks")) {
            db.createCollection("bookmarks");
            print("✅ Коллекция bookmarks создана");
        } else {
            print("ℹ️  Коллекция bookmarks уже существует");
        }
        
        // Индексы для закладок
        db.bookmarks.createIndex({ "user_id": 1, "movie_id": 1 }, { unique: true });
        db.bookmarks.createIndex({ "user_id": 1 });
        db.bookmarks.createIndex({ "movie_id": 1 });
        db.bookmarks.createIndex({ "created_at": -1 });
        print("✅ Индексы для bookmarks созданы");
    ' "Создание коллекции закладок"
}

# Функция для создания агрегационных представлений
create_aggregation_views() {
    echo "📊 Создание агрегационных представлений..."
    
    # Представление для рейтингов фильмов
    execute_mongo_command '
        db = db.getSiblingDB("ugc");
        
        // Удаляем существующие представления
        try { db.movie_stats.drop() } catch(e) {}
        try { db.review_stats.drop() } catch(e) {}
        
        // Создаем представление для статистики по фильмам
        db.createView("movie_stats", "movie_ratings", [
            {
                $group: {
                    _id: "$movie_id",
                    average_rating: { $avg: "$rating" },
                    ratings_count: { $sum: 1 },
                    likes_count: {
                        $sum: { $cond: [{ $eq: ["$rating", 10] }, 1, 0] }
                    },
                    dislikes_count: {
                        $sum: { $cond: [{ $eq: ["$rating", 0] }, 1, 0] }
                    }
                }
            },
            {
                $project: {
                    movie_id: "$_id",
                    average_rating: { $round: ["$average_rating", 2] },
                    ratings_count: 1,
                    likes_count: 1,
                    dislikes_count: 1,
                    _id: 0
                }
            }
        ]);
        print("✅ Представление movie_stats создано");
    ' "Создание представления статистики фильмов"
    
    # Представление для статистики рецензий
    execute_mongo_command '
        db = db.getSiblingDB("ugc");
        
        db.createView("review_stats", "review_likes", [
            {
                $lookup: {
                    from: "reviews",
                    localField: "review_id",
                    foreignField: "review_id",
                    as: "review_info"
                }
            },
            {
                $unwind: "$review_info"
            },
            {
                $group: {
                    _id: "$review_id",
                    likes_count: {
                        $sum: { $cond: [{ $eq: ["$like_value", 10] }, 1, 0] }
                    },
                    dislikes_count: {
                        $sum: { $cond: [{ $eq: ["$like_value", 0] }, 1, 0] }
                    },
                    movie_id: { $first: "$review_info.movie_id" },
                    user_id: { $first: "$review_info.user_id" },
                    review_text: { $first: "$review_info.text" }
                }
            },
            {
                $project: {
                    review_id: "$_id",
                    movie_id: 1,
                    user_id: 1,
                    likes_count: 1,
                    dislikes_count: 1,
                    review_preview: { $substr: ["$review_text", 0, 100] },
                    _id: 0
                }
            }
        ]);
        print("✅ Представление review_stats создано");
    ' "Создание представления статистики рецензий"
}

# Функция для создания валидации схем
create_schema_validations() {
    echo "🛡️  Настройка валидации схем..."
    
    # Валидация для пользователей
    execute_mongo_command '
        db = db.getSiblingDB("ugc");
        
        db.runCommand({
            collMod: "users",
            validator: {
                $jsonSchema: {
                    bsonType: "object",
                    required: ["user_id", "username", "created_at"],
                    properties: {
                        user_id: {
                            bsonType: "string",
                            description: "Уникальный идентификатор пользователя - обязателен"
                        },
                        username: {
                            bsonType: "string",
                            description: "Имя пользователя - обязателен"
                        },
                        email: {
                            bsonType: "string",
                            pattern: "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$",
                            description: "Email должен быть валидным"
                        },
                        created_at: {
                            bsonType: "date",
                            description: "Дата создания - обязательна"
                        }
                    }
                }
            },
            validationLevel: "moderate"
        });
        print("✅ Валидация для users настроена");
    ' "Настройка валидации пользователей"
    
    # Валидация для оценок фильмов
    execute_mongo_command '
        db = db.getSiblingDB("ugc");
        
        db.runCommand({
            collMod: "movie_ratings",
            validator: {
                $jsonSchema: {
                    bsonType: "object",
                    required: ["user_id", "movie_id", "rating", "created_at"],
                    properties: {
                        user_id: {
                            bsonType: "string",
                            description: "ID пользователя - обязателен"
                        },
                        movie_id: {
                            bsonType: "string",
                            description: "ID фильма - обязателен"
                        },
                        rating: {
                            bsonType: "int",
                            minimum: 0,
                            maximum: 10,
                            description: "Рейтинг должен быть от 0 до 10"
                        },
                        created_at: {
                            bsonType: "date",
                            description: "Дата оценки - обязательна"
                        }
                    }
                }
            },
            validationLevel: "strict"
        });
        print("✅ Валидация для movie_ratings настроена");
    ' "Настройка валидации оценок"
}

# Функция для создания тестовых данных (опционально)
create_test_data() {
    echo "🎭 Создание тестовых данных..."
    
    execute_mongo_command '
        db = db.getSiblingDB("ugc");
        
        // Тестовые пользователи
        if (db.users.countDocuments() === 0) {
            db.users.insertMany([
                {
                    user_id: "user_1",
                    username: "cinema_lover",
                    email: "user1@example.com",
                    created_at: new Date()
                },
                {
                    user_id: "user_2", 
                    username: "film_critic",
                    email: "user2@example.com",
                    created_at: new Date()
                },
                {
                    user_id: "user_3",
                    username: "movie_fan",
                    email: "user3@example.com", 
                    created_at: new Date()
                }
            ]);
            print("✅ Тестовые пользователи созданы");
        } else {
            print("ℹ️  Пользователи уже существуют, пропускаем создание тестовых");
        }
        
        // Тестовые фильмы
        if (db.movies.countDocuments() === 0) {
            db.movies.insertMany([
                {
                    movie_id: "movie_1",
                    title: "Inception",
                    description: "A thief who steals corporate secrets through dream-sharing technology.",
                    release_year: 2010,
                    genres: ["Action", "Sci-Fi", "Thriller"],
                    created_at: new Date()
                },
                {
                    movie_id: "movie_2",
                    title: "The Shawshank Redemption", 
                    description: "Two imprisoned men bond over a number of years.",
                    release_year: 1994,
                    genres: ["Drama"],
                    created_at: new Date()
                },
                {
                    movie_id: "movie_3",
                    title: "The Dark Knight",
                    description: "Batman faces the Joker, a criminal mastermind.",
                    release_year: 2008,
                    genres: ["Action", "Crime", "Drama"],
                    created_at: new Date()
                }
            ]);
            print("✅ Тестовые фильмы созданы");
        } else {
            print("ℹ️  Фильмы уже существуют, пропускаем создание тестовых");
        }
    ' "Создание тестовых данных"
}

# Функция проверки созданной структуры
verify_structure() {
    echo "🔍 Проверка созданной структуры..."
    
    execute_mongo_command '
        db = db.getSiblingDB("ugc");
        
        print("📋 Список коллекций:");
        db.getCollectionNames().forEach(col => print("   - " + col));
        
        print("\n📊 Статистика коллекций:");
        const collections = ["users", "movies", "movie_ratings", "reviews", "review_likes", "bookmarks"];
        collections.forEach(col => {
            if (db[col]) {
                print("   " + col + ": " + db[col].countDocuments() + " документов");
            }
        });
        
        print("\n📈 Индексы для основных коллекций:");
        collections.forEach(col => {
            if (db[col]) {
                print("\n   " + col + ":");
                db[col].getIndexes().forEach(idx => {
                    print("     - " + idx.name + ": " + JSON.stringify(idx.key));
                });
            }
        });
    ' "Проверка структуры базы данных"
}

# Проверка доступности MongoDB
check_mongo_connection() {
    echo "⏳ Проверка подключения к MongoDB..."
    if ! docker exec -i mongos1 mongosh --eval "db.adminCommand('ping')" &>/dev/null; then
        echo "❌ Ошибка: MongoDB не доступен в контейнере mongos1"
        echo "💡 Убедитесь, что контейнеры запущены: docker-compose ps"
        exit 1
    fi
    echo "✅ Подключение к MongoDB успешно"
}

# Основная функция
main() {
    echo "🎯 Начало инициализации структуры данных MongoDB"
    echo "================================================"
    
    # Проверяем доступность MongoDB
    check_mongo_connection
    
    # Последовательная инициализация
    init_database_structure
    sleep 2
    
    create_aggregation_views
    sleep 2
    
    create_schema_validations
    sleep 2
    
    # Опционально: раскомментируйте следующую строку если нужны тестовые данные
    # create_test_data
    # sleep 2
    
    verify_structure
    
    echo ""
    echo "🎉 Инициализация структуры данных завершена!"
    echo ""
    echo "📖 Краткая информация о созданной структуре:"
    echo "   - База данных: ugc"
    echo "   - Основные коллекции: users, movies, movie_ratings, reviews, review_likes, bookmarks"
    echo "   - Агрегационные представления: movie_stats, review_stats"
    echo "   - Валидация схем для критически важных данных"
    echo ""
    echo "💡 Примеры использования:"
    echo "   Подключение: mongosh localhost:27019/ugc"
    echo "   Просмотр статистики фильма: db.movie_stats.find({movie_id: 'movie_1'})"
    echo "   Поиск рецензий: db.reviews.find({movie_id: 'movie_1'}).sort({created_at: -1})"
}

# Запуск основной функции
main "$@"