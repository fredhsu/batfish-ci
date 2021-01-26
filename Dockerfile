FROM python:3

WORKDIR /batfish
COPY requirements.txt .

ENV BF_HOST="10.90.226.72"
ENV GITLAB_ARTIFACT_URL "http://dmz-gitlab.sjc.aristanetworks.com/network/cloudvision/-/jobs/artifacts/master/raw/demo.zip?job=buildconfigs"
ENV GITLAB_PROJECT_ID="5"
ENV GITLAB_PRIVATE_TOKEN="Rx53465zsbKZcYXYS8xz"

RUN pip install pybatfish requests
COPY src ./src
CMD ["python", "./src/batfish.py"]

