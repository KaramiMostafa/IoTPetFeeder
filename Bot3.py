import paho.mqtt.client as mqtt
import json
import requests
import logging
import time
from telegram import Update
from telegram.ext import (
    Updater,
    CommandHandler,
    CallbackContext,
)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)
logger = logging.getLogger(__name__)

class botAppConfiguration(object):

    def __init__(self, type=None, fileName="Bot.json"):

        self.content = None
        self.rc_address = None
        self.client_id = None
        with open(fileName, "r") as jsonfile:
            self.content = json.load(jsonfile)
            self.rc_address = self.content["rc_address"]
            self.client_id = self.content["client_id"]


class Bot_Functions(object):

    def __init__(self):
        self.conf = botAppConfiguration()
        self.client_id = None
        self.Connected = False
        self.broker_address = None
        self.servo_url = None
        self.port = 1883
        self.rc_address = self.conf.rc_address
        self.client_id = self.conf.client_id
        self.client = mqtt.Client(self.client_id)
        self.ConfigBroker()
        self.chat_id = None
        self.context = None

#################################### Broker Configuration ####################################

    def ConfigBroker(self):
        print('Contacting Service Catalog...')
        while True:
            try:
                self.bi_raw = requests.get(self.rc_address + 'services')
                conf = json.loads(self.bi_raw.text)
                self.broker_address = conf['broker_address']
                self.port = conf['broker_port']
                self.subscribing_topic = conf['mqtt_listening_topic']
                self.servo_url = conf['servo_url']
                print ("Connected to %s" % (self.subscribing_topic))
                break
            except Exception as error:
                error = 'Oops something went wrong'
                print(error)
                time.sleep(5)
                pass

#################################### Bot Configuration ####################################

    def Start_bot(self, update, context):
        startText = "Welcome Dear {update.effective_user.first_name} *__*.\n" \
            'We are here to help you and your cat to have an easier world.' \
            '_Commands_:\n' \
            '/About to see detail of the project;\n' \
            '/Dispense to dispense food .\n' \
            '/Feeding_Process to collect weight sensor data.\n' \
            'Anyway, write /help to display this message again.\n' \

        update.message.reply_text(startText)


    def About_Project(self, update, context):
        text_detail = 'The cat feeder is designed to make life easier for you and your pet. It is IoT-based technology and includes a Weight sensor, Servo motor, and Raspberry pi.' \
            'Design, Development, Data & Modelling:\n \nAmirreza Tavakol - https://www.linkedin.com/in/amirreza-tavakol-092249173/ \n \nIrakliy Darzhaniya - https://www.linkedin.com/in/irakliy-darzhaniya1656a0100/ \n \nMostafa Karami - https://www.linkedin.com/in/mostafakarami/ \n \nSahand Hamzehei - www.linkedin.com/in/sahand-hamzehei \n \n\n\n' \
            'Programming Language - Python\n' \
            'Language - English\n' \
            'Age rating - 16+\n' \
            'Price - Free\n' \

        update.message.reply_text(text_detail)

    def Dispense(self, update, context):
        requests.post(self.servo_url + "BB1")
        text_turn_on = 'Device dispenced food'
        update.message.reply_text(text_turn_on)

#################################### Start MQTT ####################################

    def start(self, update: Update, context: CallbackContext) -> None:
        if self.client.is_connected:
            self.client.disconnect()
            self.client.loop_stop()
        self.chat_id = update.message.chat_id
        self.context = context
        print('Start connecting to Broker and subscribing to topics...')
        self.client.on_connect = self.myOnConnect
        self.client.on_message = self.myOnMessageReceived
        self.client.connect(self.broker_address, port=int(self.port))
        print ("Connected to broker, broker address: %s and subscribed to topic: %s" % (self.broker_address,self.subscribing_topic))
        self.client.subscribe(self.subscribing_topic, 0)
        self.client.loop_start()
        while not self.Connected:
            time.sleep(0.1)

    def myOnConnect(self, client, userdata, flags, rc):
        if rc == 0:
            print("connected to broker")
            self.Connected = True
        else:
            print("Connection Failed")
            self.Connected = False

    def myOnMessageReceived(self, client, userdata, msg):
        try:
            msg = json.loads(msg.payload)
            print("Message Received", " ", msg)
            weight = 0
            for x in msg["e"]:
                if x["n"] == "weight":
                    weight = x["v"]
                    response = "Feeder dispenced: "+str(weight)+" "+x["u"]
                    self.context.bot.send_message(self.chat_id,
                                                  text=response)

        except Exception as error:
            error = 'Oops something went wrong, incorrect packet'
            print(error)

#################################### Main Part ####################################

if __name__ == '__main__':

    # get Token data by consideration of the json due to the privacy 
    conf = json.load(open("Bot.json"))
    token = conf["token"]
    updater = Updater(token)
    dp = updater.dispatcher

    # Bot command running
    f = Bot_Functions()
    dp.add_handler(CommandHandler("start", f.Start_bot))
    dp.add_handler(CommandHandler("help", f.Start_bot))
    dp.add_handler(CommandHandler("About", f.About_Project))
    dp.add_handler(CommandHandler("Dispense", f.Dispense))
    dp.add_handler(CommandHandler("Feeding_Process", f.start))

    updater.start_polling()
    updater.idle()
