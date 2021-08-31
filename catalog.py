import json
import cherrypy
import sys
sys.path.insert(0, "../")


class serviceCatalogConfiguration(object):
    def __init__(self, fileName="catalog.json"):
        self.devices = None
        self.services = None
        with open(fileName, "r") as jsonfile:
            self.content = json.load(jsonfile)
            self.devices = self.content["devices"]
            self.services = self.content["services"]

    def get_device(self, dev_id):
        for dev in self.devices:
            print(dev)
            if dev["dev_id"] == dev_id:
                return dev
        return None

    def add_device(self, dev_id):
        pass

    def get_services(self):
        return self.services


@cherrypy.expose
class scWebservice(object):

    def __init__(self):
        self.sc = serviceCatalogConfiguration()
        pass

    def GET(self, *uri, **params):
        '''
        - GET: catalog/device/<device_id>
        - GET: catalog/services

        '''

        res = None
        try:
            if uri[0] == 'device' and len(uri) == 2:
                # Find device by type and id
                device_id = str(uri[1])
                res = self.sc.get_device(device_id)
            elif uri[0] == 'services':
                res = self.sc.get_services()
            else:
                res = None

        except Exception as e:
            res = str(e)

        if res:
            return json.dumps(res)
        else:
            return self._responsJson('Bad Request', False)

    def POST(self, *uri, **params):
        '''
        - catalog/device/<device_id>
        - catalog/services

        '''
        return True

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
    cherrypy.tree.mount(scWebservice(), '/catalog', conf)
    cherrypy.server.socket_host = "0.0.0.0"
    cherrypy.server.socket_port = 8181
    cherrypy.engine.start()
    cherrypy.engine.block()
