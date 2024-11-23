import asyncio
import signal
import gmqtt
import json
import math

# HiveMQ Cloud Broker Details
BROKER_ADDRESS_PUBLISH = '14c25b0e91f540059e4503c11ccfc962.s1.eu.hivemq.cloud'
BROKER_PORT = 8883  # Secure MQTT port
PUBLISH_USERNAME = 'mqtt_publish_user'
PUBLISH_PASSWORD = 'UR9XVEXA*%X*4k'

PUBLISH_TOPIC = 'my/topic/watts'
KEEPALIVE_INTERVAL = 55  # seconds

STOP = asyncio.Event()

def on_connect_publish(client, flags, rc, properties):
    print('Connected to publish broker')

def on_disconnect(client, packet, exc=None):
    print('Disconnected')

async def keepalive_message(client):
    while not STOP.is_set():
        client.publish(PUBLISH_TOPIC, 'keepalive', qos=0)
        await asyncio.sleep(KEEPALIVE_INTERVAL)

def ask_exit(*args):
    STOP.set()

async def main():
    global publish_client

    # Client for publishing
    publish_client = gmqtt.Client("publish-client-id")
    publish_client.on_connect = on_connect_publish
    publish_client.on_disconnect = on_disconnect

    # Set authentication
    publish_client.set_auth_credentials(PUBLISH_USERNAME, PUBLISH_PASSWORD)

    # Connect to the HiveMQ Cloud broker
    await publish_client.connect(BROKER_ADDRESS_PUBLISH, port=BROKER_PORT, ssl=True)

    # Publish keepalive messages
    asyncio.create_task(keepalive_message(publish_client))

    await STOP.wait()
    await publish_client.disconnect()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    for sig in ('SIGINT', 'SIGTERM'):
        loop.add_signal_handler(getattr(signal, sig), ask_exit)
    loop.run_until_complete(main())
