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
channel.queue_declare(queue="sms_queue", durable=True)


def send_message(phone):
    print(f"Sending message to {phone}...")
    time.sleep(1)
    print("Sent ✔")


def callback(ch, method, properties, body):

    contact_id = body.decode()

    contact = Contact.objects(id=ObjectId(contact_id)).first()

    if contact:

        send_message(contact.phone)

        print("DB NAME:", get_db().name)

        contact.is_sent = True
        contact.save()

        print(f"Updated contact {contact.fullname} {contact.prefer_sms}")


channel.basic_consume(
    queue="sms_queue",
    on_message_callback=callback,
    auto_ack=True
)


print("Waiting for sms...")
channel.start_consuming()
