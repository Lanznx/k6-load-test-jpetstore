import re
import requests
import json
import mysql.connector
import time
import sys
import pprint
import os
import dotenv

dotenv.load_dotenv()

args = sys.argv[1:]
ENV_ID = args[0]
ROUND = args[1]
VU = args[2]
TIME_RANGE = args[3]
PATH_TO_TXT = args[4]

mydb = mysql.connector.connect(
  host=os.getenv('LOCAL_MYSQL_HOST'),
  user=os.getenv('LOCAL_MYSQL_USER'),
  passwd=os.getenv('LOCAL_MYSQL_PASSWORD'),
  database="mysql"
)


mycursor = mydb.cursor()


def main():
    prometheus_url = 'http://jpetstore.cerana.tech:30000'

    results, match_success, match_fail = clean_data(data)
    error_rate = 100 * calculate_error_rate(match_success, match_fail)
    response_time = get_response_time(results)

    cpu_by_container_data, cpu_by_instance_data, memory_by_container_data, memory_by_instance_data = get_metrics(prometheus_url, TIME_RANGE)
    metric = {
        'env_id': ENV_ID,
        'round': ROUND,
        'VU': VU,
        'error_rate': error_rate,
        'response_time': response_time,
        'cpu_container_jpetstore_backend': cpu_by_container_data[0]['value'][1],
        'cpu_container_mysql': cpu_by_container_data[1]['value'][1],
        'memory_container_jpetstore_backend': memory_by_container_data[0]['value'][1],
        'memory_container_mysql': memory_by_container_data[1]['value'][1],
        'cpu_instance_jpetstore_backend': cpu_by_instance_data[0]['value'][1], # cfliao1
        # 'cpu_instance_mysql': cpu_by_instance_data[1]['value'][1], # cfliao2
        'cpu_instance_mysql': 0, #單顆 node 適用
        'memory_instance_jpetstore_backend': memory_by_instance_data[0]['value'][1], # cfliao1
        # 'memory_instance_mysql': memory_by_instance_data[1]['value'][1], # cfliao2
        'memory_instance_mysql': 0, #單顆 node 適用
        'timestamp': int(time.time())
    }
    pprint.pprint(metric)
    insert_data_to_mysql(metric)



with open(PATH_TO_TXT, 'r') as f:
    data = f.readlines()[-2:]

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

def get_response_time(results):
    values = re.findall(r'\d+\.\d+', results)
    response_time = float(values[0])
    if(response_time < 9):
        response_time*=1000
    return response_time

def get_data_from_prometheus(promql, prometheus_url):
    response = requests.get(
        f'{prometheus_url}/api/v1/query',
        params={
            'query': promql
        }
    )
    data = json.loads(response.text)
    return data['data']['result']

def get_metrics(prometheus_url, time_range):
    cpu_by_container = f'sum(increase(container_memory_working_set_bytes{{container!="POD",container!="",namespace="jpetstore"}}[{time_range}m])) by (container)'
    cpu_by_instance = f'sum(increase(container_cpu_usage_seconds_total{{container!="POD", container!="", namespace="jpetstore"}}[{time_range}m])) by (instance)'
    memory_by_container = f'sum(increase(container_cpu_usage_seconds_total{{container!="POD", container!="", namespace="jpetstore"}}[{time_range}m])) by (container)'
    memory_by_instance = f'sum(increase(container_memory_working_set_bytes{{container!="POD",container!="",namespace="jpetstore"}}[{time_range}m])) by (instance)'

    cpu_by_container_data = get_data_from_prometheus(cpu_by_container, prometheus_url)
    cpu_by_instance_data = get_data_from_prometheus(cpu_by_instance, prometheus_url)
    memory_by_container_data = get_data_from_prometheus(memory_by_container, prometheus_url)
    memory_by_instance_data = get_data_from_prometheus(memory_by_instance, prometheus_url)

    return cpu_by_container_data, cpu_by_instance_data, memory_by_container_data, memory_by_instance_data



def insert_data_to_mysql(data):
    add_data = ("""
    INSERT INTO k6.metric (
        env_id, round, VU, error_rate, response_time,
        `cpu_container_jpetstore-backend`, cpu_container_mysql, `memory_container_jpetstore-backend`,
        memory_container_mysql, `cpu_instance_jpetstore-backend`, cpu_instance_mysql,
        `memory_instance_jpetstore-backend`, memory_instance_mysql, timestamp
    ) VALUES (
        %(env_id)s, %(round)s, %(VU)s, %(error_rate)s, %(response_time)s,
        %(cpu_container_jpetstore_backend)s, %(cpu_container_mysql)s, %(memory_container_jpetstore_backend)s,
        %(memory_container_mysql)s, %(cpu_instance_jpetstore_backend)s, %(cpu_instance_mysql)s,
        %(memory_instance_jpetstore_backend)s, %(memory_instance_mysql)s, %(timestamp)s
    )
    """)
    mycursor.execute(add_data, data)
    mydb.commit()

if __name__ == '__main__':
    main()
