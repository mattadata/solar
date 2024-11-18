import asyncio
import signal
import gmqtt
import json

BROKER_ADDRESS_READ = '192.168.1.244'
#BROKER_ADDRESS_PUBLISH = 'localhost'
BROKER_ADDRESS_PUBLISH = 'test.mosquitto.org'
KEEPALIVE_TOPIC = 'R/b827eb3be7e4/keepalive'
PV_WATTS_TOPIC = 'N/b827eb3be7e4/system/0/Dc/Pv/Power'
SOC_TOPIC = 'N/b827eb3be7e4/system/0/Dc/Battery/Soc'
BATTERY_VOLTS_TOPIC = 'N/b827eb3be7e4/system/0/Dc/Battery/Voltage'
DC_LOAD_A = 'N/b827eb3be7e4/solarcharger/288/Dc/0/Current'
DC_LOAD_V = 'N/b827eb3be7e4/solarcharger/288/Dc/0/Voltage'
SHUNT = 'N/b827eb3be7e4/system/0/Batteries'

PUBLISH_TOPIC = 'my/topic/watts'
PUBLISH_TOPIC_SOC = 'my/topic/soc'
PUBLISH_TOPIC_BAT_V = 'my/topic/bat_v'
PUBLISH_TOPIC_LOAD_A = 'my/topic/load_a'
PUBLISH_TOPIC_BAT_POWER = 'my/topic/battery_power'
KEEPALIVE_INTERVAL = 55  # seconds

STOP = asyncio.Event()

def on_connect_read(client, flags, rc, properties):
    print('Connected to read broker')
    client.subscribe(PV_WATTS_TOPIC)
    client.subscribe(SOC_TOPIC)
    client.subscribe(BATTERY_VOLTS_TOPIC)
    client.subscribe(SHUNT)
def on_connect_publish(client, flags, rc, properties):
    print('Connected to publish broker')

def on_message(client, topic, payload, qos, properties):
    if topic == PV_WATTS_TOPIC:
        try:
            data = json.loads(payload.decode('utf-8'))  # Decode the payload from bytes to string and parse JSON
            power_value = float(data.get('value', 0))  # Extract the 'value' field and convert to float
            truncated_value = int(power_value)
            publish_client.publish(PUBLISH_TOPIC, str(truncated_value), qos=0, retain=True)
            print(f"Received: {data}, Published: {truncated_value}")
        except (ValueError, json.JSONDecodeError) as e:
            print(f"Invalid payload: {payload}, Error: {e}")
    elif topic == SOC_TOPIC:
        try:
            data = json.loads(payload.decode('utf-8'))  # Decode the payload from bytes to string and parse JSON
            soc_value = float(data.get('value', 0))  # Extract the 'value' field and convert to float
            truncated_value = int(soc_value)
            publish_client.publish(PUBLISH_TOPIC_SOC, str(truncated_value), qos=0, retain=True)
            print(f"Received: {data}, Published: {truncated_value}")
        except (ValueError, json.JSONDecodeError) as e:
            print(f"Invalid payload: {payload}, Error: {e}")
    elif topic == BATTERY_VOLTS_TOPIC:
        try:
            data = json.loads(payload.decode('utf-8'))  # Decode the payload from bytes to string and parse JSON
            bat_v = float(data.get('value', 0))  # Extract the 'value' field and convert to float
            bat_v = round(bat_v,2)
            publish_client.publish(PUBLISH_TOPIC_BAT_V, str(bat_v), qos=0, retain=True)
            print(f"Received: {data}, Published: {bat_v}")
        except (ValueError, json.JSONDecodeError) as e:
            print(f"Invalid payload: {payload}, Error: {e}")
    elif topic == DC_LOAD_A:
        try:
            data = json.loads(payload.decode('utf-8'))  # Decode the payload from bytes to string and parse JSON
            load_a = float(data.get('value', 0))  # Extract the 'value' field and convert to float
            load_a = round(load_a,2)
            publish_client.publish(PUBLISH_TOPIC_LOAD_A, str(load_a), qos=0, retain=True)
            print(f"Received: {data}, Published Load Amps: {load_a}")
        except (ValueError, json.JSONDecodeError) as e:
            print(f"Invalid payload: {payload}, Error: {e}")
    elif topic == SHUNT:
        try:
            data = json.loads(payload.decode('utf-8'))  # Decode the payload from bytes to string and parse JSON
            battery_info = data["value"][0]
            battery_power = round(float(battery_info.get("power", 0))  ,0)
                      #load_a = round(load_a,2)
            publish_client.publish(PUBLISH_TOPIC_BAT_POWER, str(battery_power), qos=0, retain=True)
            #print(f"Received: {data}, Published battery power: {battery_power}")
        except (ValueError, json.JSONDecodeError) as e:
            print(f"Invalid payload: {payload}, Error: {e}")
            
def on_disconnect(client, packet, exc=None):
    print('Disconnected')

def on_subscribe(client, mid, qos, properties):
    print('Subscribed to:', PV_WATTS_TOPIC)

async def keepalive_message(client):
    while not STOP.is_set():
        client.publish(KEEPALIVE_TOPIC, 'keepalive', qos=0)
        await asyncio.sleep(KEEPALIVE_INTERVAL)

def ask_exit(*args):
    STOP.set()

async def main():
    global publish_client

    # Client for reading
    read_client = gmqtt.Client("read-client-id")
    read_client.on_connect = on_connect_read
    read_client.on_message = on_message
    read_client.on_disconnect = on_disconnect
    read_client.on_subscribe = on_subscribe

    # Client for publishing
    publish_client = gmqtt.Client("publish-client-id")
    publish_client.on_connect = on_connect_publish

    await read_client.connect(BROKER_ADDRESS_READ)
    await publish_client.connect(BROKER_ADDRESS_PUBLISH, port=1883)

    asyncio.create_task(keepalive_message(read_client))

    await STOP.wait()
    await read_client.disconnect()
    await publish_client.disconnect()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    for sig in ('SIGINT', 'SIGTERM'):
        loop.add_signal_handler(getattr(signal, sig), ask_exit)
    loop.run_until_complete(main())
    