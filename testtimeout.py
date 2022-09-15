import func_timeout

@func_timeout.func_set_timeout(5)
def askMQTTPlatform():
    return input("What MQTT broker platform are you working with (awsiot/mosquitto)? ")

try:
    things_location = askMQTTPlatform()
except func_timeout.exceptions.FunctionTimedOut as e:
    things_location = 'mosquitto'

print(things_location)
