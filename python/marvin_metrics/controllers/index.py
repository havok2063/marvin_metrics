#!/usr/bin/env python
# encoding: utf-8

from __future__ import print_function, division, absolute_import
from flask import Blueprint, render_template, jsonify
from flask_classy import FlaskView, route
from itertools import groupby
from collections import OrderedDict, Counter
import numpy as np
index = Blueprint("index_page", __name__)


class Index(FlaskView):

    route_base = '/'

    def __init__(self):

        from marvin_metrics.tools.metric import FlaskProfiler
        self.fp = FlaskProfiler()
        self.dates = self.fp.pad_dates()

    @route('/', methods=['GET'], endpoint='index')
    def index(self):
        ''' This is the Main page.  I run every time someone (re)loads this page.

        Now that I'm a blueprint, you build my url as blueprint_name.method_name or
        blueprint_name.endpoint , e.g. index_page.index

        '''

        # Create a dictionary to contain all the parameters you want to pass into the Jinja2 template
        output = {}
        output['title'] = 'Marvin Metrics'
        output['page'] = 'dashboard'

        return render_template('index.html', **output)

    @route('/getjson/', methods=['GET'], endpoint='getjson')
    def getjson(self):
        ''' Gets the JSON
        '''

        data = [{'time': 1, 'date': '2017-01-13', 'count': 5}, {'time': 1, 'date': '2017-01-13', 'count': 3},
                {'time': 2, 'date': '2017-02-28', 'count': 50}, {'time': 2, 'date': '2017-02-10', 'count': 1}]

        data = [{'time': 1, 'date': 1, 'count': np.random.randint(1,10)}, {'time': 1, 'date': 2, 'count': np.random.randint(1,10)},
                {'time': 2, 'date': 1, 'count': np.random.randint(1,10)}, {'time': 2, 'date': 2, 'count': np.random.randint(1,10)},
                {'time': 2, 'date': 3, 'count': np.random.randint(1,10)}, {'time': 1, 'date': 3, 'count': np.random.randint(1,10)}]

        return jsonify(data)

    @route('/getlinejson/', methods=['GET'], endpoint='getlinejson')
    def getlinejson(self):
        ''' Gets the JSON
        '''
        values = []
        for date in self.dates:
            thedate = date.date()
            dsum = sum(self.fp.dips[thedate].values()) if thedate in self.fp.dips else 0
            values.append([thedate.isoformat(), dsum])
        data = [{'key': 'requests', 'values': values}]
        return jsonify(data)

    @route('/getuniqvisits/', methods=['GET'], endpoint='getuniqvisits')
    def getuniqvisits(self):
        ''' Gets the JSON
        '''
        values = []
        for date in self.dates:
            thedate = date.date()
            dsum = len(self.fp.dips[thedate]) if thedate in self.fp.dips else 0
            values.append([thedate.isoformat(), dsum])
        data = [{'key': 'unique visitors', 'values': values}]
        return jsonify(data)

    @route('/getppv/', methods=['GET'], endpoint='getppv')
    def getppv(self):
        ''' Gets the JSON
        '''

        t = []

        values = []
        for date in self.dates:
            thedate = date.date()
            uniqip = len(self.fp.dips[thedate]) if thedate in self.fp.dips else 0
            uniqname = len(self.fp.dnames[thedate]) if thedate in self.fp.dnames else 0
            ppv = float(uniqname) / uniqip if uniqip != 0 else 0
            values.append([thedate.isoformat(), ppv])

            # get other way
            if thedate in self.fp.thed:
                f = {k: list(g) for k, g in groupby(sorted(self.fp.thed[thedate], key=lambda t: t.ip), lambda t: t.ip)}
                t.append([thedate.isoformat(), np.mean([len(Counter([l.name for l in v])) for k, v in f.items()])])
            else:
                t.append([thedate.isoformat(), 0])

        data = [{'key': 'pages per visit', 'values': values}, {'key': 'avg ppv', 'values': t}]
        return jsonify(data)

    @route('/getnewlost/', methods=['GET'], endpoint='getnewlost')
    def getnewlost(self):
        ''' Gets the JSON
        '''
        data = []
        new, lost, rep, bounce = self.fp.get_newlosers()

        newvalues = []
        lostvals = []
        repvals = []
        bouncevals = []
        for k, v in new.items():
            newvalues.append([k.isoformat(), v])
            lostvals.append([k.isoformat(), lost[k]])
            repvals.append([k.isoformat(), rep[k]])
            bouncevals.append([k.isoformat(), bounce[k]])
        data = [{'key': 'new users', 'values': newvalues},
                {'key': 'repeat users', 'values': repvals},
                {'key': 'lost users', 'values': lostvals},
                {'key': 'bounce users', 'values': bouncevals}]
        return jsonify(data)

    @route('/gettd/', methods=['GET'], endpoint='gettd')
    def gettd(self):
        ''' Gets the JSON
        '''

        values = []
        for date in self.dates:
            thedate = date.date()
            if thedate in self.fp.thed:
                f = {k: list(g) for k, g in groupby(sorted(self.fp.thed[thedate], key=lambda t: t.ip), lambda t: t.ip)}
                tdlist = []
                for k, v in f.items():
                    tds = self.fp.get_timedeltas(meas=v)
                    tdlist.append(sum(tds[:-1]))
                tdstats = [np.min(tdlist), np.median(tdlist), np.max(tdlist)]
                values.append([thedate.isoformat(), tdstats[1] / 60.])

        data = [{'key': 'avg time deltas', 'values': values}]
        return jsonify(data)

    @route('/getpagestream/', methods=['GET'], endpoint='getpagestream')
    def getpagestream(self):
        ''' Gets the JSON
        '''

        topten = [u'/marvin2/api/maps/<name>/<bintype>/<template_kin>/',
                  u'/marvin2/api/maps/<name>/<bintype>/<template_kin>/map/<property_name>/<channel>/',
                  u'/marvin2/api/cubes/<name>/', u'/marvin2/galaxy/<galid>',
                  u'/marvin2/api/general/getroutemap/', u'/marvin2/galaxy/getspaxel',
                  u'/marvin2/api/modelcubes/<name>/<bintype>/<template_kin>/',
                  u'/marvin2/api/spaxels/<name>/properties/<template_kin>/<x>/<y>/',
                  u'/marvin2/api/spaxels/<name>/spectra/<x>/<y>/',
                  u'/marvin2/api/spaxels/<name>/models/<template_kin>/<x>/<y>/']

        data = []
        test = {k: list(g) for k, g in groupby(sorted(self.fp.meas, key=lambda t: t.name), lambda t: t.name)}
        for k, v in test.items():
            values = []
            if k in topten:
                c = Counter([m.starttime.date() for m in v])
                for date in self.dates:
                    values.append([date.date().isoformat(), c[date.date()] if date.date() in c else 0])
                tmp = {'key': k, 'values': values}
                data.append(tmp)

        return jsonify(data)

Index.register(index)
