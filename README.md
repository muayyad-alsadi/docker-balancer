# Dynamic Loadbalancer for Docker

Listen to local docker events and update haproxy config accordingly.
Whenever a new container is added and running it will check to see if
it exports port `80/tcp` and has a special label or env called
`container_host` then it update `haproxy.cfg` based on `jinja2` template and validate it and reload it

## Usage

- `./update.py -1` will do it once
- `./update.py -w` will loop waiting for docker events

## Requirments and Installation

```
yum install haproxy python-docker-py python-jinja2
git clone https://github.com/muayyad-alsadi/docker-balancer.git
cd docker-balancer
cp docker-balancer.rc.in docker-balancer.rc
vim docker-balancer.rc # set sysadmin email
cp docker-balancer.service /etc/systemd/system/docker-balancer.service
systemctl daemon-reload
systemctl start docker-balancer
```

and here is an example

```
docker run -d -name my_wp -l container_host=wordpress.example.com wordpress
docker run -d -name my_wp2 -e container_host=wordpress2.example.com wordpress
```

