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
        self.endpoints = ['charts', 'chart', 'data', 'badge.svg', 'allmetrics']
        super().activate()
    
    def build_base_url(self, sheme, host, port, endpoint):
        "Build full url from parameters"
        return sheme + "://" + host + ":" + str(port) + self.api_path + endpoint

    def yield_err(url, status, msg):
        """Print an error message if fetch fails"""
        yield url
        yield str(status)  + ": " + msg
        
    def fetch_url(self, url, http_fields, ret_fields, method='GET'):
        """Fetch an URL from Netdata"""
        ret = self.http.request(method, url, http_fields)
        if(ret.status != 200):
            self.yield_err(url, ret.status, ret.reason)
            return {}
        jdata = json.loads(ret.data.decode('utf-8'))
        retlist = {}
        for elem in ret_fields:
            retlist[elem] = jdata[elem]
        return retlist

    @arg_botcmd('host', type=str, help="Netdata Hostname")
    @arg_botcmd('--port', type=int, default=19999, help="Netdata Port (Default:19999)")
    @arg_botcmd('--sheme', type=str, default='http', help="Url scheme (Default:http)", unpack_args=False)
    def netdata_names(self, message, args):
        """
        Get Available Charts from host
        """
        base_url = self.build_base_url(args.sheme, args.host, args.port, self.endpoints[0])
        ret = self.fetch_url(base_url, {}, ['charts'])
    
        if ret == {}:
            return
        
        for key in ret['charts'].keys():
            yield "  * " + key + "\n"

    def get_chart_info(self, sheme, host, port, endpoint, name):
        """Get Infor about a particular Chart"""
        base_url = self.build_base_url(sheme, host, port, endpoint)
        
        return self.fetch_url(base_url, {'chart':name}, ['data_url', 'title', 'chart_type'])

    def get_chart_data(self, sheme, host, port, endpoint, after, points, group):
        """Get data for a chart"""
        data_url = sheme + "://" + host + ":" + str(port) + endpoint
        data_ret = self.fetch_url(
                data_url, 
                {'after': str(after),
                 'points': str(points),
                 'group': group,
                 'format': 'csv',
                 'options':'jsonwrap'},
                ['result'])
        
        if data_ret == {}:
            return ""
        
        return data_ret['result']
        

    @arg_botcmd('host', type=str)
    @arg_botcmd('name', type=str)
    @arg_botcmd('--after', type=int, default=-600)
    @arg_botcmd('--points', type=int, default=20)
    @arg_botcmd('--group', type=str, default="average")
    @arg_botcmd('--port', type=int, default=19999)
    @arg_botcmd('--sheme', type=str, default='http', unpack_args=False)
    def netdata_chart(self, message, args): 
        """
        Get Chart and send Plot
        """
        chart_info = self.get_chart_info(args.sheme, args.host, args.port, self.endpoints[1], args.name)
        if chart_info == {}:
            return
        
        chart_data = self.get_chart_data(args.sheme, args.host, args.port, chart_info['data_url'], args.after, args.points, args.group)
        if chart_data == "":
            return

    @arg_botcmd('host', type=str)
    @arg_botcmd('name', type=str)
    @arg_botcmd('--after', type=int, default=-600)
    @arg_botcmd('--points', type=int, default=20)
    @arg_botcmd('--group', type=str, default="average")
    @arg_botcmd('--port', type=int, default=19999)
    @arg_botcmd('--sheme', type=str, default='http', unpack_args=False)
    def netdata_table(self, message, args): 
        """
        Get Chart and send as Markdown Table
        """
        chart_info = self.get_chart_info(args.sheme, args.host, args.port, self.endpoints[1], args.name)
        if chart_info == {}:
            return
        
        chart_data = self.get_chart_data(args.sheme, args.host, args.port, chart_info['data_url'], args.after, args.points, args.group)
        if chart_data == "":
            return
        
        yield "# " + chart_info['title']
        yield "\n"
        table = ""
        outlist = chart_data.splitlines()
        header = "|" 
        headersep = "|"
        for item in outlist[0].split(','):
            header = header + " " + item + " | "
            headersep = headersep + " --- |"
        
        table += header + "\n"
        table += headersep + "\n"
                
        for line in outlist[1:]:
            outstr = "|"
            for token in line.split(','):
                outstr = outstr + " " + token + " |"
            table += outstr + "\n"
        yield table
        
        
