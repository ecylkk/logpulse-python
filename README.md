# 📡 LogPulse: Distributed Log Observability System

A real-time log collection and anomaly detection pipeline built with **Python**, **Apache Kafka**, and **Docker**.

## 🏗️ Architecture
```
[Log Producer] ---> [Kafka Cluster] ---> [Log Analyzer]
  (Python)           (KRaft Mode)          (Python)
  Generates logs     High-throughput       Detects ERROR
  every 1 second     message backbone      level anomalies
```

## 🚀 DevOps Highlights
- **Zero-Dependency**: Runs entirely in Docker. No local Python/Kafka installation needed.
- **Microservice Pattern**: Producer and Analyzer are independent containers communicating via Kafka.
- **Cloud-Ready**: Designed for deployment on Render with Upstash Kafka integration.

## 🛠️ Quick Start
```bash
docker-compose up --build
```

## 🔍 What You'll See
- `📤` Producer sending JSON logs every second
- `✅` Analyzer processing normal logs
- `🚨 ALERT` Analyzer catching ERROR-level anomalies

---
*Part of the Enterprise DevOps Combat series by DYsensei.*
