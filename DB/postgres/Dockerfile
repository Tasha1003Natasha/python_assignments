FROM python:3.12-slim

WORKDIR /app

COPY . .

RUN pip install psycopg2-binary

CMD ["python", "app.py"]