import os
import sys
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# 1. Встановлюємо тестові змінні середовища НА САМОМУ ПОЧАТКУ
os.environ["DATABASE_NAME"] = "library_test"
os.environ["DATABASE_URL"] = os.getenv("DATABASE_URL_TEST", "mongodb://mongo_admin:password@localhost:27017")

@pytest.fixture
def client_app():
    """Створює тестовий клієнт Flask."""
    # Відкладений імпорт: завантажуємо app лише в момент запуску тесту
    from main import app
    
    app.config["TESTING"] = True
    with app.test_client() as testing_client:
        with app.app_context():
            yield testing_client

@pytest.fixture(autouse=True)
def reset_db():
    """Очищує БД перед кожним тестом і додає початкові дані."""
    # Відкладений імпорт БД
    from app.database import client
    
    db_test = client[os.environ["DATABASE_NAME"]]
    
    # Видаляємо всі документи з колекції books
    db_test.books.drop()

    # Додаємо базову книгу для тестів
    seed_book = {
        "title": "Alice's Adventures in Wonderland",
        "author": "Lewis Carroll",
        "description": "A novel about Alice",
        "status": "available",
        "release_year": 1865,
    }
    db_test.books.insert_one(seed_book)
    
    yield