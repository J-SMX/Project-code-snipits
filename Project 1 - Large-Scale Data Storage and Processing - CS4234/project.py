#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Mar 14 22:00:09 2020

@author: ufac001
"""

from email.parser import Parser
import re
import time
from datetime import datetime, timezone, timedelta

def date_to_dt(date):
    def to_dt(tms):
        def tz():
            return timezone(timedelta(seconds=tms.tm_gmtoff))
        return datetime(tms.tm_year, tms.tm_mon, tms.tm_mday, 
                      tms.tm_hour, tms.tm_min, tms.tm_sec, 
                      tzinfo=tz())
    return to_dt(time.strptime(date[:-6], '%a, %d %b %Y %H:%M:%S %z'))

# Q1: replace pass with your code
def extract_email_network(rdd):
    def parse_email(email_text):
        try:
            email = Parser().parsestr(email_text)
            sender = email.get('From', '').strip()
            recipients = set()
            for field in ['To', 'Cc', 'Bcc']:
                if email.get(field):
                    recipients.update(re.findall(r'[\w\.-]+@enron\.com', email[field]))
            
            timestamp = email.get('Date', '').strip()
            dt = None
            if timestamp:
                dt = date_to_dt(timestamp)
            
            return [(sender, recipient, dt) for recipient in recipients if sender != recipient and dt]
        except Exception:
            return []
    
    return rdd.flatMap(lambda email: parse_email(email)).distinct()

# Q2: replace pass with your code
def convert_to_weighted_network(rdd, drange=None):

    def filter_by_date(record):
        sender, recipient, timestamp = record
        if drange is None:
            return True
        return drange[0] <= timestamp <= drange[1]
    
    return (rdd.filter(filter_by_date).map(lambda x: ((x[0], x[1]), 1)).reduceByKey(lambda a, b: a + b).map(lambda x: (x[0][0], x[0][1], x[1])))


# Q3.1: replace pass with your code
def get_out_degrees(rdd):
    all_nodes = rdd.flatMap(lambda x: [x[0], x[1]]).distinct()
    out_degrees = rdd.map(lambda x: (x[0], x[2])).reduceByKey(lambda a, b: a + b)
    final_rdd = all_nodes.map(lambda n: (n, 0)).leftOuterJoin(out_degrees)\
                         .map(lambda x: (x[1][1] if x[1][1] else 0, x[0]))\
                         .sortBy(lambda x: (-x[0], x[1]))
    return final_rdd
# Q3.2: replace pass with your code         
def get_in_degrees(rdd):
    all_nodes = rdd.flatMap(lambda x: [x[0], x[1]]).distinct()
    in_degrees = rdd.map(lambda x: (x[1], x[2])).reduceByKey(lambda a, b: a + b)
    final_rdd = all_nodes.map(lambda n: (n, 0)).leftOuterJoin(in_degrees)\
                         .map(lambda x: (x[1][1] if x[1][1] else 0, x[0]))\
                         .sortBy(lambda x: (-x[0], x[1]))
    return final_rdd
# Q4.1: replace pass with your code            
def get_out_degree_dist(rdd):
    out_degrees = get_out_degrees(rdd)
    degree_dist = out_degrees.map(lambda x: (x[0], 1)).reduceByKey(lambda a, b: a + b)
    return degree_dist.sortBy(lambda x: x[0])

# Q4.2: replace pass with your code
def get_in_degree_dist(rdd):
    in_degrees = get_in_degrees(rdd)
    degree_dist = in_degrees.map(lambda x: (x[0], 1)).reduceByKey(lambda a, b: a + b)
    return degree_dist.sortBy(lambda x: x[0])

# Q5: replace pass with your code
def get_monthly_contacts(rdd):
    monthly_contacts = rdd.map(lambda x: (x[0], f"{x[2].month}/{x[2].year}", x[1]))
    sender_month_counts = monthly_contacts.distinct().map(lambda x: ((x[0], x[1]), 1))\
                                           .reduceByKey(lambda a, b: a + b)
    formatted = sender_month_counts.map(lambda x: (x[0][0], (x[0][1], x[1])))
    max_monthly_contacts = formatted.reduceByKey(lambda a, b: a if a[1] >= b[1] else b)
    result = max_monthly_contacts.map(lambda x: (x[0], x[1][0], x[1][1]))
    return result.sortBy(lambda x: (-x[2], x[0]))
