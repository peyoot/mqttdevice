#### discription
mqttdevice is a demo client device to publish & subscribe topics to a MQTT server like mosquitto or AWSIOT. This is part of awsiot demo.

#### folder structure
├── aws_certs                     the certs and keys from AWSIOT 
│   ├──AmazonRootCA1.pem
│   ├──XXX-certificates.pem.crt
│   ├──XXX-private.pem.key
|   
├── certs                         the certs and keys from your pki
│   ├── CA.crt
│   ├── thing1.crt
│   ├── thing1.key
| ...
├── awsiot.py
| ...
├── README.md
└── README-cn.md