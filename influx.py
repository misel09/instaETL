from kafka import KafkaConsumer
from influxdb_client import InfluxDBClient, Point, WritePrecision
import json
from datetime import datetime

# --- InfluxDB Config ---
token = "UxZ1w2blgHNuMW4BvjxkItyfjQZyNUZ-0L1jKq1ZEQQacpfSDFLh1dApB8muHVEaSMW763OsNhSr0IkJA7tskQ=="
org = "InstaOrg"
bucket = "insta_metrics"
url = "http://localhost:8086"

client = InfluxDBClient(url=url, token=token, org=org)
write_api = client.write_api()

# --- Kafka Config ---
consumer = KafkaConsumer(
    "insta-business-data",
    bootstrap_servers="localhost:9092",
    value_deserializer=lambda m: json.loads(m.decode("utf-8"))
)

print("✅ Connected to Kafka and InfluxDB")

for message in consumer:
    data = message.value
    print(f"📥 Received from Kafka: {data}")

    try:
        account = data.get("account", "unknown")

        # Parse likes (convert if string like "3381 likes")
        likes_raw = data.get("likes", 0)
        if isinstance(likes_raw, str):
            likes = int("".join(filter(str.isdigit, likes_raw)))
        else:
            likes = int(likes_raw)

        # Parse comment count
        comments_raw = data.get("comment_count", 0)
        if isinstance(comments_raw, str):
            comment_count = int("".join(filter(str.isdigit, comments_raw)))
        else:
            comment_count = int(comments_raw)

        # Parse posts/followers/following
        posts = int(data.get("posts", 0))
        followers = int(data.get("followers", 0))
        following = int(data.get("following", 0))

        # Image URL
        image_url = data.get("image_url", "N/A")

        # Use scraping_date + scraping_time for timestamp if available
        timestamp = None
        if data.get("scraping_date") and data.get("scraping_time"):
            try:
                timestamp = datetime.strptime(
                    f"{data['scraping_date']} {data['scraping_time']}",
                    "%Y-%m-%d %H:%M:%S"
                )
            except:
                timestamp = datetime.utcnow()
        else:
            timestamp = datetime.utcnow()

        # Build point for InfluxDB
        point = (
            Point("instagram_posts")
            .tag("account", account)
            .field("likes", likes)
            .field("comment_count", comment_count)
            .field("posts", posts)
            .field("followers", followers)
            .field("following", following)
            .field("image_url", image_url)
            .time(timestamp, WritePrecision.NS)
        )

        # Write to InfluxDB
        write_api.write(bucket=bucket, org=org, record=point)
        print(f"✅ Data written to InfluxDB for account {account} (likes={likes}, comments={comment_count}, followers={followers})")

    except Exception as e:
        print(f"❌ Error processing message: {e}")