import paho.mqtt.client as mqttc
import ssl


clientID = "iotdevice-test"
broker = "52.80.119.72"
mqtt_port = 8883

mqtt_client = mqttc.Client(clientID)
mqtt_client.tls_set("certs/ca.crt","certs/client1.crt","certs/client1.key")
#mqtt_client.tls_set(ca_certs=rootCA, certfile=cert, keyfile=key, cert_reqs=ssl.CERT_REQUIRED, tls_version=ssl.PROTOCOL_TLSv1_2, ciphers=None)
mqtt_client.connect(broker, port=mqtt_port, keepalive=60)

mqtt_client.publish("test/try","hiya", qos=1)


