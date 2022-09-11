from http import client
import paho.mqtt.client as mqtt
import time
import threading
import ssl
import logging
#import thingsboard_objects as Things
import random
import datetime
logging.basicConfig(level=logging.INFO)

#define iotgateway itself as group name
groupid="iotgateway1"

# Certs define
AWS_ROOTCA = "./aws_certs/AmazonRootCA1.pem"
AWS_CERT = "./aws_certs/17f000a56e4ecf9510dd5d5fa153ca8877d8f727865e2bf7b01722827cf47b04-certificate.pem.crt"
AWS_KEY = "./aws_certs/17f000a56e4ecf9510dd5d5fa153ca8877d8f727865e2bf7b01722827cf47b04-private.pem.key"
AWS_ENDPOINT = "a1nl1xxmre4mok.ats.iot.cn-north-1.amazonaws.com.cn"

MY_CA = "./certs/ca.crt"
MY_CERT = "./certs/client1.crt"
MY_KEY = "./certs/client1.key"
MY_BROKER = "52.80.119.72"

#define end device that will managed by gateway
my_devices = [{"name": "deivce1", "deviceid": "0001", "type": "type1"},{"name": "deivce2", "deviceid": "0002", "type": "type2"}]
  

init_time = time.time()


def Connect(client, broker, port, cacert, certfile, keyfile, device_type, keepalive, run_forever=False):
    connflag = False
    delay = 5
    print("connecting ",client)
    badcount = 0  # counter for bad connection attempts
    while not connflag:
        print(logging.info("connecting to broker " + str(broker)))
        #print("connecting to broker "+str(broker)+":"+str(port))
        #print("cacert =",cacert)
        #print("certfile = ",certfile)
        print("Attempts ", str(badcount))
        time.sleep(2)
        try:
            #client.username_pw_set(token)
            #client.tls_set(ca_certs=aws_rootCA, certfile=aws_cert, keyfile=aws_key, cert_reqs=ssl.CERT_REQUIRED, tls_version=ssl.PROTOCOL_TLSv1_2, ciphers=None)
            client.tls_set(ca_certs=cacert, certfile=certfile, keyfile=keyfile, cert_reqs=ssl.CERT_REQUIRED, tls_version=ssl.PROTOCOL_TLSv1_2, ciphers=None)
            client.connect(broker, port, keepalive)
            connflag = True

        except:
            client.badconnection_flag = True
            logging.info("connection failed " + str(badcount))
            badcount += 1
            if badcount >= 3 and not run_forever:
                return -1
                raise SystemExit  # give up

    return 0


def wait_for(client, msgType, period=1, wait_time=20, running_loop=False):
    """Will wait for a particular event gives up after period*wait_time, Default=10
seconds.Returns True if succesful False if fails"""
    # running loop is true when using loop_start or loop_forever
    client.running_loop = running_loop  #
    wcount = 0
    while True:
        logging.info("waiting" + msgType)
        if msgType == "CONNACK":
            if client.on_connect:
                if client.connected_flag:
                    return True
                if client.bad_connection_flag:  #
                    return False

        if msgType == "SUBACK":
            if client.on_subscribe:
                if client.suback_flag:
                    return True
        if msgType == "MESSAGE":
            if client.on_message:
                if client.message_received_flag:
                    return True
        if msgType == "PUBACK":
            if client.on_publish:
                if client.puback_flag:
                    return True

        if not client.running_loop:
            client.loop(.01)  # check for messages manually
        time.sleep(period)
        wcount += 1
        if wcount > wait_time:
            print("return from wait loop taken too long")
            return False
    return True


def client_loop(client, broker, port, cacert, certfile, keyfile, deviceid, device_type, loop_function=None, keepalive=300,
                loop_delay=10, run_forever=False):
    """runs a loop that will auto reconnect and subscribe to topics
    pass topics as a list of tuples. You can pass a function to be
    called at set intervals determined by the loop_delay
    """
    client.run_flag = True
    client.broker = broker
    
    print("running loop ")
    print("device id is ", deviceid)
    client.reconnect_delay_set(min_delay=1, max_delay=12)

    while client.run_flag:  # loop forever

        if client.bad_connection_flag:
            break
        if not client.connected_flag:
            print("Connecting to " + broker)
            if Connect(client, broker, port, cacert, certfile, keyfile, device_type, keepalive, run_forever) != -1:
                if not wait_for(client, "CONNACK"):
                    client.run_flag = False  # break no connack
            else:  # connect fails
                client.run_flag = False  # break
                print("quitting loop for  broker ", broker)

        client.loop(0.01)

        if client.connected_flag and loop_function:  # function to call
            loop_function(client, deviceid, loop_delay)  # call function ,ie pub

    time.sleep(1)
    print("disconnecting from", broker)
    if client.connected_flag:
        client.disconnect()
        client.connected_flag = False


def on_log(client, userdata, level, buf):
    print(buf)


#def on_message(client, userdata, message):
#    time.sleep(1)
#    print("message received", str(message.payload.decode("utf-8")))


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        client.connected_flag = True  # set flag
        time.sleep(2)
        for c in clients:
            #print("connected ok")
            if client == c["client"]:
                if c["type"] != "":
                    sub_topic = "demo/"+groupid+"/"+c["type"]
                    client.subscribe(sub_topic)

                    print("connected OK",c["name"],c["deviceid"],c["client_id"],"type is", c["type"], "subscribe to", sub_topic)
    else:
        print("Bad connection Returned code=", rc)
        client.loop_stop()


def on_disconnect(client, userdata, rc):
    client.connected_flag = False  # set flag
    # print("client disconnected ok")


def on_publish(client, userdata, mid):
    print("In on_pub callback mid= ", mid)
    print("client is", client)


def pub(client, deviceid, loop_delay):
    if deviceid == "0001":
        print("0001 device matched, you can put function here")
        pub_topic = "demo/"+groupid+"/"+deviceid
    
    if deviceid == "0002":
        print("0002 device matched, you can put function here")
        pub_topic = "demo/"+groupid+deviceid

    rmd_current = round(random.uniform(0.6, 50.0), 2)
    rmd_pressure = round(random.uniform(0.6, 50.0), 2)
    global init_time
    if time.time() - init_time >= 3600:
        rmd_mnc = round(random.uniform(5.0, 30.0), 2)
        rmd_sdc = round(random.random(), 2)
        rmd_mnp = round(random.uniform(5.0, 30.0), 2)
        rmd_sdp = round(random.random(), 2)

        client.publish(pub_topic,
                       '{"Current": "%s","Pressure": "%s","Str": "12341","Stp": "12340"}' % (rmd_current, rmd_pressure))
        client.publish(pub_topic,
                       '{"MnC": "%s", "SdC": "%s", "Str": "2554","Stp": "2554","MnP": "%s", "SdP": "%s"}' % (rmd_mnc, rmd_sdc, rmd_mnp, rmd_sdp))
        print("one hour reached, publish to %s done!" % pub_topic)
        init_time = time.time()
    else:
        client.publish(pub_topic, 
                       '{"Current": "%s","Pressure": "%s"}' % (rmd_current, rmd_pressure))
        print("publish to %s done!" % pub_topic)
    print(datetime.datetime.now())
    time.sleep(loop_delay)
    pass


def Create_connections():
    for i in range(n_clients):
        cname = "client" + str(i)+"_"
        t = int(time.time())
        client_id = cname + str(t)  # create unique client_id
        client = mqtt.Client(client_id)  # create new instance
        clients[i]["client"] = client
        clients[i]["client_id"] = client_id
        clients[i]["cname"] = cname
        #clients[i]["index"] = i
        broker = clients[i]["broker"]
        port = clients[i]["port"]
        cacert = clients[i]["cacert"]
        certfile = clients[i]["certfile"]
        keyfile = clients[i]["keyfile"]
        deviceid = clients[i]["deviceid"]
        device_type = clients[i]["type"]
        #token = clients[i]["token"]
        client.on_connect = on_connect
        client.on_disconnect = on_disconnect
        client.on_publish = on_publish
        #client.on_message = on_message
        t = threading.Thread(target=client_loop, args=(client, broker, port, cacert, certfile, keyfile, deviceid, device_type, pub, 300))
        threads.append(t)
        t.start()


if __name__ == '__main__':

    things_location = input("What MQTT broker platform are you working with (awsiot/mosquitto)? ")

    if things_location == "awsiot":
        #type_install = 'thingboard.demo:8080'
        broker = AWS_ENDPOINT
        cacert = AWS_ROOTCA
        certfile = AWS_CERT
        keyfile = AWS_KEY
    else:
        broker = MY_BROKER
        cacert = MY_CA
        certfile = MY_CERT
        keyfile = MY_KEY
 
    #clients[index] will append name and topic, so we can only define topic in my_devices
    #index start from 0
    clients = []
    for device in my_devices:
    #    device_info = {"broker": broker, "port": 1883, "name": device["name"], "deviceid": device["deviceid"], "type": device["type"]}
        device_info = {"broker": broker, "port": 8883, "cacert": cacert, "certfile": certfile, "keyfile": keyfile, "name": device["name"], "deviceid": device["deviceid"], "type": device["type"]}
        clients.append(device_info)

    n_clients = len(clients)
    mqtt.Client.connected_flag = False  # create flag in class
    mqtt.Client.bad_connection_flag = False  # create flag in class

    threads = []
    print("Creating Connections ")
    no_threads = threading.active_count()
    print("current threads =", no_threads)
    print("Publishing ")
    Create_connections()

    print("All clients connected ")
    no_threads = threading.active_count()
    print("current threads =", no_threads)
    print("starting main loop")
    try:
        while no_threads == 3:
            time.sleep(10)
            no_threads = threading.active_count()
            print("current threads =", no_threads)
            for c in clients:
                if not c["client"].connected_flag:
                    print("broker ", c["broker"], " is disconnected")

    except KeyboardInterrupt:
        print("ending")
        for c in clients:
            c["client"].run_flag = False
    time.sleep(10)