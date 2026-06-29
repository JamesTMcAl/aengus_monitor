"""Aengus - homelab metric anomaly detection."""
from dotenv import load_dotenv
load_dotenv()
import os
import time
import statistics
from collections import deque
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

URL    = os.environ.get("AENGUS_INFLUX_URL", "http://192.168.0.109:8086")
TOKEN  = os.environ.get("AENGUS_INFLUX_TOKEN")
ORG    = os.environ.get("AENGUS_INFLUX_ORG", "HomeJames")
BUCKET = os.environ.get("AENGUS_INFLUX_BUCKET", "proxmox")


def latest_iowait(query_api):
    """Fetch the most recent cpu usage_iowait value for the proxmox host."""
    flux = f'''
    from(bucket: "{BUCKET}")
      |> range(start: -2m)
      |> filter(fn: (r) => r._measurement == "cpu")
      |> filter(fn: (r) => r._field == "usage_iowait")
      |> filter(fn: (r) => r.host == "proxmox")
      |> last()
    '''
    tables = query_api.query(flux, org=ORG)
    for table in tables:
        for record in table.records:
            return record.get_time(), record.get_value()
    return None, None


def zscore(history):
    """How many standard deviations the latest value is from the recent mean."""
    if len(history) < 5:
        return 0.0  # not enough history to judge yet
    current = history[-1]
    prior = list(history)[:-1]
    mu = statistics.fmean(prior)
    sigma = statistics.pstdev(prior)
    if sigma == 0:
        return 0.0  # flat history, no deviation possible
    return (current - mu) / sigma


def write_reading(write_api, value, score):
    """Write the raw value and its anomaly score to the aengus measurement."""
    point = (
        Point("aengus")
        .tag("host", "proxmox")
        .tag("metric", "cpu.usage_iowait")
        .field("value", float(value))
        .field("anomaly_score", float(score))
    )
    write_api.write(bucket=BUCKET, org=ORG, record=point)


def main():
    client = InfluxDBClient(url=URL, token=TOKEN, org=ORG)
    query_api = client.query_api()
    write_api = client.write_api(write_options=SYNCHRONOUS)

    history = deque(maxlen=60)
    last_ts = None

    print("Aengus started - polling every 15s")

    while True:
        ts, value = latest_iowait(query_api)
        if value is None:
            print("No data returned - check measurement/field/host")
        elif ts == last_ts:
            pass  # same sample as last poll, skip so we don't score it twice
        else:
            last_ts = ts
            history.append(value)
            score = zscore(history)
            write_reading(write_api, value, abs(score))
            flag = "  <-- ANOMALY" if abs(score) > 3 else ""
            print(f"{ts}  iowait={value:5.2f}  z={score:+.2f}{flag}")
        time.sleep(15)


if __name__ == "__main__":
    main()