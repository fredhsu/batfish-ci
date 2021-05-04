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

import zipfile

BF_HOST = os.getenv('BF_HOST')
GITLAB_ARTIFACT_URL = os.getenv('GITLAB_ARTIFACT_URL')
NETWORK_NAME = "demo_network"
SNAPSHOT_NAME = "new"
SNAPSHOT_PATH = "/batfish/demo.zip"
GITLAB_PROJECT_ID = os.getenv('GITLAB_PROJECT_ID')
GITLAB_API_URL = "http://dmz-gitlab.sjc.aristanetworks.com/api/v4"
GITLAB_BRANCH = os.getenv('CI_COMMIT_BRANCH')
PRIVATE_TOKEN = os.getenv('GITLAB_PRIVATE_TOKEN')


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


print(f"Executing on branch {GITLAB_BRANCH}")
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

with zipfile.ZipFile(SNAPSHOT_PATH) as myzip:
    with myzip.open('networks/configs/acl.cfg') as myfile:
        acl_text = myfile.read().decode("utf-8")


# Now create the network and initialize the snapshot
bf_session.host = BF_HOST
load_questions()
# bf_set_network(NETWORK_NAME)
# bf_init_snapshot(SNAPSHOT_PATH, name=SNAPSHOT_NAME, overwrite=True)
print(acl_text)
acl_snapshot = bf_session.init_snapshot_from_text(
    acl_text,
    platform="arista",
    snapshot_name="original",
    overwrite=True)

# node_name = "DMZ-LF18"  # The router to change
# filter_name = "demo"      # Name of the ACL to change

result = bfq.nodeProperties().answer().frame()
# permiturl = 'http://dmz-gitlab.sjc.aristanetworks.com/network/cloudvision/-/raw/master/permit.json'
permit_url = GITLAB_API_URL + "/projects/" + GITLAB_PROJECT_ID + \
    "/repository/files" + "/permit.json" + "/raw?ref=" + GITLAB_BRANCH
resp = requests.get(permit_url, headers=tokenheader)
permits = resp.json()
print(f"ACL SNAPSHOT: {acl_snapshot}")
for p in permits['permit']:
    headers = HeaderConstraints(dstIps=p["dstIps"],
                                ipProtocols=p["ipProtocols"],
                                dstPorts=p["dstPorts"])
    # print(headers)
    # answer = bfq.searchFilters(headers=headers,
    #                            action="permit").answer(snapshot=SNAPSHOT_NAME)
    answer2 = bfq.searchFilters(
        headers=headers, action="permit").answer(snapshot=acl_snapshot)
    # print(answer.frame())
    print("*********")
    # print(answer2.frame())
    if answer2.frame().empty:
        print(
            f"{bcolors.FAIL}*** Traffic is unable to reach {headers.dstIps}{bcolors.ENDC}")
        exit(1)
    else:
        print(f"{bcolors.OKGREEN}*** Host {headers.dstIps} is reachable{bcolors.ENDC}")
        continue

exit(0)
