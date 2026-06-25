# Aengus

Streaming anomaly detection for homelab infrastructure metrics.

A self-hosted ML service that learns the normal behaviour of system telemetry
(CPU, memory, disk I/O, network) from InfluxDB and flags anomalies in real time,
with results surfaced back into Grafana.

Named after the wandering Aengus - endlessly seeking.

## Status
Early development.

## Requirements
influxdb-client
python-dotenv

## env. Example
AENGUS_INFLUX_URL=http://192.168.0.109:8086
AENGUS_INFLUX_TOKEN=your-token-here
AENGUS_INFLUX_ORG=Orgname
AENGUS_INFLUX_BUCKET=proxmox