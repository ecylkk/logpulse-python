package com.logpulse;

import org.apache.kafka.clients.producer.KafkaProducer;
import org.apache.kafka.clients.producer.ProducerConfig;
import org.apache.kafka.clients.producer.ProducerRecord;
import org.apache.kafka.common.serialization.StringSerializer;

import java.util.Properties;
import java.util.Random;
import java.time.Instant;

public class ProducerApp {
    private static final String TOPIC = "logs";
    private static final String BOOTSTRAP_SERVERS = System.getenv().getOrDefault("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092");

    public static void main(String[] args) throws InterruptedException {
        Properties props = new Properties();
        props.put(ProducerConfig.BOOTSTRAP_SERVERS_CONFIG, BOOTSTRAP_SERVERS);
        props.put(ProducerConfig.KEY_SERIALIZER_CLASS_CONFIG, StringSerializer.class.getName());
        props.put(ProducerConfig.VALUE_SERIALIZER_CLASS_CONFIG, StringSerializer.class.getName());

        KafkaProducer<String, String> producer = new KafkaProducer<>(props);
        Random random = new Random();
        String[] levels = {"INFO", "INFO", "INFO", "WARN", "ERROR"};

        System.out.println("🚀 Log Producer started (connecting to " + BOOTSTRAP_SERVERS + ")...");

        try {
            while (true) {
                String level = levels[random.nextInt(levels.length)];
                String logEntry = String.format(
                    "{\"timestamp\":\"%s\", \"level\":\"%s\", \"msg\":\"System heartbeat check %d\"}",
                    Instant.now().toString(), level, random.nextInt(1000)
                );

                producer.send(new ProducerRecord<>(TOPIC, null, logEntry));
                System.out.println("📤 Sent: " + logEntry);
                Thread.sleep(1000);
            }
        } finally {
            producer.close();
        }
    }
}
