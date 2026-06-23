from typing import Dict, List

import redis
from redis_lru import RedisLRU

from connect import *
from models import Author, Quote


client = redis.StrictRedis(
    host="localhost",
    port=6379,
    password=None,
    decode_responses=True
)

cache = RedisLRU(client)


@cache
def find_by_author(author: str) -> Dict[str, List[str]]:
    print(f"MongoDB query by author: {author}")

    authors = Author.objects(fullname__iregex=author)

    result = {}

    for a in authors:
        quotes = Quote.objects(author=a)
        result[a.fullname] = [q.quote for q in quotes]

    return result


@cache
def find_by_tag(tag: str) -> List[str]:
    print(f"MongoDB query by tag: {tag}")

    quotes = Quote.objects(tags__iregex=tag)
    return [q.quote for q in quotes]


def find_by_tags(tags: str) -> List[str]:
    tags_list = [tag.strip() for tag in tags.split(",")]

    quotes = Quote.objects(tags__in=tags_list)

    return [q.quote for q in quotes]


def main():
    while True:

        command = input(">>> ").strip()

        if command.lower() == "exit":
            print("Good bye!")
            break

        try:
            cmd, value = command.split(":", 1)

            cmd = cmd.strip().lower()
            value = value.strip()

            if cmd == "name":

                result = find_by_author(value)
                print("result", result)

                if not result:
                    print("Nothing found")
                    continue

                for author, quotes in result.items():
                    print(f"\n{author}:")

                    for quote in quotes:
                        print(f" - {quote}")

            elif cmd == "tag":

                result = find_by_tag(value)

                if not result:
                    print("Nothing found")
                    continue

                for quote in result:
                    print(f" - {quote}")

            elif cmd == "tags":

                result = find_by_tags(value)

                if not result:
                    print("Nothing found")
                    continue

                for quote in result:
                    print(f" - {quote}")

            else:
                print("Unknown command")

        except ValueError:
            print("Wrong format. Use:")
            print("name:Steve Martin")
            print("tag:life")
            print("tags:life,live")
            print("exit")


if __name__ == "__main__":
    main()
