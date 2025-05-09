#!/usr/bin/env python3

import paho.mqtt.client as mqtt #import the client1

import time
############
def on_message(client, userdata, message):
    print("message received " ,str(message.payload.decode("utf-8")))
    print("message topic=",message.topic)
    print("message qos=",message.qos)
    print("message retain flag=",message.retain)

def on_disconnect(client, userdata, rc):
    if rc != 0:
        print("Unexpected disconnection.")
########################################

#broker_address="192.168.0.1"
broker_address = "broker.mqtt.cool"
#broker_address="iot.eclipse.org"
print("creating new instance")
client = mqtt.Client() #create new instance

client.on_message=on_message #attach function to callback
client.connect(broker_address, 1883, 60)
client.subscribe("1TM")

print("Publishing message to topic","1TM")
client.publish("1TM","Hello world!", qos=1)

client.will_set("1TM", "Disconnected without calling disconnect")

client.on_disconnect = on_disconnect

client.loop_start() #start the loop
time.sleep(10) # wait
client.loop_stop() #stop the loop
