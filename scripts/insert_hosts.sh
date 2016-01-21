#!/bin/bash
if [ -z $1 ]; then
  echo "Provide hostnames file as argument"
  exit 1
fi
COUNTER=100
while IFS='' read -r line || [[ -n "$line" ]]; do
    echo "Deleting host data for : $line"
    su - postgres -c 'psql -U postgres ambari -c "delete from ambari.hoststate where host_id = '"'"''''$COUNTER''''"'"';"'
    su - postgres -c 'psql -U postgres ambari -c "delete from ambari.clusterhostmapping where host_id = '"'"''''$COUNTER''''"'"';"'
    su - postgres -c 'psql -U postgres ambari -c "delete from ambari.hosts where host_id = '"'"''''$COUNTER''''"'"';"'

    echo "Adding host to ambari database: $line"    
    #su - postgres -c 'psql -c  "\c ambari; select * from ambari.hosts;"'
    su - postgres -c 'psql -U postgres ambari -c "insert into ambari.hosts values ('"'"''''$COUNTER''''"'"', '"'"''''$line''''"'"', 4, 4, '"'"''"'"', '"'"''"'"', '"'"''"'"', '"'"''"'"', '"'"''"'"', '"'"''"'"', 1453238404725, '"'"''"'"', '"'"''"'"', '"'"'centos6'"'"', '"'"''"'"', 16334600)"'
    echo 'Insert into hosts succeeded'
    su - postgres -c 'psql -U postgres ambari -c "insert into ambari.hoststate values ('"'"'{"\""version"\"":"\""2.2.1.0"\""}'"'"', 15147476, '"'"'INIT'"'"', '"'"'{"\""healthStatus"\"":"\""UNKNOWN"\"","\""healthReport"\"":"\"""\""}'"'"', '"'"''''$COUNTER''''"'"', 1453238404725, NULL)"'
    echo "Insert into hoststate succeeded"
    su - postgres -c 'psql -U postgres ambari -c "insert into ambari.clusterhostmapping values (2, '"'"''''$COUNTER''''"'"')"'
    echo "Insert into clusterhostmapping succeeded"
    su - postgres -c 'psql -U postgres ambari -c "insert into ambari.hostcomponentdesiredstate values (2, '"'"'NODEMANAGER'"'"', 5, '"'"'INSTALLED'"'"', '"'"''''$COUNTER''''"'"', '"'"'YARN'"'"', NULL, '"'"'OFF'"'"', '"'"'UNSECURED'"'"', 0)"'
    su - postgres -c 'psql -U postgres ambari -c "insert into ambari.hostcomponentstate values ('"'"''''$COUNTER''''"'"', 2, '"'"'NODEMANAGER'"'"', '"'"'2.3.6.0-3511'"'"', 5, '"'"'INSTALLED'"'"', '"'"''''$COUNTER''''"'"', '"'"'YARN'"'"', '"'"'NONE'"'"', '"'"'UNSECURED'"'"')"'
    #su - postgres -c 'psql -U postgres ambari -c "update hoststate set maintenance_state=NULL where host_id='"'"''''$COUNTER''''"'"';"' 
    su - postgres -c 'psql -U postgres ambari -c "select * from ambari.hosts where host_name='"'"''''$line''''"'"';"'
    let COUNTER=COUNTER+1
done < "$1"
