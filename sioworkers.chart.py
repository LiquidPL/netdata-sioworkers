from bases.FrameworkServices.SimpleService import SimpleService

from six.moves.xmlrpc_client import ServerProxy

ORDER = ['workers']

CHARTS = {
    'workers': {
        'options': [None, 'Active workers', 'counts', 'workers', 'workers', 'stacked'],
        'lines' : [
            ['capacity', 'Capacity', 'absolute'],
            ['load', 'Task load', 'absolute'],
        ]
    }
}

CONF_PARAM_HOST = 'host'
DEFAULT_HOST = 'http://localhost:7889'

class Service(SimpleService):
    def __init__(self, configuration=None, name=None):
        SimpleService.__init__(self, configuration=configuration, name=name)
        self.order = ORDER
        self.definitions = CHARTS
        self.host = self.configuration.get(CONF_PARAM_HOST, DEFAULT_HOST)

        try:
            self.server = ServerProxy(self.host, allow_none=True)
        except:
            self.server = None

    def check(self):
        if self.server is None:
            self.error('error connecting to the sioworkers server {0}'.format(self.host))

        return True

    def get_data(self):
        if self.server is None:
            return None

        capacity = 0
        load = 0

        workers = self.server.get_workers()

        for worker in workers:
            concurrency = worker['info']['concurrency']

            capacity += concurrency

            if bool(worker['is_running_cpu_exec']):
                load += concurrency
            else:
                load += len(worker['tasks'])

        return dict({'capacity': capacity, 'load': load})
