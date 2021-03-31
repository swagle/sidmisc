'''
Licensed to the Apache Software Foundation (ASF) under one
or more contributor license agreements.  See the NOTICE file
distributed with this work for additional information
regarding copyright ownership.  The ASF licenses this file
to you under the Apache License, Version 2.0 (the
"License"); you may not use this file except in compliance
with the License.  You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
'''

import os
import os.path
import json
import pandas as pd


def get_metric_paths_dict(metric, metrics_data):
    result = temp = {}
    paths = metric.split('/')
    for path in paths[:-1]:
        temp[path] = {}
        temp = temp[path]

    temp[paths[-1]] = metrics_data
    return result


def get_metrics_json(data, metric, host, start, end, limit, operation):
    result = {
        "href": "",
        "HostRoles": {
            "cluster_name": "test",
            "component_name": "EXPORT",
            "host_name": host
        },
        "host": {
            "href": ""
        },
    }

    if operation:
        query_results = data[(data.metricname == metric)
                             & (start <= data.timestamp) & (
                             data.timestamp <= end)][
            ['metricvalue', 'timestamp']].groupby(['timestamp'])
        if operation == 'avg':
            query_results = query_results['metricvalue'].mean()
        elif operation == "min":
            query_results = query_results['metricvalue'].min()
        elif operation == "max":
            query_results = query_results['metricvalue'].max()
        elif operation == "sum":
            query_results = query_results['metricvalue'].sum()
        query_results = query_results.reset_index()

        query_results = query_results.sort_values(['timestamp'])[
            ['metricvalue', 'timestamp']].values.tolist()
        metric = metric + "._" + operation
    else:
        query_results = data[
            (data.hostname == host)
            & (data.metricname == metric)
            & (start <= data.timestamp) & (data.timestamp <= end)].sort_values(
            ['timestamp'])[['metricvalue', 'timestamp']].values.tolist()

    metric_dict = get_metric_paths_dict(metric, query_results)
    result.update(metric_dict)
    return result


def load_dataframe(filename, source):
    with open(filename) as f:
        jason_obj = json.load(f)

    if not jason_obj['metrics']:
        return source

    metrics = jason_obj['metrics'][0]
    hostname = metrics['hostname']
    appid = metrics['appid']
    real_metrics = metrics['metrics']
    metricname = "metrics/" + metrics['metricname'].replace('.', '/')
    print "Loaded Metric " + metricname

    df = pd.DataFrame(columns=('hostname', 'appid', 'timestamp', 'metricvalue',
                               'metricname'), index=['metricname',
                                                     'hostname', 'timestamp'])
    for timestamp, metricvalue in real_metrics.items():
        timestamp_val = int(timestamp) / 1000
        df = df.append({'hostname': str(hostname), 'appid': str(appid),
                        'timestamp': timestamp_val,
                        'metricvalue': float(metricvalue),
                        'metricname': str(metricname)}, ignore_index=True)

    if source is not None and not source.empty:
        # return pd.concat([source[~source.index.isin(df.index)], df])
        return source.append(df)
    else:
        return df


def get_components_json(component_id):
    return {
        "href": "",
        "ServiceComponentInfo": {
            "cluster_name": "test",
            "component_name": component_id,
            "service_name": "EXPORT"
        }
    }


def get_metrics_dirs(d):
    for o in os.listdir(d):
        if 'ambari_metrics_export_' in o and os.path.isdir(os.path.join(d, o)):
            yield os.path.join(d, o)


def read_all_metric_files(root_dir):
    df = None
    for metric_dir in get_metrics_dirs(root_dir):
        print "Processing directory " + metric_dir
        for root, dirnames, filenames in os.walk(metric_dir):
            for f in filenames:
                full_path = os.path.join(root, f)
                print "Processing file " + full_path
                df = load_dataframe(full_path, df)
    return df


def read_metrics(input_dir, metrics):
    for metrics_dir in get_metrics_dirs(input_dir):
        for host in os.listdir(metrics_dir):
            host_dir = os.path.join(metrics_dir, host)
            for metric in os.listdir(host_dir):
                metric_file = os.path.join(host_dir, metric)
                metric = "metrics/" + metric.replace('.', '/')
                if metric not in metrics:
                    metrics[metric] = {}
                if host not in metrics[metric]:
                    metrics[metric][host] = []
                metrics[metric][host].append(metric_file)

    return metrics


def get_all_component_descriptors(data):
    return {
        "href": "",
        "items": [
            {
                "href": "",
                "StackServices": {
                    "service_name": "EXPORT",
                    "stack_name": "HDP",
                    "stack_version": "2.3"
                },
                "artifacts": [
                    {
                        "href": "",
                        "Artifacts": {
                            "artifact_name": "metrics_descriptor",
                            "service_name": "EXPORT",
                            "stack_name": "HDP",
                            "stack_version": "2.3"
                        },
                        "artifact_data": {
                            "EXPORT": {
                                "EXPORT": {
                                    "Component": [
                                        {
                                            "type": "ganglia",
                                            "properties": None,
                                            "metrics": {
                                                "default": {}
                                            }
                                        }
                                    ]
                                }
                            }
                        }
                    }
                ]
            }
        ]
    }


def get_artifacts(metrics, service_id):
    exported_obj = {
        "href": "",
        "items": [
            {
                "href": "",
                "StackServices": {
                    "service_name": "EXPORT",
                    "stack_name": "HDP",
                    "stack_version": "2.3"
                },
                "artifacts": [
                    {
                        "href": "",
                        "Artifacts": {
                            "artifact_name": "metrics_descriptor",
                            "service_name": "EXPORT",
                            "stack_name": "HDP",
                            "stack_version": "2.3"
                        },
                        "artifact_data": {
                            "EXPORT": {
                                "EXPORT": {
                                    "Component": [
                                        {
                                            "type": "ganglia",
                                            "properties": None,
                                            "metrics": {
                                                "default": {}
                                            }
                                        }
                                    ]
                                }
                            }
                        }
                    }
                ]
            }
        ]
    }
    exported_obj["items"][0]["artifacts"][0]["artifact_data"][
        "EXPORT"]["EXPORT"]["Component"][0]["metrics"][
        "default"] = get_metrics_string(metrics)
    return exported_obj


def get_metrics_string(metrics):
    metrics_obj = {}
    for metric in metrics:
        metrics_obj[metric] = {
            'pointInTime': True,
            'temporal': True,
            'amsHostMetric': False,
            'unit': "unitless",
            'name': metric
        }

    return metrics_obj


def get_hosts_json(metrics, metric):
    host_names = []
    if metric:
        host_names = metrics[metric].keys()
    else:
        for v in metrics.values():
            host_names += v.keys()
            host_names = list(set(host_names))
    hosts = []
    for host in host_names:
        hosts.append(
            {
                "href": "",
                "Hosts": {
                    "cluster_name": "test",
                    "host_name": host
                }
            })
    return {'href': '', 'items': hosts}
