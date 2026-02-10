import json, time, random
from kafka import KafkaProducer

producer = KafkaProducer(
    bootstrap_servers="localhost:9092",
    value_serializer=lambda v: json.dumps(v).encode()
)

while True:
    producer.send("telemetry_raw", {
        "car_id": random.choice(["44", "16", "55"]),
        "speed": random.uniform(250, 340),
        "rpm": random.randint(9000, 12000),
        "event_time": int(time.time() * 1000)
    })
    producer.flush()
    time.sleep(1)
