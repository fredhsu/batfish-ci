import os
import json
import requests

# import urllib.request
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

print(bfq.nodeProperties(properties='Configuration_Format').answer())
result = bfq.nodeProperties().answer().frame()
print(result.iloc[0]["IP_Access_Lists"])
permiturl = 'http://dmz-gitlab.sjc.aristanetworks.com/network/cloudvision/-/raw/master/permit.json'
permit_url = GITLAB_API_URL + "/projects/" + GITLAB_PROJECT_ID + \
    "/repository/files" + "/permit.json" + "/raw?ref=master"
resp = requests.get(permit_url, headers=tokenheader)
permits = resp.json()
# https://gitlab.example.com/api/v4/projects/13083/repository/files/app%2Fmodels%2Fkey%2Erb/raw?ref=master"
urllib.request.urlretrieve(permiturl, '/batfish/permit.json')
print("Going to parse the permit")
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


# print("Going to use downloaded file")
# with open('/batfish/permit.json') as permit_file:
#     data = json.load(permit_file)
#     for p in data['permit']:
#         headers = HeaderConstraints(dstIps=p["dstIps"],
#                                     ipProtocols=p["ipProtocols"],
#                                     dstPorts=p["dstPorts"])
#         # print(headers)
#         answer = bfq.searchFilters(headers=headers,
#                                    action="permit").answer(
#                                        snapshot=SNAPSHOT_NAME)
#         print(answer.frame())
#         if answer.frame().empty:
#             exit(1)
#         else:
#             continue

# Check if the intended traffic is already permitted in the current snapshot
# answer = bfq.searchFilters(headers=change_traffic,
#                            filters=filter_name,
#                            nodes=node_name,
#                            action="permit").answer(
#                                snapshot=SNAPSHOT_NAME)
#
# If the frame is empty, then the host traffic given was not allowed and we should fail with exit code 1
# otherwise, exit normally with exit code 0
exit(0)
