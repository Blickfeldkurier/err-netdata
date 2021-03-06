"""Access Netdata from Errbot"""
import json
import urllib3
import base64
import io
import datetime
import matplotlib
# Force matplotlib to not use any Xwindows backend.
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from errbot import BotPlugin, arg_botcmd

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
        
        outstring = ""
        for key in ret['charts'].keys():
            outstring += "  * " + key + "\n"
        yield outstring

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
    @arg_botcmd('--xkcd', type=bool, default=True)
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
        
        plotlist = chart_data.splitlines()
        outDict = {}
        headerMap = []
        for item in plotlist[0].split(','):
            outDict[item] = []
            headerMap.append(item)
        
        for item in plotlist[1:]:
            counter = 0
            for value in item.split(','):
                plotkey = headerMap[counter]
                if counter == 0:
                    date = datetime.datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
                    outDict[plotkey].append(matplotlib.dates.date2num(date))
                else:
                    outDict[plotkey].append(float(value))
                counter = counter + 1
                
        if(args.xkcd == True):
            plt.xkcd()
            
        fig = plt.figure()
        ax = plt.subplot2grid((1, 5), (0, 0), colspan=4)
        plt.title(chart_info['title'])
        for key, values in outDict.items():
            if(key != headerMap[0]):
                plt.plot_date(
                        outDict[headerMap[0]],
                        values,
                        label=key,
                        linestyle='solid',
                        marker='None')
       
        fig.autofmt_xdate()
        ax.legend(loc='upper left',prop={'size':10}, bbox_to_anchor=(1,1))
        plt.grid()
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        string = base64.b64encode(buf.read())
        
        plt.close(fig)
        plt.cla()
        plt.close()

        uri = 'data:image/png;base64,' + string.decode('utf-8')
        self.send_card(
                to=message.frm,
                image=uri)

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
        
        
