import pika
from faker import Faker
from .connect import *
from .models import Contact


fake = Faker()

connection = pika.BlockingConnection(
    pika.ConnectionParameters("localhost")
)
channel = connection.channel()
channel.queue_declare(queue="email_queue", durable=True)
channel.queue_declare(queue="sms_queue", durable=True)


def create_contacts(n=5):

    for _ in range(n):

        contact = Contact(
            fullname=fake.name(),
            email=fake.email(),
            phone=fake.phone_number(),
            is_sent=False,
            prefer_sms=fake.boolean(),
        )
        contact.save()

        if contact.prefer_sms:
            queue_name = "sms_queue"
        else:
            queue_name = "email_queue"

        channel.basic_publish(
            exchange="",
            routing_key=queue_name,
            body=str(contact.id)
        )

        print(f"Sent to {queue_name}: {contact.id}")


if __name__ == "__main__":
    create_contacts(10)
