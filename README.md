
# Fraud Detection Pipeline Project

This project demonstrates a streaming data pipeline using Apache Beam and Google Cloud Platform components like Pub/Sub and Cloud Storage. The pipeline reads simulated transaction data from Pub/Sub, processes it, and writes outputs to Cloud Storage.

---

## Project Overview

The goal is to build a real-time fraud detection pipeline that:

- Simulates streaming transaction data via a Pub/Sub topic.
- Consumes the streaming data with an Apache Beam pipeline.
- Writes processed data into Cloud Storage.
- Handles windowing to batch streaming data by fixed intervals.

---

## Components and Files

### 1. Publisher Simulator (`publisher_simulator.py`)

- Reads transaction data from a JSON file.
- Publishes each transaction message to a Pub/Sub topic to simulate real-time streaming.

```python
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
````

**How to run:**

```bash
python3 publisher_simulator.py
```

---

### 2. Streaming Pipeline (`fraud_pipeline_base.py`)

* Reads streaming messages from the Pub/Sub subscription.
* Applies fixed windowing (60 seconds).
* Writes raw messages as text files to Google Cloud Storage.

```python
import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions, StandardOptions
import apache_beam.transforms.window as window

PROJECT_ID = "sakina-gcp"
SUBSCRIPTION = f"projects/{PROJECT_ID}/subscriptions/transactions-sub"

def run():
    options = PipelineOptions(
        streaming=True,
        project=PROJECT_ID,
        temp_location="gs://raw_bronze1/temp/",
        region="us-central1",
        save_main_session=True
    )
    options.view_as(StandardOptions).streaming = True

    with beam.Pipeline(options=options) as p:
        (
            p
            | "ReadFromPubSub" >> beam.io.ReadFromPubSub(subscription=SUBSCRIPTION)
            | "WindowIntoFixed" >> beam.WindowInto(window.FixedWindows(60))
            | "WriteToGCS" >> beam.io.WriteToText(
                file_path_prefix="gs://curated-silver/raw/transactions",
                file_name_suffix=".txt",
                shard_name_template='',
                num_shards=1
            )
        )

if __name__ == "__main__":
    run()
```

---

### 3. Running the Pipeline

**DirectRunner (local testing):**

```bash
python3 fraud_pipeline_base.py \
  --runner=DirectRunner \
  --project=sakina-gcp \
  --streaming
```

**DataflowRunner (cloud execution):**

```bash
python3 fraud_pipeline_base.py \
  --runner=DataflowRunner \
  --project=sakina-gcp \
  --region=us-central1 \
  --temp_location=gs://raw_bronze1/temp/ \
  --staging_location=gs://raw_bronze1/staging/ \
  --job_name=fraud-simple-pipeline \
  --streaming
```

---

## Progress and Status

* Successfully published simulated transactions to Pub/Sub.
* Successfully read streaming data from Pub/Sub with Apache Beam pipeline.
* Applied fixed windowing of 60 seconds and wrote output to Cloud Storage as text files.
* Encountered an error related to `GroupByKey` and global windowing while attempting to apply aggregation or certain transforms on unbounded data.  
* Currently focusing on reading and writing data without aggregations to confirm the pipeline works end-to-end.

---

## How to Verify

* Use `gcloud pubsub subscriptions pull` or Google Cloud Console to verify messages are arriving in Pub/Sub.
* Check the Cloud Storage bucket `gs://curated-silver/raw/` for output files written by the pipeline.
* Monitor pipeline job status in Google Cloud Dataflow UI when running on DataflowRunner.

---

## Next Steps

* Fix the `GroupByKey` windowing error by adjusting windowing strategy or triggers before applying aggregation transforms.
* Implement additional fraud detection logic such as filtering or flagging suspicious transactions.
* Enhance data output with partitioning and schema-enforced storage (e.g., BigQuery).
* Add monitoring and alerting.

---

## Prerequisites

* Google Cloud SDK installed and configured.
* Apache Beam SDK installed (`pip install apache-beam[gcp]`).
* GCP project with Pub/Sub topic and subscription created.
* Cloud Storage buckets created for temp, staging, and output.

---

 
 
