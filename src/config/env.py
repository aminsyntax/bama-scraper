import dotenv
import os

dotenv.load_dotenv()

DRIVER_CONFIG = {
    "target_url_1": os.environ.get("target_url_1"),
    "target_url_2": os.environ.get("target_url_2"),
    "local_webdriver_path": os.environ.get("local_webdriver_path"),
}

MOMGO_CONFIG = {
    "mongodb_url": os.environ.get("mongodb_url"),
    "mongo_database": os.environ.get("database"),
    "collection": os.environ.get("collection"),
}

RABBITMQ_CONFIG = {
    "amqp_url": os.environ.get("amqp_url"),
    "rabbitmq_host": os.environ.get("rabbitmq_host"),
}