build: ## Build the container
    docker build . -t fredhsu/pybatfish


run: ## Run container on port configured in `config.env`
    docker run --rm fredhsu/pybatfish
	# docker run -i -t --rm --env-file=./config.env -p=$(PORT):$(PORT) --name="$(APP_NAME)" $(APP_NAME)

push:
    docker push fredhsu/pybatfish

all:
	build push