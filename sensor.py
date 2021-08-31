import paho.mqtt.client as mqtt
import time
import json
import requests
from senPacket import senPacket as snmsg
from random import randrange


class WeightSensorConfig(object):
    def __init__(self, type=None, fileName="sensor_conf.json"):
        self.details = None
        self.rc_address = None
        self.device_id = None
        with open(fileName, "r") as jsonfile:
            self.details = json.load(jsonfile)
            self.rc_address = self.details["rc_address"]
            self.device_id = self.details["device_id"]


class WeightSensor(object):
    def __init__(self):
        self.topic = None
        self.broker_address = ''
        self.port = 1883
        self.conf = WeightSensorConfig("sensor_conf.json")
        self.rc_address = self.conf.rc_address
        self.device_id = self.conf.device_id
        self.configureApp()
        self.topic = self.get_sensor_topic()
        self.servo_topic = self.get_servo_topic()
        self.client = mqtt.Client(self.device_id+"_sensor")

    def configureApp(self):
        print('Contacting Service Catalog...')
        print(self.rc_address)
        while True:
            try:
                # Retrieve broker URL and Port of mqtt broker
                bi_raw = requests.get(self.rc_address + 'services')
                # print(bi_raw)
                conf = json.loads(bi_raw.text)
                # Set the broker URL and Port
                self.broker_address = conf['broker_address']
                self.port = conf['broker_port']
                break
            except Exception as e:
                # Retry to reconnect in 30 seconds
                print(e)
                time.sleep(5)
                pass

    def on_disconnect(self, client, userdata, rc):
        if rc != 0:
            self.isConnected = False
            print("Unexpected disconnection.")

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print("connected to broker")
            self.isConnected = True
        else:
            print("Connection Failed")

    def start(self):
        print('Connecting to Broker and starting transmittion')
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        self.client.on_message = self.on_message
        self.client.connect(self.broker_address, port=int(self.port))
        print("subscribing to servo topic: " + self.servo_topic)
        self.client.subscribe(self.servo_topic, 0)
        self.client.loop_forever()

    def on_message(self, client, userdata, msg):
        try:
            msg = json.loads(msg.payload)
            print(msg)
            if msg == 1:
                print(msg)
                self.publish_sensor_reading()

        except Exception as e:
            print(e)
            print("incorrect packet")

    def publish_sensor_reading(self):
        print("Reading weight sensor values...")
        time.sleep(1)
        msg = snmsg()
        msg.setValues(weight=randrange(50),
                      bn=self.device_id,
                      bt=int(time.time()))
        self.client.publish(self.topic, msg.toJson())
        print("published ", msg)

    def get_sensor_topic(self):
        print("getting publishing topic...")
        while True:
            try:
                raw = requests.get(self.rc_address +
                                   'device/' + self.device_id)
                res = json.loads(raw.text)
                if res:
                    return res["sensor_topic"]
                else:
                    pass
            except Exception as e:
                print(e)
                pass

    def get_servo_topic(self):
        print("getting servo action topic...")
        while True:
            try:
                raw = requests.get(self.rc_address +
                                   'device/' + self.device_id)
                res = json.loads(raw.text)
                if res:
                    return res["servo_topic"]
                else:
                    pass
            except Exception as e:
                print(e)
                pass

    def disconnect(self):
        self.client.disconnect()
        self.client.loop_stop()
        print("\nConnection Closed")


if __name__ == '__main__':

    sensorapp = WeightSensor()
    sensorapp.start()
