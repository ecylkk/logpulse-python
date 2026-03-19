import json
import os
from confluent_kafka import Consumer
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
from collections import deque
import logging

logging.basicConfig(level=logging.ERROR) # suppress verbose debug logs


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

# --- PREMIUM SRE LOG DASHBOARD (For Interview Wow Factor) ---
recent_logs = deque(maxlen=50) # Maintain last 50 logs in memory
stats = {"total": 0, "errors": 0}

HTML_DASHBOARD = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>LogPulse Command Center</title>
    <style>
        body { background-color: #0f172a; color: #f8fafc; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 40px 20px; }
        .header { text-align: center; border-bottom: 2px solid #1e293b; padding-bottom: 30px; margin-bottom: 30px; }
        .header h1 { margin: 0; color: #38bdf8; font-size: 3em; letter-spacing: 2px; text-transform: uppercase; text-shadow: 0 0 20px rgba(56,189,248,0.5); }
        .header p { color: #94a3b8; font-size: 1.2em; margin-top: 10px; }
        .stats { display: flex; justify-content: center; gap: 40px; margin-bottom: 40px; }
        .stat-box { background: #1e293b; padding: 20px 50px; border-radius: 12px; border: 1px solid #334155; text-align: center; box-shadow: 0 10px 15px -3px rgba(0,0,0,0.5); width: 200px; }
        .stat-box h2 { margin: 0; font-size: 1.1em; color: #94a3b8; text-transform: uppercase; letter-spacing: 1px; }
        .stat-box .value { font-size: 3em; font-weight: 800; margin-top: 10px; }
        .value.total { color: #10b981; }
        .value.errors { color: #ef4444; }
        .grid { display: flex; flex-direction: column; gap: 12px; max-width: 1000px; margin: 0 auto; height: 50vh; overflow-y: auto; padding-right: 10px; }
        .grid::-webkit-scrollbar { width: 8px; }
        .grid::-webkit-scrollbar-thumb { background: #334155; border-radius: 4px; }
        .log-entry { background: #1e293b; padding: 18px 24px; border-radius: 8px; border-left: 6px solid #3b82f6; display: flex; justify-content: space-between; align-items: center; box-shadow: 0 4px 6px rgba(0,0,0,0.2); transition: transform 0.2s; }
        .log-entry:hover { transform: translateX(5px); }
        .log-content { font-family: 'Courier New', Courier, monospace; font-size: 1.1em; color: #cbd5e1; }
        .log-service { font-weight: bold; color: #e2e8f0; margin-right: 15px; }
        .log-badge { padding: 4px 12px; border-radius: 20px; font-weight: bold; font-size: 0.85em; letter-spacing: 1px; }
        .log-entry.ERROR { border-left-color: #ef4444; }
        .log-entry.ERROR .log-badge { background: rgba(239, 68, 68, 0.2); color: #fca5a5; border: 1px solid rgba(239, 68, 68, 0.5); }
        .log-entry.INFO { border-left-color: #10b981; }
        .log-entry.INFO .log-badge { background: rgba(16, 185, 129, 0.2); color: #6ee7b7; border: 1px solid rgba(16, 185, 129, 0.5); }
        .log-entry.WARN { border-left-color: #f59e0b; }
        .log-entry.WARN .log-badge { background: rgba(245, 158, 11, 0.2); color: #fcd34d; border: 1px solid rgba(245, 158, 11, 0.5); }
        .pulse { animation: pulse 2s infinite; display: inline-block; }
        @keyframes pulse { 0% { opacity: 1; transform: scale(1); } 50% { opacity: 0.5; transform: scale(0.9); } 100% { opacity: 1; transform: scale(1); } }
    </style>
</head>
<body>
    <div class="header">
        <h1>LogPulse Command Center <span class="pulse">🔴</span></h1>
        <p>Live Distributed Streaming via Aiven Kafka Cloud</p>
    </div>
    <div class="stats">
        <div class="stat-box"><h2>Total Events</h2><div class="value total" id="val-total">0</div></div>
        <div class="stat-box"><h2>Critical Alerts</h2><div class="value errors" id="val-errors">0</div></div>
    </div>
    <div class="grid" id="log-container"></div>
    <script>
        async function fetchLogs() {
            try {
                const res = await fetch('/api/logs');
                const data = await res.json();
                document.getElementById('val-total').innerText = data.stats.total;
                document.getElementById('val-errors').innerText = data.stats.errors;
                
                const container = document.getElementById('log-container');
                container.innerHTML = '';
                data.logs.forEach(log => {
                    const div = document.createElement('div');
                    div.className = `log-entry ${log.level}`;
                    div.innerHTML = `
                        <div class="log-content">
                            <span class="log-service">[${log.service}]</span>
                            <span>${log.msg || 'System Alert Logged'}</span>
                        </div>
                        <div class="log-badge">${log.level}</div>
                    `;
                    container.appendChild(div);
                });
            } catch (e) { console.error(e); }
        }
        setInterval(fetchLogs, 1000);
        fetchLogs();
    </script>
</body>
</html>
"""

class HealthRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/api/logs':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            payload = {"stats": stats, "logs": list(recent_logs)[::-1]}
            self.wfile.write(json.dumps(payload).encode('utf-8'))
        else:
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(HTML_DASHBOARD.encode('utf-8'))
        
    def log_message(self, format, *args):
        pass # Suppress noisy HTTP logs in console

def run_health_server():
    port = int(os.environ.get('PORT', 8080))
    server = HTTPServer(('0.0.0.0', port), HealthRequestHandler)
    print(f'🌐 SRE UI Dashboard started on port {port}')
    server.serve_forever()

threading.Thread(target=run_health_server, daemon=True).start()

try:
    while True:
        msg = consumer.poll(1.0)
        if msg is None:
            continue
        if msg.error():
            print(f'❌ Kafka error: {msg.error()}')
            continue

        log = json.loads(msg.value().decode('utf-8'))
        stats["total"] += 1

        if log['level'] == 'ERROR':
            stats["errors"] += 1
            print(f'🚨 ALERT [{stats["errors"]} / {stats["total"]}]: {json.dumps(log)}')
        else:
            print(f'✅ OK ({stats["total"]}): [{log["level"]}] {log["service"]} - {log["msg"]}')
            
        recent_logs.append(log)
        
finally:
    consumer.close()


