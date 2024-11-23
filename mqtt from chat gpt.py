<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MQTT Web Client</title>
    <script src="https://unpkg.com/mqtt/dist/mqtt.min.js"></script>
</head>
<body>
    <h1>MQTT Web Client</h1>
    <div>
        <p>Status: <span id="status">Disconnected</span></p>
        <p>Messages:</p>
        <ul id="messages"></ul>
    </div>

    <script>
        // Broker details
        const brokerUrl = "wss://14c25b0e91f540059e4503c11ccfc962.s1.eu.hivemq.cloud:8884/mqtt"; // WebSocket secure URL
        const options = {
            username: "mqtt_publish_user", // Your HiveMQ username
            password: "your-password-here", // Your HiveMQ password
            clientId: "web-client-" + Math.random().toString(16).substring(2, 8), // Unique client ID
            clean: true // Start with a clean session
        };

        // Connect to the broker
        const client = mqtt.connect(brokerUrl, options);

        // Connection event handlers
        const statusElement = document.getElementById("status");
        const messagesElement = document.getElementById("messages");

        client.on("connect", () => {
            statusElement.textContent = "Connected";
            console.log("Connected to broker");

            // Subscribe to a topic
            client.subscribe("my/topic/watts", (err) => {
                if (err) {
                    console.error("Subscription error:", err);
                } else {
                    console.log("Subscribed to topic");
                }
            });

            // Publish a test message (optional)
            client.publish("my/topic/watts", "Hello from HTML!");
        });

        client.on("message", (topic, payload) => {
            console.log(`Received message on ${topic}: ${payload.toString()}`);
            const li = document.createElement("li");
            li.textContent = `Topic: ${topic}, Message: ${payload}`;
            messagesElement.appendChild(li);
        });

        client.on("error", (err) => {
            console.error("Connection error:", err);
            statusElement.textContent = "Error";
        });

        client.on("close", () => {
            console.log("Disconnected");
            statusElement.textContent = "Disconnected";
        });
    </script>
</body>
</html>
