# !usr/bin/env python2
# -*- coding: utf-8 -*-
#
# Licensed under a 3-clause BSD license.
#
# @Author: Brian Cherinka
# @Date:   2017-03-08 16:46:38
# @Last modified by:   Brian Cherinka
# @Last Modified time: 2017-03-10 15:55:48

from __future__ import print_function, division, absolute_import
import dateutil
import copy
import leather
import itertools
import numpy as np
from collections import Counter, OrderedDict, deque, defaultdict
from functools import wraps
from dateutil.rrule import rrule, DAILY, HOURLY
from marvin_metrics.model.db import profiledb, Measurements
try:
    import ipwhois
except ImportError as e:
    ipwhois = None


class OrderedDefaultDict(OrderedDict, defaultdict):
    def __init__(self, default_factory=None, *args, **kwargs):
        # in python3 you can omit the args to super
        super(OrderedDefaultDict, self).__init__(*args, **kwargs)
        self.default_factory = default_factory


def get_meas(func):
    ''' Decorator that gets the measurements to act on '''
    @wraps(func)
    def decorated_function(inst, *args, **kwargs):
        if not inst.meas:
            inst.meas = inst.meas
        else:
            inst.meas = copy.deepcopy(inst.allmeas)
        return func(inst, *args, **kwargs)
    return decorated_function


class FlaskProfiler(object):
    def __init__(self):
        self.db = profiledb
        self.session = self.db.Session()
        self.meas = None
        self.allmeas = self.session.query(Measurements).order_by(Measurements.startedAt).all()
        # from marvin import config
        # self._urlmap = config.urlmap
        # self.endpoints = {d['url'].replace('{', '<').replace('}', '>'): e for k, v in self._urlmap.items() for e, d in self._urlmap[k].items()}
        self.build_dicts()

    def build_dicts(self):
        ''' builds some initial dictionaries that we want by date '''
        dips = OrderedDefaultDict(list)
        dnames = OrderedDefaultDict(list)
        thed = OrderedDefaultDict(list)
        for m in self.allmeas:
            thed[m.starttime.date()].append(m)
            dips[m.starttime.date()].append(m.ip)
            dnames[m.starttime.date()].append(m.name)
        self.thed = thed
        for k, v in dips.items():
            dips[k] = Counter(v)
        for k, v in dnames.items():
            dnames[k] = Counter(v)
        self.dips = dips
        self.dnames = dnames
        #self.dips = self.sort_and_order(dips)
        #self.dnames = self.sort_and_order(dnames)

    def remove_devs(self):
        ''' filter out the developer ip addresses '''
        iplist = ['128.220.160.159', '74.109.254.28']
        self.meas = [m for m in self.allmeas if m.ip not in iplist]

    def get_ips(self):
        ''' Get a list of all ips used across the entire sample, and a list of uniqips '''
        self.ips = [m.ip for m in self.allmeas]
        self.uniqips = list(set(self.ips))

    def get_ipmeas(self, ip):
        ''' a list of measurements from a specific ip address '''
        self.meas = self.get_meas_subset('ip', ip)

    def get_meas_subset(self, name, value):
        ''' retrives a measurement subset filtered by where name == value '''
        self.meas = [m for m in self.allmeas if m.__getattribute__(name) == value]

    @get_meas
    def get_timedeltas(self, meas=None):
        if not meas:
            meas = self.meas if self.meas else self.allmeas

        # timedeltas = []
        # starttimes = [m.starttime for m in meas]
        # shft_st = deque(starttimes)
        # shft_st.rotate(-1)
        # for i, m in enumerate(meas):
        #     timedeltas.append((shft_st[i] - m.endtime).total_seconds())
        # self.timedeltas = timedeltas

        # starttimes = [m.starttime for m in meas]
        # endtimes = [m.endtime for m in meas]
        # shft_st = deque(starttimes)
        # shft_st.rotate(-1)
        # self.timedeltas = [(sst - endtimes[i]).total_seconds() for i, sst in enumerate(shft_st)]

        starttimes = [m.starttime for m in meas]
        endtimes = [m.endtime for m in meas]
        elapsed = [m.elapsed for m in meas]
        shft_st = deque(starttimes)
        shft_st.rotate(-1)
        timedeltas = [(a - b).total_seconds() - c for a, b, c in zip(shft_st, endtimes, elapsed)]
        return timedeltas

    def split_datetime(self, dt):
        ''' split a datetime into a tuple of string iso format date and time '''
        return (dt.date().isoformat(), dt.time().isoformat())

    def get_count(self, param):
        ''' retrieves date independent count of a given parameter across the entire set of measurements '''
        paramlist = [m.__getattribute__(param) for m in self.allmeas]
        count = Counter(paramlist)
        return count

    def pad_times(self, start_time='20170101T000000', num_hours=24):
        ''' make a list of datetimes from the specified start time with num_hours long'''
        times = []
        for dt in rrule(HOURLY, dtstart=dateutil.parser.parse(start_time), count=num_hours):
            times.append(dt)
        self._times = times
        return times

    def pad_dates(self, from_date=None, to_date=None):
        ''' make a list of datetimes from the specified start time to end time '''

        # get date range
        if not from_date:
            fd = min(self.thed.keys())
        else:
            fd = dateutil.parser.parse(from_date).date()
        if not to_date:
            td = max(self.thed.keys())
        else:
            td = dateutil.parser.parse(to_date).date()

        # create dates
        dates = []
        for dt in rrule(DAILY, dtstart=fd, until=td):
            dates.append(dt)
        self._dates = dates
        return dates

    def quick_plot(self, data, file='testleather.svg', title='Temporal Plot', name='name1'):
        ''' quick plot with leather '''

        t = {date.date(): data[date.date()] for date in self._dates}
        t = self.sort_and_order(t)

        chart = leather.Chart(title)
        chart.add_x_scale(min(t.keys()), max(t.keys()))
        chart.add_line(t.items(), name=name)
        chart.add_dots(t.items(), name=name)
        chart.to_svg(file)

    # webdates=[m.starttime.date().isoformat() for m in allmeas if not m.is_api
    # apidates=[m.starttime.date().isoformat() for m in allmeas if m.is_api
    # apicount = Counter(apidates)
    # webcount = Counter(webdates)

    def sort_and_order(self, mydict):
        ''' create a sorted Ordered Dict, sorted by input dict key '''
        return OrderedDict(sorted(mydict.items(), key=lambda k: k[0]))

    def getnewipset(self, date):
        ''' returns a list of all previous ip addresses up to the given date '''
        tmp = []
        for d in self._dates:
            thedate = d.date()
            if thedate == date:
                break
            else:
                if thedate in self.dips:
                    tmp.extend(self.dips[thedate].keys())
        return set(tmp)

    def getlostipset(self, date):
        ''' returns a list of all future ip addresses past the given date '''
        tmp = []
        for d in self._dates:
            thedate = d.date()
            if thedate > date:
                if thedate in self.dips:
                    tmp.extend(self.dips[thedate].keys())
            else:
                pass
        return set(tmp)

    def get_ipsets(self, date):
        ''' returns a tuple of both all previous and future ip addresses from the given date '''
        newtmp = []
        lostmp = []
        dateindex = self.dips.keys().index(date)
        newdict = OrderedDict(self.dips.items()[0:dateindex])
        lostdict = OrderedDict(self.dips.items()[dateindex + 1:])
        newmerged = set(itertools.chain(*[val.keys() for val in newdict.values()]))
        lostmerged = set(itertools.chain(*[val.keys() for val in lostdict.values()]))
        return newmerged, lostmerged

    def get_newlosers(self, percent=False):
        ''' return dictionaries of new, lost, repeated, and bounced users

        Returns sorted ordered dicts by date of the percentage of
            new users - users who have never used Marvin before
            lost users - users who have never used Marvin again
            repeated users - (1-new users), users who have used Marvin before
            bounced users - users who are both new and lost

        '''
        newips = {}
        lostips = {}
        repeatips = {}
        bounceips = {}
        totalips = len(self.get_count('ip'))
        #self.dips = self.sort_and_order(self.dips)
        for date in self._dates:
            thedate = date.date()
            if thedate in self.dips:
                preips = self.getnewipset(thedate)
                postips = self.getlostipset(thedate)
                # preips, postips = self.get_ipsets(thedate)
                theips = self.dips[thedate].keys()
                # lost users
                liplist = [i for i in theips if i not in set(postips)]
                lips = len(liplist)
                lostips[thedate] = (float(lips) / totalips) * 100. if percent else lips
                # new users
                niplist = [i for i in theips if i not in set(preips)]
                nips = len(niplist)
                # newips[thedate] = (float(nips) / len(theips)) * 100.
                # repeated users
                rips = len(theips) - nips
                repeatips[thedate] = (float(rips) / totalips) * 100. if percent else rips
                # bounced users
                biplist = list(set(liplist) & set(niplist))
                bips = len(biplist)
                # bounceips[thedate] = (float(bips) / len(theips)) * 100.
                # subtract bounce users from new users
                nips = nips - bips
                bounceips[thedate] = (float(bips) / totalips) * 100. if percent else bips
                newips[thedate] = (float(nips) / totalips) * 100. if percent else nips
            else:
                newips[thedate] = 0
                repeatips[thedate] = 0
                lostips[thedate] = 0
                bounceips[thedate] = 0
        newips = self.sort_and_order(newips)
        lostips = self.sort_and_order(lostips)
        repeatips = self.sort_and_order(repeatips)
        bounceips = self.sort_and_order(bounceips)
        return newips, lostips, repeatips, bounceips

    def make_cdf(self, data, norm_by='ip'):
        ''' make a cumulative sum of some data '''
        if norm_by == 'ip':
            allx = len(set(itertools.chain(*[d.keys() for d in self.dips.values()])))

        if isinstance(data, dict):
            values = data.values()

        cdf = np.cumsum(values) / allx
        return cdf

    def lookup_ips(self, ip=None, method='whois'):
        ''' Look up the locations of the ips '''

        self.locations = []
        self.get_ips()

        if ip and ip != '127.0.0.1':
            self.locations.append(self.get_ip_dict(ip, method=method))
        else:
            myips = self.uniqips
            for ip in myips:
                if ip is not None and ip != '127.0.0.1':
                    self.locations.append(self.get_ip_dict(ip, method=method))

    def get_ip_dict(self, ip, method='whois'):
        ''' Get the ip lookup dictionary '''

        if not ipwhois:
            raise ImportError('Cannot look up ips.  You do not have the ipwhois package installed!')

        assert method in ['whois', 'rdap'], 'Method must either be rdap or whois'

        ipwho = ipwhois.IPWhois(ip)
        self.ipmethod = method
        ipdict = None
        if method == 'whois':
            try:
                ipdict = ipwho.lookup_whois()
            except Exception as e:
                print('Could not lookup ip {0}: {1}'.format(ip, e))
        elif method == 'rdap':
            try:
                ipdict = ipwho.lookup_rdap()
            except Exception as e:
                print('Could not lookup ip {0}: {1}'.format(ip, e))
        return ipdict

    def extract_locations(self):
        ''' Extraction the location info from the ip output '''
        self.places = []
        for loc in self.locations:
            nets = loc['nets'][0] if len(loc['nets']) > 0 else None
            locdict = {'asn_country_code': loc['asn_country_code'],
                       'place': {'city': nets['city'] if nets else None,
                                 'state': nets['state'] if nets else None,
                                 'country': nets['country'] if nets else None}}
            self.places.append(locdict)



