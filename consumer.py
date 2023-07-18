import pymongo
import pika
import json

class CarDataConsumer:
    def __init__(self, amqp_url, mongodb_url):
        self.amqp_url = amqp_url
        self.mongodb_url = mongodb_url
        self.client = None

    def connect_to_mongodb(self):
        self.client = pymongo.MongoClient(self.mongodb_url)

    def process_message(self, channel, method, properties, body):
        data = json.loads(body)

        # Save the data to MongoDB
        db = self.client["bama"]
        collection = db["cars"]
        collection.insert_one(data)

        channel.basic_ack(delivery_tag=method.delivery_tag)
        print(f'finished processing and acknowledged message')

    def start_consuming(self):
        connection = pika.BlockingConnection(pika.URLParameters(self.amqp_url))
        channel = connection.channel()
        channel.queue_declare(queue='scraped_data')
        channel.basic_consume(queue='scraped_data', on_message_callback=self.process_message)

        channel.start_consuming()
     

# Usage
amqp_url = "amqp://guest:guest@localhost:5672/"
mongodb_url = "mongodb://localhost:27017/"

consumer = CarDataConsumer(amqp_url, mongodb_url)
consumer.connect_to_mongodb()
consumer.start_consuming()

