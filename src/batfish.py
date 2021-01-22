import os
import json

import urllib.request
import pandas as pd
from pybatfish.client.commands import *
from pybatfish.datamodel import *
from pybatfish.datamodel.answer import *
from pybatfish.datamodel.flow import *
from pybatfish.question import *
from pybatfish.question import bfq

# TODO pass in the BF host using envirnoment vars
# BF_HOST = os.getenv('BF_HOST', "10.90.226.72")
BF_HOST = os.getenv('BF_HOST')
NETWORK_NAME = "demo_network"
SNAPSHOT_NAME = "current"


print('Beginning file download with urllib2...')

url = 'http://i3.ytimg.com/vi/J---aiyznGQ/mqdefault.jpg'
urllib.request.urlretrieve(url, '/batfish/demo.zip')

SNAPSHOT_PATH = "/batfish/demo.zip"
SNAPSHOT_PATH = "/batfish/networks/demo"

# Now create the network and initialize the snapshot
bf_session.host = BF_HOST
load_questions()
bf_set_network(NETWORK_NAME)
# Can we download a zip of the configs to upload to batfish server?
# https://batfish.readthedocs.io/en/stable/batfish_commands.html#pybatfish.client.commands.bf_init_snapshot
bf_init_snapshot(SNAPSHOT_PATH, name=SNAPSHOT_NAME, overwrite=True)

node_name = "DMZ-LF18"  # The router to change
filter_name = "demo"      # Name of the ACL to change

# The traffic to allow
# change_traffic = HeaderConstraints(dstIps="18.18.18.0/27",
#                                    ipProtocols=["tcp"],
#                                    dstPorts="80, 8080")
# 158.175.122.199
# TODO Pull destinations to be checked
with open('aclTest/permit.json') as permit_file:
    data = json.load(permit_file)
    for p in data['permit']:
        change_traffic = HeaderConstraints(dstIps=p.dstIps,
                                   ipProtocols=p.ipProtocols,
                                   dstPorts=p.dstPorts)
        answer = bfq.searchFilters(headers=change_traffic,
                                   filters=filter_name,
                                   nodes=node_name,
                                   action="permit").answer(
                                       snapshot=SNAPSHOT_NAME)
        print(answer.frame())

# Check if the intended traffic is already permitted in the current snapshot
# TODO : grab a list of nodes to query against
# answer = bfq.searchFilters(headers=change_traffic,
#                            filters=filter_name,
#                            nodes=node_name,
#                            action="permit").answer(
#                                snapshot=SNAPSHOT_NAME)
# 
# If the frame is empty, then the host traffic given was not allowed and we should fail with exit code 1
# otherwise, exit normally with exit code 0
if answer.frame().empty:
    exit(1)
else:
    exit(0)
