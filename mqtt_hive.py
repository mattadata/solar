# push from terminal app to Rpi from Terminal
# scp /Users/mattangelo/Documents/solar/mqtt_hive.py root@192.168.1.244:/home/root/

import asyncio
import signal
import gmqtt
import json
import math
#import logging
#logging.basicConfig(level=logging.DEBUG)

BROKER_ADDRESS_READ = '192.168.1.244'
KEEPALIVE_TOPIC = 'R/b827eb3be7e4/keepalive'
PV_WATTS_TOPIC = 'N/b827eb3be7e4/system/0/Dc/Pv/Power'
SOC_TOPIC = 'N/b827eb3be7e4/system/0/Dc/Battery/Soc'
BATTERY_VOLTS_TOPIC = 'N/b827eb3be7e4/system/0/Dc/Battery/Voltage'
DC_LOAD_A = 'N/b827eb3be7e4/solarcharger/288/Dc/0/Current'
DC_LOAD_V = 'N/b827eb3be7e4/solarcharger/288/Dc/0/Voltage'
#SHUNT = 'N/b827eb3be7e4/system/0/Batteries'        #old way. worked, but didn't update as frequent
SHUNT  = 'N/b827eb3be7e4/system/0/Dc/Battery/Power' #new way seems to update quicker
TIMETOGO = 'N/b827eb3be7e4/system/0/Dc/Battery/TimeToGo' #number of seconds of battery life left based on current solar input

#hiveMQ
BROKER_ADDRESS_PUBLISH = '14c25b0e91f540059e4503c11ccfc962.s1.eu.hivemq.cloud'
BROKER_PORT = 8883  # Secure MQTT port
PUBLISH_USERNAME = 'mqtt_publish_user'
PUBLISH_PASSWORD = 'UR9XVEXA*%X*4k'

PUBLISH_TOPIC           = 'my/topic/watts'
PUBLISH_TOPIC_SOC       = 'my/topic/soc'
PUBLISH_TOPIC_BAT_V     = 'my/topic/bat_v'
PUBLISH_TOPIC_LOAD_A    = 'my/topic/load_a'
PUBLISH_TOPIC_BAT_POWER = 'my/topic/battery_power'
PUBLISH_TIME_TO_GO      = 'my/topic/time_to_go'
KEEPALIVE_INTERVAL = 55  # seconds


STOP = asyncio.Event()

def on_connect_read(client, flags, rc, properties):
    print('Connected to read broker')
    client.subscribe(PV_WATTS_TOPIC)
    client.subscribe(SOC_TOPIC)
    client.subscribe(BATTERY_VOLTS_TOPIC)
    client.subscribe(SHUNT)
    client.subscribe(TIMETOGO)
def on_connect_publish(client, flags, rc, properties):
    print('Connected to HiveMQ broker')

def on_message(client, topic, payload, qos, properties):
    if topic == PV_WATTS_TOPIC:
        try:
            data = json.loads(payload.decode('utf-8'))  # Decode the payload from bytes to string and parse JSON
            power_value = float(data.get('value', 0))  # Extract the 'value' field and convert to float
            truncated_value = int(power_value)
            publish_client.publish(PUBLISH_TOPIC, str(truncated_value), qos=0, retain=True)
            print(f"Received Watts: {data}, Published: {truncated_value}")
        except (ValueError, json.JSONDecodeError) as e:
            print(f"Invalid payload: {payload}, Error: {e}")
    elif topic == SOC_TOPIC:
        try:
            data = json.loads(payload.decode('utf-8'))  # Decode the payload from bytes to string and parse JSON
            soc_value = float(data.get('value', 0))  # Extract the 'value' field and convert to float
            truncated_value = round(soc_value, 3)
            publish_client.publish(PUBLISH_TOPIC_SOC, str(truncated_value), qos=0, retain=True)
            print(f"Received SOC: {data}, Published: {truncated_value}")
        except (ValueError, json.JSONDecodeError) as e:
            print(f"Invalid payload: {payload}, Error: {e}")
    elif topic == BATTERY_VOLTS_TOPIC:
        try:
            data = json.loads(payload.decode('utf-8'))  # Decode the payload from bytes to string and parse JSON
            bat_v = float(data.get('value', 0))  # Extract the 'value' field and convert to float
            bat_v = round(bat_v,2)
            publish_client.publish(PUBLISH_TOPIC_BAT_V, str(bat_v), qos=0, retain=True)
            print(f"Received Volts: {data}, Published: {bat_v}")
        except (ValueError, json.JSONDecodeError) as e:
            print(f"Invalid payload: {payload}, Error: {e}")
    elif topic == DC_LOAD_A:
        try:
            data = json.loads(payload.decode('utf-8'))  # Decode the payload from bytes to string and parse JSON
            load_a = float(data.get('value', 0))  # Extract the 'value' field and convert to float
            load_a = round(load_a,2)
            publish_client.publish(PUBLISH_TOPIC_LOAD_A, str(load_a), qos=0, retain=True)
            print(f"Received Amps: {data}, Published Load Amps: {load_a}")
        except (ValueError, json.JSONDecodeError) as e:
            print(f"Invalid payload: {payload}, Error: {e}")
    elif topic == SHUNT:
        try:
            data = json.loads(payload.decode('utf-8'))  # Decode the payload from bytes to string and parse JSON
            #battery_info = data["value"][0]
            #battery_power = round(float(battery_info.get("power", 0))  ,0)
            battery_power = float(data.get('value', 0))  # Extract the 'value' field and convert to float
            battery_power = round(battery_power,2)            
            publish_client.publish(PUBLISH_TOPIC_BAT_POWER, str(battery_power), qos=0, retain=True)
            print(f"Received B_power: {data}, Published battery power: {battery_power}")
        except (ValueError, json.JSONDecodeError) as e:
            print(f"Invalid payload: {payload}, Error: {e}")
    elif topic == TIMETOGO:
        try:
            data = json.loads(payload.decode('utf-8'))  # Decode the payload from bytes to string and parse JSON
            value = data.get('value')
            if value is None:
                formatted_time = "∞"  # Display infinity symbol if value is null
            else:
                # Convert the value to float, round, and process it
                time_to_go = round(float(value), 2)
    
                # Convert to hours and minutes
                hours = math.floor(time_to_go / 3600)  # Get the whole number of hours
                minutes = math.floor((time_to_go % 3600) / 60)  # Get the remaining minutes
    
                # Format the result
                formatted_time = f"{hours}h {minutes}m"
            publish_client.publish(PUBLISH_TIME_TO_GO, str(formatted_time), qos=0, retain=True) 
            print(f"Received TTGO: {data}, Published time to go: {formatted_time}")
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
    # Set Last Will directly using the will_message attribute --doesn't seem like it gets called
    will_message = gmqtt.Message(
        topic=PUBLISH_TIME_TO_GO,
        payload="Not Publishing!",
        qos=1,  # Quality of Service level (0, 1, or 2)
        retain=True  # Retain flag
    )
    publish_client = gmqtt.Client("publish-client-id",will_message=will_message)
    publish_client.on_connect = on_connect_publish
    publish_client.on_disconnect = on_disconnect



    # Set authentication
    publish_client.set_auth_credentials(PUBLISH_USERNAME, PUBLISH_PASSWORD)

    await read_client.connect(BROKER_ADDRESS_READ)
    # Connect to the HiveMQ Cloud broker
    await publish_client.connect(BROKER_ADDRESS_PUBLISH, port=BROKER_PORT, ssl=True)

    asyncio.create_task(keepalive_message(read_client))

    await STOP.wait()
    await read_client.disconnect()
    await publish_client.disconnect()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    for sig in ('SIGINT', 'SIGTERM'):
        loop.add_signal_handler(getattr(signal, sig), ask_exit)
    loop.run_until_complete(main())
    
