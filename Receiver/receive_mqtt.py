# -*- coding: utf-8 -*-
"""
Created on Mon Sep 13 23:45:08 2021

@author: Swapnil
"""

import paho.mqtt.client as mqtt
import base64

image_name = "error.jpg" #Default image name

def on_connect(client, userdata, rc, properties):
    print("Connect" + str(rc))
    client.subscribe("image") 
    client.subscribe("imageName")
    client.subscribe("cloudType")
    client.subscribe("battery")

def on_message(client, userdata, msg):
    global image_name
    print("Topic : ", msg.topic)
    
    if (msg.topic == "image"):
        f = open('images/'+image_name+'.jpg', "wb")
        #print("message : ", msg.payload)
        f.write(base64.b64decode(msg.payload))
        f.close()
    elif (msg.topic == "battery"):
        print("Battery Level : ", msg.payload.decode("utf-8"))
    elif (msg.topic == "cloudType"):
        print("Cloud Type : ", msg.payload.decode("utf-8"))
    elif (msg.topic == "imageName"):
        image_name = msg.payload.decode("utf-8")

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.username_pw_set("your_username", "your_pwd")
client.connect("your_broker_address", port, 60)

client.loop_forever()