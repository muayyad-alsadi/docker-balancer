#! /bin/bash

cd `dirname $0`

source ./docker-balancer.rc

[ -e /etc/sysconfig/haproxy ] && source /etc/sysconfig/haproxy
email=${email:-root@localhost.localdomain}

backup="/etc/haproxy/haproxy.cfg.old.$$"

touch /etc/haproxy/haproxy.cfg
cp -a /etc/haproxy/haproxy.cfg "$backup"
cp ./haproxy.cfg /etc/haproxy/haproxy.cfg

output=`haproxy -c -f /etc/haproxy/haproxy.cfg $OPTIONS 2>&1` || {
    echo -e "Reply-To: $email\nSubject: invalid haproxy config on `hostname`\n\n$output" | sendmail $email
    cp "$backup" /etc/haproxy/haproxy.cfg
    exit -1
}

/usr/bin/systemctl reload haproxy

echo -e "Reply-To: $email\nSubject: loadbalancer on `hostname` deployed\n\ndeployed at `date`" | sendmail $email

