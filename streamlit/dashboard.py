import json
import time
from collections import deque

import pandas as pd
import streamlit as st
import plotly.express as px
from kafka import KafkaConsumer

# -------------------------------------------------
# Streamlit setup
# -------------------------------------------------
st.set_page_config(
    page_title="Motorsports proj",
    layout="wide"
)

st.title("Flink wala dashboard of cute cars yum")
st.caption("Source: Kafka topic telemetry_analytics ")

# -------------------------------------------------
# Kafka Consumer (CRITICAL SETTINGS)
# -------------------------------------------------
@st.cache_resource
def get_consumer():
    return KafkaConsumer(
        "telemetry_analytics",
        bootstrap_servers="kafka:29092",   # Docker internal
        value_deserializer=lambda v: json.loads(v.decode("utf-8")),
        auto_offset_reset="earliest",       # 🔑 replay existing data
        enable_auto_commit=True,
        group_id="streamlit-ui-v3"          # 🔑 NEW group
    )

consumer = get_consumer()

# -------------------------------------------------
# Buffer (keeps last N records)
# -------------------------------------------------
if "buffer" not in st.session_state:
    st.session_state.buffer = deque(maxlen=200)

# -------------------------------------------------
# Poll Kafka
# -------------------------------------------------
records = consumer.poll(timeout_ms=1000)

message_count = sum(len(v) for v in records.values())
st.caption(f"Kafka messages received in this poll: {message_count}")

for _, messages in records.items():
    for msg in messages:
        event = msg.value
        event["ui_time"] = pd.Timestamp.utcnow()
        st.session_state.buffer.append(event)

# -------------------------------------------------
# Render dashboard
# -------------------------------------------------
if st.session_state.buffer:
    df = pd.DataFrame(st.session_state.buffer)

    c1, c2, c3 = st.columns(3)
    c1.metric("Cars", df["car_id"].nunique())
    c2.metric("Avg Speed", f"{df['avg_speed'].mean():.1f}")
    c3.metric("Avg RPM", f"{df['avg_rpm'].mean():.0f}")

    st.plotly_chart(
        px.line(
            df,
            x="ui_time",
            y="avg_speed",
            color="car_id",
            title="Average Speed (Event-time windows)"
        ),
        use_container_width=True
    )

    st.plotly_chart(
        px.line(
            df,
            x="ui_time",
            y="avg_rpm",
            color="car_id",
            title="Average RPM (Event-time windows)"
        ),
        use_container_width=True
    )

    st.dataframe(df.tail(10), use_container_width=True)

else:
    st.info("Waiting for data...")

# -------------------------------------------------
# Auto refresh
# -------------------------------------------------
time.sleep(2)
st.rerun()
