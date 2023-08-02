import pymongo
import pika
import json

from src.config.env import MOMGO_CONFIG, RABBITMQ_CONFIG

class CarDataConsumer:
    def __init__(self, amqp_url, mongodb_url):
        self.amqp_url = amqp_url
        self.mongodb_url = mongodb_url
        self.client = None

    def connect_to_mongodb(self):
        self.client = pymongo.MongoClient(self.mongodb_url)

    def process_message(self, channel, method, properties, body):
        data = json.loads(body)
        queue_name = method.routing_key  # Get the queue name from the routing key

        # Save the data to the corresponding MongoDB collection
        db = self.client[MOMGO_CONFIG["mongo_database"]]
        collection = db[queue_name]  # Use the queue name as the collection name
        collection.insert_one(data)

        channel.basic_ack(delivery_tag=method.delivery_tag)
        print(f'Finished processing and acknowledged message from queue: {queue_name}')

    def start_consuming(self):
        connection = pika.BlockingConnection(pika.URLParameters(self.amqp_url))
        channel = connection.channel()

        # Declare both queues with their respective names
        channel.queue_declare(queue='scraped_data_0')
        channel.queue_declare(queue='scraped_data_1')

        # Start consuming from both queues
        channel.basic_consume(queue='scraped_data_0', on_message_callback=self.process_message)
        channel.basic_consume(queue='scraped_data_1', on_message_callback=self.process_message)

        print("Waiting for messages. To exit press CTRL+C")
        channel.start_consuming()

# Usage
consumer = CarDataConsumer(RABBITMQ_CONFIG["amqp_url"], MOMGO_CONFIG["mongodb_url"])
consumer.connect_to_mongodb()
consumer.start_consuming()
