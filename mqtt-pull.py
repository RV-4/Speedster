#!/usr/bin/env python3

import paho.mqtt.client as mqtt


# This is the Subscriber

def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    client.subscribe("1TM")

def on_message(client, userdata, msg):
    tag,value = msg.payload.decode() .split(",")
    print("tag = ", tag, "  value = ", value)
    if tag == "IAS":
        print("IAS: ", value)
    elif tag == "Hobbs":
        print("Hobbs: ", value)
    elif tag == "Smoke":
        print("Smoke Tank Level:", value)
    elif tag == "Fuel":
        print("Fuel Remaining: ", value)
    elif tag == "Flaps":
        print("Flaps at: ", value)
#        client.disconnect()


client = mqtt.Client()
client.connect("broker.mqtt.cool", 1883, 60)


client.on_connect = on_connect
client.on_message = on_message

client.loop_forever()
