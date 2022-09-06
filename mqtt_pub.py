import paho.mqtt.client as mqtt
from random import randrange,uniform
import time

mqttBroker = "broker-cn.emqx.io"
client = mqtt.Client("Test1")
client.connect(mqttBroker)

while True:
    randNumber = uniform(20.0,21.0)
    client.publish("/temperature/test",randNumber)
    print("Just published" + str(randNumber) + " to Topic: /temperature/test")
    time.sleep(10)