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

import optparse
import sys
import os
import logging
import urllib2
import json
import datetime
import time

AMS_HOSTNAME = 'localhost'
AMS_PORT = '6188'
AMS_APP_ID = None
HOSTS_FILE = None
METRICS_FILE = None
OUT_DIR = None
PRECISION = 'minutes'
START_TIME = None
END_TIME = None

def get_collector_uri(metricNames, hostname = None):
  if hostname:
    return 'http://{0}:{1}/ws/v1/timeline/metrics?metricNames={2}&hostname={3}&appId={4}&startTime={5}&endTime={6}&precision={7}'\
      .format(AMS_HOSTNAME, AMS_PORT, metricNames, hostname, AMS_APP_ID,
              START_TIME, END_TIME, PRECISION)
  else:
    return 'http://{0}:{1}/ws/v1/timeline/metrics?metricNames={2}&appId={3}&startTime={4}&endTime={5}&precision={6}'\
      .format(AMS_HOSTNAME, AMS_PORT, metricNames, AMS_APP_ID, START_TIME,
              END_TIME, PRECISION)

def get_metrics(collector_uri):
  req = urllib2.Request(collector_uri)
  data = None
  try:
    data = urllib2.urlopen(req)
  except Exception as e:
    logger.error('Error on metrics GET request: %s' % collector_uri)
    logger.error(str(e))

  # Validate json before dumping
  json_data = None
  if data:
    try:
      json_data = json.loads(data.read())
    except Exception as e:
      logger.warn('Error parsing json data returned from URI: %s' % collector_uri)
      logger.debug(str(e))

  return json_data

def write_metrics_to_file(metrics, host = None):
  for metric in metrics:
    uri = get_collector_uri(metric, host)
    logger.info('Request URI: %s' % str(uri))
    metrics_json = get_metrics(uri)
    if metrics_json:
      if host:
        path = os.path.join(OUT_DIR, host, metric)
      else:
        path = os.path.join(OUT_DIR, metric)
      logger.info('Writing metric file: %s' % path)
      with open(path, 'w') as file:
        file.write(json.dumps(metrics_json))
  pass

def export_ams_metrics():
  if not os.path.exists(METRICS_FILE):
    logger.error('Metrics file is required.')
    sys.exit(1)

  logger.info('Reading metrics file.')
  metrics = []
  with open(METRICS_FILE, 'r') as file:
    for line in file:
      metrics.append(line.strip())
  pass

  logger.info('Reading hosts file.')
  hosts = []
  if HOSTS_FILE and os.path.exists(HOSTS_FILE):
    with open(HOSTS_FILE, 'r') as file:
      for line in file:
        hosts.append(line.strip())
  else:
    logger.info('No hosts file found, aggregate metrics will be exported.')

  logger.info('Creating output dir.')
  os.makedirs(OUT_DIR)

  if hosts:
    for host in hosts:
      os.makedirs(os.path.join(OUT_DIR, host)) # create host dir
      write_metrics_to_file(metrics, host)
  else:
    write_metrics_to_file(metrics, None)


  pass

def get_epoch(input):
  if (len(input) == 13):
    return int(input)
  elif (len(input) == 20):
    return int(time.mktime(datetime.datetime.strptime(input,'%Y-%m-%dT%H:%M:%SZ').timetuple())*1000)
  else:
    return -1

  pass

#
# Main.
#
def main():

  parser = optparse.OptionParser(usage="usage: %prog [options]")
  parser.set_description('This python program is a Ambari thin client and '
                         'supports export of ambari metric data for an app '
                         'from Ambari Metrics Service to a output dir. '
                         'The metrics will be exported to a file with name of '
                         'the metric and in a directory with the name as the '
                         'hostname under the output dir.')

  d = datetime.datetime.now()
  time_suffix = '{0}-{1}-{2}-{3}-{4}-{5}'.format(d.year, d.month, d.day,
                                                 d.hour, d.minute, d.second)
  print 'Time: %s' % time_suffix
  logfile = os.path.join('/tmp', 'ambari_metrics_export.out')
  output_dir = os.path.join('/tmp', 'ambari_metrics_export_' + time_suffix)

  parser.add_option("-v", "--verbose", dest="verbose", action="store_false",
                  default=False, help="output verbosity.")
  parser.add_option("-s", "--host", dest="server_hostname",
                  help="AMS host name.")
  parser.add_option("-p", "--port", dest="server_port",
                  default="6188" ,help="AMS port. [default: 6188]")
  parser.add_option("-a", "--app-id", dest="app_id",
                  help="AMS app id.")
  parser.add_option("-f", "--host-file", dest="hosts_file",
                  help="Host file with hostnames to query. New line separated.")
  parser.add_option("-m", "--metrics-file", dest="metrics_file",
                  help="Metrics file with metric names to query. New line separated.")
  parser.add_option("-o", "--output-dir", dest="output_dir", default=output_dir,
                  help="Output dir. [default: %s]" % output_dir)
  parser.add_option("-l", "--logfile", dest="log_file", default=logfile,
                  metavar='FILE', help="Log file. [default: %s]" % logfile)
  parser.add_option("-r", "--precision", dest="precision",
                  default='minutes', help="AMS API precision, default = minutes.")
  parser.add_option("-b", "--start_time", dest="start_time",
                    help="Start time in milliseconds since epoch or UTC timestamp in YYYY-MM-DDTHH:mm:ssZ format.")
  parser.add_option("-e", "--end_time", dest="end_time",
                    help="End time in milliseconds since epoch or UTC timestamp in YYYY-MM-DDTHH:mm:ssZ format.")

  (options, args) = parser.parse_args()

  global AMS_HOSTNAME
  AMS_HOSTNAME = options.server_hostname

  global AMS_PORT
  AMS_PORT = options.server_port

  global AMS_APP_ID
  AMS_APP_ID = options.app_id

  global HOSTS_FILE
  HOSTS_FILE = options.hosts_file

  global METRICS_FILE
  METRICS_FILE = options.metrics_file

  global PRECISION
  PRECISION = options.precision

  if options.log_file:
    logfile = options.log_file

  global logger
  logger = logging.getLogger('AmbariMetricsExport')
  formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
  filehandler = logging.FileHandler(logfile)
  consolehandler = logging.StreamHandler()
  filehandler.setFormatter(formatter)
  consolehandler.setFormatter(formatter)
  logger.addHandler(filehandler)
  logger.addHandler(consolehandler)
  # set verbose
  if options.verbose:
    #logging.basicConfig(level=logging.DEBUG)
    logger.setLevel(logging.DEBUG)
  else:
    #logging.basicConfig(level=logging.INFO)
    logger.setLevel(logging.INFO)


  if not options.metrics_file or not os.path.exists(options.metrics_file):
    logger.warn('No valid metrics file path provided.')
    logger.info('Aborting...')
    sys.exit(1)

  if options.output_dir and os.path.exists(options.output_dir):
    logger.warn('Output directory {0} already exists.'.format(options.output_dir))
    logger.info('Aborting...')
    sys.exit(1)

  if options.output_dir:
    output_dir = options.output_dir

  global OUT_DIR
  OUT_DIR = output_dir

  global START_TIME
  START_TIME = get_epoch(options.start_time)

  if START_TIME == -1:
    logger.warn('No start time provided, or it is in the wrong format. Please '
                'provide milliseconds since epoch or a value in YYYY-MM-DDTHH:mm:ssZ format')
    logger.info('Aborting...')
    sys.exit(1)

  global END_TIME
  END_TIME = get_epoch(options.end_time)

  if END_TIME == -1:
    logger.warn('No end time provided, or it is in the wrong format. Please '
                'provide milliseconds since epoch or a value in YYYY-MM-DDTHH:mm:ssZ format')
    logger.info('Aborting...')
    sys.exit(1)

  export_ams_metrics()

if __name__ == "__main__":
  try:
    main()
  except (KeyboardInterrupt, EOFError):
    print("\nAborting ... Keyboard Interrupt.")
    sys.exit(1)

