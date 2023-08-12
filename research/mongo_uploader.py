"""Этот скрипт выполняет вставку данных в коллекции MongoDB."""

import __future__
import logging
import typing

import pymongo # type: ignore

from config import mongo_cfg, MongoDBConfig
from fake_data import (
    create_bookmarks,
    create_reviews,
    create_film_ratings,
)

logger = logging.getLogger(__name__)


class MongoUploader:
    """Класс MongoUploader используется для загрузки данных в MongoDB."""

    def __init__(
        self,
        config: MongoDBConfig,
        client: typing.Optional[pymongo.MongoClient] = None,
    ) -> None:
        """
        Инициализирует объект класса, конфигурацию и клиент MongoDB.

        Args:
            config (MongoDBConfig): Конфигурация MongoDB, содержащая информацию
                                    для подключения к серверу.
            client (pymongo.MongoClient, optional): Пользовательский объект
                                                    MongoClient
                                                    вместо создания нового.
        """
        self._config = config
        self._client = client

    @property
    def mongo_conn(self) -> typing.Union[pymongo.MongoClient, None]:
        """
        Устанавливает соединение с сервером MongoDB.

        Returns:
            pymongo.MongoClient: Объект MongoClient,
            представляющий соединение с сервером MongoDB.
        """
        try:
            if self._client is None or not self._client.admin.command("ping"):
                self._client = self.create_client()
        except pymongo.errors.PyMongoError as er:
            logger.error("Mongo connection error: %s", er)
            return None
        return self._client

    def create_client(self) -> pymongo.MongoClient:
        """
        Создать новое подключение для Mongo.

        Returns:
            объект pymongo.MongoClient для подключения к MongoDB.
        """
        return pymongo.MongoClient(
            self._config.mongo_connection_string,
        )

    def get_database(self) -> typing.Union[pymongo.database.Database, None]:
        """
        Получает объект базы данных из текущего подключения к MongoDB.

        Returns:
            pymongo.database.Database: Объект БД.
        """
        if self.mongo_conn is None:
            return None
        return self.mongo_conn[self._config.db_name]

    def create_batch(
        self,
        iterable: typing.Iterator,
        batch_size: int,
    ) -> typing.Iterator[list]:
        """
        Разбивает итерируемый объект на пакеты заданного размера.

        Args:
            iterable: Итерируемый объект, который нужно разбить на пакеты.
            batch_size: Размер пакета.

        Yields:
            list: Список элементов из входного итерируемого объекта.
        """
        batch = []
        for elem in iterable:
            batch.append(elem)
            if len(batch) % batch_size == 0:
                yield batch
                batch = []
        if batch:
            yield batch

    def drop_db(self) -> None:
        """Удаляет базу данных MongoDB."""
        if self.mongo_conn:
            self.mongo_conn.drop_database(self._config.db_name)

    def checking_collection_in_db(
        self,
        collection_name: str,
        doc_id: str,
    ) -> None:
        """
        Проверяет наличие коллекции в базе данных.

        Args:
            collection_name: Имя коллекции, которую следует проверить.
                                и создать при необходимости.
            doc_id: Идентификатор документа в коллекции, используемый
                    для установки индекса (если коллекция создается).

        Примечание:
        - Проверка осуществляется путем сравнения переданного имени коллекции
        с именами коллекций, доступных в базе данных.
        - Если коллекция с указанным именем не существует,
        вызывается метод create_and_configure_collection() для ее создания.
        """
        database = self.get_database()
        if database:
            if collection_name not in database.list_collection_names():
                self.create_and_configure_collection(
                    self.get_database(),
                    collection_name,
                    self._client,
                    doc_id,
                )

    def create_collections(self) -> None:
        """Создает коллекции в MongoDB."""
        self.checking_collection_in_db(
            self._config.film_ratings_collection,
            "film_id",
        )
        self.checking_collection_in_db(
            self._config.reviews_collection,
            "film_id",
        )
        self.checking_collection_in_db(
            self._config.bookmarks_collection,
            "user_id",
        )

    def create_and_configure_collection(
        self,
        database,
        collection,
        client,
        index,
    ) -> None:
        """
        Создает коллекцию в базе данных и настраивает её параметры.

        Args:
            database: Объект базы данных.
            collection: Имя коллекции, которую нужно создать.
            client: Клиент подключения к MongoDB.
            index: Имя поля или атрибута для создания индекса.
        """
        database.create_collection(collection)
        client.admin.command("enableSharding", self._config.db_name)
        client.admin.command(
            "shardCollection",
            f"{database}.{self._config.film_ratings_collection}",
            key={"_id": "hashed"},
        )
        database[collection].create_index([(index, pymongo.ASCENDING)])

    def insert_data_into_collection(
        self,
        collection_name: str,
        collection_data: typing.List[dict],
    ) -> None:
        """
        Вставляет данные в коллекцию в MongoDB.

        Args:
            collection_name: Имя коллекции, в которую нужно вставить данные.
            collection_data: Список словарей с данными, которые нужно вставить.
        """
        database = self.get_database()
        if database:
            database[collection_name].insert_many(collection_data)

    def get_collection_counts(self, collection_name: str) -> typing.Union[int, None]:
        """
        Возвращает количество документов в указанной коллекции.

        Args:
            collection_name: Имя коллекции.

        Returns:
            int: Количество документов в коллекции.
        """
        database = self.get_database()
        if database:
            return database[collection_name].count_documents({})
        return None

    def ratings_insert(self, num: int) -> None:
        """
        Вставляет данные о рейтингах фильмов пользователей в коллекцию MongoDB.

        Args:
            num: Колличество элементов для вставки в коллекцию.
        """
        film_ratings = create_film_ratings(num)
        for count, batch in enumerate(
            self.create_batch(film_ratings, self._config.batch_size),
            start=1,
        ):
            self.insert_data_into_collection(
                self._config.film_ratings_collection,
                [user_film_rating.__dict__ for user_film_rating in batch],
            )
            logger.info(self._config.batch_size * count, "rows inserted")

    def reviews_insert(self, num: int) -> None:
        """
        Вставляет данные о рецензиях в коллекцию MongoDB.

        Args:
            num: Колличество элементов для вставки в коллекцию.
        """
        reviews = create_reviews(num)
        for count, batch in enumerate(
            self.create_batch(reviews, self._config.batch_size),
            start=1,
        ):
            self.insert_data_into_collection(
                self._config.reviews_collection,
                [review.__dict__ for review in batch],
            )
            logger.info(self._config.batch_size * count, "rows inserted")

    def bookmarks_insert(self, num: int) -> None:
        """
        Вставляет данные о закладках в коллекцию MongoDB.

        Args:
            num: Колличество элементов для вставки в коллекцию.
        """
        bookmarks = create_bookmarks(num)
        for count, batch in enumerate(
            self.create_batch(bookmarks, self._config.batch_size),
            start=1,
        ):
            self.insert_data_into_collection(
                self._config.bookmarks_collection,
                [bookmark.__dict__ for bookmark in batch],
            )
            logger.info(self._config.batch_size * count, "rows inserted")


def main() -> None:
    """Главная функция загрузки данных в MongoDB."""
    mongo_uploader = MongoUploader(config=mongo_cfg)
    mongo_uploader.create_collections()
    mongo_uploader.drop_db()

    collections = [
        (mongo_uploader.ratings_insert, mongo_cfg.film_ratings_collection),
        (mongo_uploader.reviews_insert, mongo_cfg.reviews_collection),
        (mongo_uploader.bookmarks_insert, mongo_cfg.bookmarks_collection),
    ]

    for insert_func, collection_name in collections:
        insert_func(mongo_cfg.num_elements)
        count = mongo_uploader.get_collection_counts(collection_name)
        print(f"Collection '{collection_name}' count: {count}")

    print("Data insertion completed successfully!")


if __name__ == "__main__":
    main()
