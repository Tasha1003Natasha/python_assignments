from mongoengine import Document, StringField, BooleanField


class Contact(Document):
    fullname = StringField(required=True)
    email = StringField(required=True)
    phone = StringField(required=True)
    is_sent = BooleanField(default=False)
    prefer_sms = BooleanField(default=False)

    meta = {"collection": "contacts"}
