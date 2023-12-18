import re
import sys
import requests
import json
import mysql.connector
import time
import argparse
import pprint
import os
import dotenv
from mysql.connector import Error

dotenv.load_dotenv()

def parse_arguments():
    parser = argparse.ArgumentParser(description='Metric Data Processing Script.')
    parser.add_argument('env_id', type=str, help='Environment ID')
    parser.add_argument('round', type=str, help='Round')
    parser.add_argument('vu', type=str, help='Virtual User count')
    parser.add_argument('time_range', type=str, help='Time Range for metrics')
    parser.add_argument('path_to_txt', type=str, help='Path to the text file')
    return parser.parse_args()

def connect_to_database():
    try:
        return mysql.connector.connect(
            host=os.getenv('LOCAL_MYSQL_HOST'),
            user=os.getenv('LOCAL_MYSQL_USER'),
            passwd=os.getenv('LOCAL_MYSQL_PASSWORD'),
            database="mysql"
        )
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        sys.exit(1)

def read_file(path_to_txt):
    try:
        with open(path_to_txt, 'r') as f:
            return f.readlines()[-2:]
    except IOError as e:
        print(f"Error reading file {path_to_txt}: {e}")
        sys.exit(1)

def fetch_prometheus_query(promql, prometheus_url):
    try:
        response = requests.get(
            f'{prometheus_url}/api/v1/query',
            params={'query': promql}
        )
        response.raise_for_status()
        data = json.loads(response.text)
        return data['data']['result']
    except requests.RequestException as e:
        print(f"Error querying Prometheus: {e}")
        sys.exit(1)

def retrieve_metrics(prometheus_url, time_range):
    cpu_by_container = f'sum(rate(container_cpu_usage_seconds_total{{container!="POD",container!="",namespace="jpetstore"}}[{time_range}m])) by (container)'
    memory_by_container = f'sum(rate(container_memory_working_set_bytes{{container!="POD",container!="",namespace="jpetstore"}}[{time_range}m])) by (container)'
    cpu_by_instance = f'sum(rate(container_cpu_usage_seconds_total{{container!="POD", container!="", namespace="jpetstore"}}[{time_range}m])) by (instance)'
    memory_by_instance = f'sum(rate(container_memory_working_set_bytes{{container!="POD",container!="",namespace="jpetstore"}}[{time_range}m])) by (instance)'

    cpu_by_container_data = fetch_prometheus_query(cpu_by_container, prometheus_url)
    memory_by_container_data = fetch_prometheus_query(memory_by_container, prometheus_url)
    cpu_by_instance_data = fetch_prometheus_query(cpu_by_instance, prometheus_url)
    memory_by_instance_data = fetch_prometheus_query(memory_by_instance, prometheus_url)

    return cpu_by_container_data, memory_by_container_data, cpu_by_instance_data, memory_by_instance_data

def compute_performance_metrics(data, env_id, round, vu, time_range, prometheus_url):
    results, match_success, match_fail = clean_data(data)
    error_rate = 100 * calculate_error_rate(match_success, match_fail)
    response_time = extract_response_time(results)

    cpu_cont_data, mem_cont_data, cpu_inst_data, mem_inst_data = retrieve_metrics(prometheus_url, time_range)

    # ------------------ TODO: make sure all metrics are correct && Add other metrics here ------------------
    metric = {
        'env_id': env_id,
        'round': round,
        'VU': vu,
        'error_rate': error_rate,
        'response_time': response_time,
        'timestamp': int(time.time()),
        'cpu_container_SUT': cpu_cont_data[0]['value'][1],
        'cpu_container_DB': cpu_cont_data[1]['value'][1],
        'memory_container_SUT': mem_cont_data[0]['value'][1],
        'memory_container_DB': mem_cont_data[1]['value'][1],
        'cpu_instance_SUT': cpu_inst_data[0]['value'][1],
        'cpu_instance_DB': cpu_inst_data[1]['value'][1],
        'memory_instance_SUT': mem_inst_data[0]['value'][1],
        'memory_instance_DB': mem_inst_data[1]['value'][1],
    }
    #  ------------------ TODO: make sure all metrics are correct && Add other metrics here ------------------
    return metric


def clean_data(data):
    data = ''.join(data)
    results = re.findall(r'http_req_duration.+', data)[0]
    match_success = re.findall(r"✓ (\d+)", data)[0]
    match_fail = re.findall(r"✗ (\d+)", data)[0]
    return results, match_success, match_fail

def calculate_error_rate(match_success, match_fail):
    if(int(match_fail) == 0):
        error_rate = int(match_fail)
    else:
        error_rate = int(match_fail) / (int(match_success)+int(match_fail) )

    if(error_rate > 1):
        error_rate = 1
    return error_rate

def extract_response_time(results):
    values = re.findall(r'\d+\.\d+', results)
    response_time = float(values[0])
    if(response_time < 9):
        response_time*=1000
    return response_time


def insert_data_to_mysql(data, mycursor, mydb):
    add_data = ("""
    INSERT INTO k6.metric (
        env_id, round, VU, error_rate, response_time, timestamp
        # Add other fields here
    ) VALUES (
        %(env_id)s, %(round)s, %(VU)s, %(error_rate)s, %(response_time)s, %(timestamp)s
        # Add other value placeholders here
    )
    """)
    try:
        mycursor.execute(add_data, data)
        mydb.commit()
    except Error as e:
        print(f"Error inserting data into MySQL: {e}")
        mydb.rollback()

def main():
    args = parse_arguments()
    # mydb = connect_to_database()
    # mycursor = mydb.cursor()
    prometheus_url = 'http://140.119.163.226:30000'
    data = read_file(args.path_to_txt)
    metric = compute_performance_metrics(data, args.env_id, args.round, args.vu, args.time_range, prometheus_url)
    pprint.pprint(metric)
    # insert_data_to_mysql(metric, mycursor, mydb)
    # mycursor.close()
    # mydb.close()

if __name__ == '__main__':
    main()
