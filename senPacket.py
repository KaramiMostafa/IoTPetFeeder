import json

class senPacket(object):
    def __init__(self):
        self.senml = {}

    def toJson(self):
        jsonFile = json.dumps(self.senml)
        return jsonFile

    def toDict(self):
        return self.senml

    def setValues(self, weight, bn, bt):
        self.senml = {
            'bn': bn,
            'bt': bt,
            'e': [
                {'n': 'weight', 'u': 'grams', 'v': weight}
            ]}
        return True
