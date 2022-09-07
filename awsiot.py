import paho.mqtt.client as mqttc
import ssl


clientID = "iotdevice-test"
broker = "52.80.119.72"
mqtt_port = 8883

rootCA="./certs/ca.crt"
cert="./certs/client1.crt"
key="./certs/client1.key"

#用自己CA和证书，仍会碰到ssl.SSLCertVerificationError，因此最好是用官方的CA和证书，把自己的服务器那一句和AWS区分开了，不用的注释掉

mqtt_client = mqttc.Client(clientID)

#Connect to my own mosquitto
##mqtt_client.tls_set("certs/ca.crt","certs/client1.crt","certs/client1.key")
#mqtt_client.tls_set(ca_certs=rootCA, certfile=cert, keyfile=key, cert_reqs=ssl.CERT_REQUIRED, tls_version=ssl.PROTOCOL_TLSv1_2, ciphers=None)
#mqtt_client.connect(broker, port=mqtt_port, keepalive=60)

#Connect to aws
aws_rootCA="./aws_certs/AmazonRootCA1.pem"
aws_cert="./aws_certs/17f000a56e4ecf9510dd5d5fa153ca8877d8f727865e2bf7b01722827cf47b04-certificate.pem.crt"
aws_key="./aws_certs/17f000a56e4ecf9510dd5d5fa153ca8877d8f727865e2bf7b01722827cf47b04-private.pem.key"
#aws broker a1nl1xxmre4mok.ats.iot.cn-north-1.amazonaws.com.cn
aws_broker="a1nl1xxmre4mok.ats.iot.cn-north-1.amazonaws.com.cn"
mqtt_client.tls_set(ca_certs=aws_rootCA, certfile=aws_cert, keyfile=aws_key, cert_reqs=ssl.CERT_REQUIRED, tls_version=ssl.PROTOCOL_TLSv1_2, ciphers=None)
mqtt_client.connect(aws_broker, port=mqtt_port, keepalive=60)


mqtt_client.publish("test/try","hiya", qos=1)


