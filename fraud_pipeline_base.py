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
        region="us-central1"
    )
    options.view_as(StandardOptions).streaming = True

    with beam.Pipeline(options=options) as p:
        (
            p
            | "ReadFromPubSub" >> beam.io.ReadFromPubSub(subscription=SUBSCRIPTION)
            | "WindowIntoFixed" >> beam.WindowInto(window.FixedWindows(60))
            | "WriteToGCS" >> beam.io.WriteToText(
                file_path_prefix="gs://curated-silver/raw/transactions",
                file_name_suffix=".txt"
            )
        )

if __name__ == "__main__":
    run()
