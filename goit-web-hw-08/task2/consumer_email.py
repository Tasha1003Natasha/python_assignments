from bson import ObjectId
from .models import Contact
import pika
import time
from .connect import *

from mongoengine.connection import get_db

connection = pika.BlockingConnection(
    pika.ConnectionParameters("localhost")
)

channel = connection.channel()
channel.queue_declare(queue="email_queue", durable=True)


def send_email(email):
    print(f"Sending email to {email}...")
    time.sleep(1)
    print("Sent ✔")


def callback(ch, method, properties, body):

    contact_id = body.decode()

    contact = Contact.objects(id=ObjectId(contact_id)).first()

    if contact:

        send_email(contact.email)

        print("DB NAME:", get_db().name)

        contact.is_sent = True
        contact.save()

        print(f"Updated contact {contact.fullname} {contact.is_sent}")


channel.basic_consume(
    queue="email_queue",
    on_message_callback=callback,
    auto_ack=True
)


print("Waiting for messages...")
channel.start_consuming()
