# !usr/bin/env python2
# -*- coding: utf-8 -*-
#
# Licensed under a 3-clause BSD license.
#
# @Author: Brian Cherinka
# @Date:   2017-03-08 16:43:52
# @Last modified by:   Brian Cherinka
# @Last Modified time: 2017-03-08 17:52:35

from __future__ import print_function, division, absolute_import
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, Float, String
import datetime
import json
import os


class ProfileDb(object):
    def __init__(self, database_connection_string=None, expire_on_commit=True):
        self.database_connection_string = database_connection_string

        # change 'echo' to print each SQL query (for debugging/optimizing/the curious)
        self.engine = create_engine(self.database_connection_string, echo=False)

        self.metadata = MetaData()
        self.metadata.bind = self.engine
        self.Base = declarative_base(bind=self.engine)
        self.Session = scoped_session(sessionmaker(bind=self.engine, autocommit=True,
                                                   expire_on_commit=expire_on_commit))

sqlpath = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'flask_profiler.sql')
database_connection_string = 'sqlite:///{0}'.format(sqlpath)
profiledb = ProfileDb(database_connection_string=database_connection_string)
Base = profiledb.Base


class Measurements(Base):
    __tablename__ = 'measurements'

    ID = Column(Integer, primary_key=True)
    startedAt = Column(Float)
    endedAt = Column(Float)
    elapsed = Column(Float)
    args = Column(String)
    kwargs = Column(String)
    method = Column(String)
    context = Column(String)
    name = Column(String)

    @property
    def starttime(self):
        ''' converts to local EST date/time from Unix timestamp in sec, [from time.time()]'''
        return datetime.datetime.fromtimestamp(float(self.startedAt))

    @property
    def endtime(self):
        ''' converts to local EST date/time from Unix timestamp in sec, [from time.time()]'''
        return datetime.datetime.fromtimestamp(float(self.endedAt))

    @property
    def startdate(self):
        return self.starttime.date().isoformat()

    @property
    def enddate(self):
        return self.endtime.date().isoformat()

    @property
    def context_dict(self):
        return json.loads(self.context)

    @property
    def header_dict(self):
        return self.context_dict['headers']

    @property
    def ip(self):
        return self.context_dict['ip']

    @property
    def url(self):
        return self.context_dict['url']

    @property
    def is_api(self):
        return 'api.sdss.org' in self.url

    @property
    def route(self):
        return 'api' if self.is_api else 'web'

    @property
    def referer(self):
        return self.header_dict['Referer'] if 'Referer' in self.header_dict.keys() else None

    def __repr__(self):
        return '<Measurements(id={0}, name={1}, startedAt={2}, method={3})>'.format(self.ID, self.name, self.starttime.isoformat(), self.method)

