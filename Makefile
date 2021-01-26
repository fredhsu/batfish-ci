build: src/batfish.py
	docker build -t fredhsu/pybatfish .

run:
	docker run --rm fredhsu/pybatfish

push:
	docker push fredhsu/pybatfish

all: build push