#!/usr/bin/env python

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

import re
import optparse
from flask import Flask
from flask.ext.cors import CORS
from flask_restful import Resource, Api, reqparse
import ams_fs_core

APP_ENVIRONMENT = {
    'dataframe': None,
    'metrics': None,
    'fields_regex': re.compile(
        '(?P<metric>[A-Za-z0-9/_=-]+)(?:\._(?P<operation>avg|sum|min|max))?' +
        '\[(?P<start>\d+),(?P<end>\d+),(?P<limit>\d+)\]'),
    'fields_parser': None,
    'last_metric': ""

}


def setup_environment(input_dir):
    APP_ENVIRONMENT['metrics'] = ams_fs_core.read_metrics(input_dir, {})
    APP_ENVIRONMENT['dataframe'] = ams_fs_core.read_all_metric_files(input_dir)
    parser = reqparse.RequestParser()
    parser.add_argument('fields')
    APP_ENVIRONMENT['fields_parser'] = parser


def parse_fields():
    parsed_args = APP_ENVIRONMENT['fields_parser'].parse_args()
    fields = parsed_args.get('fields', '')
    match_obj = APP_ENVIRONMENT['fields_regex'].search(fields)
    if match_obj:
        return match_obj.groups()
    else:
        raise FieldsParseError('unknown fields ' + fields)


class FieldsParseError(Exception):
    pass


class HostsJson(Resource):
    def get(self):
        return ams_fs_core.get_hosts_json(APP_ENVIRONMENT['metrics'],
                                          APP_ENVIRONMENT['last_metric'])


class Artefacts(Resource):
    def get(self):
        return ams_fs_core.get_all_component_descriptors(
            APP_ENVIRONMENT['dataframe'])


class NodeManagerArtefacts(Resource):
    def get(self):
        return ams_fs_core.get_artifacts(APP_ENVIRONMENT['metrics'])


class NodeManagerMetricArtefacts(Resource):
    def get(self, service_id):
        return ams_fs_core.get_artifacts(APP_ENVIRONMENT['metrics'], service_id)[
            "items"][0]["artifacts"][0]


class Components(Resource):
    def get(self, component_id):
        try:
            metric, operation, start, end, limit = parse_fields()
            print metric, operation, start, end, limit
            APP_ENVIRONMENT['last_metric'] = metric
            return ams_fs_core.get_metrics_json(APP_ENVIRONMENT['dataframe'],
                                                metric,
                                                None, int(start), int(end),
                                                int(limit), operation)
        except FieldsParseError:
            return ams_fs_core.get_components_json(component_id)


class TimeSeriesJson(Resource):
    def get(self, host_id):

        try:
            metric, operation, start, end, limit = parse_fields()
            print metric, operation, start, end, limit
            return ams_fs_core.get_metrics_json(APP_ENVIRONMENT['dataframe'],
                                                metric,
                                                host_id, int(start), int(end),
                                                int(limit), operation)
        except FieldsParseError, e:
            return str(e), 404


if __name__ == '__main__':
    options_parser = optparse.OptionParser(usage="usage: %prog [options]")
    options_parser.set_description('''This python program is a thin REST server
    that implements a subset of the Ambari and Ambari metrics server interfaces.
    You can use it to visualize information exported by the AMS thin client.
    ''')

    options_parser.add_option("-i", "--input-dir", dest="input_dir",
                              default='/tmp',
                              help="Input directory for AMS metrics exports. [default: /tmp]")

    (options, args) = options_parser.parse_args()

    app = Flask(__name__)
    api = Api(app)
    cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

    api.add_resource(HostsJson, '/api/v1/clusters/test/hosts/')
    api.add_resource(TimeSeriesJson,
                     '/api/v1/clusters/test/hosts/<string:host_id>/host_components/EXPORT')
    api.add_resource(Artefacts, '/api/v1/stacks/HDP/versions/2.3/services')
    api.add_resource(Components,
                     '/api/v1/clusters/test/services/EXPORT/components/<string:component_id>')
    api.add_resource(NodeManagerMetricArtefacts,
                     '/api/v1/stacks/HDP/versions/2.3/services/<string:service_id>/artifacts/metrics_descriptor')

    setup_environment(options.input_dir)

    app.run(debug=True)
