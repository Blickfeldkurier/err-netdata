"""Access Netdata from Errbot"""
import json
import urllib3
import matplotlib.pyplot as plt
import csv
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

    def yield_err(url, status, msg):
        yield url
        yield str(status)  + ": " + msg

    @arg_botcmd('host', type=str, help="Netdata Hostname")
    @arg_botcmd('--port', type=int, default=19999, help="Netdata Port (Default:19999)")
    @arg_botcmd('--sheme', type=str, default='http', help="Url scheme (Default:http)", unpack_args=False)
    def netdata_names(self, message, args):
        """
        Get Available Charts from host
        """
        base_url = self.build_base_url(args.sheme, args.host, args.port, self.enpoints[0])
        ret = self.http.request('GET', base_url)
        if ret.status != 200:
            self.yield_err(base_url, ret.status, ret.reason)
            return
        
        jdata = json.loads(ret.data.decode('utf-8'))
        for key in jdata['charts'].keys():
            yield "  * " + key + "\n"
            
    @arg_botcmd('host', type=str)
    @arg_botcmd('name', type=str)
    @arg_botcmd('--after', type=int, default=-600)
    @arg_botcmd('--points', type=int, default=20)
    @arg_botcmd('--group', type=str, default="average")
    @arg_botcmd('--port', type=int, default=19999)
    @arg_botcmd('--sheme', type=str, default='http', unpack_args=False)
    def netdata_chart(self, message, args): 
        """
        Get Chart
        """
        base_url = self.build_base_url(args.sheme, args.host, args.port, self.enpoints[1])
        chart_ret = self.http.request(
                'GET', 
                base_url,
                fields={'chart' : args.name})
        
        if chart_ret.status != 200:
            self.yield_err(base_url, chart_ret.status, chart_ret.reason)
            return
        
        jchart = json.loads(chart_ret.data.decode('utf-8'))
        data_endpoint = jchart['data_url']
        data_url = args.sheme + "://" + args.host + ":" + str(args.port) + data_endpoint
        data_ret = self.http.request(
                'GET',
                data_url,
                fields={'after': str(args.after),
                        'points': str(args.points),
                        'group': args.group,
                        'format': 'csv',
                        'options':'jsonwrap'}
                )
        
        if data_ret.status != 200:
            self.yield_err(base_url, data_ret.status, data_ret.reason)
            return
        
        data_json = json.loads(data_ret.data.decode('utf-8'))
        
        
        
        
        
