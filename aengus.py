"""Aengus - homelab metric anomaly detection. Read path first."""

import os
from influxdb_client import InfluxDBClient

URL    = os.environ.get("AENGUS_INFLUX_URL", "http://192.168.0.109:8086")
TOKEN  = os.environ.get("AENGUS_INFLUX_TOKEN")
ORG    = os.environ.get("AENGUS_INFLUX_ORG", "HomeJames")
BUCKET = os.environ.get("AENGUS_INFLUX_BUCKET", "proxmox")


def latest_iowait(query_api):
    """Fetch the most recent cpu usage_iowait value for the proxmox host"""
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


def main():
    client = InfluxDBClient(url=URL, token=TOKEN, org=ORG)
    ts, value = latest_iowait(client.query_api())
    if value is None:
        print("No data returned - check measurement/field/host")
    else:
        print(f"{ts}  usage_iowait = {value:.2f}")


if __name__ == "__main__":
    main()