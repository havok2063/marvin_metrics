#!/usr/bin/env python
# encoding: utf-8

from __future__ import print_function, division, absolute_import
from flask import Blueprint, render_template, jsonify
from flask_classy import FlaskView, route
import numpy as np
index = Blueprint("index_page", __name__)


class Index(FlaskView):

    route_base = '/'

    def __init__(self):
        pass

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
        # data = [{'x': '2017-01-13', 'y': 5}, {'x': '2017-01-13', 'y': 3},
        #         {'x': '2017-02-28', 'y': 50}, {'x': '2017-02-10', 'y': 1}]
        # return jsonify({'key': 'Stream1', 'values': data})

        data = [{'values': [['2017-01-13', 4983], ['2017-01-14', 2976], ['2017-01-15', 0], ['2017-01-16', 441],
                            ['2017-01-17', 176], ['2017-01-18', 334], ['2017-01-19', 829], ['2017-01-20', 8999],
                            ['2017-01-21', 7], ['2017-01-22', 387], ['2017-01-23', 1170], ['2017-01-24', 1322],
                            ['2017-01-25', 8454], ['2017-01-26', 194], ['2017-01-27', 319], ['2017-01-28', 5],
                            ['2017-01-29', 0], ['2017-01-30', 2734], ['2017-01-31', 2879], ['2017-02-01', 983],
                            ['2017-02-02', 15633], ['2017-02-03', 11143], ['2017-02-04', 7952], ['2017-02-05', 630],
                            ['2017-02-06', 14962], ['2017-02-07', 19252], ['2017-02-08', 13741], ['2017-02-09', 5256],
                            ['2017-02-10', 0], ['2017-02-11', 0], ['2017-02-12', 0], ['2017-02-13', 0], ['2017-02-14', 0],
                            ['2017-02-15', 0], ['2017-02-16', 12367], ['2017-02-17', 22406], ['2017-02-18', 3150],
                            ['2017-02-19', 0], ['2017-02-20', 60], ['2017-02-21', 2461], ['2017-02-22', 71],
                            ['2017-02-23', 1121], ['2017-02-24', 808], ['2017-02-25', 0]], 'key': 'api'},
                {'values': [['2017-01-13', 98], ['2017-01-14', 155], ['2017-01-15', 56], ['2017-01-16', 152],
                            ['2017-01-17', 106], ['2017-01-18', 246], ['2017-01-19', 73], ['2017-01-20', 231], ['2017-01-21', 7],
                            ['2017-01-22', 37], ['2017-01-23', 37], ['2017-01-24', 86], ['2017-01-25', 106], ['2017-01-26', 171],
                            ['2017-01-27', 159], ['2017-01-28', 14], ['2017-01-29', 39], ['2017-01-30', 448], ['2017-01-31', 189],
                            ['2017-02-01', 322], ['2017-02-02', 83], ['2017-02-03', 139], ['2017-02-04', 27], ['2017-02-05', 42],
                            ['2017-02-06', 104], ['2017-02-07', 163], ['2017-02-08', 168], ['2017-02-09', 195], ['2017-02-10', 0],
                            ['2017-02-11', 0], ['2017-02-12', 0], ['2017-02-13', 0], ['2017-02-14', 0], ['2017-02-15', 0],
                            ['2017-02-16', 205], ['2017-02-17', 1302], ['2017-02-18', 22], ['2017-02-19', 0], ['2017-02-20', 315],
                            ['2017-02-21', 265], ['2017-02-22', 133], ['2017-02-23', 100], ['2017-02-24', 479], ['2017-02-25', 0]],
                 'key': 'web'}];

        return jsonify(data)

Index.register(index)
