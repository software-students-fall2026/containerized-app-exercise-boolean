"""Created this file to start all three containers"""

import os
import time

from pymongo import MongoClient


def main():
    client = MongoClient(os.environ["MONGO_URI"])
    client.admin.command("ping")
    print("Connected to MongoDB", flush=True)

    while True:
        time.sleep(2)


if __name__ == "__main__":
    main()