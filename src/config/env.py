import dotenv
import os

dotenv.load_dotenv()

# Retrieve the "target_url" environment variable as a comma-separated string
target_url_str = os.environ.get("target_url")

# Convert the comma-separated string to a list if it's not None
target_url_list = target_url_str.split(',') if target_url_str else []
DRIVER_CONFIG = {
    "target_url": target_url_list,
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