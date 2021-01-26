import os
import json
import requests

import pandas as pd
from pybatfish.client.commands import *
from pybatfish.datamodel import *
from pybatfish.datamodel.answer import *
from pybatfish.datamodel.flow import *
from pybatfish.question import *
from pybatfish.question import bfq

BF_HOST = os.getenv('BF_HOST')
GITLAB_ARTIFACT_URL = os.getenv('GITLAB_ARTIFACT_URL')
NETWORK_NAME = "demo_network"
SNAPSHOT_NAME = "new"
SNAPSHOT_PATH = "/batfish/demo.zip"
GITLAB_PROJECT_ID = os.getenv('GITLAB_PROJECT_ID')
GITLAB_API_URL = "http://dmz-gitlab.sjc.aristanetworks.com/api/v4"
PRIVATE_TOKEN = os.getenv('GITLAB_PRIVATE_TOKEN')


joburl = GITLAB_API_URL + "/projects/" + GITLAB_PROJECT_ID + "/jobs"
tokenheader = {'PRIVATE-TOKEN':  PRIVATE_TOKEN}
# print(joburl)
resp = requests.get(joburl, headers=tokenheader)
# print(resp.json())
jobs = resp.json()
jobid = 0
for job in jobs:
    if job['name'] == 'buildconfigs':
        jobid = job['id']
        break
af_filename = "demo.zip"
artifact_url = GITLAB_API_URL + "/projects/" + GITLAB_PROJECT_ID + \
    "/jobs/" + str(jobid) + "/artifacts/" + af_filename
resp = requests.get(artifact_url, headers=tokenheader, stream=True)
with open(SNAPSHOT_PATH, 'wb') as fd:
    for chunk in resp.iter_content(chunk_size=128):
        fd.write(chunk)

# Now create the network and initialize the snapshot
bf_session.host = BF_HOST
load_questions()
# bf_set_network(NETWORK_NAME)
bf_init_snapshot(SNAPSHOT_PATH, name=SNAPSHOT_NAME, overwrite=True)

# node_name = "DMZ-LF18"  # The router to change
filter_name = "demo"      # Name of the ACL to change

result = bfq.nodeProperties().answer().frame()
permiturl = 'http://dmz-gitlab.sjc.aristanetworks.com/network/cloudvision/-/raw/master/permit.json'
permit_url = GITLAB_API_URL + "/projects/" + GITLAB_PROJECT_ID + \
    "/repository/files" + "/permit.json" + "/raw?ref=master"
resp = requests.get(permit_url, headers=tokenheader)
permits = resp.json()
for p in permits['permit']:
    headers = HeaderConstraints(dstIps=p["dstIps"],
                                ipProtocols=p["ipProtocols"],
                                dstPorts=p["dstPorts"])
    print(headers)
    answer = bfq.searchFilters(headers=headers,
                               action="permit").answer(
        snapshot=SNAPSHOT_NAME)
    print(answer.frame())
    if answer.frame().empty:
        exit(1)
    else:
        continue

exit(0)
