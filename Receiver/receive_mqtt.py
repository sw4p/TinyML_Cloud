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
        f = open(image_name, "wb")  #there is a output.jpg which is different
        f.write(base64.b64decode(msg.payload))
        f.close()
    elif (msg.topic == "battery"):
        print("Battery Level : ", msg.payload)
    elif (msg.topic == "cloudType"):
        print("Cloud Type : ", msg.payload)
    elif (msg.topic == "imageName"):
        image_name = msg.payload

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.username_pw_set("kukgfblp", "Ti0MEQ-43WEU")
client.connect("m24.cloudmqtt.com", 15462, 60)

client.loop_forever()