# Table of contents
1. [AMS Export Tool](#introduction)
2. [Visualizing AMS Export Data](#paragraph1)
    1. [Prerequisites](#subparagraph1)
    2. [Analysis](#subparagraph2)
3. [Metric Names](#metricnames)
   * [ResourceManager](#rmmetrics)
   * [RM Queue Metrics](#rmqueuemetrics)
   * [NodeManager](#nmmetrics)
   * [RM RPC Metrics](#nmrpcmetrics)
   * [RPC Metrics](#nodemanager)
   * [NM RPC Metrics](#nmrpcmetrics)
   * [MetricsSystem Metrics](#metricsmetrics)
   * [JVM Metrics](#jvmmetrics)
   * [Host Metrics](#hostmetrics)

There are two scripts in this directory:

## AMS Export Tool <a name="amsexporttool"></a>
```
python export_ams_metrics.py -s ams-host -a RESOURCEMANAGER -f hosts.txt -m rm-metrics -b 2016-03-06T01:01:01Z -e 2016-03-11T01:01:01Z

Usage: export_ams_metrics.py [options]

This python program is a Ambari thin client and supports export of ambari
metric data for an app from Ambari Metrics Service to a output dir. The
metrics will be exported to a file with name of the metric and in a directory
with the name as the hostname under the output dir.

Options:
  -h, --help            show this help message and exit
  -v, --verbose         output verbosity.
  -s SERVER_HOSTNAME, --host=SERVER_HOSTNAME
                        AMS host name.
  -p SERVER_PORT, --port=SERVER_PORT
                        AMS port. [default: 6188]
  -a APP_ID, --app-id=APP_ID
                        AMS app id.
  -f HOSTS_FILE, --host-file=HOSTS_FILE
                        Host file with hostnames to query. New line separated.
  -m METRICS_FILE, --metrics-file=METRICS_FILE
                        Metrics file with metric names to query. New line
                        separated.
  -o OUTPUT_DIR, --output-dir=OUTPUT_DIR
                        Output dir. [default:
                        /tmp/ambari_metrics_export_2016-3-12-6-47-46]
  -l FILE, --logfile=FILE
                        Log file. [default: /tmp/ambari_metrics_export.out]
  -r PRECISION, --precision=PRECISION
                        AMS API precision, default = minutes.
  -b START_TIME, --start_time=START_TIME
                        Start time in milliseconds since epoch or UTC
                        timestamp in YYYY-MM-DDTHH:mm:ssZ format.
  -e END_TIME, --end_time=END_TIME
                        End time in milliseconds since epoch or UTC timestamp
                        in YYYY-MM-DDTHH:mm:ssZ format.
```
This will produce a directory of the form ambari_metrics_export_2016-3-12-6-47-46.
Zip the directory and upload to the support case.

## Visualizing AMS Export Data within Grafana <a name="paragraph1"></a>

We use AMS Export Web Service to visualize AMS exports. Here are the steps to get it going:

### Pre-requisites (one time only) <a name="subparagraph1"></a>
1. Install Ambari-Grafana within your Linux VM from https://github.com/u39kun/ambari-grafana
   1. sudo yum install https://grafanarel.s3.amazonaws.com/builds/grafana-2.6.0-1.x86_64.rpm
   2. sudo wget https://github.com/u39kun/ambari-grafana/raw/master/dist/ambari-grafana.tgz
   3. sudo tar zxvf ambari-grafana.tgz -C /usr/share/grafana/public/app/plugins/datasource
   4. sudo service grafana-server start

2. Create the AMS Export Grafana Datasource:
   1. Click on Data Sources
   2. Click on Data Sources > Add New
   3. Pick Ambari as the type of data source
   4. Speficy the URL to your AMS Export Web Service (usually http://localhost:5000)
   5. Ensure the Access dropdown is set to direct and not proxy
   6. Fill in anything for name, cluster, stack, version. we dont use them

3. Install the python environment
   1. virtualenv venv
   2. source venv/bin/activate
   3. pip install -r requirements.txt

### For each analysis<a name="subparagraph2"></a>
1. Copy the AMS export directory to your file system, lets say it is at ~/scratch/ambari_metrics_export_2016-3-12-6-47-46
2. Start the AMS Export Web Service:
```
venv/bin/python ams_fs_ws.py -i ~/scratch/
```
3. Open Grafana Dashboards, add panels with your data source
   1. Select EXPORT from the drop down for component or type it in
   2. Select the metric name
   3. Select the host

### Known issues:
1. As you attempt to add a metric to a panel you might see an error like "Undefined" from the auto-complete system.

## Metric Names <a name="metricnames"></a>
How do I get the metric names:

The real way is from the AMS Phoenix database and/or metadata service:
```
select  distinct(metric_name)
from METRIC_AGGREGATE_DAILY
where app_id = 'resourcemanager
```

As of HDP 2.3.4 here are some interesting metrics:

## ResourceManager metrics <a name="rmmetrics"></a>
ugi.UgiMetrics.GetGroupsAvgTime  
ugi.UgiMetrics.GetGroupsNumOps  
ugi.UgiMetrics.LoginFailureAvgTime  
ugi.UgiMetrics.LoginFailureNumOps  
ugi.UgiMetrics.LoginSuccessAvgTime  
ugi.UgiMetrics.LoginSuccessNumOps  
yarn.ClusterMetrics.AMLaunchDelayAvgTime  
yarn.ClusterMetrics.AMLaunchDelayNumOps  
yarn.ClusterMetrics.AMRegisterDelayAvgTime  
yarn.ClusterMetrics.AMRegisterDelayNumOps  
yarn.ClusterMetrics.NumActiveNMs  
yarn.ClusterMetrics.NumDecommissionedNMs  
yarn.ClusterMetrics.NumLostNMs  
yarn.ClusterMetrics.NumRebootedNMs  
yarn.ClusterMetrics.NumUnhealthyNMs  

## Per Queue metrics <a name="rmqueuemetrics"></a>
yarn.QueueMetrics.Queue=root.AMResourceLimitMB  
yarn.QueueMetrics.Queue=root.AMResourceLimitVCores  
yarn.QueueMetrics.Queue=root.ActiveApplications  
yarn.QueueMetrics.Queue=root.ActiveUsers  
yarn.QueueMetrics.Queue=root.AggregateContainersAllocated  
yarn.QueueMetrics.Queue=root.AggregateContainersReleased  
yarn.QueueMetrics.Queue=root.AggregateNodeLocalContainersAllocated  
yarn.QueueMetrics.Queue=root.AggregateOffSwitchContainersAllocated  
yarn.QueueMetrics.Queue=root.AggregateRackLocalContainersAllocated  
yarn.QueueMetrics.Queue=root.AllocatedContainers  
yarn.QueueMetrics.Queue=root.AllocatedMB  
yarn.QueueMetrics.Queue=root.AllocatedVCores  
yarn.QueueMetrics.Queue=root.AppAttemptFirstContainerAllocationDelayAvgTime  
yarn.QueueMetrics.Queue=root.AppAttemptFirstContainerAllocationDelayNumOps  
yarn.QueueMetrics.Queue=root.AppsCompleted  
yarn.QueueMetrics.Queue=root.AppsFailed  
yarn.QueueMetrics.Queue=root.AppsKilled  
yarn.QueueMetrics.Queue=root.AppsPending  
yarn.QueueMetrics.Queue=root.AppsRunning  
yarn.QueueMetrics.Queue=root.AppsSubmitted  
yarn.QueueMetrics.Queue=root.AvailableMB  
yarn.QueueMetrics.Queue=root.AvailableVCores  
yarn.QueueMetrics.Queue=root.PendingContainers  
yarn.QueueMetrics.Queue=root.PendingMB  
yarn.QueueMetrics.Queue=root.PendingVCores  
yarn.QueueMetrics.Queue=root.ReservedContainers  
yarn.QueueMetrics.Queue=root.ReservedMB  
yarn.QueueMetrics.Queue=root.ReservedVCores  
yarn.QueueMetrics.Queue=root.UsedAMResourceMB  
yarn.QueueMetrics.Queue=root.UsedAMResourceVCores  

## RM RPC Metrics <a name="rmrpcmetrics"></a>
rpcdetailed.rpcdetailed.AllocateAvgTime  
rpcdetailed.rpcdetailed.AllocateNumOps  
rpcdetailed.rpcdetailed.FinishApplicationMasterAvgTime  
rpcdetailed.rpcdetailed.FinishApplicationMasterNumOps  
rpcdetailed.rpcdetailed.ForceKillApplicationAvgTime  
rpcdetailed.rpcdetailed.ForceKillApplicationNumOps  
rpcdetailed.rpcdetailed.GetApplicationReportAvgTime  
rpcdetailed.rpcdetailed.GetApplicationReportNumOps  
rpcdetailed.rpcdetailed.GetApplicationsAvgTime  
rpcdetailed.rpcdetailed.GetApplicationsNumOps  
rpcdetailed.rpcdetailed.GetClusterMetricsAvgTime  
rpcdetailed.rpcdetailed.GetClusterMetricsNumOps  
rpcdetailed.rpcdetailed.GetClusterNodeLabelsAvgTime  
rpcdetailed.rpcdetailed.GetClusterNodeLabelsNumOps  
rpcdetailed.rpcdetailed.GetClusterNodesAvgTime  
rpcdetailed.rpcdetailed.GetClusterNodesNumOps  
rpcdetailed.rpcdetailed.GetNewApplicationAvgTime  
rpcdetailed.rpcdetailed.GetNewApplicationNumOps  
rpcdetailed.rpcdetailed.GetQueueInfoAvgTime  
rpcdetailed.rpcdetailed.GetQueueInfoNumOps  
rpcdetailed.rpcdetailed.GetQueueUserAclsAvgTime  
rpcdetailed.rpcdetailed.GetQueueUserAclsNumOps  
rpcdetailed.rpcdetailed.NodeHeartbeatAvgTime  
rpcdetailed.rpcdetailed.NodeHeartbeatNumOps  
rpcdetailed.rpcdetailed.RegisterApplicationMasterAvgTime  
rpcdetailed.rpcdetailed.RegisterApplicationMasterNumOps  
rpcdetailed.rpcdetailed.RegisterNodeManagerAvgTime  
rpcdetailed.rpcdetailed.RegisterNodeManagerNumOps  
rpcdetailed.rpcdetailed.SubmitApplicationAvgTime  
rpcdetailed.rpcdetailed.SubmitApplicationNumOps  

## Generic RPC Metrics <a name="rpcmetrics"></a>
rpc.rpc.CallQueueLength  
rpc.rpc.NumOpenConnections  
rpc.rpc.ReceivedBytes  
rpc.rpc.RpcAuthenticationFailures  
rpc.rpc.RpcAuthenticationSuccesses  
rpc.rpc.RpcAuthorizationFailures  
rpc.rpc.RpcAuthorizationSuccesses  
rpc.rpc.RpcClientBackoff  
rpc.rpc.RpcProcessingTimeAvgTime  
rpc.rpc.RpcProcessingTimeNumOps  
rpc.rpc.RpcQueueTimeAvgTime  
rpc.rpc.RpcQueueTimeNumOps  
rpc.rpc.RpcSlowCalls  
rpc.rpc.SentBytes  

## JVM Metrics <a name="jvmmetrics"></a>
jvm.JvmMetrics.GcCount  
jvm.JvmMetrics.GcCountPS MarkSweep  
jvm.JvmMetrics.GcCountPS Scavenge  
jvm.JvmMetrics.GcTimeMillis  
jvm.JvmMetrics.GcTimeMillisPS MarkSweep  
jvm.JvmMetrics.GcTimeMillisPS Scavenge  
jvm.JvmMetrics.LogError  
jvm.JvmMetrics.LogFatal  
jvm.JvmMetrics.LogInfo  
jvm.JvmMetrics.LogWarn  
jvm.JvmMetrics.MemHeapCommittedM  
jvm.JvmMetrics.MemHeapMaxM  
jvm.JvmMetrics.MemHeapUsedM  
jvm.JvmMetrics.MemMaxM  
jvm.JvmMetrics.MemNonHeapCommittedM  
jvm.JvmMetrics.MemNonHeapMaxM  
jvm.JvmMetrics.MemNonHeapUsedM  
jvm.JvmMetrics.ThreadsBlocked  
jvm.JvmMetrics.ThreadsNew  
jvm.JvmMetrics.ThreadsRunnable  
jvm.JvmMetrics.ThreadsTerminated  
jvm.JvmMetrics.ThreadsTimedWaiting  
jvm.JvmMetrics.ThreadsWaiting  

## Metrics on Metrics <a name="metricsmetrics"></a>
metricssystem.MetricsSystem.DroppedPubAll  
metricssystem.MetricsSystem.NumActiveSinks  
metricssystem.MetricsSystem.NumActiveSources  
metricssystem.MetricsSystem.NumAllSinks  
metricssystem.MetricsSystem.NumAllSources  
metricssystem.MetricsSystem.PublishAvgTime  
metricssystem.MetricsSystem.PublishNumOps  
metricssystem.MetricsSystem.Sink_timelineAvgTime  
metricssystem.MetricsSystem.Sink_timelineDropped  
metricssystem.MetricsSystem.Sink_timelineNumOps  
metricssystem.MetricsSystem.Sink_timelineQsize  
metricssystem.MetricsSystem.SnapshotAvgTime  
metricssystem.MetricsSystem.SnapshotNumOps  

## NodeManager Metrics <a name="nmmetrics"></a>
yarn.NodeManagerMetrics.AllocatedContainers  
yarn.NodeManagerMetrics.AllocatedGB  
yarn.NodeManagerMetrics.AllocatedVCores  
yarn.NodeManagerMetrics.AvailableGB  
yarn.NodeManagerMetrics.AvailableVCores  
yarn.NodeManagerMetrics.BadLocalDirs  
yarn.NodeManagerMetrics.BadLogDirs  
yarn.NodeManagerMetrics.ContainerLaunchDurationAvgTime  
yarn.NodeManagerMetrics.ContainerLaunchDurationNumOps  
yarn.NodeManagerMetrics.ContainersCompleted  
yarn.NodeManagerMetrics.ContainersFailed  
yarn.NodeManagerMetrics.ContainersIniting  
yarn.NodeManagerMetrics.ContainersKilled  
yarn.NodeManagerMetrics.ContainersLaunched  
yarn.NodeManagerMetrics.ContainersRunning  
yarn.NodeManagerMetrics.GoodLocalDirsDiskUtilizationPerc  
yarn.NodeManagerMetrics.GoodLogDirsDiskUtilizationPerc  

## NodeManager UGI Metrics <a name="nmugimetrics"></a>
ugi.UgiMetrics.GetGroupsAvgTime  
ugi.UgiMetrics.GetGroupsNumOps  
ugi.UgiMetrics.LoginFailureAvgTime  
ugi.UgiMetrics.LoginFailureNumOps  
ugi.UgiMetrics.LoginSuccessAvgTime  
ugi.UgiMetrics.LoginSuccessNumOps  

## NodeManager RPC Metrics <a name="nmrpcmetrics"></a>
rpcdetailed.rpcdetailed.GetContainerStatusesAvgTime  
rpcdetailed.rpcdetailed.GetContainerStatusesNumOps  
rpcdetailed.rpcdetailed.HeartbeatAvgTime  
rpcdetailed.rpcdetailed.HeartbeatNumOps  
rpcdetailed.rpcdetailed.NullPointerExceptionAvgTime  
rpcdetailed.rpcdetailed.NullPointerExceptionNumOps  
rpcdetailed.rpcdetailed.StartContainersAvgTime  
rpcdetailed.rpcdetailed.StartContainersNumOps  
rpcdetailed.rpcdetailed.StopContainersAvgTime  
rpcdetailed.rpcdetailed.StopContainersNumOps  

## NodeManager Shuffle Service Metrics <a name="nmmrshufflemetrics"></a>
mapred.ShuffleMetrics.ShuffleConnections  
mapred.ShuffleMetrics.ShuffleOutputBytes  
mapred.ShuffleMetrics.ShuffleOutputsFailed  
mapred.ShuffleMetrics.ShuffleOutputsOK  

## Host Metrics <a name="hostmetrics"></a>
bytes_in  
bytes_out  
cpu_idle  
cpu_intr  
cpu_nice  
cpu_num  
cpu_sintr 
cpu_steal  
cpu_system  
cpu_user  
cpu_wio  
disk_free  
disk_percent  
disk_total  
disk_used  
load_fifteen  
load_five  
load_one  
mem_buffered  
mem_cached  
mem_free  
mem_shared  
mem_total  
mem_used  
pkts_in  
pkts_out  
proc_run  
proc_total  
read_bps  
read_bytes  
read_count  
read_time  
swap_free  
write_bps  
write_bytes  
write_count  
write_time  



