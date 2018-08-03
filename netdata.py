"""Access Netdata from Errbot"""
import json
import urllib3
from errbot import BotPlugin, botcmd, arg_botcmd, webhook


class Netdata(BotPlugin):
    """
    Get Graphs from Netdata hosts
    """

    def activate(self):#Is thre a way to register self.*  from __init__?
        """Init Netdata Class"""
        self.http = urllib3.PoolManager()
        self.api_path = '/api/v1/'
        self.enpoints = ['charts', 'chart', 'data', 'badge.svg', 'allmetrics']
        super().activate()
    
    def build_base_url(self, sheme, host, port, endpoint):
        "Build full url from parameters"
        return sheme + "://" + host + ":" + str(port) + self.api_path + endpoint

    @arg_botcmd('host', type=str)
    @arg_botcmd('--port', type=int, default=19999)
    @arg_botcmd('--sheme', type=str, default='http', unpack_args=False)
    def netdata_info(self, message, args):
        """
        Get Available Charts from host
        """
        ret = self.http.request('GET', self.build_base_url(args.sheme, args.host, args.port, self.enpoints[0]))
        jdata = json.loads(ret.data.decode('utf-8'))
        for key in jdata['charts'].keys():
            yield "  * " + key + "\n"
