FROM python:3

WORKDIR /batfish
COPY requirements.txt .

ENV BF_HOST="10.90.226.72"

RUN pip install pybatfish
COPY src ./src
CMD ["python", "./src/batfish.py"]

