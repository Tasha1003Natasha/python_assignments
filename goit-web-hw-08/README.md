# GOIT Web HW-08

## Description

This project contains two independent tasks:

- **Task 1** – Search quotes in MongoDB using MongoEngine with Redis caching.
- **Task 2** – Email/SMS message queue simulation using RabbitMQ and MongoDB.

---

## Installation

Clone the repository:

```bash
git clone <repository_url>
cd goit-web-hw-08
```

Create a virtual environment:

```bash
python -m venv venv
```

Activate the virtual environment.

macOS/Linux:

```bash
source venv/bin/activate
```

Windows:

```bash
venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## Environment variables

Create a `.env` file in the project root.

Example:

```env
MONGODB_URI=mongodb+srv://<username>:<password>@<cluster>/<database>
```

---

# Task 1

Load data into MongoDB:

```bash
python -m task1.seed
```

Run the application:

```bash
python -m task1.main
```

Available commands:

```
name:Steve Martin
tag:life
tags:life,live
exit
```

---

# Task 2

Start RabbitMQ server.

macOS (Homebrew):

```bash
brew services start rabbitmq
```

Run Email consumer:

```bash
python -m task2.consumer_email
```

Run SMS consumer:

```bash
python -m task2.consumer_sms
```

In another terminal run Producer:

```bash
python -m task2.producer
```

Producer creates fake contacts and sends them to RabbitMQ queues.
Consumers receive messages, simulate sending notifications and update the `is_sent` field in MongoDB.

---

## Project Structure

```
goit-web-hw-08
│
├── task1
│   ├── connect.py
│   ├── models.py
│   ├── seed.py
│   └── main.py
│
├── task2
│   ├── connect.py
│   ├── models.py
│   ├── producer.py
│   ├── consumer_email.py
│   └── consumer_sms.py
│
├── requirements.txt
├── README.md
└── .env
```