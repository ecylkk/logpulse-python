# 🔴 LogPulse: Cloud-Native SRE Kafka Pipeline

![Live Status](https://img.shields.io/badge/Status-Live_Streaming-success.svg?style=for-the-badge&logo=apachekafka&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.11+-yellow?style=for-the-badge&logo=python&logoColor=white)
![Cloud](https://img.shields.io/badge/Cloud-Aiven%20%7C%20Render-purple?style=for-the-badge&logo=googlecloud&logoColor=white)

> **🚀 [LIVE REAL-TIME DASHBOARD: View Global Log Stream](https://logpulse-analyzer.onrender.com/)**

**LogPulse** is an enterprise-grade, zero-dependency Python logging and real-time analysis pipeline. It was engineered specifically to demonstrate modern Site Reliability Engineering (SRE), cross-border cloud networking, and high-performance Event-Driven Architecture (EDA). 

---

## 🌟 Premium Architecture Features

1. **Distributed Decoupling via Apache Kafka**: Replaces brittle, monolithic local logging with a high-throughput asynchronous messaging queue hosted entirely on **Aiven Cloud**.
2. **Mutual TLS (mTLS) Security**: All data transferred over the public internet is encrypted end-to-end using X.509 client certificates.
3. **Environment Secret Injection (Secrets-as-Code)**: Hardcoded credentials are strictly avoided. The cloud runtime horizontally reconstructs complex `.pem` and `.key` files purely from CI/CD Environment Variables on the fly.
4. **Cloud-Native Auto-Healing**: The Python Consumer automatically manages `SSL_HANDSHAKE` reconnects, DNS propagation latency across GFW borders, and dynamic port binding for PaaS health checks.
5. **Real-Time SRE Command Center**: A zero-dependency, asynchronous Web UI that visualizes global system heartbeats and traps critical alert spikes in real-time.

---

## 🏗️ System Topology

1. **Producer (`Edge Data Source`)**: Generates simulated global traffic, authentication heartbeats, and payment gateway alerts. Pushes directly to Aiven's distributed brokers.
2. **Message Broker (`Aiven Cloud / Confluent`)**: A fully managed cloud Kafka cluster acting as the resilient, decoupled nervous system of the architecture.
3. **Analyzer (`Render PaaS`)**: A 24/7 cloud-hosted multi-threaded worker that consumes the Kafka topic in real-time, calculates live metrics, and serves an interactive web dashboard.

---

## 🛠️ Tech Stack 
* **Language**: Pure Python (No complex JVM memory footprint).
* **Driver**: `confluent-kafka` (High-performance C-bindings under the hood).
* **Infrastructure**: `Aiven (DBaaS)`, `Render (PaaS)`, `GitHub (Version Control)`, `Docker Compose`.

> *Designed and implemented to definitively showcase SRE problem-solving capabilities, cloud platform limits, and robust CI/CD integration.*
