import paho.mqtt.client as mqttc
from random import randrange,uniform
import time
import ssl

AWSIOT_ENABLE = False
#change linux to a specific device ID like ix15 or cc6ulsbc-1, or device ID
MQTT_SUBTOPIC="iotdevice/linux/cli"
clientID = "iotdevice-linux"
mqtt_port = 8883


#stuff for my own mosquitto server 
broker = "52.80.119.72"
rootCA="./certs/ca.crt"
cert="./certs/client1.crt"
key="./certs/client1.key"

#aws stuff
#用自己CA和证书,在AWS上仍会碰到ssl.SSLCertVerificationError，因此最好是用官方的CA和证书，把自己的服务器那一句和AWS区分开了，不用的注释掉
#aws broker can be found in things endpoint
aws_broker="a1nl1xxmre4mok.ats.iot.cn-north-1.amazonaws.com.cn"
aws_rootCA="./aws_certs/AmazonRootCA1.pem"
aws_cert="./aws_certs/17f000a56e4ecf9510dd5d5fa153ca8877d8f727865e2bf7b01722827cf47b04-certificate.pem.crt"
aws_key="./aws_certs/17f000a56e4ecf9510dd5d5fa153ca8877d8f727865e2bf7b01722827cf47b04-private.pem.key"

#callback define
def on_connect(mosq, obj, rc):
    print("connecting to broker "+str(broker)+":"+str(port))
    print("cacert =",rootCA)
    mqttc.subscribe(MQTT_SUBTOPIC, 0)

def on_message(mosq, obj, msg):
	print ("Topic: " + str(msg.topic))
	print ("QoS: " + str(msg.qos))
	print ("Payload: " + str(msg.payload))

def on_subscribe(mosq, obj, mid, granted_qos):
    print("Subscribed to Topic: " + 
	MQTT_SUBTOPIC + " with QoS: " + str(granted_qos))

#prepare data
#data can either comes from true sensor, or just a random fake one
#temp_randNumber = uniform(20.0,21.0)
#hum_randNumber = uniform(45.0,46.0)


#main process start here
#Initialize a mqtt client
mqtt_client = mqttc.Client(clientID)


# Assign event callbacks
mqtt_client.on_message = on_message
mqtt_client.on_connect = on_connect
mqtt_client.on_subscribe = on_subscribe



#Connect to my own mosquitto
##mqtt_client.tls_set("certs/ca.crt","certs/client1.crt","certs/client1.key")
mqtt_client.tls_set(ca_certs=rootCA, certfile=cert, keyfile=key, cert_reqs=ssl.CERT_REQUIRED, tls_version=ssl.PROTOCOL_TLSv1_2, ciphers=None)
mqtt_client.connect(broker, port=mqtt_port, keepalive=60)
#mqtt_client.loop_start()
time.sleep(20)
mqtt_client.loop_stop()
print("quitting mqtt connection")
# Continue monitoring the incoming messages for subscribed topic
#mqtt_client.loop_forever()


#while True:
#    temp_randNumber = uniform(20.0,21.0)
#    mqtt_client.publish("demo/temperature",temp_randNumber)
#    print("Just published" + str(temp_randNumber) + " to Topic: demo/temperature")
#    time.sleep(10)

#doing awsiot part here
if AWSIOT_ENABLE == True:
  aws_mqtt_client = mqttc.Client(clientID)
  # Assign event callbacks
  aws_mqtt_client.on_message = on_message
  aws_mqtt_client.on_connect = on_connect
  aws_mqtt_client.on_subscribe = on_subscribe
  aws_mqtt_client.tls_set(ca_certs=aws_rootCA, certfile=aws_cert, keyfile=aws_key, cert_reqs=ssl.CERT_REQUIRED, tls_version=ssl.PROTOCOL_TLSv1_2, ciphers=None)
  aws_mqtt_client.connect(aws_broker, port=mqtt_port, keepalive=60)
#  aws_mqtt_client.publish("demo/temperature",temp_randNumber, qos=1)
#  aws_mqtt_client.loop_forever


