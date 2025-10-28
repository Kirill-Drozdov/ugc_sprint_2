import time
import random
from datetime import datetime
from typing import Any, List, Dict
from faker import Faker
from pymongo import MongoClient
from pymongo.collection import Collection

# Статистика производительности
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
    def __init__(self, host: str = 'localhost', port: int = 27019, db_name: str = 'ugc'):
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

    def insert_many_documents(self, *, collection: Collection, data: List[dict]) -> List[Any]:
        res = collection.insert_many(data)
        return res.inserted_ids

    def find(self, *, collection: Collection, condition: dict, multiple: bool = False):
        if multiple:
            results = collection.find(condition)
            return [item for item in results]
        return collection.find_one(condition)

    def update_document(self, *, collection: Collection, condition: dict, new_values: dict):
        collection.update_one(condition, {'$set': new_values})

    def delete_document(self, *, collection: Collection, condition: dict):
        collection.delete_one(condition)

    @measure_time("Генерация тестовых пользователей")
    def generate_test_users(self, count: int = 100) -> List[Dict]:
        """Генерация тестовых пользователей"""
        users = []
        for i in range(count):
            user = {
                "user_id": f"user_{i + 1}",
                "username": self.fake.user_name(),
                "email": self.fake.email(),
                "first_name": self.fake.first_name(),
                "last_name": self.fake.last_name(),
                "created_at": self.fake.date_time_between(start_date="-2y", end_date="now"),
                "last_login": self.fake.date_time_between(start_date="-30d", end_date="now"),
                "profile": {
                    "bio": self.fake.text(max_nb_chars=200),
                    "avatar_url": self.fake.image_url(),
                    "location": self.fake.city()
                }
            }
            users.append(user)

        self.insert_many_documents(collection=self.users, data=users)
        print(f"✅ Создано {count} тестовых пользователей")
        return users

    @measure_time("Генерация тестовых фильмов")
    def generate_test_movies(self, count: int = 200) -> List[Dict]:
        """Генерация тестовых фильмов"""
        genres = ["Action", "Comedy", "Drama", "Thriller", "Sci-Fi",
                  "Horror", "Romance", "Documentary", "Animation", "Fantasy"]
        movies = []

        for i in range(count):
            movie = {
                "movie_id": f"movie_{i + 1}",
                "title": self.fake.sentence(nb_words=3),
                "description": self.fake.text(max_nb_chars=300),
                "release_year": random.randint(1980, 2023),
                "genres": random.sample(genres, random.randint(1, 3)),
                "duration_minutes": random.randint(80, 180),
                "director": self.fake.name(),
                "cast": [self.fake.name() for _ in range(random.randint(3, 8))],
                "country": self.fake.country(),
                "language": self.fake.language_name(),
                "budget": random.randint(1000000, 200000000),
                "created_at": self.fake.date_time_between(start_date="-1y", end_date="now"),
                "poster_url": self.fake.image_url(),
                "imdb_rating": round(random.uniform(3.0, 9.5), 1)
            }
            movies.append(movie)

        self.insert_many_documents(collection=self.movies, data=movies)
        print(f"✅ Создано {count} тестовых фильмов")
        return movies

    @measure_time("Генерация оценок фильмов")
    def generate_movie_ratings(self, users: List[Dict], movies: List[Dict], ratings_per_user: int = 20):
        """Генерация оценок фильмов пользователями"""
        ratings = []

        for user in users:
            # Каждый пользователь оценивает случайные фильмы
            rated_movies = random.sample(
                movies, min(ratings_per_user, len(movies)))

            for movie in rated_movies:
                rating = {
                    "user_id": user["user_id"],
                    "movie_id": movie["movie_id"],
                    # 0-10, где 10 - лайк, 0 - дизлайк
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

        self.insert_many_documents(collection=self.movie_ratings, data=ratings)
        print(f"✅ Создано {len(ratings)} оценок фильмов")

    @measure_time("Генерация рецензий")
    def generate_reviews(self, users: List[Dict], movies: List[Dict], reviews_per_user: int = 5):
        """Генерация рецензий на фильмы"""
        reviews = []
        review_id_counter = 1

        for user in users:
            # Каждый пользователь пишет рецензии на случайные фильмы
            reviewed_movies = random.sample(
                movies, min(reviews_per_user, len(movies)))

            for movie in reviewed_movies:
                review = {
                    "review_id": f"review_{review_id_counter}",
                    "user_id": user["user_id"],
                    "movie_id": movie["movie_id"],
                    "title": self.fake.sentence(nb_words=6),
                    "text": self.fake.text(max_nb_chars=1000),
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
                review_id_counter += 1

        self.insert_many_documents(collection=self.reviews, data=reviews)
        print(f"✅ Создано {len(reviews)} рецензий")
        return reviews

    @measure_time("Генерация лайков рецензий")
    def generate_review_likes(self, users: List[Dict], reviews: List[Dict], likes_per_user: int = 10):
        """Генерация лайков/дизлайков рецензий"""
        review_likes = []

        for user in users:
            # Пользователь лайкает случайные рецензии (кроме своих)
            user_reviews = [
                r for r in reviews if r["user_id"] != user["user_id"]]
            liked_reviews = random.sample(
                user_reviews,
                min(likes_per_user, len(user_reviews))
            )

            for review in liked_reviews:
                like_value = random.choice([0, 10])  # 0 - дизлайк, 10 - лайк
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

                # Обновляем счетчик лайков в рецензии
                if like_value == 10:
                    self.reviews.update_one(
                        {"review_id": review["review_id"]},
                        {"$inc": {"likes_count": 1}}
                    )
                else:
                    self.reviews.update_one(
                        {"review_id": review["review_id"]},
                        {"$inc": {"dislikes_count": 1}}
                    )

        self.insert_many_documents(
            collection=self.review_likes, data=review_likes)
        print(f"✅ Создано {len(review_likes)} лайков/дизлайков рецензий")

    @measure_time("Генерация закладок")
    def generate_bookmarks(self, users: List[Dict], movies: List[Dict], bookmarks_per_user: int = 8):
        """Генерация закладок пользователей"""
        bookmarks = []

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
                    "notes": random.choice([None, self.fake.sentence(nb_words=8)])
                }
                bookmarks.append(bookmark)

        self.insert_many_documents(collection=self.bookmarks, data=bookmarks)
        print(f"✅ Создано {len(bookmarks)} закладок")

    @measure_time("ТЕСТ: Поиск пользователя по email")
    def test_find_user_by_email(self):
        """Тест поиска пользователя по email"""
        email = self.users.find_one()["email"]
        result = self.find(
            collection=self.users,
            condition={"email": email}
        )
        return result is not None

    @measure_time("ТЕСТ: Поиск фильмов по жанру")
    def test_find_movies_by_genre(self):
        """Тест поиска фильмов по жанру"""
        results = self.find(
            collection=self.movies,
            condition={"genres": "Action"},
            multiple=True
        )
        return len(results)

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
        movie_id = self.movies.find_one()["movie_id"]
        results = list(self.reviews.find(
            {"movie_id": movie_id}
        ).sort("created_at", -1).limit(20))
        return len(results)

    @measure_time("ТЕСТ: Получение закладок пользователя")
    def test_get_user_bookmarks(self):
        """Тест получения закладок пользователя"""
        user_id = self.users.find_one()["user_id"]
        results = self.find(
            collection=self.bookmarks,
            condition={"user_id": user_id},
            multiple=True
        )
        return len(results)

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
        """Генерация всех тестовых данных"""
        print("🎭 Начало генерации тестовых данных...")
        print("=" * 50)

        # Генерация базовых данных
        users = self.generate_test_users(100_000)
        movies = self.generate_test_movies(200_000)

        # Генерация связных данных
        self.generate_movie_ratings(users, movies, 20_000)
        reviews = self.generate_reviews(users, movies, 5_000)
        self.generate_review_likes(users, reviews, 10_000)
        self.generate_bookmarks(users, movies, 8_000)

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
        self.users.delete_many({})
        self.movies.delete_many({})
        self.movie_ratings.delete_many({})
        self.reviews.delete_many({})
        self.review_likes.delete_many({})
        self.bookmarks.delete_many({})
        print("✅ Все тестовые данные удалены!")


def main():
    # Создание тестера
    tester = MongoDBTester()

    try:
        # Очистка старых данных (опционально)
        tester.cleanup_test_data()

        # Генерация тестовых данных
        tester.generate_all_test_data()

        # Вывод статистики
        tester.print_statistics()

        # Запуск тестов производительности
        tester.run_performance_tests()

        # Вывод сводки по производительности
        tester.print_performance_summary()

    except Exception as e:
        print(f"❌ Ошибка: {e}")
    finally:
        # Закрытие соединения
        tester.client.close()
        print("\n🔚 Соединение с MongoDB закрыто")


if __name__ == '__main__':
    main()
