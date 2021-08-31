import paho.mqtt.client as mqtt
import json
import cherrypy
import requests
import time


class servoAppConfiguration(object):
    def __init__(self, type=None, fileName="servo.json"):
        self.content = None
        self.rc_address = None
        self.dev_id = None
        with open(fileName, "r") as jsonfile:
            self.content = json.load(jsonfile)
            self.rc_address = self.content["rc_address"]
            self.dev_id = self.content["dev_id"]


class servoMqtt(object):

    def __init__(self):
        self.client_id = None
        self.Connected = False
        self.broker_address = None
        self.port = 1883
        self.conf = servoAppConfiguration()
        self.rc_address = self.conf.rc_address
        self.client_id = self.conf.dev_id
        self._confBroker()
        self.client = mqtt.Client(self.client_id+"_servo")

    def _confBroker(self):
        print('Contacting Service Catalog...')
        while True:
            try:
                bi_raw = requests.get(self.rc_address + 'services')
                conf = json.loads(bi_raw.text)
                self.broker_address = conf['broker_address']
                self.port = conf['broker_port']
                break
            except Exception as e:
                print(e)
                time.sleep(5)
                pass

    def _get_servo_topic(self, device_id):
        print("getting servo action topic...")
        print(device_id)
        while True:
            try:
                raw = requests.get(self.rc_address +
                                   'device/' + device_id)
                res = json.loads(raw.text)
                if res:
                    return res["servo_topic"]
                else:
                    pass
            except Exception as e:
                print(e)
                pass

    def _on_disconnect(self, client, userdata, rc):
        if rc != 0:
            self.isConnected = False
            print("Unexpected disconnection.")

    def _on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print("connected to broker")
            self.Connected = True
        else:
            print("Connection Failed")
            self.Connected = False

    def publish_turn_on(self, device_id):
        print('Connecting to Broker and subscribing to topics...')
        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect
        print("broker address: " + self.broker_address)
        self.client.connect(self.broker_address, port=int(self.port))
        self.client.loop_start()
        publishing_topic = self._get_servo_topic(device_id)
        print(publishing_topic)
        self.client.publish(publishing_topic, "1")
        print("published ")
        self.client.disconnect()
        self.client.loop_stop()


@cherrypy.expose
class servoWebservice(object):

    def __init__(self):
        pass

    def POST(self, *uri, **params):
        '''
        - /<device_id>

        '''
        serv = servoMqtt()
        serv.publish_turn_on(uri[0])
        return

    def _responsJson(self, result, success):
        tempJson = {'result': result, 'success': success}
        return json.dumps(tempJson)


if __name__ == '__main__':

    conf = {
        '/': {
            'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
            'tools.sessions.on': True
        }
    }
    cherrypy.tree.mount(servoWebservice(), '/servo', conf)
    cherrypy.server.socket_host = "0.0.0.0"
    cherrypy.server.socket_port = 8383
    cherrypy.engine.start()
    cherrypy.engine.block()
