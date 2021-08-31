import json
import logging
import os
import time

import paho.mqtt.client as mqtt
import requests

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(filename)s] [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)

class ThingSpeakConnector:
    is_connected = False

    def __init__(self, conf_file="ts_config.json"):
        self.logger = logging.getLogger("thing_speak_logger")
        self.is_connected = False
        self.broker_address = None
        self.port = None
        self.conf = self._load_init_conf(conf_file)
        self.rc_address = self.conf["rc_address"]
        self.client_id = self.conf["client_id"]
        self._fetch_service_conf()
        self.client = mqtt.Client(self.client_id)

    def _load_init_conf(self, file_name):
        if not os.path.exists(file_name):
            raise FileNotFoundError("No conf file")

        with open(file_name, "r") as fs:
            return json.load(fs)

    @property
    def service_url(self):
        return self.rc_address + 'services'

    def device_url(self, dev_id):
        return self.rc_address + 'device/' + dev_id

    def _fetch_service_conf(self):
        self.logger.info('Contacting Service Catalog...')
        while True:
            try:
                response = requests.get(self.service_url)
                self.conf = response.json()
                self.broker_address = self.conf['broker_address']
                self.port = self.conf['broker_port']
                self.subscribing_topic = self.conf['mqtt_listening_topic']
                break
            except Exception as e:
                self.logger.error("Can not fetch config:")
                self.logger.exception(e)
                time.sleep(5)
                pass

    def _on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            self.logger.info("connected to broker")
            self.is_connected = True
        else:
            self.logger.error("Connection Failed")
            self.is_connected = False

    def start(self):
        self.logger.info('Connecting to Broker and subscribing to topics...')
        self.client.on_connect = self._on_connect
        self.client.on_message = self.on_message
        self.logger.info("broker address: " + self.broker_address)
        self.client.connect(self.broker_address, port=int(self.port))
        self.logger.info("subscribing to the topic: " + self.subscribing_topic)
        self.client.subscribe(self.subscribing_topic, 0)
        self.client.loop_forever()
        while not self.is_connected:
            time.sleep(0.1)

    def fetch_publish_url(self, dev_id):
        self.logger.info('fetching thingspeak publishing url...')
        try:
            response = requests.get(self.device_url(dev_id))
            res = response.json()
            if res:
                return res["ts_url"]
            else:
                return None
        except Exception as e:
            self.logger.exception(e)

    def parse_weight_from_message(self, msg):
        weight = 0
        for x in msg["e"]:
            if x["n"] == "weight":
                weight = x["v"]
        return weight

    def on_message(self, client, userdata, msg):
        try:
            msg = json.loads(msg.payload)
            weight = self.parse_weight_from_message(msg)
            base_url = self.fetch_publish_url(msg["bn"])
            url = base_url + str(weight)
            response = requests.get(url)

            if response.status_code == 200:
                self.logger.info("published: ", msg)
            else:
                self.logger.error("failed to send")

        except Exception as e:
            self.logger.info(e)
            self.logger.info("incorrect packet")

    def disconnect(self):
        self.client.disconnect()
        self.client.loop_stop()
        self.logger.info("\nConnection Closed")


if __name__ == '__main__':
    tsc = ThingSpeakConnector()
    tsc.start()
