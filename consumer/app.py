import json
import os
from confluent_kafka import Consumer
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading


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

conf = {
    'bootstrap.servers': BOOTSTRAP,
    'group.id': os.getenv('KAFKA_GROUP_ID', 'log-analyzer-group'),
    'auto.offset.reset': 'earliest'
}

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

consumer = Consumer(conf)
consumer.subscribe([TOPIC])

print(f'🔍 Log Analyzer started (Listening: {BOOTSTRAP})...')

# DUMMY HTTP SERVER FOR RENDER HEALTH CHECK
class HealthRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(b"LogPulse Analyzer is actively streaming logs from Aiven Kafka!")
        
def run_health_server():
    port = int(os.environ.get('PORT', 8080))
    server = HTTPServer(('0.0.0.0', port), HealthRequestHandler)
    print(f'🌐 Render Health server started on port {port}')
    server.serve_forever()

threading.Thread(target=run_health_server, daemon=True).start()

error_count = 0
total = 0

try:
    while True:
        msg = consumer.poll(1.0)
        if msg is None:
            continue
        if msg.error():
            print(f'❌ Kafka error: {msg.error()}')
            continue

        log = json.loads(msg.value().decode('utf-8'))
        total += 1

        if log['level'] == 'ERROR':
            error_count += 1
            print(f'🚨 ALERT [{error_count} errors / {total} total]: {json.dumps(log)}')
        else:
            print(f'✅ OK ({total}): [{log["level"]}] {log["service"]} - {log["msg"]}')
finally:
    consumer.close()

