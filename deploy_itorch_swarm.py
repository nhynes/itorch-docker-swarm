from configparser import RawConfigParser as ConfigParser
import argparse
import os
import time

import boto.ec2
from boto.ec2.blockdevicemapping import BlockDeviceMapping, BlockDeviceType

TIMEOUT_SECS = 180
POLL_INTERVAL = 15

NODE_INIT = """
#!/bin/bash
yum update
curl -sSL https://get.docker.com/ | sh
echo "OPTIONS+=\\" -H tcp://0.0.0.0:2376 -H unix:///var/run/docker.sock\\"" >> /etc/sysconfig/docker
service docker start
"""

HUB_INIT = """
hubip=$(ip -o -4 a show eth0 | awk '{print $4}' | sed 's/\/[0-9]\+$//')
docker run -d \
    -p 8500:8500 \
    --name=consul \
    progrium/consul -server -bootstrap
docker run -d \
    -p 3376:3376 \
    swarm manage \
    -H :3376 \
    --advertise=$hubip:3376 \
    consul://$hubip:8500
docker run \
    -p 8080:8080 -p 8081:8081 -p 80:8000 \
    -e "HUB_IP=$(ip -o -4 a show eth0 | awk '{print $4}' | sed 's/\/[0-9]\+$//')" \
    -e "OPEN_SESAME=%s" \
    quay.io/nhynes/jupyterhub
"""

NB_INIT = """
nodeip=$(ip -o -4 a show eth0 | awk '{print $4}' | sed 's/\/[0-9]\+$//')
docker pull quay.io/nhynes/itorch-singleuser
docker run -d \
    swarm join \
    --advertise=$nodeip:2376 \
    consul://%s:8500
"""


def req_instances(ec2, type, price, count=1, sec_groups=[], init='', **kwargs):
    user_data = NODE_INIT + init
    return ec2.request_spot_instances(price,
                                      'ami-31490d51', # amazon linux
                                      instance_type=type,
                                      count=count,
                                      security_group_ids=['sg-2ebbeb4a'] + sec_groups,
                                        # world ssh; vpc 2376
                                      key_name='nhynes_mit_nocal',
                                      placement='us-west-1c',
                                      subnet_id='subnet-3bc81d5f',
                                      user_data=user_data.encode('utf8'),
                                      **kwargs
                                     )

def poll(ec2, sirs):
    req_ids = [sir.id for sir in sirs]
    for _ in range(0, TIMEOUT_SECS + POLL_INTERVAL, POLL_INTERVAL):
        time.sleep(POLL_INTERVAL)
        sirs = ec2.get_all_spot_instance_requests(request_ids=req_ids)
        if all(sir.status.code == 'fulfilled' for sir in sirs):
            return sirs
    raise 'Instances did not spawn!'


#===============================================================================
parser = argparse.ArgumentParser()
parser.add_argument('sesame', help='Login password for SesameAuthenticator')

parser.add_argument('--hub-inst-type', default='m3.medium')
parser.add_argument('--hub-inst-price', default=0.03, type=float)

parser.add_argument('--num-nbs', default=1, type=int)
parser.add_argument('--nb-inst-type', default='c4.xlarge')
parser.add_argument('--nb-inst-price', default=0.20, type=float)
parser.add_argument('--nb-hdd', default=50, type=int)

parser.add_argument('--existing-hub')
args = parser.parse_args()
#===============================================================================

creds = ConfigParser()
creds.read(os.path.expanduser('~/.aws/credentials'))
access_key = creds.get('default', 'aws_access_key_id')
secret_key = creds.get('default', 'aws_secret_access_key')

ec2 = boto.ec2.connect_to_region('us-west-1',
                                 aws_access_key_id=access_key,
                                 aws_secret_access_key=secret_key)

if args.existing_hub is None:
    hub_sir = req_instances(ec2, args.hub_inst_type, args.hub_inst_price,
                            sec_groups=['sg-0dbeee69'], # world 80; vpc 3376, 8500
                            init=HUB_INIT % args.sesame)
    hub_sir = poll(ec2, hub_sir)
    hub_inst = ec2.get_only_instances([hub_sir[0].instance_id])[0]
    hub_inst.add_tag('Name', 'its-hub')
    hub_ip = hub_inst.private_ip_address
else:
    hub_ip = args.existing_hub

print('hub ips (public, private): (%s, %s)' % (hub_inst.ip_address, hub_ip))

dev_map = BlockDeviceMapping()
dev_map['/dev/xvda'] = BlockDeviceType(size=args.nb_hdd,
                                       volume_type='gp2',
                                       delete_on_termination=True)

nb_sirs = req_instances(ec2, args.nb_inst_type, args.nb_inst_price,
                        count=args.num_nbs, init=NB_INIT % hub_ip,
                        block_device_map=dev_map)
nb_sirs = poll(ec2, nb_sirs)
nb_insts = ec2.get_only_instances([nb_sir.instance_id for nb_sir in nb_sirs])

for i, nb_inst in enumerate(nb_insts):
    nb_inst.add_tag('Name', 'its-nb%d' % i)
