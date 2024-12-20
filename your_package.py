#! /opt/bitnami/miniforge/bin/python3

# You can add your custom code here

from pyspark.sql import SparkSession
import os
import socket
from pyspark import find_spark_home; 
from typing import Dict
from kubernetes import client, config


JUPYTERHUB_USER=os.environ['JUPYTERHUB_USER']
# Set Jupyterhub User as Spark User
os.environ['SPARK_USER'] = JUPYTERHUB_USER
SPARK_HOME=find_spark_home._find_spark_home()
IP = socket.gethostbyname(socket.gethostname())   # Get pod IP
namespace="default" # Specify your namespace
SPARK_DRIVER_HOST= f"{IP.replace('.', '-')}.{namespace}.pod.cluster.local" # you can create headless service but managing it, will be little hassle.
config.load_incluster_config()  # Load Kubernetes configuration
v1 = client.CoreV1Api() # Create a CoreV1Api instance

def __get_pods():
    pods = v1.list_namespaced_pod(namespace)
    user_pods=[]
    for pod in pods.items:
        if JUPYTERHUB_USER in pod.metadata.name:
            user_pods.append(pod)
    return user_pods

def delete_completed_pods() -> None:
    """
    Function to clear completed pods in a specified namespace for JUPYTERHUB_USER.

    """
    pods = __get_pods()
    for pod in pods:
        if pod.status.phase.lower() == 'succeeded':
            print(f"Deleting completed pod: {pod.metadata.name}")
            v1.delete_namespaced_pod(name=pod.metadata.name, namespace=namespace)

def get_executor_pods() -> None:
    """
    Function to fetch and print all pods in a specified namespace for JUPYTERHUB_USER.
    """
    try:
        # List pods in the specified namespace
        pods = __get_pods()
        for pod in pods:
            # Get pod status
            pod_status = pod.status.phase

            # Print pod details
            print(f"\n - Pod Name: {pod.metadata.name}, \t Status: {pod.status.phase}")

    except Exception as e:
        print(f"An error occurred: {e}")


def get_or_create_sparksession(appName: str = "", extra_spark_conf: Dict = None) -> SparkSession:
    """
    Get or create a SparkSession with optional appName and configuration dictionary.
    
    Parameters:
        appName (str): Name of the Spark application (default: "jhub-spark-JUPYTERHUB_USER").
        extra_spark_conf (Dict): A dictionary of Spark configurations (default: None).
        
    Returns:
        SparkSession: The created or retrieved SparkSession.
    """
    # PREREQUISITE BEFORE CREATING SPARK SESSION
    
    with open(f"{SPARK_HOME}/conf/spark-defaults.conf","r") as template:
        spark_config = template.read()
    
    config_lines = [line.strip() for line in spark_config.splitlines() if line.strip()]
    config = dict(line.split('=') for line in config_lines if '=' in line)
    config["spark.driver.host"] = SPARK_DRIVER_HOST
    config["spark.kubernetes.executor.podNamePrefix"] = f"executor-{JUPYTERHUB_USER}"
    
    if extra_spark_conf is not None:
        for k, v in extra_spark_conf.items():
            config[k]=v

    # Create SparkSession
    if len(appName) == 0:
        spark_builder = SparkSession.builder.appName(f"jhub-spark-{JUPYTERHUB_USER}")
    else:
        spark_builder = SparkSession.builder.appName(f"{appName}-jhub-spark-{JUPYTERHUB_USER}")
        
    for key, value in config.items():
        spark_builder = spark_builder.config(key, value)
    
    session = spark_builder.getOrCreate()
    return session  