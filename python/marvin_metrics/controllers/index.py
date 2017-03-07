#!/usr/bin/env python
# encoding: utf-8

from __future__ import print_function, division, absolute_import
from flask import Blueprint, render_template
index_page = Blueprint("index_page", __name__)


# All defined routes should be attached to this Blueprint

@index_page.route('/', methods=['GET'])
def index():
    ''' This is the Main page.  I run every time someone (re)loads this page.

    Now that I'm a blueprint, you build my url as blueprint_name.method_name or
    blueprint_name.endpoint , e.g. index_page.index

    '''

    # Create a dictionary to contain all the parameters you want to pass into the Jinja2 template
    output = {}
    output['title'] = 'Marvin Metrics'
    output['page'] = 'dashboard'

    return render_template('index.html', **output)
