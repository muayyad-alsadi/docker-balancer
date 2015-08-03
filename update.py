#! /bin/python

import sys, os, os.path

from collections import defaultdict
from jinja2 import Environment, FileSystemLoader
from docker import Client

here = os.path.dirname(__file__)
template_env = Environment(loader=FileSystemLoader(os.path.join(here, 'templates')))

def reconfig_haproxy(docker):
    hosts=defaultdict(list)
    for cn in docker.containers():
        c_id=cn['Id']
        c_details=docker.inspect_container(c_id)
        is_running=c_details[u'State'][u'Running']
        c_env = c_details[u'Config'].get(u'Labels', {}) or {}
        c_env_unparsed = c_details[u'Config'].get(u'Env', None) or []
        for env_entry in c_env_unparsed:
            key,value=env_entry.split('=', 1)
            c_env[key]=value

        host=c_env.get('container_host', None)
        ip=c_details[u'NetworkSettings'][u'IPAddress']
        is_web=c_details[u'NetworkSettings'][u'Ports'].has_key(u'80/tcp')
        # c_details[u'Volumes'] # /var/lib/docker/vfs/dir/
        if is_running and is_web and host:
            hosts[host].append(ip)
    template = template_env.get_template('haproxy.cfg.j2')
    f=open(os.path.join(here, 'haproxy.cfg'), 'w+')
    f.truncate()
    f.write(template.render(hosts=hosts))
    f.close()
    os.system(os.path.join(here,'test_n_reload.sh'))

def loop(docker):
    print "waiting for docker events"
    watch_set=set(('die','start',))
    for event in docker.events(decode=True):
        # it looks like this {"status":"die","id":"123","from":"foobar/eggs:latest","time":1434047926}
        if event['status'] in watch_set:
            reconfig_haproxy(docker)

def usage():
    print "pass -w to wait/watch for changes"
    print "pass -1 to run once"

def main():
    docker = Client(base_url='unix://var/run/docker.sock')
    if len(sys.argv)==2:
       if sys.argv[1]=='-w':
            reconfig_haproxy(docker)
            loop(docker)
       elif sys.argv[1]=='-1':
            reconfig_haproxy(docker)
       else:
            usage()
    else:
            usage()

main()
