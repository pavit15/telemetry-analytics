import json
from pyflink.common import Types
from pyflink.common.time import Time, Duration
from pyflink.common.serialization import SimpleStringSchema
from pyflink.common.watermark_strategy import WatermarkStrategy
from pyflink.datastream import StreamExecutionEnvironment
from pyflink.datastream.window import TumblingEventTimeWindows
from pyflink.datastream.connectors.kafka import KafkaSource, KafkaSink, KafkaRecordSerializationSchema


env = StreamExecutionEnvironment.get_execution_environment()
env.set_parallelism(1)

source = (
    KafkaSource.builder()
    .set_bootstrap_servers("kafka:29092")
    .set_topics("telemetry_raw")
    .set_group_id("telemetry-analytics")
    .set_value_only_deserializer(SimpleStringSchema())
    .build()
)


def parse_event(value):
    d = json.loads(value)
    return d["car_id"], float(d["speed"]), int(d["rpm"]), int(d["event_time"])


stream = (
    env.from_source(
        source,
        WatermarkStrategy
        .for_bounded_out_of_orderness(Duration.of_seconds(2))
        .with_timestamp_assigner(lambda e, ts: e[3]),
        "Kafka Source"
    )
    .map(
        parse_event,
        output_type=Types.TUPLE([
            Types.STRING(),
            Types.FLOAT(),
            Types.INT(),
            Types.LONG()
        ])
    )
)

aggregated = (
    stream
    .map(lambda x: (x[0], x[1], x[2], 1),
         output_type=Types.TUPLE([
             Types.STRING(), Types.FLOAT(), Types.INT(), Types.INT()
         ]))
    .key_by(lambda x: x[0])
    .window(TumblingEventTimeWindows.of(Time.seconds(5)))
    .reduce(
        lambda a, b: (
            a[0],
            a[1] + b[1],
            a[2] + b[2],
            a[3] + b[3]
        )
    )
)

def to_json(v):
    return json.dumps({
        "car_id": v[0],
        "avg_speed": round(v[1] / v[3], 2),
        "avg_rpm": int(v[2] / v[3])
    })

result = aggregated.map(to_json, output_type=Types.STRING())

sink = (
    KafkaSink.builder()
    .set_bootstrap_servers("kafka:29092")
    .set_record_serializer(
        KafkaRecordSerializationSchema.builder()
        .set_topic("telemetry_analytics")
        .set_value_serialization_schema(SimpleStringSchema())
        .build()
    )
    .build()
)

result.sink_to(sink)

env.execute("Telemetry Analytics")
