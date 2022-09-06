from pydoc import cli
import paho.mqtt.client as mqtt
import time

def on_message(client,userdata,message):
    print("Received message: ", str(message.payload.decode("utf-8")))

mqttBroker = "broker-cn.emqx.io"
client = mqtt.Client("smartphone")
client.connect(mqttBroker)

client.loop_start()
client.subscribe("/temperature/#")
client.on_message = on_message
time.sleep(30)
client.loop_stop()


