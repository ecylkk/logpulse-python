import json
import random
import time
import os
from datetime import datetime, timezone
from confluent_kafka import Producer

# Config from Environment (Default to local)
BOOTSTRAP = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'kafka:9092')
TOPIC = os.getenv('KAFKA_TOPIC', 'logs')

# Aiven SSL Paths
CA_PATH = os.getenv('KAFKA_CA_PATH', 'certs/ca.pem')
CERT_PATH = os.getenv('KAFKA_CERT_PATH', 'certs/service.cert')
KEY_PATH = os.getenv('KAFKA_KEY_PATH', 'certs/service.key')

# --- SRE SECRET INJECTION: Recreate certs from ENV if missing ---
def inject_certs():
    if not os.path.exists('certs'):
        os.makedirs('certs')
    
    envs = {
        'KAFKA_CA_CERT': CA_PATH,
        'KAFKA_SERVICE_CERT': CERT_PATH,
        'KAFKA_SERVICE_KEY': KEY_PATH
    }
    
    for env_name, file_path in envs.items():
        content = os.getenv(env_name)
        if content and not os.path.exists(file_path):
            with open(file_path, 'w') as f:
                f.write(content.strip())
            print(f"📡 Injected {file_path} from ENV var {env_name}")

inject_certs()

conf = {'bootstrap.servers': BOOTSTRAP}

# Add SSL if certificates exist
if os.path.exists(CA_PATH) and os.path.exists(CERT_PATH) and os.path.exists(KEY_PATH):
    print("🔐 Using Aiven SSL Authentication")
    conf.update({
        'security.protocol': 'SSL',
        'ssl.ca.location': CA_PATH,
        'ssl.certificate.location': CERT_PATH,
        'ssl.key.location': KEY_PATH,
    })
# Add SASL if Cloud Credentials provided (Legacy/Upstash)
elif os.getenv('KAFKA_API_KEY') and os.getenv('KAFKA_API_SECRET'):
    print("🔐 Using SASL Authentication")
    conf.update({
        'security.protocol': 'SASL_SSL',
        'sasl.mechanisms': 'SCRAM-SHA-256',
        'sasl.username': os.getenv('KAFKA_API_KEY'),
        'sasl.password': os.getenv('KAFKA_API_SECRET'),
    })

producer = Producer(conf)
levels = ['INFO', 'INFO', 'INFO', 'WARN', 'ERROR']
services = ['auth-service', 'payment-gateway', 'order-engine', 'user-api', 'cache-layer']

print(f'🚀 Log Producer started (Target: {BOOTSTRAP})...')

while True:
    log_data = {
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'level': random.choice(levels),
        'service': random.choice(services),
        'latency_ms': round(random.uniform(2, 120), 1),
        'msg': f'Heartbeat #{random.randint(1, 9999)}'
    }
    log_str = json.dumps(log_data)
    producer.produce(TOPIC, value=log_str)
    producer.flush()
    print(f'📤 {log_str}')
    time.sleep(1)
