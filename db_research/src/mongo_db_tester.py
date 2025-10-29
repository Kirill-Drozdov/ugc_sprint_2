import time
import random
import uuid
from datetime import datetime
from typing import Any, List, Dict
from faker import Faker
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.errors import BulkWriteError

# Статистика производительности.
performance_stats = {}


def measure_time(operation_name: str):
    """Декоратор для измерения времени выполнения операций"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            end_time = time.time()
            execution_time = end_time - start_time

            if operation_name not in performance_stats:
                performance_stats[operation_name] = []
            performance_stats[operation_name].append(execution_time)

            print(f"⏱️  {operation_name}: {execution_time:.4f} секунд")
            return result
        return wrapper
    return decorator


class MongoDBTester:
    def __init__(
        self,
        host: str = 'localhost',
        port: int = 27019,
        db_name: str = 'ugc',
    ):
        self.client = MongoClient(host, port)
        self.db = self.client[db_name]
        self.fake = Faker()

        # Коллекции
        self.users = self.db['users']
        self.movies = self.db['movies']
        self.movie_ratings = self.db['movie_ratings']
        self.reviews = self.db['reviews']
        self.review_likes = self.db['review_likes']
        self.bookmarks = self.db['bookmarks']

    def insert_document(self, *, collection: Collection, data: dict) -> Any:
        res = collection.insert_one(data)
        return res.inserted_id

    def insert_many_documents(
        self,
        *,
        collection: Collection,
        data: List[dict],
    ) -> List[Any]:
        """Безопасная вставка множества документов с обработкой ошибок
            дубликатов.
        """
        try:
            res = collection.insert_many(data, ordered=False)
            return res.inserted_ids
        except BulkWriteError as e:
            # Игнорируем ошибки дубликатов, продолжаем с успешными вставками
            inserted_ids = [
                op['_id']
                for op in e.details['writeErrors'] if 'insertedIds' in op
            ]
            print(
                f"⚠️  Вставлено {len(inserted_ids)} документов, "
                f"пропущено {len(e.details['writeErrors'])} дубликатов"
            )
            return inserted_ids

    def insert_many_safe(
        self,
        *,
        collection: Collection,
        data: List[dict],
        batch_size: int = 1000,
    ) -> int:
        """Безопасная вставка больших объемов данных с пакетной обработкой"""
        total_inserted = 0
        for i in range(0, len(data), batch_size):
            batch = data[i:i + batch_size]
            try:
                result = collection.insert_many(batch, ordered=False)
                total_inserted += len(result.inserted_ids)
                print(
                    f"📦 Вставлено {len(result.inserted_ids)} документов "
                    f"(батч {i // batch_size + 1})"
                )
            except BulkWriteError as e:
                # Подсчитываем успешные вставки
                inserted_count = e.details['nInserted']
                total_inserted += inserted_count
                print(
                    f"📦 Вставлено {inserted_count} документов "
                    f"(батч {i // batch_size + 1}), пропущено "
                    f"{len(e.details['writeErrors'])} дубликатов"
                )
            except Exception as e:
                print(f"❌ Ошибка при вставке батча {i // batch_size + 1}: {e}")

        return total_inserted

    def find(
        self,
        *,
        collection: Collection,
        condition: dict,
        multiple: bool = False,
    ):
        if multiple:
            results = collection.find(condition)
            return [item for item in results]
        return collection.find_one(condition)

    def update_document(
        self,
        *,
        collection: Collection,
        condition: dict,
        new_values: dict,
    ):
        collection.update_one(condition, {'$set': new_values})

    def delete_document(self, *, collection: Collection, condition: dict):
        collection.delete_one(condition)

    @measure_time("Генерация тестовых пользователей")
    def generate_test_users(self, count: int = 10000) -> List[Dict]:
        """Генерация тестовых пользователей с гарантированно
            уникальными email.
        """
        users = []
        used_emails = set()

        for i in range(count):
            # Генерация гарантированно уникального email
            base_email = self.fake.email()
            unique_email = f"user{i + 1}_{base_email}"

            # Дополнительная проверка на уникальность
            while unique_email in used_emails:
                unique_email = f"user{i + 1}_{uuid.uuid4().hex[:8]}_{self.fake.email()}"  # noqa

            used_emails.add(unique_email)

            user = {
                "user_id": f"user_{i + 1}",
                "username": f"user_{i + 1}_{self.fake.user_name()}",
                "email": unique_email,
                "first_name": self.fake.first_name(),
                "last_name": self.fake.last_name(),
                "created_at": self.fake.date_time_between(start_date="-2y", end_date="now"),  # noqa
                "last_login": self.fake.date_time_between(start_date="-30d", end_date="now"),  # noqa
                "profile": {
                    "bio": self.fake.text(max_nb_chars=200),
                    "avatar_url": f"https://picsum.photos/200/200?random={i}",
                    "location": self.fake.city()
                }
            }
            users.append(user)

        total_inserted = self.insert_many_safe(
            collection=self.users, data=users, batch_size=1000)
        print(f"✅ Создано {total_inserted} тестовых пользователей")
        # Возвращаем только вставленные пользователи
        return users[:total_inserted]

    @measure_time("Генерация тестовых фильмов")
    def generate_test_movies(self, count: int = 20000) -> List[Dict]:
        """Генерация тестовых фильмов"""
        genres = ["Action", "Comedy", "Drama", "Thriller", "Sci-Fi",
                  "Horror", "Romance", "Documentary", "Animation", "Fantasy"]
        movies = []

        for i in range(count):
            movie = {
                "movie_id": f"movie_{i + 1}",
                "title": f"{self.fake.sentence(nb_words=3)} ({i + 1})",
                "description": self.fake.text(max_nb_chars=300),
                "release_year": random.randint(1980, 2023),
                "genres": random.sample(genres, random.randint(1, 3)),
                "duration_minutes": random.randint(80, 180),
                "director": self.fake.name(),
                "cast": [
                    self.fake.name() for _ in range(random.randint(3, 8))
                ],
                "country": self.fake.country(),
                "language": self.fake.language_name(),
                "budget": random.randint(1000000, 200000000),
                "created_at": self.fake.date_time_between(start_date="-1y", end_date="now"),  # noqa
                "poster_url": f"https://picsum.photos/300/450?random={i}",
                "imdb_rating": round(random.uniform(3.0, 9.5), 1)
            }
            movies.append(movie)

        total_inserted = self.insert_many_safe(
            collection=self.movies, data=movies, batch_size=1000)
        print(f"✅ Создано {total_inserted} тестовых фильмов")
        return movies[:total_inserted]

    @measure_time("Генерация оценок фильмов")
    def generate_movie_ratings(
        self,
        users: List[Dict],
        movies: List[Dict],
        ratings_per_user: int = 20,
    ):
        """Генерация оценок фильмов пользователями"""
        ratings = []

        if not users or not movies:
            print("⚠️  Нет пользователей или фильмов для генерации оценок")
            return

        for user in users:
            # Каждый пользователь оценивает случайные фильмы
            rated_movies = random.sample(
                movies, min(ratings_per_user, len(movies)))

            for movie in rated_movies:
                rating = {
                    "user_id": user["user_id"],
                    "movie_id": movie["movie_id"],
                    "rating": random.randint(0, 10),
                    "created_at": self.fake.date_time_between(
                        start_date=user["created_at"],
                        end_date="now"
                    ),
                    "updated_at": self.fake.date_time_between(
                        start_date=user["created_at"],
                        end_date="now"
                    )
                }
                ratings.append(rating)

        total_inserted = self.insert_many_safe(
            collection=self.movie_ratings, data=ratings, batch_size=2000)
        print(f"✅ Создано {total_inserted} оценок фильмов")

    @measure_time("Генерация рецензий")
    def generate_reviews(
        self,
        users: List[Dict],
        movies: List[Dict],
        reviews_per_user: int = 5,
    ):
        """Генерация рецензий на фильмы"""
        reviews = []

        if not users or not movies:
            print("⚠️  Нет пользователей или фильмов для генерации рецензий")
            return []

        for user in users:
            # Каждый пользователь пишет рецензии на случайные фильмы
            reviewed_movies = random.sample(
                movies, min(reviews_per_user, len(movies)))

            for movie in reviewed_movies:
                review = {
                    "review_id": f"review_{len(reviews) + 1}",
                    "user_id": user["user_id"],
                    "movie_id": movie["movie_id"],
                    "title": self.fake.sentence(nb_words=6),
                    # Уменьшил длину для производительности
                    "text": self.fake.text(max_nb_chars=500),
                    "rating": random.randint(1, 10),
                    "contains_spoilers": random.choice([True, False]),
                    "created_at": self.fake.date_time_between(
                        start_date=user["created_at"],
                        end_date="now"
                    ),
                    "updated_at": self.fake.date_time_between(
                        start_date=user["created_at"],
                        end_date="now"
                    ),
                    "likes_count": 0,
                    "dislikes_count": 0
                }
                reviews.append(review)

        total_inserted = self.insert_many_safe(
            collection=self.reviews, data=reviews, batch_size=2000)
        print(f"✅ Создано {total_inserted} рецензий")
        return reviews[:total_inserted]

    @measure_time("Генерация лайков рецензий")
    def generate_review_likes(
        self,
        users: List[Dict],
        reviews: List[Dict],
        likes_per_user: int = 10,
    ):
        """Генерация лайков/дизлайков рецензий"""
        review_likes = []

        if not users or not reviews:
            print("⚠️  Нет пользователей или рецензий для генерации лайков")
            return

        for user in users:
            # Пользователь лайкает случайные рецензии (кроме своих)
            user_reviews = [
                r for r in reviews if r["user_id"] != user["user_id"]]

            if not user_reviews:
                continue

            liked_reviews = random.sample(
                user_reviews,
                min(likes_per_user, len(user_reviews))
            )

            for review in liked_reviews:
                like_value = random.choice([0, 10])
                review_like = {
                    "user_id": user["user_id"],
                    "review_id": review["review_id"],
                    "like_value": like_value,
                    "created_at": self.fake.date_time_between(
                        start_date=review["created_at"],
                        end_date="now"
                    )
                }
                review_likes.append(review_like)

        # Вставляем лайки
        total_inserted = self.insert_many_safe(
            collection=self.review_likes, data=review_likes, batch_size=2000)
        print(f"✅ Создано {total_inserted} лайков/дизлайков рецензий")

        # Обновляем счетчики лайков в рецензиях
        self._update_review_likes_counters(review_likes)

    def _update_review_likes_counters(self, review_likes: List[Dict]):
        """Обновление счетчиков лайков в рецензиях"""
        review_stats = {}
        for like in review_likes:
            review_id = like["review_id"]
            if review_id not in review_stats:
                review_stats[review_id] = {"likes": 0, "dislikes": 0}

            if like["like_value"] == 10:
                review_stats[review_id]["likes"] += 1
            else:
                review_stats[review_id]["dislikes"] += 1

        # Пакетное обновление счетчиков
        for review_id, stats in review_stats.items():
            self.reviews.update_one(
                {"review_id": review_id},
                {"$set": {
                    "likes_count": stats["likes"],
                    "dislikes_count": stats["dislikes"]
                }}
            )

    @measure_time("Генерация закладок")
    def generate_bookmarks(
        self,
        users: List[Dict],
        movies: List[Dict],
        bookmarks_per_user: int = 8,
    ):
        """Генерация закладок пользователей"""
        bookmarks = []

        if not users or not movies:
            print("⚠️  Нет пользователей или фильмов для генерации закладок")
            return

        for user in users:
            # Пользователь добавляет случайные фильмы в закладки
            bookmarked_movies = random.sample(
                movies, min(bookmarks_per_user, len(movies)))

            for movie in bookmarked_movies:
                bookmark = {
                    "user_id": user["user_id"],
                    "movie_id": movie["movie_id"],
                    "created_at": self.fake.date_time_between(
                        start_date=user["created_at"],
                        end_date="now"
                    ),
                    "notes": random.choice(
                        [None, self.fake.sentence(nb_words=8)]
                    )
                }
                bookmarks.append(bookmark)

        total_inserted = self.insert_many_safe(
            collection=self.bookmarks, data=bookmarks, batch_size=2000)
        print(f"✅ Создано {total_inserted} закладок")

    @measure_time("ТЕСТ: Поиск пользователя по email")
    def test_find_user_by_email(self):
        """Тест поиска пользователя по email"""
        user = self.users.find_one()
        if user:
            result = self.find(
                collection=self.users,
                condition={"email": user["email"]}
            )
            return result is not None
        return False

    @measure_time("ТЕСТ: Поиск фильмов по жанру")
    def test_find_movies_by_genre(self):
        """Тест поиска фильмов по жанру"""
        results = self.find(
            collection=self.movies,
            condition={"genres": "Action"},
            multiple=True
        )
        return len(results)  # type: ignore

    @measure_time("ТЕСТ: Получение среднего рейтинга фильма")
    def test_get_movie_avg_rating(self):
        """Тест расчета среднего рейтинга фильма"""
        pipeline = [
            {"$group": {
                "_id": "$movie_id",
                "avg_rating": {"$avg": "$rating"},
                "rating_count": {"$sum": 1}
            }},
            {"$sort": {"avg_rating": -1}},
            {"$limit": 10}
        ]
        results = list(self.movie_ratings.aggregate(pipeline))
        return results

    @measure_time("ТЕСТ: Поиск рецензий с сортировкой по дате")
    def test_find_reviews_sorted(self):
        """Тест поиска рецензий с сортировкой"""
        movie = self.movies.find_one()
        if movie:
            results = list(self.reviews.find(
                {"movie_id": movie["movie_id"]}
            ).sort("created_at", -1).limit(20))
            return len(results)
        return 0

    @measure_time("ТЕСТ: Получение закладок пользователя")
    def test_get_user_bookmarks(self):
        """Тест получения закладок пользователя"""
        user = self.users.find_one()
        if user:
            results = self.find(
                collection=self.bookmarks,
                condition={"user_id": user["user_id"]},
                multiple=True
            )
            return len(results)  # type: ignore
        return 0

    @measure_time("ТЕСТ: Получение популярных рецензий")
    def test_get_popular_reviews(self):
        """Тест получения популярных рецензий (по лайкам)"""
        results = list(self.reviews.find(
            {"likes_count": {"$gt": 0}}
        ).sort("likes_count", -1).limit(10))
        return len(results)

    @measure_time("ТЕСТ: Обновление рейтинга фильма")
    def test_update_movie_rating(self):
        """Тест обновления рейтинга фильма"""
        rating = self.movie_ratings.find_one()
        if rating:
            self.update_document(
                collection=self.movie_ratings,
                condition={"_id": rating["_id"]},
                new_values={"rating": random.randint(
                    0, 10), "updated_at": datetime.now()}
            )
            return True
        return False

    @measure_time("ТЕСТ: Поиск по тексту рецензий")
    def test_text_search_reviews(self):
        """Тест полнотекстового поиска по рецензиям"""
        # Создаем текстовый индекс если его нет
        if "text_text" not in self.reviews.index_information():
            self.reviews.create_index([("text", "text")])

        # Ищем рецензии содержащие популярные слова
        results = list(self.reviews.find(
            {"$text": {"$search": "great amazing excellent"}}
        ).limit(10))
        return len(results)

    def run_performance_tests(self):
        """Запуск всех тестов производительности"""
        print("🚀 Запуск тестов производительности...")
        print("=" * 50)

        tests = [
            self.test_find_user_by_email,
            self.test_find_movies_by_genre,
            self.test_get_movie_avg_rating,
            self.test_find_reviews_sorted,
            self.test_get_user_bookmarks,
            self.test_get_popular_reviews,
            self.test_update_movie_rating,
            self.test_text_search_reviews
        ]

        for test in tests:
            try:
                result = test()
                print(f"✅ {test.__name__} - Успех")
                if isinstance(result, (int, bool)):
                    print(f"   Результат: {result}")
            except Exception as e:
                print(f"❌ {test.__name__} - Ошибка: {e}")

    def generate_all_test_data(self):
        """Генерация всех тестовых данных с контролируемыми объемами"""
        print("🎭 Начало генерации тестовых данных...")
        print("=" * 50)

        # Генерация базовых данных с реалистичными объемами
        print("👥 Генерация пользователей...")
        # 10K пользователей.
        users = self.generate_test_users(10000)

        print("🎬 Генерация фильмов...")
        # 20K фильмов.
        movies = self.generate_test_movies(20000)

        # Генерация связных данных с реалистичными соотношениями
        print("⭐ Генерация оценок...")
        # 20 оценок на пользователя
        self.generate_movie_ratings(users, movies, 20)

        print("📝 Генерация рецензий...")
        # 5 рецензий на пользователя.
        reviews = self.generate_reviews(users, movies, 5)

        print("👍 Генерация лайков рецензий...")
        # 10 лайков на пользователя
        self.generate_review_likes(users, reviews, 10)

        print("🔖 Генерация закладок...")
        # 8 закладок на пользователя.
        self.generate_bookmarks(users, movies, 8)

        print("✅ Все тестовые данные сгенерированы!")

    def print_statistics(self):
        """Вывод статистики по данным"""
        print("\n📊 Статистика базы данных:")
        print("=" * 30)
        print(f"👥 Пользователи: {self.users.count_documents({})}")
        print(f"🎬 Фильмы: {self.movies.count_documents({})}")
        print(f"⭐ Оценки: {self.movie_ratings.count_documents({})}")
        print(f"📝 Рецензии: {self.reviews.count_documents({})}")
        print(f"👍 Лайки рецензий: {self.review_likes.count_documents({})}")
        print(f"🔖 Закладки: {self.bookmarks.count_documents({})}")

    def print_performance_summary(self):
        """Вывод сводки по производительности"""
        print("\n📈 Сводка по производительности:")
        print("=" * 35)

        for operation, times in performance_stats.items():
            if times:  # Проверяем, что есть данные
                avg_time = sum(times) / len(times)
                max_time = max(times)
                min_time = min(times)
                print(f"\n{operation}:")
                print(f"  Среднее: {avg_time:.4f} сек")
                print(f"  Максимум: {max_time:.4f} сек")
                print(f"  Минимум: {min_time:.4f} сек")
                print(f"  Количество выполнений: {len(times)}")

    def cleanup_test_data(self):
        """Очистка тестовых данных"""
        print("🧹 Очистка тестовых данных...")
        try:
            # Удаляем данные в правильном порядке из-за foreign key constraints
            self.review_likes.delete_many({})
            self.bookmarks.delete_many({})
            self.reviews.delete_many({})
            self.movie_ratings.delete_many({})
            self.users.delete_many({})
            self.movies.delete_many({})
            print("✅ Все тестовые данные удалены!")
        except Exception as e:
            print(f"⚠️  Ошибка при очистке данных: {e}")

    def drop_indexes(self):
        """Удаление индексов для ускорения вставки больших объемов данных"""
        print("🗑️  Временное удаление индексов для ускорения вставки...")
        try:
            self.users.drop_indexes()
            self.movies.drop_indexes()
            self.movie_ratings.drop_indexes()
            self.reviews.drop_indexes()
            self.review_likes.drop_indexes()
            self.bookmarks.drop_indexes()
            print("✅ Индексы временно удалены")
        except Exception as e:
            print(f"⚠️  Ошибка при удалении индексов: {e}")

    def recreate_indexes(self):
        """Восстановление индексов после вставки данных"""
        print("🔧 Восстановление индексов...")
        try:
            # Пользователи
            self.users.create_index([("user_id", 1)], unique=True)
            self.users.create_index([("email", 1)], unique=True)
            self.users.create_index([("username", 1)])

            # Фильмы
            self.movies.create_index([("movie_id", 1)], unique=True)
            self.movies.create_index([("title", 1)])
            self.movies.create_index([("release_year", -1)])
            self.movies.create_index([("genres", 1)])

            # Оценки
            self.movie_ratings.create_index(
                [("user_id", 1), ("movie_id", 1)], unique=True)
            self.movie_ratings.create_index([("movie_id", 1), ("rating", 1)])

            # Рецензии
            self.reviews.create_index([("review_id", 1)], unique=True)
            self.reviews.create_index([("user_id", 1), ("movie_id", 1)])
            self.reviews.create_index([("movie_id", 1), ("created_at", -1)])
            self.reviews.create_index([("text", "text")])

            # Лайки рецензий
            self.review_likes.create_index(
                [("user_id", 1), ("review_id", 1)], unique=True)

            # Закладки
            self.bookmarks.create_index(
                [("user_id", 1), ("movie_id", 1)], unique=True)

            print("✅ Индексы восстановлены")
        except Exception as e:
            print(f"⚠️  Ошибка при восстановлении индексов: {e}")


def main():
    # Создание тестера
    tester = MongoDBTester()

    try:
        # Очистка старых данных
        tester.cleanup_test_data()

        # Временное удаление индексов для ускорения массовой вставки
        tester.drop_indexes()

        # Генерация тестовых данных
        tester.generate_all_test_data()

        # Восстановление индексов
        tester.recreate_indexes()

        # Вывод статистики
        tester.print_statistics()

        # Запуск тестов производительности
        tester.run_performance_tests()

        # Вывод сводки по производительности
        tester.print_performance_summary()

    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Закрытие соединения
        tester.client.close()
        print("\n🔚 Соединение с MongoDB закрыто")


if __name__ == '__main__':
    main()
