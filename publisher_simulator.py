import json
import time
from google.cloud import pubsub_v1

PROJECT_ID = "sakina-gcp"
TOPIC_ID = "transactions-topic"

publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path(PROJECT_ID, TOPIC_ID)

with open("iteration-1.json") as f:
    transactions = json.load(f)

for tx in transactions:
    data = json.dumps(tx).encode("utf-8")
    future = publisher.publish(topic_path, data)
    print(f"Published: {tx['transaction_id']}")
    time.sleep(1)  # simulate stream delay
