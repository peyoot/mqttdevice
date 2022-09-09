from http import client
import paho.mqtt.client as mqtt
import time
import threading
import logging
#import thingsboard_objects as Things
import random
import datetime
logging.basicConfig(level=logging.INFO)


init_time = time.time()


def Connect(client, broker, port, keepalive, run_forever=False):
    connflag = False
    delay = 5
    print("connecting ",client)
    badcount = 0  # counter for bad connection attempts
    while not connflag:
        print(logging.info("connecting to broker " + str(broker)))
        # print("connecting to broker "+str(broker)+":"+str(port))
        print("Attempts ", str(badcount))
        time.sleep(2)
        try:
            #client.username_pw_set(token)
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


def client_loop(client, broker, port, keepalive=300, loop_function=None,
                loop_delay=10, run_forever=False):
    """runs a loop that will auto reconnect and subscribe to topics
    pass topics as a list of tuples. You can pass a function to be
    called at set intervals determined by the loop_delay
    """
    client.run_flag = True
    client.broker = broker
    print("running loop ")
    client.reconnect_delay_set(min_delay=1, max_delay=12)

    while client.run_flag:  # loop forever

        if client.bad_connection_flag:
            break
        if not client.connected_flag:
            print("Connecting to " + broker)
            if Connect(client, broker, port, keepalive, run_forever) != -1:
                if not wait_for(client, "CONNACK"):
                    client.run_flag = False  # break no connack
            else:  # connect fails
                client.run_flag = False  # break
                print("quitting loop for  broker ", broker)

        client.loop(0.01)

        if client.connected_flag and loop_function:  # function to call
            loop_function(client, loop_delay)  # call function

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
                if c["sub_topic"] != "":
                    client.subscribe(c["sub_topic"])

                    print("connected OK",c["name"],c["cname"],c["client_id"],c["sub_topic"])
    else:
        print("Bad connection Returned code=", rc)
        client.loop_stop()


def on_disconnect(client, userdata, rc):
    client.connected_flag = False  # set flag
    # print("client disconnected ok")


def on_publish(client, userdata, mid):
    print("In on_pub callback mid= ", mid)


def pub(client, loop_delay):

    rmd_current = round(random.uniform(0.6, 50.0), 2)
    rmd_pressure = round(random.uniform(0.6, 50.0), 2)
    global init_time
    if time.time() - init_time >= 3600:
        rmd_mnc = round(random.uniform(5.0, 30.0), 2)
        rmd_sdc = round(random.random(), 2)
        rmd_mnp = round(random.uniform(5.0, 30.0), 2)
        rmd_sdp = round(random.random(), 2)

        client.publish('v1/devices/me/telemetry',
                       '{"Current": "%s","Pressure": "%s","Str": "12341","Stp": "12340","AL1": "~","AL2": "~",'
                       '"AL3": "~","AL4": "~","AL5": "~","AL6": "~","AL7": "~","AL8": "~"}' % (rmd_current, rmd_pressure))
        client.publish('v1/devices/me/telemetry',
                       '{"MnC": "%s", "SdC": "%s", "Str": "2554","Stp": "2554", '
                       '"MnP": "%s", "SdP": "%s"}' % (rmd_mnc, rmd_sdc, rmd_mnp, rmd_sdp))

        init_time = time.time()
    else:
        client.publish('v1/devices/me/telemetry',
                       '{"Current": "%s","Pressure": "%s","Str": "12341","Stp": "12340","AL1": "~","AL2": "~",'
                       '"AL3": "~","AL4": "~","AL5": "~","AL6": "~","AL7": "~","AL8": "~"}' % (rmd_current, rmd_pressure))
    print(datetime.datetime.now())
    time.sleep(loop_delay)
    pass


def Create_connections():
    for i in range(n_clients):
        cname = "client" + str(i)
        t = int(time.time())
        client_id = cname + str(t)  # create unique client_id
        client = mqtt.Client(client_id)  # create new instance
        clients[i]["client"] = client
        clients[i]["client_id"] = client_id
        clients[i]["cname"] = cname
        #clients[i]["index"] = i
        broker = clients[i]["broker"]
        port = clients[i]["port"]
        #token = clients[i]["token"]
        client.on_connect = on_connect
        client.on_disconnect = on_disconnect
        client.on_publish = on_publish
        #client.on_message = on_message
        t = threading.Thread(target=client_loop, args=(client, broker, port, 300, pub))
        threads.append(t)
        t.start()


if __name__ == '__main__':

    things_location = input("What platform are you working with (awsiot/mosquitto)? ")

    if things_location == "awsiot":
        #type_install = 'thingboard.demo:8080'
        broker = 'a1nl1xxmre4mok.ats.iot.cn-north-1.amazonaws.com.cn'
    else:
        type_install = broker = '52.80.119.72'

    #header = Things.get_credentials(things_location)
    my_devices = [{"name": "deivce1", "sub_topic": "topic1"},{"name": "deivce2", "sub_topic": "topic2"}]
    #clients[index] will append name and topicy, so we can only define topic in my_devices
    #index start from 0
    clients = []
    for device in my_devices:
        device_info = {"broker": broker, "port": 1883, "name": device["name"], "sub_topic": device["sub_topic"]}
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