# !usr/bin/env python2
# -*- coding: utf-8 -*-
#
# Licensed under a 3-clause BSD license.
#
# @Author: Brian Cherinka
# @Date:   2017-03-07 15:49:32
# @Last modified by:   Brian Cherinka
# @Last Modified time: 2017-03-09 15:28:31

from __future__ import print_function, division, absolute_import
from flask import Flask, Blueprint, send_from_directory, request, render_template
from flask_jsglue import JSGlue
import flask_profiler
from marvin_metrics.jinja_filters import jinjablue

import sys
import os


def create_app(debug=False):

    # -----------------------------
    # Create App
    # -----------------------------
    # instantiate the Flask app, __name__ tells Flask what belongs to the application
    app = Flask(__name__, static_url_path='/static')
    app.debug = debug

    # Load the Flask profile configuration
    # app.config["flask_profiler"] = {
    #     "enabled": True,
    #     "storage": {
    #         "engine": "sqlite",
    #         "FILE": "flask_profiler.sql"
    #     },
    #     "endpointRoot": "profiler",
    #     "basicAuth": {
    #         "enabled": False,
    #     }
    # }

    # flask_profiler.init_app(app)

    # JSGlue
    jsglue = JSGlue(app)

    # -----------------------------------
    # Set up a Logger for your application
    # -----------------------------------
    # log = standard Pythong logging thing you create here -- then add it to the Flask handler
    # app.logger.addHandler(log)
    # use your logger with app.logger.info('this is info'), don't use print statements inside Flask

    # ----------------------------------
    # Load an appropriate Flask configuration file for a debug or production version
    # ----------------------------------
    if app.debug:
        server_config_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'configuration', 'localhost.cfg')
    else:
        pass
        # Load a configuration file for a production version of your app!
        # server_config_file = /path/to/production/config/file

    # app.logger.info('Loading config file: {0}'.format(server_config_file))
    app.config.from_pyfile(server_config_file)

    # ----------------------------
    # Manually add any configuration parameters
    # ----------------------------
    app.config["UPLOAD_FOLDER"] = os.environ.get("MM_DATA_DIR", None)

    # ----------------------------------
    # Web Route Registration - Import and register all your blueprints here
    # ----------------------------------
    from marvin_metrics.controllers.index import index

    url_prefix = '/marvin_metrics'  # I can prefix all routes with a name
    url_prefix = None
    app.register_blueprint(index, url_prefix=url_prefix)

    # Register all custom Jinja filters in the file.
    app.register_blueprint(jinjablue)

    return app
