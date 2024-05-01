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
    parser = argparse.ArgumentParser(description="Metric Data Processing Script.")
    parser.add_argument("env_id", type=str, help="Environment ID")
    parser.add_argument("round", type=str, help="Round")
    parser.add_argument("txt_size", type=str, help="Path to the text file")
    return parser.parse_args()


def connect_to_database():
    try:
        mydb = mysql.connector.connect(
            host=os.getenv("LOCAL_MYSQL_HOST"),
            user=os.getenv("LOCAL_MYSQL_USER"),
            passwd=os.getenv("LOCAL_MYSQL_PASSWORD"),
            database="mysql",
        )

        mycursor = mydb.cursor()

        mycursor.execute("SHOW TABLES LIKE 'metric'")
        result = mycursor.fetchone()

        if not result:
            create_table_query = """
            CREATE TABLE mysql.metric (
                env_id VARCHAR(255),
                round VARCHAR(255),
                VU INT,
                total_request INT,
                error_rate FLOAT,
                response_time FLOAT,
                timestamp BIGINT,
                usage_cpu_SUT FLOAT,
                usage_cpu_DB FLOAT,
                saturation_cpu_SUT FLOAT,
                saturation_cpu_DB FLOAT,
                usage_mem_SUT FLOAT,
                usage_mem_DB FLOAT,
                saturation_mem_SUT FLOAT,
                saturation_mem_DB FLOAT,
                usage_read_disk_SUT FLOAT,
                usage_read_disk_DB FLOAT,
                usage_write_disk_SUT FLOAT,
                usage_write_disk_DB FLOAT,
                usage_received_network_SUT FLOAT,
                usage_received_network_DB FLOAT,
                usage_transmitted_network_SUT FLOAT,
                usage_transmitted_network_DB FLOAT
            );
            """
            mycursor.execute(create_table_query)
            mydb.commit()
            print("Table 'metric' created successfully.")

        mycursor.close()
        return mydb

    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        sys.exit(1)


def fetch_prometheus_query(promql, prometheus_url):
    try:
        response = requests.get(
            f"{prometheus_url}/api/v1/query", params={"query": promql}
        )
        response.raise_for_status()
        data = json.loads(response.text)
        if len(data["data"]["result"]) == 0:
            return [{'metric': {}, 'value': [-99999, '0']}]
        return data["data"]["result"]
    except requests.RequestException as e:
        print(f"Error querying Prometheus: {e}")
        sys.exit(1)


def retrieve_metrics(prometheus_url, time_range):
    usage_cpu = f'sum(increase(container_cpu_usage_seconds_total{{container!="POD", container!="", namespace="jpetstore"}}[{time_range}])) by (container)'
    saturation_cpu = f'sum(increase(container_cpu_cfs_throttled_seconds_total{{container!="POD", container!="", namespace="jpetstore"}}[{time_range}])) by (container)'

    usage_mem = f'avg(avg_over_time(container_memory_working_set_bytes{{container!="POD", container!="", namespace="jpetstore"}}[{time_range}])) by (container)'
    saturation_mem = f'sum(increase(container_memory_swap{{container!="POD", container!="", namespace="jpetstore"}}[{time_range}])) by (container)'

    usage_read_disk = f'sum(rate(container_fs_reads_bytes_total{{container!="POD", container!="", namespace="jpetstore"}}[{time_range}])) by (container)'
    usage_write_disk = f'sum(rate(container_fs_writes_bytes_total{{container!="POD", container!="", namespace="jpetstore"}}[{time_range}])) by (container)'

    usage_received_network_SUT = f'sum(rate(container_network_receive_bytes_total{{namespace="jpetstore", pod=~"jpetstore-backend-deployment-.*"}}[{time_range}]))'
    usage_received_network_DB = f'sum(rate(container_network_receive_bytes_total{{namespace="jpetstore", pod=~"mysql-.*"}}[{time_range}]))'

    usage_transmitted_network_SUT = f'sum(rate(container_network_transmit_bytes_total{{namespace="jpetstore", pod=~"jpetstore-backend-deployment-.*"}}[{time_range}]))'
    usage_transmitted_network_DB = f'sum(rate(container_network_transmit_bytes_total{{namespace="jpetstore", pod=~"mysql-.*"}}[{time_range}]))'

    metrics = {
        "usage_cpu": fetch_prometheus_query(usage_cpu, prometheus_url),
        "saturation_cpu": fetch_prometheus_query(saturation_cpu, prometheus_url),
        "usage_mem": fetch_prometheus_query(usage_mem, prometheus_url),
        "saturation_mem": fetch_prometheus_query(saturation_mem, prometheus_url),
        "usage_read_disk": fetch_prometheus_query(usage_read_disk, prometheus_url),
        "usage_write_disk": fetch_prometheus_query(usage_write_disk, prometheus_url),
        "usage_received_network_SUT": fetch_prometheus_query(
            usage_received_network_SUT, prometheus_url
        ),
        "usage_received_network_DB": fetch_prometheus_query(
            usage_received_network_DB, prometheus_url
        ),
        "usage_transmitted_network_SUT": fetch_prometheus_query(
            usage_transmitted_network_SUT, prometheus_url
        ),
        "usage_transmitted_network_DB": fetch_prometheus_query(
            usage_transmitted_network_DB, prometheus_url
        ),
    }

    return metrics


def retrieve_externalDB_metrics(prometheus_url, time_range):
    usage_cpu = f'sum(increase(container_cpu_usage_seconds_total{{name="mysql-container"}}[{time_range}])) by (container)'
    # saturation_cpu = f'sum(increase(container_cpu_cfs_throttled_seconds_total{{name="mysql-container"}}[{time_range}])) by (container)'

    usage_mem = f'avg(avg_over_time(container_memory_working_set_bytes{{name="mysql-container"}}[{time_range}])) by (container)'
    saturation_mem = f'sum(increase(container_memory_swap{{name="mysql-container"}}[{time_range}])) by (container)'

    usage_read_disk = f'sum(rate(container_fs_reads_bytes_total{{name="mysql-container"}}[{time_range}])) by (container)'
    usage_write_disk = f'sum(rate(container_fs_writes_bytes_total{{name="mysql-container"}}[{time_range}])) by (container)'

    usage_received_network_SUT = f'sum(rate(container_network_receive_bytes_total{{name="mysql-container"}}[{time_range}]))'
    usage_received_network_DB = f'sum(rate(container_network_receive_bytes_total{{name="mysql-container"}}[{time_range}]))'

    usage_transmitted_network_SUT = f'sum(rate(container_network_transmit_bytes_total{{name="mysql-container"}}[{time_range}]))'
    usage_transmitted_network_DB = f'sum(rate(container_network_transmit_bytes_total{{name="mysql-container"}}[{time_range}]))'

    metrics = {
        "usage_cpu": fetch_prometheus_query(usage_cpu, prometheus_url),
        # "saturation_cpu": fetch_prometheus_query(saturation_cpu, prometheus_url),
        "usage_mem": fetch_prometheus_query(usage_mem, prometheus_url),
        "saturation_mem": fetch_prometheus_query(saturation_mem, prometheus_url),
        "usage_read_disk": fetch_prometheus_query(usage_read_disk, prometheus_url),
        "usage_write_disk": fetch_prometheus_query(usage_write_disk, prometheus_url),
        "usage_received_network_SUT": fetch_prometheus_query(
            usage_received_network_SUT, prometheus_url
        ),
        "usage_received_network_DB": fetch_prometheus_query(
            usage_received_network_DB, prometheus_url
        ),
        "usage_transmitted_network_SUT": fetch_prometheus_query(
            usage_transmitted_network_SUT, prometheus_url
        ),
        "usage_transmitted_network_DB": fetch_prometheus_query(
            usage_transmitted_network_DB, prometheus_url
        ),
    }
    pprint.pprint(metrics)
    print("-" * 50)

    return metrics



def send_batch_request(txt_size):
    try:
        response_time = requests.post(
            "http://jpetstore.cerana.tech",
            headers={"Content-Type": "application/json"},
            data=json.dumps({"file_path": f"./{txt_size}.txt"}),
        ).json()["response_time"]
        return response_time
    except requests.exceptions.Timeout:
        print("The request timed out")
    except requests.exceptions.RequestException as e:
        print("An error occurred: ", e)

def convert_to_time_range(response_time):
    response_time += 60
    time_range = f"{int(response_time)}s"
    return time_range

def compute_performance_metrics(env_id, round, txt_size, prometheus_url):
    response_time = send_batch_request(txt_size)
    print(f"Response time: {response_time}")
    time_range = convert_to_time_range(response_time)
    metrics_data = retrieve_metrics(prometheus_url, time_range)
    externalDB_metrics_data = retrieve_externalDB_metrics(prometheus_url, time_range)

    try:
        metric = {
            "env_id": int(env_id),
            "total_request": -1,
            "round": int(round),
            "VU": int(txt_size.split("MB")[0]),
            "error_rate": -1,
            "response_time": response_time,
            "timestamp": int(time.time() * 1000),
            "usage_cpu_SUT": float(metrics_data["usage_cpu"][0]["value"][1]),
            "usage_cpu_DB": float(externalDB_metrics_data["usage_cpu"][0]["value"][1]),
            "saturation_cpu_SUT": float(metrics_data["saturation_cpu"][0]["value"][1]),
            
            # ============== No saturation_cpu for externalDB ============== 
            # "saturation_cpu_DB": float(externalDB_metrics_data["saturation_cpu"][0]["value"][1]), 
            # ============== No saturation_cpu for externalDB ============== 
            
            "saturation_cpu_DB": -1,
            "usage_mem_SUT": float(metrics_data["usage_mem"][0]["value"][1]),
            "usage_mem_DB": float(externalDB_metrics_data["usage_mem"][0]["value"][1]),
            "saturation_mem_SUT": float(metrics_data["saturation_mem"][0]["value"][1]),
            "saturation_mem_DB": float(externalDB_metrics_data["saturation_mem"][0]["value"][1]),
            "usage_read_disk_SUT": float(
                metrics_data["usage_read_disk"][0]["value"][1]
            ),
            "usage_read_disk_DB": float(externalDB_metrics_data["usage_read_disk"][0]["value"][1]),
            "usage_write_disk_SUT": float(
                metrics_data["usage_write_disk"][0]["value"][1]
            ),
            "usage_write_disk_DB": float(
                externalDB_metrics_data["usage_write_disk"][0]["value"][1]
            ),
            "usage_received_network_SUT": float(
                metrics_data["usage_received_network_SUT"][0]["value"][1]
            ),
            "usage_received_network_DB": float(
                externalDB_metrics_data["usage_received_network_DB"][0]["value"][1]
            ),
            "usage_transmitted_network_SUT": float(
                metrics_data["usage_transmitted_network_SUT"][0]["value"][1]
            ),
            "usage_transmitted_network_DB": float(
                externalDB_metrics_data["usage_transmitted_network_DB"][0]["value"][1]
            ),
        }
    except IndexError as e:
        print(f"Error retrieving metrics: {e}")
        metric = None
    return metric


def insert_data_to_mysql(data, mycursor, mydb):
    add_data = """
    INSERT INTO mysql.metric (
        env_id, total_request, round, VU, error_rate, response_time, timestamp, 
        usage_cpu_SUT, usage_cpu_DB, 
        saturation_cpu_SUT, saturation_cpu_DB, 
        usage_mem_SUT, usage_mem_DB,
        saturation_mem_SUT, saturation_mem_DB,
        usage_read_disk_SUT, usage_read_disk_DB,
        usage_write_disk_SUT, usage_write_disk_DB,
        usage_received_network_SUT, usage_received_network_DB,
        usage_transmitted_network_SUT, usage_transmitted_network_DB
    ) VALUES (
        %(env_id)s, %(total_request)s, %(round)s, %(VU)s, %(error_rate)s, %(response_time)s, %(timestamp)s,
        %(usage_cpu_SUT)s, %(usage_cpu_DB)s,
        %(saturation_cpu_SUT)s, %(saturation_cpu_DB)s,
        %(usage_mem_SUT)s, %(usage_mem_DB)s,
        %(saturation_mem_SUT)s, %(saturation_mem_DB)s,
        %(usage_read_disk_SUT)s, %(usage_read_disk_DB)s,
        %(usage_write_disk_SUT)s, %(usage_write_disk_DB)s,
        %(usage_received_network_SUT)s, %(usage_received_network_DB)s,
        %(usage_transmitted_network_SUT)s, %(usage_transmitted_network_DB)s
    )
    """

    try:
        mycursor.execute(add_data, data)
        mydb.commit()
    except Error as e:
        print(f"Error inserting data into MySQL: {e}")
        mydb.rollback()


def main():
    args = parse_arguments()
    mydb = connect_to_database()
    mycursor = mydb.cursor()
    prometheus_url = "http://140.119.163.226:30000"
    metric = compute_performance_metrics(
        args.env_id, args.round, args.txt_size, prometheus_url
    )
    print("-" * 50)
    pprint.pprint(metric)
    if metric is not None:
        insert_data_to_mysql(metric, mycursor, mydb)
    mycursor.close()
    mydb.close()


if __name__ == "__main__":
    main()
