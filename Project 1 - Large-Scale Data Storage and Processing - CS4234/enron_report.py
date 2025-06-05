from pyspark import SparkContext, SparkConf
from pyspark.sql import SparkSession
from datetime import datetime, timezone
import numpy as np
from project import extract_email_network
import csv

conf = SparkConf().setAppName("Enron Network Analysis")
sc = SparkContext(conf=conf)
spark = SparkSession(sc)

def utf8_decode_and_filter(rdd):
    def utf_decode(s):
        try:
          return str(s, 'utf-8')
        except:
            pass
    return rdd.map(lambda x: utf_decode(x[1])).filter(lambda x: x != None)


def convert_to_weighted_network(rdd, drange=None):
    def filter_by_date(record):
        sender, recipient, timestamp = record
        if drange is None:
            return True
        return drange[0] <= timestamp <= drange[1]

    return (rdd.filter(filter_by_date)
              .map(lambda x: ((x[0], x[1]), 1))
              .reduceByKey(lambda a, b: a + b)
              .map(lambda x: (x[0][0], x[0][1], x[1])))


def get_out_degrees(rdd):
    print("Q3.1")
    all_nodes = rdd.flatMap(lambda x: [x[0], x[1]]).distinct()
    out_degrees = rdd.map(lambda x: (x[0], x[2])).reduceByKey(lambda a, b: a + b)
    final_rdd = all_nodes.map(lambda n: (n, 0)).leftOuterJoin(out_degrees)\
                         .map(lambda x: (x[1][1] if x[1][1] else 0, x[0]))\
                         .sortBy(lambda x: (-x[0], x[1]))

    return final_rdd

def get_in_degrees(rdd):
    all_nodes = rdd.flatMap(lambda x: [x[0], x[1]]).distinct()
    in_degrees = rdd.map(lambda x: (x[1], x[2])).reduceByKey(lambda a, b: a + b)
    final_rdd = all_nodes.map(lambda n: (n, 0)).leftOuterJoin(in_degrees)\
                         .map(lambda x: (x[1][1] if x[1][1] else 0, x[0]))\
                         .sortBy(lambda x: (-x[0], x[1]))
    return final_rdd

rdd = utf8_decode_and_filter(sc.sequenceFile("/user/ufac001/project/enron-full"))

email_rdd = extract_email_network(rdd)

date_range = (datetime(2001, 1, 1, tzinfo=timezone.utc), datetime(2001, 12, 31, tzinfo=timezone.utc))

weighted_rdd = convert_to_weighted_network(email_rdd, date_range)

out_degrees = get_out_degrees(weighted_rdd).collect()
in_degrees = get_in_degrees(weighted_rdd).collect()

total_out_degree = sum(d for d, _ in out_degrees)
total_in_degree = sum(d for d, _ in in_degrees)

top_20_percent = int(len(out_degrees) * 0.2) or 1
top_out_degree = sum(d for d, _ in sorted(out_degrees, reverse=True)[:top_20_percent])
top_in_degree = sum(d for d, _ in sorted(in_degrees, reverse=True)[:top_20_percent])

k_max_values = []
node_counts = []
for n in range(1, 13):
    month_range = (datetime(2001, n, 1, tzinfo=timezone.utc), datetime(2001, n, 28, tzinfo=timezone.utc))
    monthly_rdd = convert_to_weighted_network(email_rdd, month_range)
    max_out = max(get_out_degrees(monthly_rdd).collect(), key=lambda x: int(x[0]) if isinstance(x[0], str) else x[0], default=(0, ""))[0]
    max_in = max(get_in_degrees(monthly_rdd).collect(), key=lambda x: int(x[0]) if isinstance(x[0], str) else x[0], default=(0, ""))[0]
    k_max_values.append((max_out, max_in))
    node_counts.append(monthly_rdd.count())

print(f"top_out_degree = {top_out_degree}")
print(f"total out degree = {total_out_degree}")
print(f"top in degree = {top_in_degree}")
print(f"total in degree = {total_in_degree}")
print("80/20 Rule Compliance (Out-degree):", top_out_degree / total_out_degree if total_out_degree else 0)
print("80/20 Rule Compliance (In-degree):", top_in_degree / total_in_degree if total_in_degree else 0)
print("Max Degree (k_max) Over Time:", k_max_values)

def get_out_degree_dist(rdd):
    out_degrees = get_out_degrees(rdd)
    degree_dist = out_degrees.map(lambda x: (x[0], 1)).reduceByKey(lambda a, b: a + b)
    return degree_dist.sortBy(lambda x: x[0])

def get_in_degree_dist(rdd):
    in_degrees = get_in_degrees(rdd)
    degree_dist = in_degrees.map(lambda x: (x[0], 1)).reduceByKey(lambda a, b: a + b)
    return degree_dist.sortBy(lambda x: x[0])

out_degrees = get_out_degrees(weighted_rdd) 
in_degrees = get_in_degrees(weighted_rdd)

out_degree_dist = get_out_degree_dist(weighted_rdd).collect()
in_degree_dist = get_in_degree_dist(weighted_rdd).collect()

with open("out_degree_results.csv", mode='a', newline='') as write_file:
    writer = csv.writer(write_file)
    for entry in out_degree_dist:
        writer.writerow(entry)

with open("in_degree_results.csv", mode='a', newline='') as write_file:
    writer = csv.writer(write_file)
    for entry in in_degree_dist:
        writer.writerow(entry)


sc.stop()
